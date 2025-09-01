"""LOESS batch corrector implementation."""

from logging import getLogger
from typing import Self

import numpy
import pydantic
from scipy.interpolate import interp1d
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import GridSearchCV, LeaveOneOut, ShuffleSplit
from sklearn.utils.validation import check_X_y
from statsmodels.nonparametric.smoothers_lowess import lowess
from tidyms2.core.dataflow import DataMatrixProcessStatus
from tidyms2.core.enums import MSInstrument, Polarity, SampleType, SeparationMode
from tidyms2.core.matrix import DataMatrix, FeatureVector
from tidyms2.core.models import Sample
from tidyms2.core.operators.matrix import ColumnTransformer, MatrixTransformer
from tidyms2.core.utils.numpy import FloatArray

logger = getLogger(__name__)

MIN_N_QC_SAMPLE_LOESS = 4  # the minimum number of QC samples required for LOESS smoothing


class BatchCorrectorRequirementUnmet(ValueError):
    """Exception raised when the pre conditions for using the batch corrector are not meet."""


class BatchCorrector(MatrixTransformer):
    r"""Correct time-dependent variations in instrumental response.

    The correction is applied as follows:

    1.  Group samples according to their analytical batch.
    2.  For each feature in a batch, model the time-dependent variation
        using reference samples (usually technical QC samples). Apply
        the correction factor to target samples (experimental samples).
    3.  Compute an inter-batch mean using reference samples and normalize
        features so the feature mean in reference samples is equal across
        batches.

    A detailed explanation of the correction algorithm can be found here:

    - doi:10.3390/metabo10100416

    To apply this correction, several preconditions must be met. First, as the
    intra-batch correction factor is computed by interpolating reference samples,
    all target samples must be surrounded by reference samples. It is recommended
    to have more than one QC sample at the beginning and at the end of each batch.

    The intra-batch correction factor is computed using LOESS smoothing, which
    requires a minimum of four observations to work. Also, the feature intensity
    must be above a detection threshold. Features are removed from the matrix
    before applying the correction if they do not meet these conditions:

    1.  There is at least one reference sample above the detection threshold that
        was measured before all target samples in each batch.
    2.  There is at least one reference sample above the detection threshold that
        was measured after all target samples in each batch.
    3.  There are at least four reference samples above the detection threshold in
        each batch.

    After these three checks, the remaining samples and features are suitable
    for LOESS batch correction.

    A final consideration is how to estimate the intra-batch mean for each
    feature. This value is usually computed as the mean of the QC values in a
    batch, but if the temporal bias becomes stronger as more samples are
    analyzed, a better estimation can be obtained using the average of the
    first samples analyzed in a batch. To this end, the `first_n_qc` parameter
    controls how many QC samples are used to estimate the intra-batch mean.

    """

    target_groups: list[str] | None = None
    """The sample groups that will be corrected. If not defined, samples with
    ``SampleType.SAMPLE`` sample type will be set as target."""

    ref_groups: list[str] | None = None
    """The list of groups used to compute the correction factor. If not
    defined, samples with ``SampleType.TECHNICAL_QC`` sample type will be set
    as reference samples."""

    frac: float | None = None
    """The LOESS smoother frac parameter. If this parameter is defined, it
    will be used as the frac parameter for all features. Otherwise, the optimal
    frac for each feature will be estimated by using a grid search."""

    threshold: float = 0.0
    """The detection threshold for reference samples. Reference samples with
    values below this threshold will be ignored."""

    first_n_qc: pydantic.PositiveInt | None = None
    """If defined, the intra-batch mean is computed using the first n reference
    samples in the batch."""

    max_workers: int | None = None
    """The maximum number of parallel workers."""

    def get_expected_status_in(self) -> DataMatrixProcessStatus:
        return DataMatrixProcessStatus(missing_imputed=True)

    def get_expected_status_out(self) -> DataMatrixProcessStatus:
        return DataMatrixProcessStatus(missing_imputed=True)

    @classmethod
    def from_defaults(cls, instrument: MSInstrument, separation: SeparationMode, polarity: Polarity):
        return cls()

    def _transform_matrix(self, data: DataMatrix) -> FloatArray:
        if self.target_groups is None:
            sample_groups = _get_groups_from_sample_type(data, SampleType.SAMPLE)
        else:
            _validate_groups(data, self.target_groups)
            sample_groups = self.target_groups

        if self.ref_groups is None:
            ref_groups = _get_groups_from_sample_type(data, SampleType.TECHNICAL_QC)
        else:
            _validate_groups(data, self.ref_groups)
            ref_groups = self.ref_groups

        _check_batches_order(*data.samples)
        self._prepare_data(data, sample_groups, ref_groups)
        target_groups = sample_groups + ref_groups
        corrected = self._apply_intra_batch_correction(data, target_groups, ref_groups)
        corrected = self._apply_inter_batch_correction(corrected, target_groups, ref_groups)

        return corrected.get_data()

    def _prepare_data(self, data: DataMatrix, sample_groups: list[str], qc_groups: list[str]) -> None:
        invalid_samples = _find_invalid_samples(data, sample_groups, qc_groups)
        if invalid_samples:
            invalid_samples_str = ", ".join(x for x in invalid_samples)
            logger.warning(f"Batch corrector will remove invalid samples ({invalid_samples_str})")
        data.remove_samples(*invalid_samples)

        invalid_features = _find_invalid_features(data, sample_groups, qc_groups, self.threshold)
        if invalid_features:
            invalid_features_str = ", ".join(str(x) for x in invalid_features)
            logger.warning(f"Batch corrector will remove invalid features ({invalid_features_str})")
        data.remove_features(*invalid_features)

    def _apply_intra_batch_correction(
        self, data: DataMatrix, target_groups: list[str], qc_groups: list[str]
    ) -> DataMatrix:
        batches = list()
        for _, batch_samples in data.query.group_by("batch").fetch_sample_ids():
            batch = data.create_submatrix(batch_samples)

            batch_target_sample_ids = batch.query.filter(group=target_groups).fetch_sample_ids()[0][1]
            batch_ref_sample_ids = batch.query.filter(group=qc_groups).fetch_sample_ids()[0][1]

            corrector = IntraBatchCorrector(
                max_workers=self.max_workers,
                ref_idx=batch.get_sample_index(*(x for x in batch_ref_sample_ids)),
                target_idx=batch.get_sample_index(*(x for x in batch_target_sample_ids)),
                order=[x.meta.order for x in batch.samples],
                first_n_qc=self.first_n_qc,
            )
            corrector.apply(batch)
            batches.append(batch)

        return DataMatrix.combine(*batches)

    def _apply_inter_batch_correction(
        self,
        data: DataMatrix,
        target_groups: list[str],
        qc_groups: list[str],
    ) -> DataMatrix:
        batches = list()
        inter_batch_qc_sum = numpy.zeros(shape=(1, data.get_n_features()), dtype=float)
        qc_count = 0
        for _, batch_samples in data.query.group_by("batch").fetch_sample_ids():
            batch = data.create_submatrix(batch_samples)
            batch_qc_sum, batch_n_qc = _divide_target_samples_by_intra_batch_mean(batch, qc_groups, target_groups)
            qc_count += batch_n_qc
            inter_batch_qc_sum += batch_qc_sum
            batches.append(batch)

        combined = DataMatrix.combine(*batches)
        inter_batch_mean = inter_batch_qc_sum / qc_count
        _multiply_target_samples_by_inter_batch_mean(combined, inter_batch_mean, target_groups)

        return combined


