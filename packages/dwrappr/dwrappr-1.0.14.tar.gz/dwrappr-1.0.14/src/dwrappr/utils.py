# seperated due to circular imports

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GroupShuffleSplit
import numpy as np
from typing import Union

import logging

logger = logging.getLogger(__name__)


def shuffle_split_dataframe(df: pd.DataFrame,
                            train_size: float,
                            group: str = None,
                            rnd_state: int = 42
                            ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Shuffles and splits a pandas DataFrame into training and testing sets.

    This function splits a DataFrame into two subsets while optionally grouping
    by a specified column. If a group parameter is provided, the function preserves
    grouped data in either the training or testing subset, ensuring that rows
    belonging to the same group do not span both subsets. Otherwise, it performs
    a straightforward random split. The split sizes are determined by the train_size
    parameter. Additionally, the function provides reproducibility of the split
    through a random state parameter.

    Args:
        df (pd.DataFrame): The input pandas DataFrame to be shuffled and split. train_size (float): The fraction of the dataset to include in the training set. Must be a float between 0.0 and 1.0.
        group (str): Optional. The column name in the DataFrame to be used for grouping. If specified, rows belonging to the same group will remain together in either the training or testing set. Defaults to None.
        rnd_state (int): A random seed for reproducibility of the shuffling and splitting process. Defaults to 42.
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two pandas DataFrames,
        where the first DataFrame is the training set and the second is the testing set.
    Example:
        >>> from dwrappr.utils import shuffle_split_dataframe
        >>> df = pd.DataFrame({
        ...     'feature': [1, 2, 3, 4, 5, 6],
        ...     'target': [0, 1, 0, 1, 0, 1],
        ...     'group_id': ['A', 'A', 'B', 'B', 'C', 'C']
        ... })
        >>> train_df, test_df = shuffle_split_dataframe(df, train_size=0.5)
        >>> train_df
        2025-05-18 16:33:17 [INFO] df1_size: 3, df2_size: 3
           feature  target group_id
        0        3       0        B
        1        5       0        C
        2        4       1        B
        todo (jacob): add test_df and group parameter
    """
    if not group:
        df1, df2 = train_test_split(df,
                                    train_size=train_size,
                                    random_state=rnd_state)

    elif group:
        # Define GroupShuffleSplit
        gss = GroupShuffleSplit(n_splits=1,
                                train_size=train_size,
                                random_state=42)
        # Split the DataFrame into train and test sets based on 'group'
        for df1_idx, df2_idx in gss.split(df, groups=df[group]):
            df1 = df.iloc[df1_idx]
            df2 = df.iloc[df2_idx]

    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)

    logger.info(f"df1_size: {len(df1)}, df2_size: {len(df2)}")

    return df1, df2


def deep_update(original, updates) -> None:
    """
    Recursively updates a dictionary with values from another dictionary.

    This function merges two dictionaries, with the second dictionary’s values
    overwriting or updating the first dictionary's values. If both dictionaries
    contain nested dictionaries for the same key, the function performs a deep
    update by recursing into the nested dictionaries.

    Args:
        original (dict) : The dictionary to be updated.
        updates (dict) : The dictionary containing updates to be applied to the original dictionary.
    Example:
        >>> from dwrappr.utils import deep_update
        >>> original = {'a': 1, 'b': {'x': 10, 'y': 20}}
        >>> updates = {'b': {'y': 99, 'z': 42}, 'c': 3}
        >>> deep_update(original, updates)
        >>> original
        {'a': 1, 'b': {'x': 10, 'y': 99, 'z': 42}, 'c': 3}
    """
    for key, value in updates.items():
        if isinstance(value, dict) and key in original:
            # If the value is a dictionary and the key exists in the original, recurse
            deep_update(original[key], value)
        else:
            # Otherwise, update the original dictionary with the new value
            original[key] = value


def convert_to_native_types(d):
    """
    Converts NumPy data types in a nested dictionary to native Python data types.

    This function iterates through a nested dictionary and converts any detected
    NumPy data types (e.g., np.float64, np.int64, np.bool_) to their respective
    native Python types (e.g., float, int, bool). For nested dictionaries,
    the function applies itself recursively.

    Args:
        d (dict): The input dictionary, which may contain nested dictionaries
        and values of NumPy data types.

    Returns:
        None: The function modifies the input dictionary in place, replacing
        NumPy data types with native Python equivalents.
    Examples:
        >>> import numpy as np
        >>> from dwrappr.utils import convert_to_native_types
        >>> data = {
        ...     'a': np.float64(1.5),
        ...     'b': {'x': np.int64(3), 'y': np.bool_(True)}
        ... }
        >>> convert_to_native_types(data)
        >>> data
        {'a': 1.5, 'b': {'x': 3, 'y': True}}
    """
    for key, value in d.items():
        if isinstance(value, dict):
            convert_to_native_types(value)
        elif isinstance(value, np.float64):
            d[key] = float(value)
        elif isinstance(value, np.int64):
            d[key] = int(value)
        elif isinstance(value, np.bool_):
            d[key] = bool(value)


def df_row_to_nested_dict(row) -> dict:
    """
    Converts a row of a DataFrame into a nested dictionary.

    The function processes a row from a DataFrame where the keys in the row
    contain paths separated by slashes ('/'), indicating hierarchical structure.
    It constructs a nested dictionary based on these keys, recursively creating
    dictionaries for the intermediate paths. The function also converts values
    in the resulting dictionary to their native Python types.

    Args:
        row (Mapping[str, Any]): A row from a DataFrame, which is a map-like
        object where keys are string paths (e.g., 'a/b/c') and values can be of
        any type.

    Returns:
        dict: A nested dictionary representation where keys are hierarchical
        paths broken down based on the slash ('/') delimiter.
    Examples:
        >>> import pandas as pd
        >>> from dwrappr.utils import df_row_to_nested_dict
        >>> row = pd.Series({
        ...     'a/b/c': 1,
        ...     'a/b/d': 2,
        ...     'x/y': 3
        ... })
        >>> df_row_to_nested_dict(row)
        {'a': {'b': {'c': 1, 'd': 2}}, 'x': {'y': 3}}
    """
    nested_dict = {}
    for col, value in row.items():
        keys = col.split('/')
        d = nested_dict
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
    convert_to_native_types(nested_dict)
    return nested_dict


def check_any(x: Union[np.ndarray, list]) -> bool:
    """
    Returns True if any element in the input is True/nonzero.
    Accepts numpy arrays and Python lists only.

    Args:
        x (np.ndarray or list): Input array or list.

    Returns:
        bool: True if any element is True/nonzero, else False.

    Raises:
        TypeError: If input is not a numpy array or Python list.
    Examples:
        >>> import numpy as np
        >>> from dwrappr.utils import check_any
        >>> check_any([0, 0, 1])
        True
        >>> check_any(np.array([0, 0, 0]))
        False
        >>> check_any([])
        False
    """
    if isinstance(x, np.ndarray):
        return x.any()
    elif isinstance(x, list):
        return any(x)
    else:
        raise TypeError(
            f"Input must be a numpy.ndarray or a Python list, got {type(x)}."
        )


