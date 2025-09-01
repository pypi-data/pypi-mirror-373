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
from torch.utils.data import Dataset
import numpy as np
from pyhelayers.mltoolbox.utils.util import read_filepaths
from PIL import Image
from torchvision import transforms
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from pyhelayers.mltoolbox.data_loader.dataset_wrapper import DatasetWrapper
from pyhelayers.mltoolbox.data_loader.ds_factory import DSFactory

logger = get_logger()
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
train_transformer = transforms.Compose([
    transforms.Resize(256),
    transforms.RandomResizedCrop(224, scale=(0.5, 1.0)),
    transforms.RandomHorizontalFlip(),
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

@DSFactory.register('COVID-Xray')
class CovidXrayDataset(DatasetWrapper):
    """A wrapper for the _CovidXrayDataset

    """
    def __init__(self, classes, path, **kwards):
        self.path = path
        self.classes = classes

    def get_test_data(self):
        return _CovidXrayDataset(mode='test', n_classes=self.classes, dataset_path=os.path.join(self.path, 'data'), dim=(224, 224))

    def get_val_data(self):
        return _CovidXrayDataset(mode='val', n_classes=self.classes, dataset_path=os.path.join(self.path, 'data'), dim=(224, 224))

    def get_train_data(self):
        return _CovidXrayDataset(mode='train', n_classes=self.classes, dataset_path=os.path.join(self.path, 'data'), dim=(224, 224))

    def is_imbalanced(self):
        return True
    
    def get_samples_per_class(self, dataset):
        assert (isinstance(dataset, _CovidXrayDataset))
        return dataset.samples_per_cls
    
    def get_class_labels_dict(self):
        return {'pneumonia': 0, 'normal': 1, 'COVID-19': 2}

class _CovidXrayDataset(Dataset):
    """ A dataset definition for the CovidXrayDataset, that is presented in the 'COVID-Net: a tailored deep convolutional neural network 
    design for detection of COVID-19 cases from chest X-ray images' <https://www.nature.com/articles/s41598-020-76550-z.pdf> paper.
    The data can be found in several sources, which are detailed in the following notebook: https://github.com/lindawangg/COVID-Net/blob/master/create_COVIDx.ipynb.
    The above notebook shows how to create the dataset from all the different sources.
    The data needs to be manually downloaded and preprocessed to the following file structure:
    - root_dir
        - data
            - train_split.txt
            - test_split.txt
            - val_split.txt
            - test
                - img1.png
                - img2.png
                - ......
            - train
                - img1.png
                - img2.png
                - ......
            - val
                - img1.png
                - img2.png
                - ......
    """
    def __init__(self, mode, n_classes=3, dataset_path='./data', dim=(224, 224)):
        self.root = str(dataset_path) + '/' + mode + '/'
        self.CLASSES = n_classes
        self.dim = dim
        self.LABEL2NAME_DICT = {'pneumonia': 0, 'normal': 1, 'COVID-19': 2}

        data_txt_file = os.path.join(dataset_path, f'{mode}_split.txt')

        paths, labels = read_filepaths(data_txt_file)
        self.paths, self.labels = [], []
        for i in range(len(paths)):
            if os.path.exists(os.path.join(self.root, paths[i])):
                self.paths.append(paths[i])
                self.labels.append(labels[i])

        if len(paths) != len(self.paths):
            logger.info(f'WARNING: {len(paths) - len(self.paths)} files were missing, ignoring them')

        self.samples_per_cls = []

        for cls in self.LABEL2NAME_DICT.keys():
            indices = np.where(np.array(self.labels) == cls)[0]
            self.samples_per_cls.append(len(indices))
        logger.info(f"samples per class: {self.samples_per_cls}")
        self.transform = transformer_dict[mode]

        logger.info("{} examples =  {}".format(mode, len(self.paths)))
        self.mode = mode

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, index):
        try:
            image_tensor = self.load_image(os.path.join(self.root, self.paths[index]), self.dim, augmentation=self.mode)
            label_tensor = torch.tensor(self.LABEL2NAME_DICT[self.labels[index]], dtype=torch.long)
        except Exception as e:
            print(f'Image path: {self.paths[index]}, INDEX: {index}')
            print(e)
            return None, None
        return image_tensor, label_tensor

    def load_image(self, img_path, dim, augmentation='test'):
        if not os.path.exists(img_path):
            print("IMAGE DOES NOT EXIST {}".format(img_path))
        image = Image.open(img_path).convert('RGB')
        image = image.resize(dim)

        image_tensor = self.transform(image)

        return image_tensor