class IntraBatchCorrector(ColumnTransformer):
    """Correct samples from a single batch."""

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    target_idx: list[int]
    """The list sample indices to be corrected."""

    ref_idx: list[int]
    """The list sample indices that to generate the correction."""

    order: list[int]
    """The order of each sample in the array."""

    frac: float | None = None
    """The frac parameter, passed to the LOESS smoother. If this parameter is defined,
    it will be used as the frac parameter for all features. Otherwise, the optimal value
    for each feature will be estimated by using using a grid search."""

    threshold: float = 0.0
    """The detection threshold for QC samples."""

    first_n_qc: pydantic.PositiveInt | None = None
    """If defined, the intra batch mean for each feature is computed using the first n
    QC samples in the batch."""

    def get_expected_status_in(self) -> DataMatrixProcessStatus:
        return DataMatrixProcessStatus(missing_imputed=True)

    def get_expected_status_out(self) -> DataMatrixProcessStatus:
        return DataMatrixProcessStatus(missing_imputed=True)

    @classmethod
    def from_defaults(cls, instrument: MSInstrument, separation: SeparationMode, polarity: Polarity):
        """Not required as it is an internal operator."""
        raise NotImplementedError

    @pydantic.model_validator(mode="after")
    def _ensure_first_n_qc_lower_than_n_qc_in_batch(self) -> Self:
        msg = "`first_n_qc` must be lower than the number of QC samples in the batch."
        assert self.first_n_qc is None or self.first_n_qc < len(self.order), msg
        return self

    @pydantic.model_validator(mode="after")
    def _ensure_ref_index_are_in_target_index(self) -> Self:
        assert set(self.ref_idx).issubset(self.target_idx), "reference indices must also be target indices"
        return self

    def _transform_column(self, column: FeatureVector) -> FeatureVector:
        ref_order = numpy.array([self.order[i] for i in self.ref_idx])[:, numpy.newaxis]
        ref_int = column.data[self.ref_idx]
        target_order = numpy.array([self.order[i] for i in self.target_idx])[:, numpy.newaxis]

        estimator = _get_estimator(self.frac, len(self.ref_idx))
        estimator.fit(ref_order, ref_int)

        if not isinstance(estimator, _LoessEstimator):
            estimator = estimator.best_estimator_

        if self.first_n_qc is not None:
            ref_mean_int = ref_int[: self.first_n_qc].mean()
        else:
            ref_mean_int = ref_order.mean()

        # the predicted intensity of reference sample at fixee sample order
        ref_int_in_target = estimator.predict(target_order)

        factor = numpy.zeros_like(ref_int_in_target)
        # correct nan in zero values and negative values generated during LOESS
        factor = numpy.divide(ref_mean_int, ref_int_in_target, out=factor, where=ref_int_in_target > 0)

        column.data[self.target_idx] *= factor
        return column


