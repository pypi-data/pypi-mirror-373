# pymechlab
Python Package for Mechanical Laboratory Testing

This package is used for calculating the A-basis and B-Basis mechanical properties from mechanical laboratory test results and data.

An example from CMH-17 is shown below.

## Input file 'cmh17_pg_8-87.json':

```json
{
    "Material": "Graphite/Epoxy",
    "Property": "Compression Strength",
    "Test Environment": "ETW",
    "Program": "Qualification Data",
    "batches": {
        "1": {
            "datasets": {
                "1": {
                    "coupons": {
                        "1": 106.358,
                        "2": 105.899,
                        "3": 88.464,
                        "4": 103.902,
                        "5": 80.206,
                        "6": 109.2,
                        "7": 61.014
                    }
                }
            }
        },
        "2": {
            "datasets": {
                "2": {
                    "coupons": {
                        "1": 99.321,
                        "2": 115.862,
                        "3": 82.613,
                        "4": 85.369,
                        "5": 115.802,
                        "6": 44.322,
                        "7": 117.328,
                        "8": 88.678
                    }
                }
            }
        },
        "3": {
            "datasets": {
                "3": {
                    "coupons": {
                        "1": 107.677,
                        "2": 108.960,
                        "3": 116.123,
                        "4": 80.233,
                        "5": 106.146,
                        "6": 104.668,
                        "7": 104.235
                    }
                }
            }
        }
    }
}
```

## Python script 'cmh17_script.py':

```python
#%%
# Import Dependencies
from IPython.display import display_markdown

from pymechlab.classes.cmh17statistics import pool_from_json

#%%
# Import JSON File
jsonfilepath  = '../files/cmh17_pg_8-87.json'
pool = pool_from_json(jsonfilepath)
display_markdown(pool)

#%%
# Import JSON File
jsonfilepath  = '../files/cmh17_pg_8-92.json'
pool = pool_from_json(jsonfilepath)
display_markdown(pool)
```

## The output results in markdown are as follows:

| Pool Information    |                Value |
| :------------------ | -------------------: |
| Material            |       Graphite/Epoxy |
| Property            | Compression Strength |
| Test Environment    |                  ETW |
| Program             |   Qualification Data |
| Number of Specimens |                   22 |
| Number of Batches   |                    3 |
| Number of Data Sets |                    3 |
| Minimum Value       |               44.322 |
| Maximum Value       |              117.328 |

<br/>

| Batch ID | Data Set ID | Coupon ID | Data Values | Before Pooling | After Pooling |
| :------: | :---------: | :-------: | :---------: | :------------: | :-----------: |
| 1        | 1           | 1         |     106.358 |                |               |
| 1        | 1           | 2         |     105.899 |                |               |
| 1        | 1           | 3         |      88.464 |                |               |
| 1        | 1           | 4         |     103.902 |                |               |
| 1        | 1           | 5         |      80.206 |                |               |
| 1        | 1           | 6         |       109.2 |                |               |
| 1        | 1           | 7         |      61.014 |                |               |
| 2        | 2           | 1         |      99.321 |                |               |
| 2        | 2           | 2         |     115.862 |                |               |
| 2        | 2           | 3         |      82.613 |                |               |
| 2        | 2           | 4         |      85.369 |                |               |
| 2        | 2           | 5         |     115.802 |                |               |
| 2        | 2           | 6         |      44.322 |                | X             |
| 2        | 2           | 7         |     117.328 |                |               |
| 2        | 2           | 8         |      88.678 |                |               |
| 3        | 3           | 1         |     107.677 |                |               |
| 3        | 3           | 2         |      108.96 |                |               |
| 3        | 3           | 3         |     116.123 |                |               |
| 3        | 3           | 4         |      80.233 | X              |               |
| 3        | 3           | 5         |     106.146 |                |               |
| 3        | 3           | 6         |     104.668 |                |               |
| 3        | 3           | 7         |     104.235 |                |               |

<br/>

| Anderson k-Sample Test        |    Value |
| :---------------------------- | -------: |
| ADK Statistic                 | 0.328731 |
| AD Critical (&alpha; = 0.250) | 0.449259 |
| AD Critical (&alpha; = 0.100) |  1.30528 |
| AD Critical (&alpha; = 0.050) |  1.94342 |
| AD Critical (&alpha; = 0.025) |  2.57697 |
| AD Critical (&alpha; = 0.010) |  3.41635 |
| AD Critical (&alpha; = 0.005) |   4.0721 |
| AD Critical (&alpha; = 0.001) |  5.56419 |
| ADK p-value                   |   0.2888 |

<br/>

| Normal Distribution Statistics    |      Value |
| :-------------------------------- | ---------: |
| Observed Significance Level (OSL) | 0.00605107 |
| Mean                              |    96.9264 |
| Standard Deviation                |    18.8048 |
| Coefficient of Variation (%)      |   19.4012% |
| B-Basis Value                     |    61.4527 |
| A-Basis Value                     |    36.1265 |

<br/>

| Log Normal Distribution Statistics |       Value |
| :--------------------------------- | ----------: |
| Observed Significance Level (OSL)  | 0.000307372 |
| Log Mean                           |     4.55097 |
| Log Standard Deviation             |    0.234756 |
| B-Basis Value                      |     60.8328 |
| A-Basis Value                      |     44.3433 |

<br/>

| Two Param Weibull Distribution Statistics |     Value |
| :---------------------------------------- | --------: |
| Observed Significance Level (OSL)         | 0.0218837 |
| Scale Parameter                           |   103.847 |
| Shape Parameter                           |   7.28576 |
| B-Basis Value                             |    66.864 |
| A-Basis Value                             |   43.1806 |

<br/>

| Non-Parametric Statistics  |     Value |
| :------------------------- | --------: |
| B-Basis Method             | Hans-Koop |
| A-Basis Method             | Hans-Koop |
| B-Basis Rank               |        10 |
| A-Basis Rank               |       N/A |
| B-Basis Hans-Koop k Factor |   1.18418 |
| A-Basis Hans-Koop k Factor |    2.2602 |
| B-Basis Value              |   37.8853 |
| A-Basis Value              |   12.9966 |

<br/>

| Parameter |    Value |
| :-------- | -------: |
| Fcalc     |  1.50529 |
| pcalc     | 0.247263 |
| Fcrit     |  4.67443 |

<br/>

| ANOVA Statistics                               |   Value |
| :--------------------------------------------- | ------: |
| Sample Between-batch Mean Sq. (MSB)            | 257.302 |
| Error Mean Square (MSE)                        | 363.761 |
| Estimate of Pop. Std. Deviation(s)             | 18.6873 |
| B-Basis Tolerance Limit Factor (T<sub>B</sub>) | 1.88641 |
| A-Basis Tolerance Limit Factor (T<sub>A</sub>) |  3.2332 |
| B-Basis Value                                  | 61.6745 |
| A-Basis Value                                  | 36.5067 |

<br/>
