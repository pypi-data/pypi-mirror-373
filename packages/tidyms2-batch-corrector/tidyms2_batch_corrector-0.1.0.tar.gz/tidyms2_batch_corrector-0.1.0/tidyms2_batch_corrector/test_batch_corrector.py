"""Test LOESS batch corrector."""

from pathlib import Path

import numpy as np
import pytest
from tidyms2.core.enums import SampleType
from tidyms2.core.matrix import DataMatrix
from tidyms2.core.models import FeatureGroup, GroupAnnotation, Sample
from tidyms2.core.operators.pipeline import Pipeline
from tidyms2.simulation.base import InstrumentResponseSpec
from tidyms2.simulation.lcms import SimulatedLCMSAdductSpec, simulate_data_matrix
from tidyms2.simulation.utils import create_sample_list

import tidyms2_batch_corrector.batch_corrector as batch_corrector
from tidyms2_batch_corrector.batch_corrector import BatchCorrectorRequirementUnmet


def create_feature_group(group: int) -> FeatureGroup:
    """Create a dummy feature group."""
    ann = GroupAnnotation(label=group)
    descriptors = {"mz": 100.0}
    return FeatureGroup(group=group, annotation=ann, descriptors=descriptors)


class TestFindInvalidSamplesInBatch:
    """Test find invalid samples."""

    def test_less_qc_than_minimum_required_remove_all_samples(self):
        samples = list()
        for i in range(3):
            sample = Sample.model_validate(
                {
                    "id": f"sample-{i}",
                    "path": Path("."),
                    "meta": {"group": "QC"},
                }
            )
            samples.append(sample)

        qc_groups = ["QC"]
        sample_groups = ["g1", "g2", "g3"]

        expected = [x.id for x in samples]
        actual = batch_corrector._find_invalid_samples_in_batch(samples, sample_groups, qc_groups)
        assert actual == expected

    def test_remove_samples_before_qc(self):
        samples = list()
        for i in range(1, 21):  # starts on non QC samples, end on QC samples
            r = i % 4
            sample = Sample.model_validate(
                {
                    "id": f"sample-{i}",
                    "path": Path("."),
                    "meta": {"group": "QC" if r == 0 else f"g{r}", "order": i},
                }
            )
            samples.append(sample)

        qc_groups = ["QC"]
        sample_groups = ["g1", "g2", "g3"]

        expected = ["sample-1", "sample-2", "sample-3"]
        actual = batch_corrector._find_invalid_samples_in_batch(samples, sample_groups, qc_groups)
        assert actual == expected

    def test_remove_samples_after_qc(self):
        samples = list()
        for i in range(1, 21):  # starts on non QC samples, end on QC samples
            r = i % 4
            sample = Sample.model_validate(
                {
                    "id": f"sample-{i}",
                    "path": Path("."),
                    "meta": {"group": "QC" if r == 0 else f"g{r}", "order": i},
                }
            )
            samples.append(sample)

        qc_groups = ["QC"]
        sample_groups = ["g1", "g2", "g3"]

        expected = ["sample-1", "sample-2", "sample-3"]
        actual = batch_corrector._find_invalid_samples_in_batch(samples, sample_groups, qc_groups)
        assert actual == expected