class _LoessEstimator(BaseEstimator, RegressorMixin):
    """Intra-batch corrector implementation using sklearn.

    :param frac: the fraction of samples used for local regressions

    """

    def __init__(self, frac: float = 0.66):
        self.frac = frac
        self.interpolator_ = None

    def fit(self, X, y):
        X, y = check_X_y(X, y)  # Check that X and y have correct shape
        x = X.flatten()
        y_fit = lowess(y, x, frac=self.frac, is_sorted=True, return_sorted=False)
        self.interpolator_ = interp1d(x, y_fit, bounds_error=False)
        return self

    def predict(self, X):
        if self.interpolator_ is None:
            raise NotFittedError
        xf = X.flatten()
        x_interp = self.interpolator_(xf)
        return x_interp


def _multiply_target_samples_by_inter_batch_mean(
    matrix: DataMatrix,
    inter_batch_mean: FloatArray,
    target_groups: list[str],
) -> None:
    assert inter_batch_mean.shape == (1, matrix.get_n_features())
    target_sample_ids = matrix.query.filter(group=target_groups).fetch_sample_ids()[0][1]

    data = matrix.get_data()
    target_idx = matrix.get_sample_index(*target_sample_ids)
    data[target_idx, :] *= inter_batch_mean
    matrix.set_data(data)


