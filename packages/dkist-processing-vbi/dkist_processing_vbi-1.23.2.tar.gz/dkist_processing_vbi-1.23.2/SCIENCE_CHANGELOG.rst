v1.1.0 (2022-12-15)
===================




- Don't re-compress already compressed data that are processed at the summit. This ensures L1 files served by the Data Center are *exactly* the same as those processed on the summit. (`#39 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/39>`__)
