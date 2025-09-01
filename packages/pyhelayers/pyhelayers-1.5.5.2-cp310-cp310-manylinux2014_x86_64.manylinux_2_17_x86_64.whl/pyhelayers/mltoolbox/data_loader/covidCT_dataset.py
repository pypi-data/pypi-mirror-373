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

import os

import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms
import numpy as np
from pyhelayers.mltoolbox.data_loader.dataset_wrapper import DatasetWrapper
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from pyhelayers.mltoolbox.data_loader.ds_factory import DSFactory

TXT_FILE = '{}_COVIDx_CT-2A.txt'
COVID_CT_DIR_NAME = 'covid_ct_2A'
MAX_SAMPLES_PER_CLASS = {'train': 10000, 'val': 1000, 'test': 1000}
logger = get_logger()

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

train_transformer = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomResizedCrop(224, scale=(0.8, 1.2)),
    transforms.RandomRotation(15),
    transforms.RandomHorizontalFlip(p=0.1),
    transforms.RandomVerticalFlip(p=0.1),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
    transforms.ToTensor(),
    normalize
])

val_transformer = transforms.Compose([
    transforms.Resize(224),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalize
])

test_transformer = val_transformer

transformer_dict = {'train': train_transformer,
                    'val': val_transformer,
                    'test': test_transformer}


@DSFactory.register('COVID_CT')
class CovidCTDataset(DatasetWrapper):
    """A wrapper for the _CovidCT2A_Dataset

    """
    def __init__(self, classes, path, **kwards):
        """
        Initializes the CovidCTDataset wrapper for the _CovidCT2A_Dataset. 
        This class is registered under the name 'COVID_CT' in the DSFactory.

        Args:
            classes (int): The number of classes in the dataset.
            path (str): The base directory where the dataset is stored.
            **kwargs: Additional keyword arguments. Not used. (Maintained for consistency with other dataset constructors)
        """
        self.path = os.path.join(path, 'data')
        self.classes = classes

    def get_test_data(self):
        return _CovidCT2A_Dataset(mode='test', n_classes=self.classes, dataset_path=self.path)

    def get_val_data(self):
        return _CovidCT2A_Dataset(mode='val', n_classes=self.classes, dataset_path=self.path)

    def get_train_data(self):
        return _CovidCT2A_Dataset(mode='train', n_classes=self.classes, dataset_path=self.path)

    def is_imbalanced(self):
        return False
    
    def get_class_labels_dict(self):
        return {'Pneumonia': 0, 'Normal': 1, 'COVID19': 2}