def _divide_target_samples_by_intra_batch_mean(
    batch: DataMatrix,
    ref_groups: list[str],
    target_groups: list[str],
) -> tuple[FloatArray, int]:
    ref_sample_ids = batch.query.filter(group=ref_groups).fetch_sample_ids()[0][1]
    batch_qc_data = batch.get_data(sample_ids=ref_sample_ids)
    intra_batch_mean = batch_qc_data.mean(axis=0, keepdims=True)

    target_sample_ids = batch.query.filter(group=target_groups).fetch_sample_ids()[0][1]
    patch = numpy.zeros(shape=(len(target_sample_ids), batch.get_n_features()), dtype=batch.get_data().dtype)
    numpy.divide(batch.get_data(sample_ids=target_sample_ids), intra_batch_mean, out=patch, where=intra_batch_mean > 0)

    data = batch.get_data()
    target_idx = batch.get_sample_index(*target_sample_ids)
    data[target_idx, :] = patch

    batch.set_data(data)

    return batch_qc_data.sum(axis=0, keepdims=True), len(ref_sample_ids)


def _find_invalid_samples(matrix: DataMatrix, sample_groups: list[str], qc_groups: list[str]) -> list[str]:
    """Find samples that cannot be corrected using LOESS batch correction.

    :param matrix: the data matrix to correct
    :param sample_groups: the sample groups to correct. If not defined, use all samples with `sample` type.
    :param qc_groups: the sample groups that generate the correction. If not defined, use all samples with `qc` type.
    :return: a list of sample id that need to be removed before applying the LOESS correction

    """
    invalid_samples = list()

    for _, sample_ids in matrix.query.group_by("batch").fetch_sample_ids():
        batch_samples = [matrix.get_sample(x) for x in sample_ids]
        invalid_samples.extend(_find_invalid_samples_in_batch(batch_samples, sample_groups, qc_groups))

    return invalid_samples


def _find_invalid_samples_in_batch(samples: list[Sample], sample_groups: list[str], qc_groups: list[str]) -> list[str]:
    """Find invalid samples in a single batch."""
    qc_samples = [x for x in samples if x.meta.group in qc_groups]
    batch = samples[0].meta.batch  # all samples have the same batch

    if len(qc_samples) < MIN_N_QC_SAMPLE_LOESS:
        logger.info(
            f"The number of QC samples in batch {batch} is lower than the minimum required ({MIN_N_QC_SAMPLE_LOESS})."
            " for LOESS correction. Removing all samples in the batch."
        )
        return [x.id for x in samples]

    # remove samples that are not bracketed by QC samples
    first_qc_order = qc_samples[0].meta.order
    last_qc_order = qc_samples[-1].meta.order
    correct_samples = [x for x in samples if x.meta.group in sample_groups]
    return [x.id for x in correct_samples if not (first_qc_order < x.meta.order < last_qc_order)]


def _check_batches_order(*samples: Sample) -> None:
    """Ensure that samples with the same batch number form contiguous blocks.

    :param samples: a list of samples ordered by sample order.

    """
    batches = set()
    current: int | None = None
    for sample in samples:
        if current is None:
            current = sample.meta.batch
            batches.add(current)

        if sample.meta.batch != current:
            if sample.meta.batch in batches:
                raise BatchCorrectorRequirementUnmet("Sample batches do not form contiguous blocks.")
            current = sample.meta.batch
            batches.add(sample.meta.batch)


def _get_groups_from_sample_type(matrix: DataMatrix, type_: SampleType) -> list[str]:
    """Retrieve the list of sample groups associated with a sample type."""
    query_result = matrix.query.filter(type=type_).fetch_sample_ids()
    if not query_result or not query_result[0][1]:
        raise BatchCorrectorRequirementUnmet(f"No samples found with type {type_}")
    sample_ids = query_result[0][1]
    return list({matrix.get_sample(x).meta.group for x in sample_ids})


