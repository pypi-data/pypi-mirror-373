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
import torchvision
import torch
from torch.utils.data import Dataset, random_split, Subset
from torchvision import transforms,datasets
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from pyhelayers.mltoolbox.data_loader.dataset_wrapper import DatasetWrapper
from pyhelayers.mltoolbox.data_loader.ds_factory import DSFactory
import numpy as np


logger = get_logger()


@DSFactory.register('Places365')
class places365Dataset(DatasetWrapper):
    """A wrapper to the places365 dataset, available at http://places.csail.mit.edu/. The current wrapper class supplyes
    the required transformations, and also implements the required DatasetWrapper methods.

    Args:
        DatasetWrapper (_type_): _description_
    """
    def __init__(self, classes=365, path='places365_small_download', **kwards):
        self.path = path
        self.classes = classes
        self.train_ds = None
        self.test_ds = None
        self.val_ds = None
        self.transform_test = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.transform_train = transforms.Compose([
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                             std=[0.229, 0.224, 0.225])
        ])

    def get_train_pipe_ffcv(self, args):
        """Returns the training data as ffcv pipeline
        Params:
                - args (Arguments): user arguments
        Returns:
                - Dictionary: a dictionary of shape {'image': <image_pipeline>, 'label': <label_pipeline>} representing the corresponding ffcv pipelines, as explained: https://docs.ffcv.io/making_dataloaders.html#pipelines
        """
        from ffcv.transforms import ToTensor, ToDevice, ToTorchImage, RandomHorizontalFlip, NormalizeImage, Squeeze
        from ffcv.fields.decoders import IntDecoder, RandomResizedCropRGBImageDecoder

        IMAGENET_MEAN = np.array([0.485, 0.456, 0.406]) * 255
        IMAGENET_STD = np.array([0.229, 0.224, 0.225]) * 255

        this_device = f'cuda:{args.local_rank}'
        # Data decoding and augmentation
        image_pipeline = [
                        RandomResizedCropRGBImageDecoder((224, 224)),
                        RandomHorizontalFlip(),
                        ToTensor(),
                        ToDevice(torch.device(this_device), non_blocking=True),
                        ToTorchImage(),
                        NormalizeImage(IMAGENET_MEAN,IMAGENET_STD, np.float16)
                        ]

        label_pipeline = [IntDecoder(), ToTensor(), Squeeze(), ToDevice(torch.device(this_device), non_blocking=True)]

        # Pipeline for each data field
        pipelines = {
            'image': image_pipeline,
            'label': label_pipeline
        }
        return pipelines


    def _get_train_data(self):
        if not self.train_ds:
            self.train_ds = self.getDS('train-standard',download = False, transform=self.transform_train) 
            self.train_ds.LABEL2NAME_DICT = self.train_ds.class_to_idx
        return self.train_ds

    def _get_test_data(self, val_split=0.005):
        if not self.test_ds:
            ds = self.getDS('val',download = False, transform=self.transform_test) 
            test_ds, val_ds = train_test_split(list(range(len(ds))), test_size=0.5, random_state=42)

            self.test_ds = Subset(ds, test_ds)
            self.val_ds = Subset(ds, val_ds)
            self.val_ds.LABEL2NAME_DICT = ds.class_to_idx

            self.val_ds.LABEL2NAME_DICT = ds.class_to_idx
            self.test_ds.LABEL2NAME_DICT = ds.class_to_idx

        return self.test_ds, self.val_ds

    def getDS(self, split, download, transform):
        return datasets.Places365(root=self.path, small=True, split=split, download=False, transform=transform)
        
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
        """Always returns False - places365 dataset is balanced"""
        return False
    
    def get_class_labels_dict(self):
        return self.train_ds.LABEL2NAME_DICT

    def get_approximation_set(self):
        """Returns data set to be used for range approximation"""
        if not self.train_ds:
            self._get_train_data()
        return self._split_approximation_set(0.05) #0.03