class _CovidCT2A_Dataset(Dataset):
    """A dataset definition for the data in https://www.kaggle.com/hgunraj/covidxct
    The data needs to be manually downloaded into the dataset_path
    """
    
    def __init__(self, mode, n_classes=3, dataset_path='./data/covid_ct_2A', dim=(224, 224)):
        """
        Args:
            txt_path (string): Annotations file location (.txt).
            root_dir (string): Images folder location.
        File structure:
        - root_dir
            - covid_ct_2A
                - 2A_images
                    - img1.png
                    - img2.png
                    - ......
                - train_COVIDx_CT-2A.txt
                - val_COVIDx_CT-2A.txt
                - test_COVIDx_CT-2A.txt
        """
        self.data_dir = os.path.join(dataset_path, COVID_CT_DIR_NAME, '2A_images')
        self.txt_path = os.path.join(dataset_path, COVID_CT_DIR_NAME, TXT_FILE.format(mode))
        self.LABEL2NAME_DICT = {'Pneumonia': 0, 'Normal': 1, 'COVID19': 2}
        self.num_cls = n_classes
        self.dim = dim
        self.transform = transformer_dict[mode]
        self.mode = mode

        self.files, self.labels, self.bboxes = self._make_dataset(mode)

        self.samples_per_cls = []
        self.labels = np.array(self.labels)
        for cls in range(n_classes):
            indices = np.where(self.labels == cls)[0]
            self.samples_per_cls.append(len(indices))
        count = len(self.files)

        logger.info(f" {self.mode}: {count} samples")

    def _get_files(self):
        """Gets image filenames and classes"""
        files, classes, bboxes = [], [], []
        with open(self.txt_path, 'r') as f:
            for line in f.readlines():
                fname, cls, xmin, ymin, xmax, ymax = line.strip('\n').split()
                files.append(os.path.join(self.data_dir, fname))
                classes.append(int(cls))
                bboxes.append([int(xmin), int(ymin), int(xmax), int(ymax)])
        return files, classes, bboxes

    def _make_dataset(self, split_file, balanced=True):
        """Creates COVIDX-CT dataset for train or val split"""
        files, classes, bboxes = self._get_files()

        if not balanced:
            return files, classes, bboxes

        files = np.asarray(files)
        classes = np.asarray(classes, dtype=np.int32)
        bboxes = np.asarray(bboxes, dtype=np.int32)

        filtered_files = []
        filtered_classes = []
        filtered_bboxes = []

        for cls in range(len(self.LABEL2NAME_DICT)):
            indices = np.where(classes == cls)[0]
            filtered_files.extend(files[indices][:MAX_SAMPLES_PER_CLASS[self.mode]])
            filtered_classes.extend(classes[indices][:MAX_SAMPLES_PER_CLASS[self.mode]])
            filtered_bboxes.extend(bboxes[indices][:MAX_SAMPLES_PER_CLASS[self.mode]])

        return filtered_files, filtered_classes, filtered_bboxes

    def __len__(self):
        return len(self.labels)

    def _load_image(self, img_path, dim, bbox=None):
        # bbox format: [xmin, ymin, xmax, ymax]
        if not os.path.exists(img_path):
            print("IMAGE DOES NOT EXIST {}".format(img_path))

        image = Image.open(img_path)
        cropped = image.crop(bbox)
        cropped = cropped.convert('RGB')
        cropped = cropped.resize(dim)

        image_tensor = self.transform(cropped)
        return image_tensor

    def __getitem__(self, index):
        try:
            image_tensor = self._load_image(self.files[index], self.dim, bbox=self.bboxes[index])
            label_tensor = torch.tensor(self.labels[index], dtype=torch.long)
        except Exception as e:
            print((self.files[index]))
            print(e)
            return None, None
        return image_tensor, label_tensor

if __name__ == '__main__':
    import h5py
    import sys

    sys.path.insert(0, 'COVID19/COVIDNet')


    mode = "test"
    MAX_SAMPLES_PER_CLASS = {'train': 10000, 'val': 1000, 'test': 35}

    save_title = '100'

    from torch.utils.data import DataLoader
    dataset = _CovidCT2A_Dataset(mode=mode, n_classes=3,
                              dataset_path='/dccstor/ai_security2/COVID19/data/',
                              dim=(224, 224))

    test_params = {'batch_size': 110,
                   'shuffle': False,
                   'num_workers': 4,
                   'pin_memory': True}

    full_labels = []
    full_images = []

    test_loader = DataLoader(dataset, **test_params)
    for idx, (images, labels) in enumerate(test_loader):

        full_images.extend(list(images.numpy()))
        full_labels.extend(list(labels.numpy()))

    full_images = np.array(full_images)
    full_labels = np.array(full_labels)

    # save
    with h5py.File(f'/dccstor/ai_security2/COVID19/data/covid_ct_2A/covidCT_{mode}_{save_title}_images.h5', 'w') as hf:
        hf.create_dataset(f"covidCT_{mode}_images", data=full_images)

    # save
    with h5py.File(f'/dccstor/ai_security2/COVID19/data/covid_ct_2A/covidCT_{mode}_{save_title}_labels.h5', 'w') as hf:
        hf.create_dataset(f"covidCT_{mode}_labels", data=full_labels)
