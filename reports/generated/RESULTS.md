# Measured preliminary results
All scores are provisional where independent annotation review is pending.

| Split | Method | CLAHE | Images | Precision | Recall | F1 | MAE | Exact count | Median ms |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| development | hough | off | 36 | 0.993 | 0.958 | 0.975 | 0.417 | 75.0% | 52.3 |
| development | hough | on | 36 | 0.756 | 0.980 | 0.853 | 2.861 | 77.8% | 71.4 |
| development | contours | off | 36 | 0.959 | 0.608 | 0.744 | 3.111 | 25.0% | 37.0 |
| development | contours | on | 36 | 0.928 | 0.676 | 0.783 | 2.306 | 30.6% | 41.7 |
| validation | hough | off | 12 | 0.991 | 0.947 | 0.969 | 0.583 | 66.7% | 55.3 |
| validation | hough | on | 12 | 0.838 | 0.956 | 0.893 | 2.167 | 66.7% | 64.6 |
| validation | contours | off | 12 | 0.953 | 0.719 | 0.820 | 2.333 | 33.3% | 40.1 |
| validation | contours | on | 12 | 0.922 | 0.728 | 0.814 | 2.000 | 41.7% | 44.4 |

Touching-coin results are not evaluated (zero available touching images), not zero performance.
Development data were used for small parameter exploration; those results are not held-out estimates.
Validation results, if present, are a separate small check after development settings were fixed. No final-test images were run.
