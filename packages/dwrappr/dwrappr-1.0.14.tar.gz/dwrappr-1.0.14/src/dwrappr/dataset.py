from typing import Tuple, List, Optional
import random
import os

import pandas as pd
import numpy as np
from dataclasses import dataclass, field, asdict

from .filehandler import save_file, load_file, get_file_extension, del_file_extension, get_folder_files
from .utils import check_any

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


@dataclass
class DataSetMeta:
    """
    Represents metadata information for a dataset, including details about its attributes,
    usage, and related files.

    This class is designed to store and manipulate metadata for datasets, providing
    an interface for converting metadata to a pandas DataFrame, loading metadata from
    JSON files and scanning directories for metadata files.

    Attributes:
        name: str
            Name of the dataset.
        time_series: bool
            Indicates whether the dataset contains time series data.
        synthetic_data: bool
            Indicates whether the dataset contains synthetic data.
        feature_names: List[str]
            List of feature names in the dataset.
        target_names: List[str]
            List of target names in the dataset.
        auxiliary_names: List[str]
            List of auxiliary  names in the dataset.
        origin: str
            Source or origin of the dataset.
        year: str
            Year associated with the dataset.
        url: str
            URL to access further information about the dataset.
        sector: str
            Sector to which the dataset belongs.
        target_type: str
            Type of the target variable (e.g., 'classification', 'regression').
        description: str
            Description or additional details about the dataset.
    """
    name: str
    feature_names: List[str]
    target_names: List[str] = field(default_factory=list)
    auxiliary_names: List[str] = field(default_factory=list)
    time_series: bool = field(init=True, default=False)
    synthetic_data: bool = field(init=True, default=False)
    origin: str = field(init=True, default=None)
    year: str = field(init=True, default=None)
    url: str = field(init=True, default=None)
    sector: str = field(init=True, default=None)
    target_type: str = field(init=True, default=None)
    description: str = field(init=True, default=None)

    def __str__(self):
        # Collect available metadata
        meta_info = [
            f"Name: {self.name}",
            f"Time Series: {self.time_series}",
            f"Synthetic Data: {self.synthetic_data}",
            f"Feature Names: {', '.join(self.feature_names)}",
        ]

        # Add optional metadata if available
        if self.target_names:
            meta_info.append(f"Target Names: {', '.join(self.target_names)}")
        if self.auxiliary_names:
            meta_info.append(f"Auxiliary Names: {', '.join(self.auxiliary_names)}")
        if self.origin:
            meta_info.append(f"Origin: {self.origin}")
        if self.year:
            meta_info.append(f"Year: {self.year}")
        if self.url:
            meta_info.append(f"URL: {self.url}")
        if self.sector:
            meta_info.append(f"Sector: {self.sector}")
        if self.target_type:
            meta_info.append(f"Target Type: {self.target_type}")
        if self.description:
            meta_info.append(f"Description: {self.description}")

        # Join all information into a single string
        return "\n".join(meta_info)

    @property
    def as_df(self) -> pd.DataFrame:
        """
        Returns the available Metadata as a Dataframe.

        This property Converts the object's attributes into a pandas DataFrame.
        Lists in attributes are transformed into comma-separated strings for better readability.

        Returns:
            pd.DataFrame: A single-row DataFrame representing the object's metadata and attributes.
        """
        # Start with dataclass fields
        meta_dict = asdict(self)
        # Add/overwrite with any additional attributes
        meta_dict.update({
            k: v for k, v in self.__dict__.items() if k not in meta_dict
        })

        # Convert lists to comma-separated strings for readability
        for key, value in meta_dict.items():
            if isinstance(value, list):
                meta_dict[key] = ', '.join(str(x) for x in value)

        # Convert the dictionary to a DataFrame
        df = pd.DataFrame([meta_dict])
        return df

    @classmethod
    def load(cls, filepath: str) -> 'DataSetMeta':
        r"""
        Loads an instance of DataSetMeta from a JSON file.

        This class method reads a JSON file and initializes an instance of
        DataSetMeta using the contents of the file. If the file provided does
        not have a .json extension, a ValueError is raised.

        Args:
            filepath (str) :The path to the JSON file that contains the data needed to initialize a DataSetMeta instance.

        Returns:
            DataSetMeta: An instance of DataSetMeta initialized with the data from the JSON file.

        Raises:
            ValueError : If the file specified by 'filepath' does not have a ".json" extension.
        Example:
            >>> file_path_meta = r"dwrappr/examples/data/example_dataset_meta.json"
            >>> meta = DataSetMeta.load(file_path_meta)
            >>> meta
            DataSetMeta(name='example_data', time_series='False', synthetic_data='True', feature_names=['feature'], target_names=['target'], origin=None, year=None, url=None, sector=None, target_type=None, description=None)

        """
        if not get_file_extension(filepath) == ".json":
            raise ValueError(f"File {filepath} should have extension '.json'")
        load_dict = load_file(filepath)
        return DataSetMeta(**load_dict)

    @classmethod
    def scan_for_meta(cls, path: str, recursive: bool = True) -> List['DataSetMeta']:
        """
        Scans the directory for metadata and corresponding dataset objects.

        This function scans a specified directory for metadata and associated dataset object files
        and returns a list of DataSetMeta instances. Files with extensions '.joblib'
        and corresponding '_meta.json' are paired, with unpaired files logged.

        Args:
            path (str): The root directory path to scan for metadata and dataset object files.
            recursive (bool, optional): Indicates whether subdirectories should also be scanned. Defaults to True.

        Returns:
            List[DataSetMeta]: A list containing DataSetMeta objects where both'.joblib' dataset files and matching '_meta.json' metadata files are found. If any of these files are missing a counterpart, a warning is logged.
        Example:
            >>> DataSetMeta.scan_for_meta(r"dwrappr/examples/data")
            [DataSetMeta(name='example_data', time_series='False', synthetic_data='True', feature_names=['feature'], target_names=['target'], origin=None, year=None, url=None, sector=None, target_type=None, description=None)]


        """
        # Use the utility function to get all file paths
        all_files = get_folder_files(path, recursive)

        # Filtered list to store the matching DataSetMeta objects
        meta_data = []

        # Dictionaries to map base names to their respective paths
        dataset_object_files = {}
        meta_json_files = {}

        # Populate the dictionaries
        for file_path in all_files:
            file_name = os.path.basename(file_path)
            base_name, ext = os.path.splitext(file_name)
            if ext == '.joblib':
                dataset_object_files[base_name] = file_path
            elif file_name.endswith('_meta.json'):
                base_name = base_name[:-5]  # Remove '_meta' from the base name
                meta_json_files[base_name] = file_path

        # Check for corresponding files and handle cases
        for base_name in dataset_object_files:
            if base_name in meta_json_files:
                # Both files exist, load the meta
                meta = cls.load(meta_json_files[base_name])
                meta.local_filepath = dataset_object_files[base_name]
                meta_data.append(meta)
            else:
                # .joblib exists without _meta.json
                logger.warning(f"Missing _meta.json-file for {dataset_object_files[base_name]}")

        for base_name in meta_json_files:
            if base_name not in dataset_object_files:
                # _meta.json exists without .joblib
                logger.warning(f"Missing dataset_object-file for {meta_json_files[base_name]}")

        return meta_data

    def save(self, filepath: str) -> None:
        """
        Saves the instance data to a specified JSON file.

        The method ensures that the file has a '.json' extension before attempting
        to save the instance data. If the extension is incorrect, a ValueError is
        raised. The instance is first converted to a dictionary representation and
        then written to the specified file path.

        Args:
            filepath (str) : The path to the file where the instance data will be saved. The file must have a '.json' extension.

        Returns:
            None

        Raises:
            ValueError: Raised if the file does not have a '.json' extension.

        """
        if not get_file_extension(filepath) == ".json":
            raise ValueError(f"File {filepath} should have extension '.json'")
        save_file(asdict(self), filepath)


