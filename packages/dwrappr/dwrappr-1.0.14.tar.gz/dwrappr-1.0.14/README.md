# 📦 dwrappr
[![pypi](https://img.shields.io/pypi/v/dwrappr.svg)](https://pypi.org/project/dwrappr/)
[![versions](https://img.shields.io/pypi/pyversions/dwrappr.svg)](https://git-ce.rwth-aachen.de/kls/dwrappr)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://git-ce.rwth-aachen.de/kls/dwrappr/-/blob/main/LICENSE?ref_type=heads)

A lightweight and extensible Python package for managing data, tailored for researchers working with structured data.
In addition to general data management features, the package introduces a data structure specifically optimized for ML
research. This common format enables researchers to efficiently test new algorithms and methods,
streamlining collaboration and ensuring consistency in data management across projects.

## 🧩 Features

- 🗃️ Consistent dataset object structure for handling structured data in ML use cases
- 🔄 Support for building a file-based internal dataset collaboration platform for researchers 
- 🧰 General utilities for managing data like saving and loading

## 🚀 Quickstart
For executing the quickstart examples and get an overview of [dwrappr's](https://pypi.org/project/dwrappr/) functionalities, please have a look at [IEEE_examples](examples/IEEE_examples.ipynb).

Additional functionalities are showcased in:
- **loading_dataset_from_file.py**: Shows how to load a dataset from an existing dataset file
- **scanning_folder_for_datasets.py**: Shows how to scann a folder vor available datasets
- **dataset_functionalities.py** : Shows some of the main functionalities of the DataSet class.

## 👀 Functionality Ipnsights
### Scan folder for dataset
```python
DATASET_FOLDER = "./data/datasets/"
available_datasets = DataSet.get_available_datasets_in_folder(
    DATASET_FOLDER
)
available_datasets.T
```
### Loading specific dataset
```python
DATASET_FILEPATH = "./data/datasets/manufacturing_process_ds.joblib"
ds = DataSet.load(DATASET_FILEPATH)
```

### Generating dataset from raw data
```python
RAW_DATA_FILEPATH= "./data/raw_data.csv"
#load raw data into pandas.DataFrame
df = pd.read_csv(RAW_DATA_FILEPATH)
"""
<some manual dataset preprocessing steps
like dropping missing values and chaning dtypes>
"""
#define metaData
meta = DataSetMeta(
    name = "example_dataset",
    synthetic_data=True,
    time_series=False,
    feature_names=["feature"],
    target_names=["target"]
)
#generate DataSet
ds = DataSet.from_dataframe(
    df=df,
    meta=meta
)
#saving dataset
ds.save("./data/example_dataset.joblib", drop_meta_json=True)
```

### Split dataset 
(train/test-split)
```python
import numpy as np
n_instances = 100
# Create the 'product_id' feature with 3 different categorical values
product_ids = np.random.choice(['1001', '2002', '3003', '4004', '5005', '6006', '7007'], size=n_instances)
# Generate two additional numeric features
feature_1 = np.random.rand(n_instances) * 100  # Random numbers between 0 and 100
feature_2 = np.random.rand(n_instances) * 50   # Random numbers between 0 and 50
# Generate a numeric target
target = feature_1 * 0.5 + feature_2 * 0.3 + np.random.randn(n_instances) * 5  # Adding some noise
# Create a DataFrame
df = pd.DataFrame({
    'product_id': product_ids,
    'feature_1': feature_1,
    'feature_2': feature_2,
    'target': target
})
```
```python
ds = DataSet.from_dataframe(
    df=df,
    meta = DataSetMeta(
        name = "example_dataset",
        synthetic_data=True,
        time_series=False,
        feature_names=["product_id", "feature_1", "feature_2"],
        target_names=["target"]
    )
)
```
```python
train_ds, test_ds = ds.split_dataset(
    first_ds_size=0.5,
    shuffle=True,
    group_by_features=["product_id"]
)
```

## 📄 Help
See [Documentation](https://dwrappr-725c08.pages.git-ce.rwth-aachen.de/) for details.

# 🛠️ Package Installation
- full version: ```pip install dwrappr```
- light version (excluding sklearn library): ```pip install dwrappr[light]```

(keep package updated with ```pip install dwrappr --upgrade```)



## 🔧 Maintainer
This project is maintained by [Nils](https://git-ce.rwth-aachen.de/nils.klasen)