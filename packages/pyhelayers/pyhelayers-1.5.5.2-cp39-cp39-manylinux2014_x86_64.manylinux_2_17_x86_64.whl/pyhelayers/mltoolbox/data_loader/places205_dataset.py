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

from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, random_split, Subset
from torchvision import transforms,datasets
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from pyhelayers.mltoolbox.data_loader.dataset_wrapper import DatasetWrapper
from pyhelayers.mltoolbox.data_loader.ds_factory import DSFactory


logger = get_logger()


class _loader(datasets.ImageFolder):
    def __init__(self, classes, csv_path, images_path, transform = None, target_transform = None, is_valid_file = None):
        self.classes = classes
        self.csv_path = csv_path
        super().__init__(images_path, transform=transform, target_transform=target_transform,is_valid_file=is_valid_file)

    def find_classes(self,directory):
            def process(line: str):
                cls, idx = line.split()
                cls = cls.split('/')[0]+"/"+cls.split('/')[1]
                return cls, int(idx)

            with open(self.csv_path, "r") as fh:
                class_to_idx = dict(process(line) for line in fh)

            filtered = {k: v for k, v in class_to_idx.items() if v < self.classes} ##50: only abc - (52K entries)
            return sorted(filtered.keys()), filtered


@DSFactory.register('Places205')
class places205Dataset(DatasetWrapper):
    """A wrapper to the places205 dataset, available at http://places.csail.mit.edu/. The current wrapper class supplyes
    the required transformations, and also implements the required DatasetWrapper methods.
    """
    def __init__(self, classes=201, path='places205_data', **kwards):
        """
        Initializes the places205Dataset wrapper, providing an interface for handling the Places205 dataset.
        This class is registered under the name 'Places205' in the DSFactory.

        Args:
            classes (int, optional): The number of classes in the dataset. Defaults to 201.
            path (str, optional): The directory where the dataset is stored. Defaults to 'places205_data'.
            **kwargs: Unused keyword arguments, included for compatibility with other dataset constructors.
        """
        self.csv_path = path + "/trainvalsplit_places205/train_places205.csv"
        self.train_path = path + '/data/train_data/'
        self.test_path = path + '/data/test_data/'
        self.classes = classes
        self.train_ds = None
        self.test_ds = None
        self.train_ds = None

    def __get_train_ds(self):
        train_ds = _loader(self.classes, self.csv_path, self.train_path, transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                             std=[0.229, 0.224, 0.225]),
        ]))

        return train_ds

    def _get_test_ds(self):
        test_ds = _loader(self.classes, self.csv_path, self.test_path, transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                             std=[0.229, 0.224, 0.225]),
        ]))
        return test_ds


    def _get_train_data(self):
        if not self.train_ds:
            self.train_ds = self.__get_train_ds()
            self.train_ds.LABEL2NAME_DICT = self.train_ds.class_to_idx
        return self.train_ds

    def _get_test_data(self, val_split=0.005):
        if not self.test_ds:
            ds = self._get_test_ds()
            test_ds, val_ds = train_test_split(list(range(len(ds))), test_size=0.5, random_state=42)

            self.test_ds = Subset(ds, test_ds)
            self.val_ds = Subset(ds, val_ds)
            self.val_ds.LABEL2NAME_DICT = ds.class_to_idx

            self.val_ds.LABEL2NAME_DICT = ds.class_to_idx
            self.test_ds.LABEL2NAME_DICT = ds.class_to_idx

        return self.test_ds, self.val_ds


    def get_train_data(self):
        """Returns the training data"""
        self._get_train_data()
        return self.train_ds

    def get_test_data(self):
        """Returns the test data"""
        self._get_test_data()
        return self.test_ds

    def get_val_data(self):
        """Returns the validation data"""
        self._get_test_data()
        return self.val_ds

    def is_imbalanced(self):
        """Always returns False - places205 dataset is balanced"""
        return False
    
    def get_class_labels_dict(self):
        if not self.train_ds:
            self.get_train_data()
        return self.train_ds.LABEL2NAME_DICT


