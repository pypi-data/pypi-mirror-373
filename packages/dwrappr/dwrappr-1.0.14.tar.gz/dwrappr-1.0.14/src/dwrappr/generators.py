from sklearn.datasets import make_regression

from .dataset import DataSet, DataSetMeta


def sklearn_regression(**kwargs) -> 'DataSet':
    """
    Generates a regression dataset using the make_regression function from sklearn and returns it
    as a DataSet object. The dataset includes predefined features and target names, and is
    tagged as synthetic and non-time-series data.

    Args:
        **kwargs: Parameters to control the regression dataset generation behavior. These parameters are passed directly to the make_regression function. For further information about the parameters, see the sklearn documentation https://scikit-learn.org/stable/modules/generated/sklearn.datasets.make_regression.html.

    Returns:
        DataSet: A DataSet object containing the generated regression dataset, with metadata describing it.
    """
    x, y = make_regression(**kwargs)
    # Create a DataFrame for the features
    feature_columns = [f'feature_{i + 1}' for i in range(x.shape[1])]

    # Create a DataFrame for the targets
    if len(y.shape) > 1:
        target_columns = [f'target_{i + 1}' for i in range(y.shape[1])]
    else:
        target_columns = ['target']

    ds = DataSet.from_list(
        features=x,
        targets=y,
        meta=DataSetMeta(
            name='sklearn_regression',
            time_series=False,
            synthetic_data=True,
            feature_names=feature_columns,
            target_names=target_columns
        )
    )
    return ds
