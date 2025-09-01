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
from pyhelayers.mltoolbox.model.nn_module import nn_module
from pyhelayers.mltoolbox.model.DNN_factory import DNNFactory


class resnet_fhe(nn_module):
    INPUT_SIZE = (3, 224, 224)
    def __init__(self, arch, classes, pooling_type='max', add_bn=False):
        super().__init__()

        if arch == 'resnet50':
            self.cnn = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2) #acc 80.858
        elif arch == 'resnet18':
            self.cnn = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1) #acc69.758 no IMAGENET1K_V2 here
        elif arch == 'resnet152':
            self.cnn = models.resnet152(weights=models.ResNet152_Weights.IMAGENET1K_V2) #acc 82.284
        elif arch == 'resnet101':
            self.cnn = models.resnet101(weights=models.ResNet101_Weights.IMAGENET1K_V2) #acc 81.88
        else:
            print("unsupported resnet arch: " + type)
            return

        # drop adaptive_avgpool
        self.cnn.avgpool = nn.AvgPool2d(7,1) 

        #change number of out classes
        if self.cnn.fc.out_features!=classes:
            print("replacing linear layer")
            self.cnn.fc = nn.Linear(self.cnn.fc.in_features, classes)
        else:
            print("keeping linear layer")

        self.make_fhe_friendly(False, pooling_type)


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        super().forward(x)
        return self.cnn(x)
    


@DNNFactory.register('resnet50')
class resnet50_fhe(resnet_fhe):
    INPUT_SIZE = (3, 224, 224)
    def __init__(self, classes, pooling_type='max', add_bn=False, **kwargs):
        super().__init__('resnet50', classes, pooling_type, add_bn)



@DNNFactory.register('resnet18')
class resnet18_fhe(resnet_fhe):
    def __init__(self, classes, pooling_type='max', add_bn=False, **kwargs):
        super().__init__('resnet18', classes, pooling_type, add_bn)


@DNNFactory.register('resnet152')
class resnet152_fhe(resnet_fhe):
    def __init__(self, classes, pooling_type='max', add_bn=False, **kwargs):
        super().__init__('resnet152', classes, pooling_type, add_bn)

@DNNFactory.register('resnet101')
class resnet101_fhe(resnet_fhe):
    def __init__(self, classes, pooling_type='max', add_bn=False, **kwargs):
        super().__init__('resnet101', classes, pooling_type, add_bn)


