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

from torch.utils.data import Dataset
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from sklearn.model_selection import train_test_split
from torch.utils.data import Subset

logger = get_logger()


class DatasetWrapper:
    """This class serves as interface for all the mltoolbox datasets.
    Each mltoolbox dataset must implement the declared functionality.
    
    The steps to extend the mltoolbox with an additional dataset:
    1. Extend the DatasetWrapper class, implementing the data retrieval methods. The data retrieval methods have to return a torch.utils.data.Dataset object.
    You may use one of torch built-in datasets, or create a custom dataset. See the list of `built-in datasets <https://pytorch.org/vision/stable/datasets.html#built-in-datasets>`__. 
    See `Creating a Custom Dataset for your files <https://pytorch.org/tutorials/beginner/basics/data_tutorial.html#creating-a-custom-dataset-for-your-files>`__. 
    More vision `base classes for custom vision datasets <https://pytorch.org/vision/stable/datasets.html#base-classes-for-custom-datasets>`__.
    2. Register the new class to DSFactory using the @DSFactory.register decoration

    .. code-block:: python

        from pyhelayers.mltoolbox.data_loader.dataset_wrapper import DatasetWrapper
        from pyhelayers.mltoolbox.data_loader.ds_factory import DSFactory
        from torch.utils.data import Dataset
        
        @DSFactory.register('new_dataset')
        class newDataset(DatasetWrapper):
           def get_train_data(self):
                return _newDatasetLoader(mode='train')
                
           def get_test_data(self):
                return _newDatasetLoader(mode='test')
                
            def get_val_data(self):
                return _newDatasetLoader(mode='val')
        
        
        class _myNewDatasetLoader(Dataset):  
            def __getitem__(self, index):
                ...
                return image_tensor, label_tensor
                

    3. Add an import to the new class in your main (so that the new class gets registered on start)
    
    .. code-block:: console

        import newDataset

    """
    def __init__(self, name, path, classes):
        """
        Initializes the DatasetWrapper, serving as a base interface for all mltoolbox datasets.
        This class enforces the implementation of data retrieval methods in subclasses.

        Args:
            name (str): The name of the dataset.
            path (str): The directory where the dataset is stored.
            classes (int): The number of classes in the dataset.
        """
        self.name = name


    def get_train_data(self) -> Dataset:
        """Returns the train dataset

        Returns:
            Dataset: train dataset
        """
        logger.info("Dataset.get_train_data: None dataset, base class used")
        return None


    def get_test_data(self) -> Dataset:
        """Returns the test dataset

        Returns:
            Dataset: test dataset
        """
        logger.info("Dataset.get_test_data: None dataset, base class used")
        return None


    def get_val_data(self) -> Dataset:
        """Returns the validation dataset

        Returns:
            Dataset: validation dataset
        """
        logger.info("Dataset.get_val_data: None dataset, base class used")
        return None

    def get_approximation_set(self) ->Dataset:
        """returns the approximation data set, to be used for range approximation

         Returns:
            Dataset: approximation dataset
        """
        return None


    def get_train_pipe_ffcv(self, args) -> dict:
        """Returns the Dictionary defining for each field the sequence of ffcv Decoders and transforms to apply.
        Fileds with missing entries will use the default pipeline, which consists of the default decoder and ToTensor(),
        but a field can also be disabled by explicitly by passing None as its pipeline.
        https://docs.ffcv.io/api/loader.html

        Params:
            - args (Arguments): user arguments

        Returns:
            Dictionary: dictionary of shape: {'image': <image_pipeline>, 'label': <label_pipeline>} as explained: https://docs.ffcv.io/making_dataloaders.html#pipelines
            another example: https://docs.ffcv.io/ffcv_examples/cifar10.html
        """
        logger.info(f'Dataset.get_train_pipe_ffcv: ffcv is not supported for dataset {args.dataset_name}. None dataset, base class used')
        return None

    def _split_approximation_set(self, size=0.05):
        """splits a subset of train data to be used for range approximation.
        (No need for the entire train subset, which would only elongate runtime)

        """
        train_data = self.get_train_data()
        _, approx_idx = train_test_split(list(range(len(train_data))), test_size=size, random_state=42)
        approximation_ds = Subset(train_data, approx_idx)
        approximation_ds.LABEL2NAME_DICT = train_data.class_to_idx

        logger.info(f'aprox set size is {len(approximation_ds)}')
        return approximation_ds


    def is_imbalanced(self) -> bool:
        """Returns True if the data is imbalanced

        Returns:
            bool: True if the data is imbalanced and False otherways
        """
        return False
    

    def get_samples_per_class(self, dataset: Dataset):
        """Returns the number of samples in each class or None (if the dataset is balanced - None is equivalent to a list with equal numbers) 
        Args:
            dataset (Dataset): the dataset split
        Returns:
            list<int>: The number of samples in each class, or None (if the dataset is balanced - None is equivalent to a list with equal numbers) 
        """
        return None
    
    def get_class_labels_dict(self):
        """Returns the class_name to index mapping

        Returns:
            Dictionary: A dictionary with items (class_name, class_index).
        """
        return None

