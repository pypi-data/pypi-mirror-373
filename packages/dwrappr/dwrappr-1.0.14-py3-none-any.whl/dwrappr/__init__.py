"""
DWrappr - A Python package for dataset handling and manipulation.

This package provides classes and utilities for working with datasets,
including loading, saving, and transforming data between different formats.

Main components:
    - DataSet: Core class for representing and manipulating datasets
    - DataSetMeta: Class for managing dataset metadata 
    - save_file: Utility function to save data to disk
    - load_file: Utility function to load data from disk

Example usage:
    from dwrap import DataSet, DataSetMeta
    ds = DataSet.from_dataframe(df, meta)
    ds.save('dataset.pkl')
"""

from .dataset import DataSet, DataSetMeta
from .filehandler import save_file, load_file

__version__ = '1.0.0'
__author__ = 'dwrap Team'

__all__ = [
    'DataSet',
    'DataSetMeta',
    'save_file',
    'load_file'
]