class TestCheckContigousBlockBatches:
    def test_contigous_block_ok(self):
        samples = list()
        # batches are 0, 0, 0, 0, 0, 1, 1, 1, 1, ...
        for i in range(1, 21):
            sample = Sample.model_validate(
                {
                    "id": f"sample-{i}",
                    "path": Path("."),
                    "meta": {"batch": i // 5, "order": i},
                }
            )
            samples.append(sample)
        batch_corrector._check_batches_order(*samples)

    def test_non_contigous_block_raise_error(self):
        samples = list()
        # batches are 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, ...
        for i in range(1, 21):
            sample = Sample.model_validate(
                {
                    "id": f"sample-{i}",
                    "path": Path("."),
                    "meta": {"batch": i % 5, "order": i},
                }
            )
            samples.append(sample)
        with pytest.raises(batch_corrector.BatchCorrectorRequirementUnmet):
            batch_corrector._check_batches_order(*samples)


class TestFindInvalidFeaturesInBatch:
    """test."""

    @pytest.fixture
    def samples(self):
        groups = [
            "QC",
            "QC",
            "sample",
            "sample",
            "QC",
            "sample",
            "QC",
            "sample",
            "QC",
            "sample",
            "QC",
            "QC",
        ]

        samples = list()
        for i, g in enumerate(groups):
            sample = Sample.model_validate(
                {
                    "id": f"sample-{i}",
                    "path": Path("."),
                    "meta": {"group": g, "order": i},
                }
            )
            samples.append(sample)

        return samples

    @pytest.fixture
    def features(self):
        return [create_feature_group(1), create_feature_group(2)]

    def test_remove_if_invalid_first_block(self, samples, features):
        data = np.array(
            [
                [10.0, 100.0],  # QC
                [10.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [100.0, 10.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [70.0, 100.0],  # QC
            ]
        )
        matrix = DataMatrix(samples, features, data)
        qc_groups = ["QC"]
        sample_groups = ["sample"]
        threshold = 50.0
        actual = batch_corrector._find_invalid_features_in_batch(
            matrix,
            sample_groups,
            qc_groups,
            threshold,
        )
        expected = [features[0].group]
        assert actual == expected

    def test_remove_if_invalid_last_block(self, samples, features):
        data = np.array(
            [
                [70.0, 100.0],  # QC
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [100.0, 10.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [10.0, 100.0],  # QC
                [10.0, 100.0],  # QC
            ]
        )
        matrix = DataMatrix(samples, features, data)
        qc_groups = ["QC"]
        sample_groups = ["sample"]
        threshold = 50.0
        actual = batch_corrector._find_invalid_features_in_batch(
            matrix,
            sample_groups,
            qc_groups,
            threshold,
        )
        expected = [features[0].group]
        assert actual == expected

    def test_remove_if_less_than_required_n_samples_below_threshold(self, samples, features):
        data = np.array(
            [
                [10.0, 100.0],  # QC
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [100.0, 10.0],  # sample
                [10.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [10.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [10.0, 100.0],  # QC
            ]
        )
        matrix = DataMatrix(samples, features, data)
        qc_groups = ["QC"]
        sample_groups = ["sample"]
        threshold = 50.0
        actual = batch_corrector._find_invalid_features_in_batch(
            matrix,
            sample_groups,
            qc_groups,
            threshold,
        )
        expected = [features[0].group]
        assert actual == expected

    def test_feature_ok_if_at_least_one_sample_is_found_on_first_block(self, samples, features):
        data = np.array(
            [
                [70.0, 100.0],  # QC
                [10.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [100.0, 10.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [70.0, 100.0],  # QC
            ]
        )
        matrix = DataMatrix(samples, features, data)
        qc_groups = ["QC"]
        sample_groups = ["sample"]
        threshold = 50.0
        actual = batch_corrector._find_invalid_features_in_batch(
            matrix,
            sample_groups,
            qc_groups,
            threshold,
        )
        expected = []
        assert actual == expected

    def test_feature_ok_if_at_least_one_sample_is_found_on_last_block(self, samples, features):
        data = np.array(
            [
                [70.0, 100.0],  # QC
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [100.0, 10.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [70.0, 100.0],  # QC
                [100.0, 100.0],  # sample
                [10.0, 100.0],  # QC
                [70.0, 100.0],  # QC
            ]
        )
        matrix = DataMatrix(samples, features, data)
        qc_groups = ["QC"]
        sample_groups = ["sample"]
        threshold = 50.0
        actual = batch_corrector._find_invalid_features_in_batch(
            matrix,
            sample_groups,
            qc_groups,
            threshold,
        )
        expected = []
        assert actual == expected


class TestIntraBatchCorrector:
    @pytest.fixture
    def samples(self):
        sample_types = [
            SampleType.TECHNICAL_QC,
            SampleType.SAMPLE,
            SampleType.TECHNICAL_QC,
            SampleType.SAMPLE,
            SampleType.TECHNICAL_QC,
            SampleType.SAMPLE,
            SampleType.TECHNICAL_QC,
        ]
        return create_sample_list(sample_types)

    @pytest.fixture
    def corrector(self, samples):
        return batch_corrector.IntraBatchCorrector(
            target_idx=[0, 1, 2, 3, 4, 5, 6],
            ref_idx=[0, 2, 4, 6],
            order=[x.meta.order for x in samples],
            frac=1.0,
            first_n_qc=1,
        )

    def test_correct_constant_vector(self, samples, corrector):
        adducts = [SimulatedLCMSAdductSpec(formula="[C10H20O4]+", n_isotopologues=1)]
        matrix = simulate_data_matrix(adducts, samples)
        corrector.apply(matrix)

        assert matrix.get_n_samples() == len(samples)
        assert matrix.get_n_features() == 1

    def test_correct_column_with_time_drift_reduces_rmse(self, samples, corrector):
        adducts = [
            SimulatedLCMSAdductSpec(
                formula="[C10H20O4]+",
                n_isotopologues=1,
                response=InstrumentResponseSpec(max_sensitivity_loss=0.5, sensitivity_decay=0.25),
            )
        ]
        matrix = simulate_data_matrix(adducts, samples)
        cv_before = matrix.metrics.cv()
        corrector.apply(matrix)
        cv_after = matrix.metrics.cv()

        assert np.all(cv_before > cv_after)

        assert matrix.get_n_samples() == len(samples)
        assert matrix.get_n_features() == 1

    def test_correct_with_cv(self, samples, corrector):
        corrector.frac = None
        adducts = [
            SimulatedLCMSAdductSpec(
                formula="[C10H20O4]+",
                n_isotopologues=1,
                response=InstrumentResponseSpec(max_sensitivity_loss=0.5, sensitivity_decay=0.25),
            )
        ]
        matrix = simulate_data_matrix(adducts, samples)
        cv_before = matrix.metrics.cv()
        corrector.apply(matrix)
        cv_after = matrix.metrics.cv()

        assert np.all(cv_before > cv_after)

        assert matrix.get_n_samples() == len(samples)
        assert matrix.get_n_features() == 1

    def test_correct_with_fixed_frac(self):
        pass


class TestInterbatchCorrector:
    @pytest.fixture
    def sample_types(self):
        return [
            SampleType.TECHNICAL_QC,
            SampleType.SAMPLE,
            SampleType.TECHNICAL_QC,
            SampleType.SAMPLE,
            SampleType.TECHNICAL_QC,
            SampleType.SAMPLE,
            SampleType.TECHNICAL_QC,
        ]

    def test_invalid_sample_group_name_raises_exception(self, sample_types):
        samples = create_sample_list(sample_types)
        corrector = batch_corrector.BatchCorrector(id="test-corrector", target_groups=["invalid_group"])
        adducts = [SimulatedLCMSAdductSpec(formula="[C10H20O4]+", n_isotopologues=1)]
        matrix = simulate_data_matrix(adducts, samples)
        with pytest.raises(BatchCorrectorRequirementUnmet):
            corrector.apply(matrix)

    def test_invalid_qc_group_name_raises_exceptions(self, sample_types):
        samples = create_sample_list(sample_types)
        corrector = batch_corrector.BatchCorrector(id="test-corrector", ref_groups=["invalid_group"])
        adducts = [SimulatedLCMSAdductSpec(formula="[C10H20O4]+", n_isotopologues=1)]
        matrix = simulate_data_matrix(adducts, samples)
        with pytest.raises(BatchCorrectorRequirementUnmet):
            corrector.apply(matrix)

    def test_single_batch_ok(self, sample_types):
        samples = create_sample_list(sample_types, n_batches=3)
        adducts = [
            SimulatedLCMSAdductSpec(
                formula="[C10H20O4]+",
                n_isotopologues=1,
                response=InstrumentResponseSpec(max_sensitivity_loss=0.5, sensitivity_decay=0.25),
            )
        ]
        matrix = simulate_data_matrix(adducts, samples)
        matrix.check_status()  # set matrix status to nan imputted
        corrector = batch_corrector.BatchCorrector(id="test-corrector", first_n_qc=1)
        cv_before = matrix.metrics.cv()
        corrector.apply(matrix)
        cv_after = matrix.metrics.cv()

        matrix.check_status()
        assert matrix.status.missing_imputed
        assert np.all(cv_before > cv_after)

        assert matrix.get_n_samples() == len(samples)
        assert matrix.get_n_features() == 1

    def test_multiple_batch_ok(self, sample_types):
        samples = create_sample_list(sample_types, n_batches=3)
        adducts = [
            SimulatedLCMSAdductSpec(
                formula="[C10H20O4]+",
                n_isotopologues=1,
                response=InstrumentResponseSpec(
                    max_sensitivity_loss=0.5,
                    sensitivity_decay=0.25,
                    interbatch_variation=0.5,
                ),
            )
        ]
        matrix = simulate_data_matrix(adducts, samples)
        matrix.check_status()  # set matrix status to nan imputted
        corrector = batch_corrector.BatchCorrector(id="test-corrector", first_n_qc=1)
        cv_before = matrix.metrics.cv()
        corrector.apply(matrix)
        cv_after = matrix.metrics.cv()

        matrix.check_status()
        assert matrix.status.missing_imputed
        assert np.all(cv_before > cv_after)

        assert matrix.get_n_samples() == len(samples)
        assert matrix.get_n_features() == 1

    def test_batch_corrector_in_pipeline(self, sample_types):
        samples = create_sample_list(sample_types)
        adducts = [
            SimulatedLCMSAdductSpec(
                formula="[C10H20O4]+",
                n_isotopologues=1,
                response=InstrumentResponseSpec(max_sensitivity_loss=0.5, sensitivity_decay=0.25),
            )
        ]
        matrix = simulate_data_matrix(adducts, samples)
        matrix.check_status()  # set matrix status to nan imputted
        corrector = batch_corrector.BatchCorrector(id="test-corrector", first_n_qc=1)
        pipe = Pipeline("test-pipe")
        pipe.add_operator(corrector)
        cv_before = matrix.metrics.cv()
        pipe.apply(matrix)
        cv_after = matrix.metrics.cv()

        matrix.check_status()
        assert matrix.status.missing_imputed
        assert np.all(cv_before > cv_after)

        assert matrix.get_n_samples() == len(samples)
        assert matrix.get_n_features() == 1
