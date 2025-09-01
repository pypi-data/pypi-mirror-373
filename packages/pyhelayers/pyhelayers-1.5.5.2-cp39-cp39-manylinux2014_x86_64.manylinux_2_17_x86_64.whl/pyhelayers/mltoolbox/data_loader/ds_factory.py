# MIT License
#
# Copyright (c) 2020 International Business Machines
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Callable
from pyhelayers.mltoolbox.data_loader.dataset_wrapper import DatasetWrapper
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger

class DSFactory:
    
    registry = {}
    
    @classmethod
    def register(self, name: str) -> Callable:
        logger = get_logger()
        def inner_wrapper(wrapped_class: DatasetWrapper) -> Callable:
            if name in self.registry:
                logger.warning('Dataset %s already exists. Will replace it', name)
            self.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper

    
    @classmethod
    def get_ds(self, name: str, **kwargs):
        """ Factory command to create the dataset.
        This method gets the appropriate dataset class from the registry
        and creates an instance of it, while passing in the parameters
        given in ``kwargs``.
        Args:
            name (str): The name of the dataset to create.
        Returns:
            An instance of the dataset that is created.
        """
        logger = get_logger()
        logger.debug(self.registry)
        if name not in self.registry:
            logger.error('Dataset %s does not exist in the registry', name)
            raise Exception("Unsupported dataset name")

        ds_class = self.registry[name]
        ds = ds_class(**kwargs)
        return ds

    @classmethod
    def print_supported_datasets(self):
        """
        A convenience method that prints all the registered datasets currently available
        """
        print(f'The supported datasets values are: {self.registry.keys()}')

