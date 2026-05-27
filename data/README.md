# Data folder

Put your dataset in:

```txt
data/raw/
```

Recommended CASAS filename:

```txt
data/raw/casas_aruba.txt
```

The loader accepts either TXT-like CASAS files or CSV files.

## CSV accepted columns

Minimum:

```csv
date,time,sensor_id,message
```

or:

```csv
timestamp,sensor_id,message
```

Optional:

```csv
activity
```

## Optional labels

If you have ground truth anomaly labels, create:

```txt
data/processed/labels.csv
```

with:

```csv
date,y_true,anomaly_type
2010-11-20,0,normal
2010-11-21,1,inactivity
```

Without labels, the project still runs, but classification metrics such as precision, recall and F1 are not computed.
