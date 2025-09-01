# TidyMS2 Batch corrector

A batch corrector plugin for TidyMS2.

Installation
------------

```shell
pip install tidyms2-batch-corrector
```

Usage
-----

This TidyMS2 plugin implements the ``BatchCorrector``, a matrix operator that
corrects time-dependent effects on data. It implements the correction described
[here](https://www.mdpi.com/2218-1989/10/10/416).

The ``BatchCorrector`` can be tuned to fit your experimental design and desired
data quality:

-   `first_n_qc`: Controls how many QC samples are used to estimate the
    intra-batch mean. Use a small value (e.g 1-3) if early QC samples best
    represent unbiased instrument response.
-   `frac`: Sets the LOESS smoothing parameter. If not specified, an optimal
    value is estimated for each feature. You can set a fixed value to control
    the degree of smoothing.
-   `threshold`: Sets the minimum intensity for QC samples to be considered in
    the correction. Increase this value to ignore low-quality or noisy reference
    measurements.
-   `target_groups` and `ref_groups`: Specify which sample groups are corrected
    and which are used as references. By default, experimental samples and technical
    QCs are used.
-   `max_workers`: Controls parallelism for batch correction, useful for large datasets.

Import it and use it as a regular matrix operator:

```python
from tidyms2_batch_corrector import BatchCorrector

bc = BatchCorrector(max_workers=4)
bc.apply(matrix)

```

Below is a minimal example of how to use the BatchCorrector with simulated data:

```python
from tidyms2.core.enums import SampleType
from tidyms2.core.operators.pipeline import Pipeline
from tidyms2.simulation.base import InstrumentResponseSpec
from tidyms2.simulation.lcms import SimulatedLCMSAdductSpec, simulate_data_matrix
from tidyms2.simulation.utils import create_sample_list

from tidyms2_batch_corrector import BatchCorrector

def create_example_matrix():
	"""Create a data matrix with time-dependent variation effects."""
	sample_types = [
		SampleType.TECHNICAL_QC,
		SampleType.SAMPLE,
		SampleType.TECHNICAL_QC,
		SampleType.SAMPLE,
		SampleType.TECHNICAL_QC,
		SampleType.SAMPLE,
		SampleType.TECHNICAL_QC,
	]
	samples = create_sample_list(sample_types, n_batches=3)
	adducts = [
		SimulatedLCMSAdductSpec(
			formula="[C10H20O4]+",
			n_isotopologues=1,
			response=InstrumentResponseSpec(max_sensitivity_loss=0.5, sensitivity_decay=0.25),
		)
	]
	return simulate_data_matrix(adducts, samples)

matrix = create_example_matrix()
matrix.check_status()
pipe = Pipeline("matrix_pipe")
bc = BatchCorrector(id="test-corrector", first_n_qc=1)
pipe.add_operator(bc)
pipe.apply(matrix)
```