@dataclass
class DataPoint:
    """
    Represents a data point with associated x and optional y data arrays.

    This class is designed to encapsulate a data point represented by Numpy arrays
    and optionally associated data. It validates inputs during initialization to
    ensure they are Numpy arrays. The class also supports saving itself to and
    loading from joblib files, with helper methods for these tasks.

    Attributes:
        x: np.ndarray
            The primary data array, must be a Numpy array.
        y: Optional[np.ndarray]
            The secondary or optional data array, can be a Numpy array or None.
    """
    x: np.ndarray
    y: Optional[np.ndarray] = field(default=None)
    z: Optional[np.ndarray] = field(default=None)

    def __post_init__(self):
        """
        Ensures proper types for the instance variables during object initialization.

        Validates that 'x' is a NumPy array and that 'y' is either a NumPy array or None.

        Raises:
            TypeError: If 'x' is not a numpy.ndarray.
            TypeError: If 'y' is neither a numpy.ndarray nor None.
        """
        if not isinstance(self.x, np.ndarray):
            raise TypeError(f"x should be a numpy.ndarray, got {type(self.x).__name__} instead.")
        if self.y is not None and not isinstance(self.y, np.ndarray):
            raise TypeError(f"y should be a numpy.ndarray or None, got {type(self.y).__name__} instead.")
        if self.z is not None and not isinstance(self.z, np.ndarray):
            raise TypeError(f"z should be a numpy.ndarray, got {type(self.z).__name__} instead.")

    @classmethod
    def load(cls, filepath: str) -> 'DataPoint':
        """
        Load a DataPoint object from a .joblib file.

        This method reads a .joblib file from the given filepath, validates
        its extension, and loads the data to instantiate a DataPoint object.

        Args:
            filepath (str) : Path to the .joblib file to be loaded. The file must have a '.joblib' extension.

        Returns:
            DataPoint : An instance of DataPoint created using the data in the file.

        Raises:
            ValueError : If the file does not have a '.joblib' extension.
        """
        if not get_file_extension(filepath) == ".joblib":
            raise ValueError(f"File {filepath} should have extension '.joblib'")
        load_dict = load_file(filepath)
        return DataPoint(**load_dict)

    def save(self, filepath: str) -> None:
        """
        Saves the object's data to a specified file in Joblib format.

        Raises an error if the specified file does not have a '.joblib' extension.
        Uses the internal representation of the object's data converted to a dictionary.

        Args:
            filepath (str) : The path to the file where the object's data will be saved.

        Raises:
            ValueError : If the specified filepath does not end with '.joblib'.
        """
        if not get_file_extension(filepath) == ".joblib":
            raise ValueError(f"File {filepath} should have extension '.joblib'")
        save_file(asdict(self), filepath)