def _validate_groups(matrix: DataMatrix, groups: list[str]) -> None:
    query_result = matrix.query.filter(group=groups).fetch_sample_ids()
    if not query_result or not query_result[0][1]:
        raise BatchCorrectorRequirementUnmet(f"No samples found with groups {groups}")


def _find_invalid_features(
    matrix: DataMatrix, sample_groups: list[str], qc_groups: list[str], threshold: float
) -> set[int]:
    """Find samples that cannot be corrected using LOESS batch correction.

    :param matrix: the data matrix to correct
    :param sample_groups: the sample groups to correct.
    :param qc_groups: the sample groups that generate the correction.
    :return: a list of sample id that need to be removed before applying the LOESS correction

    """
    invalid_features = set()

    for _, sample_ids in matrix.query.group_by("batch").fetch_sample_ids():
        batch = matrix.create_submatrix(sample_ids)
        invalid_features.update(_find_invalid_features_in_batch(batch, sample_groups, qc_groups, threshold))
    return invalid_features


def _find_invalid_features_in_batch(
    matrix: DataMatrix, sample_groups: list[str], qc_groups: list[str], threshold: float
) -> list[int]:
    """Find features that do not meet the minimum requirements for LOESS correction.

    The following checks are performed:

    -   the first block of QC samples in a batch, i.e., QC samples measured before any assay sample,
        must contain at least one value above the detection `threshold`.
    -   the last block of QC samples in the batch, i.e., QC samples measured after all assay samples,
        must contain at least one value above the detection `threshold`.
    -   At least 4 QC samples must be above the detection threshold.

    The first two requirements are needed to perform interpolation of the batch correction factor. The last
    requirement ensures that the LOESS smoothing can be applied on QC samples.

    """
    all_samples = matrix.samples
    assay_samples = [x for x in matrix.samples if x.meta.group in sample_groups]

    batch = all_samples[0].meta.batch

    if not assay_samples:
        raise ValueError(f"No samples in sample groups `{sample_groups}` found in batch {batch}.")

    # first block checks
    first_sample_order = assay_samples[0].meta.order
    first_block_samples = [x for x in all_samples if x.meta.group in qc_groups and x.meta.order < first_sample_order]
    assert first_block_samples
    first_block_data = matrix.get_data([x.id for x in first_block_samples])
    qc_missing_in_first_block = numpy.all(first_block_data < threshold, axis=0)

    # last block checks
    last_assay_sample_order = assay_samples[-1].meta.order
    last_block_samples = [
        x for x in all_samples if x.meta.group in qc_groups and x.meta.order > last_assay_sample_order
    ]
    assert last_block_samples
    last_block_data = matrix.get_data([x.id for x in last_block_samples])
    qc_missing_in_last_block = numpy.all(last_block_data < threshold, axis=0)

    # batch check
    qc_samples = [x for x in all_samples if x.meta.group in qc_groups]
    qc_data = matrix.get_data([x.id for x in qc_samples])
    n_qc_below_required = numpy.sum(qc_data >= threshold, axis=0) < MIN_N_QC_SAMPLE_LOESS

    remove_idx = numpy.where(qc_missing_in_first_block | qc_missing_in_last_block | n_qc_below_required)[0]
    features = matrix.features
    return [features[idx.item()].group for idx in remove_idx]


def _get_estimator(frac: float | None, size: int):
    if frac is None:
        cv = ShuffleSplit(n_splits=5, test_size=0.2) if size > 15 else LeaveOneOut()

        min_frac = min(MIN_N_QC_SAMPLE_LOESS / size, 1.0)
        # set the grid size to 5 for small and large QCs numbers
        if size < 9:
            frac_grid = numpy.arange(MIN_N_QC_SAMPLE_LOESS, size + 1) / size
        else:
            n_points = 5
            frac_grid = numpy.linspace(min_frac, 1.0, n_points)

        grid = {"frac": frac_grid}

        return GridSearchCV(
            _LoessEstimator(),
            grid,
            cv=cv,
            scoring="neg_mean_squared_error",
        )
    else:
        return _LoessEstimator(frac)
