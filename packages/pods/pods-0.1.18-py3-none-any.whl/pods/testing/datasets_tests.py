import unittest
import numpy as np
import pods
import types
import mock
import sys
import pytest


# pods.datasets.overide_manual_authorize=True

dataset_helpers = [
    "authorize_download",
    "clear_cache",
    "data_available",
    "discrete",
    "df2arff",
    "download_rogers_girolami_data",
    "downloard_url",
    "datenum",
    "date2num",
    "num2date",
    "datetime64_",
    "data_details_return",
    "download_data",
    "download_url",
    "integer",
    "json_object",
    "list",
    "urlopen",
    "prompt_user",
    "cmu_mocap",
    "cmu_urls_files",
    "kepler_telescope_urls_files",
    "kepler_telescope",
    "decimalyear",
    "permute",
    "categorical",
    "quote",
    "timestamp",
    "swiss_roll_generated",
    "to_arff",
    "prompt_stdin",
]


def list_datasets(module):
    """List all available datasets names and calling functions."""
    import types

    l = []
    for a in dir(module):
        func = module.__dict__.get(a)
        if a not in dataset_helpers:
            if isinstance(func, types.FunctionType):
                l.append((a, func))
    return l


positive_return_values = ["Y", "y", "Yes", "YES", "yes", "yEs"]
negative_return_values = ["N", "n", "No", "NO", "no", "nO", "eggs"]

dataset_test = []
for name, func in list_datasets(pods.datasets):
    dataset_test.append(
        {
            "dataset_name": name,
            "dataset_function": func,
            "arg": None,
            "docstr": func.__doc__,
        }
    )

dataset_selection = [
    "robot_wireless",
    "creep_rupture",
    "olympic_marathon_men",
    "xw_pen",
    "ripley_prnn_data",
]


def _test_dataset_dimensions(dataset_name, dataset_function, arg=None):
    """Test function for testing dataset dimensions."""
    with mock.patch('builtins.input', return_value="Y"):
        if arg is None:
            d = dataset_function()
        else:
            d = dataset_function(arg)
    
    ks = d.keys()
    
    # Check dimensions
    if "Y" in ks and "X" in ks:
        assert d["X"].shape[0] == d["Y"].shape[0]
    if "Ytest" in ks and "Xtest" in ks:
        assert d["Xtest"].shape[0] == d["Ytest"].shape[0]
    if "Y" in ks and "Ytest" in ks:
        assert d["Y"].shape[1] == d["Ytest"].shape[1]
    if "X" in ks and "Xtest" in ks:
        assert d["X"].shape[1] == d["Xtest"].shape[1]
    if "covariates" in ks and "X" in ks:
        assert len(d["covariates"]) == d["X"].shape[1]
    if "response" in ks and "Y" in ks:
        assert len(d["response"]) == d["Y"].shape[1]


# Generate test functions for each dataset
for dataset in dataset_test:
    test_name = f"test_{dataset['dataset_name']}_dimensions"
    test_func = lambda d=dataset: _test_dataset_dimensions(
        d["dataset_name"], d["dataset_function"], d["arg"]
    )
    test_func.__name__ = test_name
    test_func.__doc__ = f"datasets_tests: Test function pods.datasets.{dataset['dataset_name']}"
    globals()[test_name] = test_func


class DatasetsTests(unittest.TestCase):
    def download_data(self, dataset_name):
        """datasets_tests: Test the data download."""
        pods.access.clear_cache(dataset_name)
        self.assertFalse(pods.access.data_available(dataset_name))
        with mock.patch('builtins.input', return_value="Y"):
            pods.access.download_data(dataset_name)
        self.assertTrue(pods.access.data_available(dataset_name))

    def test_input(self):
        """datasets_tests: Test the prompt input checking code"""
        for v in positive_return_values:
            with mock.patch('builtins.input', return_value=v):
                self.assertTrue(pods.access.prompt_stdin("Do you pass?"))

        for v in negative_return_values:
            with mock.patch('builtins.input', return_value=v):
                self.assertFalse(pods.access.prompt_stdin("Do you fail?"))

    def test_authorize_download(self):
        """datasets_tests: Test the download authorization code."""
        with mock.patch('builtins.input', return_value="Y"):
            for dataset_name in dataset_selection:
                self.assertTrue(pods.access.authorize_download(dataset_name))

    def test_clear_cache(self):
        """datasets_tests: Test the clearing of the data cache for a data set"""
        for dataset_name in dataset_selection:
            print("Remove data", dataset_name)
            pods.access.clear_cache(dataset_name)
            self.assertFalse(pods.access.data_available(dataset_name))

    def test_data_downloads(self):
        """datasets_tests: Test the data download."""
        for dataset_name in dataset_selection:
            self.download_data(dataset_name)
