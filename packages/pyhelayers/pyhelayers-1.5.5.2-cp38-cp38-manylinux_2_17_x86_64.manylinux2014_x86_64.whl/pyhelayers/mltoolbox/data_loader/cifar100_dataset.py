# MIT License

# Copyright (c) 2020 International Business Machines

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from sklearn.model_selection import train_test_split
from torch.utils.data import Subset
import torch
from torchvision import transforms, datasets
from pyhelayers.mltoolbox.data_loader.dataset_wrapper import DatasetWrapper
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from pyhelayers.mltoolbox.data_loader.ds_factory import DSFactory
from pyhelayers.mltoolbox.utils.util import is_cuda_available
#import torchvision




class Cifar100Dataset(DatasetWrapper):
    """A wrapper to the standard Cifar100 dataset, available at torchvision.datasets.CIFAR100. The current wrapper class supplyes
    the required transformations and augmentations, and also implements the required DatasetWrapper methods

    """
    def __init__(self, resize=False, data_path ='cifar_data'):
        self.resize = resize

        self.logger = get_logger()
        norm = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

        test_transformations = [
            transforms.ToTensor(),
            norm
        ]

        if resize:
            test_transformations = [transforms.Resize(256), transforms.CenterCrop(224)] + test_transformations

        self.path = data_path


        augment_transform = [
                                transforms.RandomHorizontalFlip(),  # FLips the image w.r.t horizontal axis
                                transforms.RandomRotation(10),  # Rotates the image to a specified angel
                                transforms.RandomAffine(0, shear=10, scale=(0.8, 1.2)),  # Performs actions like zooms, change shear angles.
                                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),  # Set the color params
                            ]

        train_transformations = list([*augment_transform, *test_transformations])


        transform_test = transforms.Compose(test_transformations)
        transform_train = transforms.Compose(train_transformations)

        self._train_data =  self.__get_dataset("train", transform_train,  path=data_path)
        self._test_data, self._val_data =  self.__test_val_dataset(transform_test, path=data_path, val_split=0.5)
        self._approximation_data = self._split_approximation_set(0.2)

    def get_class_labels_dict(self):
        cls_to_idx = {str(i): i for i in range(100)}
        return cls_to_idx

    def is_imbalanced(self):
        """Always returns False - Cifar100 dataset is balanced"""
        return False

    def get_train_data(self):
        """Returns the training data"""
        return self._train_data

    def get_test_data(self):
        """Returns the test data"""
        return self._test_data

    def get_val_data(self):
        """Returns the validation data"""
        return self._val_data


    def get_samples_per_class(self, ds):
        """Returns the number of samples in each class.
        The Cifar100 dataset has the same number of images in each class.
        params:
                - dataset (VisionDataset): The dataset
        returns:
                - list<int>: the number of samples in each class.
        """
        assert (isinstance(ds, datasets.CIFAR100))
        data_len = len(ds)
        return  [data_len / 100] * 100


    def get_approximation_set(self):
        """Returns data set to be used for range approximation"""
        return self._approximation_data


    def get_train_pipe_ffcv(self, args):
        """Returns the training data as ffcv pipeline
        Params:
                - args (Arguments): user arguments
        Returns:
                - Dictionary: a dictionary of shape {'image': <image_pipeline>, 'label': <label_pipeline>} representing the corresponding ffcv pipelines, as explained: https://docs.ffcv.io/making_dataloaders.html#pipelines
        """
        from ffcv.transforms import ToTensor, ToDevice, ToTorchImage, RandomHorizontalFlip, Convert,RandomTranslate, Cutout, NormalizeImage
        from ffcv.fields.decoders import IntDecoder, RandomResizedCropRGBImageDecoder, SimpleRGBImageDecoder
        from ffcv.transforms.common import Squeeze

        this_device = f'cuda:{args.local_rank}'

        CIFAR_MEAN = [125.307, 122.961, 113.8575]
        CIFAR_STD = [51.5865, 50.847, 51.255]

        # Data decoding and augmentation
        image_pipeline = [
                        SimpleRGBImageDecoder(),
                        RandomHorizontalFlip(),
                        RandomTranslate(padding=2, fill=tuple(map(int, CIFAR_MEAN))),
                        Cutout(4, tuple(map(int, CIFAR_MEAN))),
                        ToTensor()]

        label_pipeline = [IntDecoder(), ToTensor()]

        if is_cuda_available():
            image_pipeline.extend([ToDevice(this_device, non_blocking=True)])
            label_pipeline.extend([ToDevice(this_device, non_blocking=True)])

        image_pipeline.extend([
                        ToTorchImage(),
                        Convert(torch.float16),
                     ])

        label_pipeline.extend([ Squeeze()])

        if self.resize:
            self.logger.debug("RESIZING TO 224")
            image_pipeline.extend([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                ])

        image_pipeline.extend([transforms.Normalize(CIFAR_MEAN, CIFAR_STD)])


        # Pipeline for each data field
        pipelines = {
            'image': image_pipeline,
            'label': label_pipeline
        }

        return pipelines


    def __test_val_dataset(self, transform, path, val_split=0.5):
        """Splits the data and returns validation and test sets"""
        ds = datasets.CIFAR100(root=path, train=False, download=True, transform=transform)

        test_idx, val_idx = train_test_split(list(range(len(ds))), test_size=val_split, random_state=42)
        val_ds = Subset(ds, val_idx)
        test_ds = Subset(ds, test_idx)

        val_ds.LABEL2NAME_DICT = ds.class_to_idx
        test_ds.LABEL2NAME_DICT = ds.class_to_idx

        return val_ds, test_ds


    def __get_dataset(self, mode, transform,  path):
        """returns the torchvision.datasets.CIFAR100 dataset"""
        ds = datasets.CIFAR100(root=path, train=(mode == 'train'), download=True, transform=transform)
        return ds


@DSFactory.register('CIFAR100')
class Cifar100Dataset_32(Cifar100Dataset):
    def __init__(self, path ='cifar100_data', args = None, **kwargs):
        super().__init__(False, path)


@DSFactory.register('CIFAR100_224')
class Cifar100Dataset_224(Cifar100Dataset):
    def __init__(self, path ='cifar100_data', args = None, **kwargs):
        super().__init__(True, path)
        
