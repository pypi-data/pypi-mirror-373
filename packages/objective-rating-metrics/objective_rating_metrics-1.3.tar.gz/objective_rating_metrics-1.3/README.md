# Objective Rating Metric for non ambigious signals according to ISO/TS 18571

Python implementation of ISO/TS 18571
https://www.iso.org/standard/85791.html

*ISO/TS 18571:2024 provides validation metrics and rating procedures to be used to calculate the level of correlation between two non-ambiguous signals obtained from a physical test and a computational model, and is aimed at vehicle safety applications. The objective comparison of time-history signals of model and test is validated against various loading cases under different types of physical loads such as forces, moments, and accelerations. However, other applications might be possible too, but are not within the scope of ISO/TS 18571:2024.*

## Installation guide

After cloning this repository, run the following command in your command line

```
python setup.py install
```

This will install the package to your environment. You can then import the package by simply adding the following to the top of your script:

```python
import objective_rating_metrics
```

## Usage
### Example 1
```python
import numpy as np
from objective_rating_metrics.rating import ISO18571

time_ = np.arange(0, 0.150, 0.0001)
ref = np.vstack((time_, np.sin(time_ * 20))).T
comp = np.vstack((time_, np.sin(time_ * 20) * 1.3 + 0.00)).T

iso_rating = ISO18571(reference_curve=ref, comparison_curve=comp)
print(iso_rating.overall_rating())
```
```
>>> 0.713
```
### Example 2
```python
import numpy as np
from objective_rating_metrics.rating import ISO18571

time_ = np.arange(0, 0.150, 0.0001)
# Different start and end times
ref = np.vstack((time_ + 0.02, np.sin(time_ * 20))).T
comp = np.vstack((time_ + 0.03, np.sin(time_ * 20))).T
# Find common start and end time
# Requirement: Common start and end times exist in both arrays and time resolution is the same (10 kHz)
start_time = np.max((ref[0, 0], comp[0, 0]))
end_time = np.min((ref[-1, 0], comp[-1, 0]))
# Get parts of arrays ref and comp between common start time and end time
ref_cut = ref[np.logical_and(ref[:, 0] >= start_time, ref[:, 0] <= end_time), :]
comp_cut = comp[np.logical_and(comp[:, 0] >= start_time, comp[:, 0] <= end_time), :]
iso_rating = ISO18571(reference_curve=ref_cut, comparison_curve=comp_cut)
print(iso_rating.overall_rating())
```
```
>>> 0.815
```
### Important Remarks:
Time channel is not used yet. Time series have to be prepared / preprocessed to meet the following requirements:
- Time resolution of 10 kHz
- Aligned start and end times of the 2 curves (cut sections of the curve which are only available in one of them) 


## Reference and further reading

* [ISO/TS 18571 norm](https://www.iso.org/standard/62937.html)

## Authors
The ISO standard was implemented as python code by Graz University of Technology.
2023, TU Graz