@dataclass
class DataSet:
    """
    Represents a dataset consisting of data points, metadata, and associated attributes.

    The DataSet class is designed to store and manipulate a collection of data points,
    along with metadata and data types for features and targets. It provides multiple
    methods and properties for retrieving subsets of the dataset, accessing features and
    targets in various formats (e.g., numpy array, pandas DataFrame, PyTorch tensor),
    and loading/saving datasets.

    Attributes:
        datapoints : List[DataPoint]
            A list of data point objects that make up the dataset.
        dtypes : dict[str, str]
            A dictionary mapping column names to their data types.
        meta : DataSetMeta
            Metadata object that contains information such as feature names, target names, and dataset name.
    """
    datapoints: list[DataPoint] = field(default_factory=list)
    dtypes: dict[str, str] = field(default_factory=dict)  # Dictionary to store dtypes
    meta: DataSetMeta = field(default_factory=DataSetMeta)

    def __getitem__(self, idx):
        """
        Retrieve a subset of data points from the dataset based on the specified index.
        If the index is an integer, retrieves a single data point as a subset. If the
        index is a slice, retrieves a subset of data points based on the range
        specified by the slice. The returned subset is encapsulated within a new
        DataSet instance.

        Args:
            idx (int or slice): The index or range to access. Must be an integer for retrieving a single data point, or a slice for retrieving a subset.

        Returns:
            DataSet: A new DataSet instance containing the selected subset of data points.

        Raises:
            TypeError: If the provided index is neither an integer nor a slice.

        Example:
            >>> ds[0]
            DataSet(datapoints=[DataPoint(x=array([12]), y=array([0]))], dtypes={'feature': dtype('int64'), 'target': dtype('int64')}, meta=DataSetMeta(name='example_data', time_series='False', synthetic_data='True', feature_names=['feature'], target_names=['target'], origin=None, year=None, url=None, sector=None, target_type=None, description=None))
            >>> ds[1:3]
            DataSet(datapoints=[DataPoint(x=array([7]), y=array([1])), DataPoint(x=array([15]), y=array([0]))], dtypes={'feature': dtype('int64'), 'target': dtype('int64')}, meta=DataSetMeta(name='example_data', time_series='False', synthetic_data='True', feature_names=['feature'], target_names=['target'], origin=None, year=None, url=None, sector=None, target_type=None, description=None))
        """
        if isinstance(idx, slice):
            subset_datapoints = self.datapoints[idx]
        elif isinstance(idx, int):
            subset_datapoints = [self.datapoints[idx]]
        else:
            raise TypeError("Index must be an int or slice")

        # Create a new DataSet instance with the subset of datapoints
        subset = DataSet(datapoints=subset_datapoints,
                         dtypes=self.dtypes,
                         meta=self.meta, )
        return subset

    def __str__(self) -> str:
        """
        Provides a string representation of the object.

        This function returns a string representation of the dataset object by combining its key attributes
        in a human-readable format. This method formats the details of the object's
        name, data types, metadata, number of data points, and how to access data
        points. Aim is to offer a concise summary of the object's state.

        Returns:
            str: A string representation of the object containing its essential attributes.
        Example:
            >>> ds
            DataSet(datapoints=[DataPoint(x=array([12]), y=array([0])), DataPoint(x=array([7]), y=array([1])), DataPoint(x=array([15]), y=array([0])), DataPoint(x=array([9]), y=array([1]))], dtypes={'feature': dtype('int64'), 'target': dtype('int64')}, meta=DataSetMeta(name='example_data', time_series='False', synthetic_data='True', feature_names=['feature'], target_names=['target'], origin=None, year=None, url=None, sector=None, target_type=None, description=None))
        """
        return (f"name: {self.name}\n"
                f"meta: {self.meta}\n"
                f"num_datapoints: {self.num_datapoints}\n"
                f"dtypes: acess dtypes with <{self.__class__.__name__}_instance>.dtypes\n"
                f"datapoints[list]: access datapoints with <{self.__class__.__name__}_instance>.datapoints")

    def __len__(self) -> int:
        """
        Returns the number of data points in the object.

        This method allows determining the size or length of the dataset
        or collection represented by the object. It is often used where
        an object defines a collection-like interface.

        Returns:
            int: The total number of data points contained in the object.

        Example:
            >>> len(ds)
            4
        """
        return self.num_datapoints

    @property
    def name(self) -> str:
        """
        Returns the name attribute of the meta property.

        This property retrieves the name stored in the meta attribute. It does
        not accept any arguments and directly returns the name as a string.

        Returns:
            str: The name value associated with the meta attribute.
        Example:
            >>> ds.name
            'example_data'
        """
        return self.meta.name

    @property
    def feature_names(self) -> list[str]:
        """
        Returns the names of features used in the metadata.

        This property provides access to the feature names attribute present in
        the metadata object. It retrieves and returns the list of feature names.

        Returns:
            List[str]: The list of feature names.
        Example:
            >>> ds.feature_names
            ['feature']
        """
        return self.meta.feature_names

    @property
    def target_names(self) -> list[str]:
        """
        Returns the list of target names specified in the metadata.

        The method fetches and provides a list containing the target names which
        are stored in the meta attribute. The list represents the names or labels
        that correspond to target values in a dataset or similar context.

        Returns:
            list[str]: A list of target names.
        Example:
            >>> ds.target_names
            ['target']
        """
        return self.meta.target_names

    @property
    def auxiliary_names(self) -> list[str]:
        """
        Returns the list of auxiliary names specified in the metadata.

        The method fetches and provides a list containing the auxiliary names which
        are stored in the meta attribute. The list represents the names or labels
        that correspond to auxiliary values in a dataset or similar context.

        Returns:
            list[str]: A list of auxiliary names.
        Example:
            >>> ds.auxiliary_names
            ['target']
        """
        return self.meta.auxiliary_names

    @property
    def num_datapoints(self) -> int:
        """
        Returns the number of datapoints in the dataset.

        This property calculates the total count of datapoints currently
        present and provides this information as an integer.

        Returns:
            int: The total number of datapoints in the dataset.
        """
        return len(self.datapoints)

    @property
    def x(self) -> np.array:
        """
        Returns the x-coordinates of all datapoints in the current object.

        This property compiles a list of the x-values from all elements in
        the 'datapoints' attribute and returns them as a NumPy array. The
        returning array provides a structured format of the x-coordinates
        for further computations or manipulations.

        Returns:
            np.array: A NumPy array containing the x-coordinates of the datapoints in the object.
        Example:
            >>> ds.x
            0,12
            1,7
            2,15
            3,9
        """
        return np.array([datapoint.x for datapoint in self.datapoints])

    @property
    def x_as_df(self) -> pd.DataFrame:
        """
        Returns the `x` attribute as a pandas DataFrame.

        Provides a property method to process and return the `x` attribute formatted as
        a pandas DataFrame with updated data types. The output DataFrame's schema is
        adjusted according to the stored metadata and type definitions.

        Returns:
            pd.DataFrame: A pandas DataFrame created from the `x` attribute, with columns named according to `meta.feature_names` and updated data types based on the metadata settings.
        """
        df = pd.DataFrame(self.x, columns=self.meta.feature_names)

        # Apply the stored dtypes to the DataFrame
        df = self._update_df_dtypes(df)
        return df

    @property
    def x_as_tensor(self) -> 'torch.Tensor':
        """
        Returns the `x` attribute of the instance as a PyTorch tensor.

        This property converts the `x` attribute to a PyTorch tensor of type
        torch.float32. It requires PyTorch to be installed in the environment.

        Returns:
            torch.Tensor: The x attribute of the instance converted to a tensor.

        Raises:
            ImportError: If PyTorch is not installed in the environment.
        """
        try:
            import torch
        except ImportError:
            raise ImportError("PyTorch is required to use x_as_tensor. Please install it via 'pip install torch'.")

        return torch.tensor(self.x, dtype=torch.float32)

    @property
    def y(self) -> Optional[np.ndarray]:
        """
        Returns the y values extracted from all datapoints as a NumPy array.

        Y values correspond to the 'y' attribute of each datapoint in the list of
        datapoints. If no datapoints are present, it returns None.

        Return:
            Optional[np.ndarray]: A NumPy array of y values from datapoints, or None
            if no datapoints exist.
        Example:
            >>> ds.y
            0,0
            1,1
            2,0
            3,1
        """
        return np.array([datapoint.y for datapoint in self.datapoints])

    @property
    def y_as_df(self) -> pd.DataFrame:
        """
        Returns the target variable as a pandas DataFrame.

        This property provides a DataFrame representation of the target
        variable with column names corresponding to the `target_names` attribute.
        It also ensures that the DataFrame's data types are updated consistent
        with any pre-defined data type information.

        Returns:
            pd.DataFrame: The target variable represented as a pandas
            DataFrame with appropriately updated data types.
        """
        if not self.target_names:
            return pd.DataFrame()

        df = pd.DataFrame(self.y, columns=self.target_names)

        # Apply the stored dtypes to the DataFrame
        df = self._update_df_dtypes(df)
        return df

    @property
    def y_as_tensor(self) -> 'torch.Tensor':
        """
        Returns the attribute 'y' as a PyTorch tensor.

        This property converts the 'y' attribute of the object into a PyTorch tensor
        with a data type of float32. It requires PyTorch to be installed, and will
        raise an ImportError if it is not available.

        Returns:
            torch.Tensor: The attribute 'y' represented as a tensor of type torch.float32.
        Raises:
            ImportError: If PyTorch library is not installed.
        """
        try:
            import torch
        except ImportError:
            raise ImportError("PyTorch is required to use y_as_tensor. Please install it via 'pip install torch'.")

        return torch.tensor(self.y, dtype=torch.float32)

    @property
    def z(self) -> np.ndarray:
        """
        Returns the z values extracted from all datapoints as a NumPy array.

        Z values correspond to the 'z' attribute of each datapoint in the list of
        datapoints. If no datapoints are present, it returns None.

        Return:
            Optional[np.ndarray]: A NumPy array of z values from datapoints, or None
            if no datapoints exist.
        Example:
            >>> ds.z
            0,0
            1,1
            2,0
            3,1
        """
        return np.array([datapoint.z for datapoint in self.datapoints])

    @property
    def z_as_df(self) -> pd.DataFrame:
        """
        Returns the target variable as a pandas DataFrame.

        This property provides a DataFrame representation of the target
        variable with column names corresponding to the `target_names` attribute.
        It also ensures that the DataFrame's data types are updated consistent
        with any pre-defined data type information.

        Returns:
            pd.DataFrame: The target variable represented as a pandas
            DataFrame with appropriately updated data types.
        """
        if not self.auxiliary_names:
            return pd.DataFrame()
        df = pd.DataFrame(self.z, columns=self.auxiliary_names)

        # Apply the stored dtypes to the DataFrame
        df = self._update_df_dtypes(df)
        return df

    @property
    def as_df(self) -> pd.DataFrame:
        """
        Returns the dataset object as a pandas DataFrame.

        This property converts the stored DataPoints into a DataFrame. It concatenates the
        x and y DataFrames along the columns axis and applies the stored data types to the
        resulting DataFrame before returning it.

        Returns:
            pd.DataFrame: A DataFrame representation of the stored DataPoints, with the
            stored data types applied.
        """
        # Convert DataPoints back into a DataFrame
        df = pd.concat([self.x_as_df, self.y_as_df, self.z_as_df], axis=1)

        # Apply the stored dtypes to the DataFrame
        df = self._update_df_dtypes(df)
        return df

    def _update_df_dtypes(self, df) -> pd.DataFrame:
        """
        Updates the data types of a DataFrame's columns based on a specific dtype mapping.

        This method takes a DataFrame and applies the column data types specified in
        the 'dtypes' attribute of the class to the corresponding columns in the DataFrame.
        Only the columns that exist in both the DataFrame and the dtype mapping will
        have their data types updated.

        Args:
            df (pd.DataFrame) : The DataFrame whose column data types are to be updated.

        Returns:
            None
        """
        # Filter the dtype dictionary to only use keys that exist in the DataFrame
        filtered_dtypes = {col: dtype for col, dtype in self.dtypes.items() if col in df.columns}

        # Apply the dtypes to the DataFrame using astype
        df = df.astype(filtered_dtypes)
        return df

    @classmethod
    def load(cls, filepath: str) -> 'DataSet':
        """
        Loads a dataset object.

        This function loads a DataSet object from a file in `.joblib` format while reconstructing
        necessary components such as `DataPoint` and `DataSetMeta` objects. Assumes
        the file contains serialized elements suitable for creating a DataSet.

        Args:
            filepath (str): The path to the `.joblib` file from which the DataSet will be loaded.
        Returns:
            DataSet: A fully reconstructed DataSet instance based on the data provided in the file.
        Raises:
            ValueError: If the provided file does not have the `.joblib` extension.
        """
        if not get_file_extension(filepath) == '.joblib':
            raise ValueError(f"File {filepath} should have extension '.joblib'")

        load_dict = load_file(filepath)

        # Reconstruct DataPoint objects from the loaded dictionary
        datapoints = [
            DataPoint(x=np.array(dp['x'], dtype=object),
                      y=np.array(dp['y'], dtype=object) if dp['y'] is not None else None,
                      z=np.array(dp['z'], dtype=object) if dp['z'] is not None else None)
            for dp in load_dict['datapoints']
        ]

        # Reconstruct DataSetMeta objects from the loaded dictionary
        meta = DataSetMeta(**load_dict['meta'])

        # Use all keys except 'datapoints' to create the DataSet instance
        dataset_args = {key: value for key, value in load_dict.items() if key not in ['datapoints', 'meta']}
        dataset_args['datapoints'] = datapoints
        dataset_args['meta'] = meta

        return cls(**dataset_args)

    @classmethod
    def from_dataframe(cls,
                       df: pd.DataFrame,
                       meta: DataSetMeta,
                       check_df=True) -> 'DataSet':
        """
        Create a new DataSet instance from a given pandas DataFrame and metadata.

        This method constructs a DataSet object from a DataFrame by extracting
        features and target values based on the provided metadata. It also ensures
        that the DataFrame aligns with the metadata specifications and performs a
        check if enabled. Additionally, the method captures data types of the
        specified feature and target columns for later retransformation from the
        DataSet to a DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame containing data structured according to the provided metadata.
            meta (DataSetMeta): Metadata object that specifies feature and target column names, among other dataset properties.
            check_df (bool, optional): An flag that determines whether to validate the DataFrame against the metadata. Default is True.

        Returns:
            DataSet: A new DataSet instance populated with DataPoint objects derived from the input DataFrame.

        Raises:
            No exceptions specified, as this section is not included as per the guidelines.
        Examples:
            >>> import pandas as pd
            >>> from dwrappr import DataSet, DataSetMeta
            >>> file_path_meta = r"dwrappr/examples/data/example_dataset_meta.json"
            >>> meta = DataSetMeta.load(file_path_meta)
            >>> file_path_data = r"dwrappr/examples/data/example_data.csv"
            >>> df = pd.read_csv(file_path_data)
            >>> ds = DataSet.from_dataframe(df = df, meta = meta)
            >>> ds
            DataSet(datapoints=[DataPoint(x=array([12]), y=array([0])), DataPoint(x=array([7]), y=array([1])), DataPoint(x=array([15]), y=array([0])), DataPoint(x=array([9]), y=array([1]))], dtypes={'feature': dtype('int64'), 'target': dtype('int64')}, meta=DataSetMeta(name='example_data', time_series='False', synthetic_data='True', feature_names=['feature'], target_names=['target'], origin=None, year=None, url=None, sector=None, target_type=None, description=None))
            todo (jacob): Add example without json
        """
        dataset = cls(meta=meta)

        if check_df:
            dataset._check_df(df)

        # Save dtypes for the specified feature and target columns for retransformation from DataSet to DataFrame later

        # Combine feature columns with target columns if target columns are provided and auxiliary columns if auxiliary columns are provided
        columns = meta.feature_names + (meta.target_names if meta.target_names else []) + (meta.auxiliary_names if meta.auxiliary_names else [])
        # Create the dtypes dictionary using the combined columns list
        dataset.dtypes = {col: df.dtypes[col] for col in columns}

        # Add DataPoints from DataFrame
        for _, row in df.iterrows():
            # Extract features and targets from the row
            x = row[meta.feature_names].values
            y = row[meta.target_names].values if meta.target_names else None
            z = row[meta.auxiliary_names].values if meta.auxiliary_names else None

            # Create a DataPoint and add it to the dataset
            datapoint = DataPoint(x=np.array(x), y=np.array(y), z=np.array(z))
            dataset.datapoints.append(datapoint)
        return dataset

    @classmethod
    def from_list(cls,
                  features: list,
                  meta: DataSetMeta,
                  targets: list = None,
                  ) -> 'DataSet':
        """
        Creates a DataSet object from given lists of features and targets along with a
        DataSetMeta instance.

        Args:
            features (list): A list containing the feature data, where each sub-list represents a row of feature values.
            meta (DataSetMeta): The metadata associated with the dataset, including feature and target names.
            targets  (list, optional) : A list containing the target data, where each sub-list represents a row of target values. Defaults to None.

        Returns:
            DataSet: Returns an instance of the DataSet object created from the provided features, targets, and metadata.
        """
        # Create a DataFrame from features and targets
        feature_df = pd.DataFrame(features, columns=meta.feature_names)
        df = feature_df

        if check_any(targets):
            target_df = pd.DataFrame(targets, columns=meta.target_names)

            # Concatenate the feature and target DataFrames
            df = pd.concat([feature_df, target_df], axis=1)

        return cls.from_dataframe(
            df=df,
            meta=meta,
        )

    @staticmethod
    def get_available_datasets_in_folder(path: str) -> pd.DataFrame:
        """
        Gets available datasets from a specified folder and combines them into a single DataFrame.

        Scans the folder to identify dataset metadata, retrieves the datasets,
        and concatenates them into one DataFrame.

        Args:
            path (str): The file path to the folder containing datasets.

        Returns:
            pd.DataFrame: A DataFrame containing the combined data from all
            datasets found in the folder.
        """
        datasets = DataSetMeta.scan_for_meta(path)
        dataframes = [dataset.as_df for dataset in datasets]
        df = pd.concat(dataframes, axis=0, ignore_index=True)
        return df

    # Method to validate input DataFrame
    def _check_df(self, df: pd.DataFrame) -> None:
        """
        Validates the structure and content of a given pandas DataFrame against pre-defined
        feature and target column requirements. This method checks for the existence of
        required feature and target names in the DataFrame's columns, as well as ensuring
        the DataFrame does not contain any NaN values. If any issue is found, an appropriate
        error is logged and raised.

        Args:
            df (pd.DataFrame): The pandas DataFrame that needs to be validated.

        Raises:
            ValueError: Raised if one or more required features are missing from the DataFrame.
            ValueError: Raised if one or more required targets are missing from the DataFrame.
            ValueError: Raised if the DataFrame contains NaN values.
        """
        # Check if all the features column exist in dataframe, if not raise error
        if not set(self.feature_names).issubset(df.columns):
            missing_features = set(self.meta.feature_names) - set(df.columns)
            if missing_features:
                logger.error(
                    f"The following feature/s are missing in the dataframe: {', '.join(missing_features)}")
                raise ValueError("Feature/s missing in the dataset")

        # Check if all the target columns exist in dataframe, if not raise error
        if self.target_names:
            if not set(self.target_names).issubset(df.columns):
                missing_targets = set(self.feature_names) - set(df.columns)
                if missing_targets:
                    logger.error(
                        f"The following targets/s are missing in the dataframe: {', '.join(missing_targets)}")
                    raise ValueError("Target/s missing in the dataset")
        if df.isnull().values.any():
            # Raise error if dataframe contains NaN values
            logger.error("The dataset contains NaN values")
            raise ValueError("The dataset contains NaN values")
        logger.info("Data checked successfully.")

    def save(self, filepath: str, drop_meta_json: bool = True) -> None:
        """
        Saves the current object state to a specified file path, optionally excluding a
        meta JSON file. Ensures the file has the correct extension before saving.

        Args:
            filepath (str): The file path to save the object to. Must end with '.joblib'.
            drop_meta_json (bool): Whether to drop saving the meta JSON file. Defaults to True.

        Raises:
            ValueError: If the provided file path does not have a '.joblib' extension.

        Returns:
            None
        """
        if not get_file_extension(filepath) == '.joblib':
            raise ValueError(f"File {filepath} should have extension '.joblib'")
        save_file(asdict(self), filepath)
        if drop_meta_json:
            self.meta.save(f"{del_file_extension(filepath)}_meta.json")

    def split_dataset(
            self,
            first_ds_size: float,
            shuffle: bool = True,
            random_state: int = 42,
            group_by_features: Optional[List[str]] = None
    ) -> Tuple['DataSet', 'DataSet']:
        """
        Splits the dataset into two subsets based on a specified ratio. The split can optionally
        group data points by specific feature values to ensure grouped subsets stay intact.

        Args:
            first_ds_size (float): Proportion of the dataset to assign to the first subset. Should be a value between 0 and 1.
            shuffle (bool, optional): Whether to shuffle the dataset or groups before splitting. Defaults to True.
            random_state (int, optional): Random seed for reproducibility of shuffling. Defaults to 42.
            group_by_features ([List[str]], optional): List of feature names to group data points by before splitting. If None, no grouping is applied. Defaults to None.

        Returns:
            Tuple['DataSet', 'DataSet']: A tuple containing the two resulting datasets after the split.
        Example:
            >>> ds(0.5)
            (DataSet(datapoints=[DataPoint(x=array([12]), y=array([0])), DataPoint(x=array([9]), y=array([1]))], dtypes={'feature': dtype('int64'), 'target': dtype('int64')}, meta=DataSetMeta(name='example_data', time_series='False', synthetic_data='True', feature_names=['feature'], target_names=['target'], origin=None, year=None, url=None, sector=None, target_type=None, description=None)),

            (DataSet(datapoints=[DataPoint(x=array([7]), y=array([1])), DataPoint(x=array([15]), y=array([0]))], dtypes={'feature': dtype('int64'), 'target': dtype('int64')}, meta=DataSetMeta(name='example_data', time_series='False', synthetic_data='True', feature_names=['feature'], target_names=['target'], origin=None, year=None, url=None, sector=None, target_type=None, description=None)))
        """
        random.seed(random_state)

        if group_by_features:
            # Create a mapping from feature values to datasets points
            grouped_datapoints = {}
            for datapoint in self.datapoints:
                # Create a key based on the feature values
                key = tuple(datapoint.x[self.feature_names.index(f)] for f in group_by_features)
                if key not in grouped_datapoints:
                    grouped_datapoints[key] = []
                grouped_datapoints[key].append(datapoint)

            # Convert dictionary to a list of groups
            groups = list(grouped_datapoints.values())

            # Shuffle the groups if shuffle is True
            if shuffle:
                random.shuffle(groups)

            # Calculate the number of groups to include in the first dataset
            num_groups = len(groups)
            split_index = max(1, min(num_groups - 1, int(num_groups * first_ds_size)))

            # Flatten the groups for each dataset
            ds1_datapoints = [dp for group in groups[:split_index] for dp in group]
            random.shuffle(ds1_datapoints)
            ds2_datapoints = [dp for group in groups[split_index:] for dp in group]
            random.shuffle(ds2_datapoints)
        else:
            # If no grouping, simply shuffle and split
            all_datapoints = self.datapoints
            if shuffle:
                all_datapoints = random.sample(all_datapoints, len(all_datapoints))

            split_index = max(1, min(len(all_datapoints) - 1, int(len(all_datapoints) * first_ds_size)))
            ds1_datapoints = all_datapoints[:split_index]
            ds2_datapoints = all_datapoints[split_index:]

        ds1 = DataSet(
            meta=self.meta,
            dtypes=self.dtypes,
            datapoints=ds1_datapoints
        )

        ds2 = DataSet(
            meta=self.meta,
            dtypes=self.dtypes,
            datapoints=ds2_datapoints
        )
        return ds1, ds2


if __name__ == '__main__':
    pass
