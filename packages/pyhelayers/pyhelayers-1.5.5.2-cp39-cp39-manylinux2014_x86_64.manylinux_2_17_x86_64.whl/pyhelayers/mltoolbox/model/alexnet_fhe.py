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

import torch

from torchvision import models
import torch.nn as nn
import pyhelayers.mltoolbox.he_dl_lib.poly_activations as poly_activations
from pyhelayers.mltoolbox.model.nn_module import nn_module
from pyhelayers.mltoolbox.model.DNN_factory import DNNFactory

@DNNFactory.register('alexnet')
class alexnet_fhe(nn_module):
    """Based on AlexNet model architecture with weights pretrained on Imagenet. 
    The following changes applied, to make the model FHE-Friendly:
    - batch normalization added after max-pooling (after layers 2,5,12)
    - Adaptive average-pooling removed
    - max-pooling replaced by average-pooling

    Note that the model is not fully FHE-Friendly - the Relu activations still need to be replaced
    
    """
    
    INPUT_SIZE = (3, 224, 224)
    def __init__(self, classes, pooling_type='max', add_bn=False, **kwargs):
        super().__init__()

        self.cnn = models.alexnet(pretrained=True)
        self.add_bn = add_bn

        # change padding of the first input layer
        conv_activations = poly_activations.find_modules_by_type(self.cnn, nn.Conv2d)
        (name, module) = conv_activations[0]
        poly_activations.change_module(self.cnn, name, nn.Conv2d(module.in_channels, module.out_channels,
                                                                 module.kernel_size, module.stride, padding=5))
        # Add output layer
        self.cnn.classifier[6] = nn.Linear(4096, classes)

        # drop adaptive_avgpool, and update the first linear layer size
        self.cnn.avgpool = nn.Identity()

        bn_list = []
        bn_list.append(self.bn_info("features.2",64))
        bn_list.append(self.bn_info("features.5",192))
        bn_list.append(self.bn_info("features.12",256))
        self.make_fhe_friendly(self.add_bn, pooling_type, bn_list)


    def forward(self, x):
        super().forward(x)
        return self.cnn(x)

