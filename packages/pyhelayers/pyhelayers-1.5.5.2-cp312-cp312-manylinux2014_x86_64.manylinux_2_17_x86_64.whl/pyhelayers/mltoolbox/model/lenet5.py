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
import torch.nn as nn
from pyhelayers.mltoolbox.model.nn_module import nn_module
from pyhelayers.mltoolbox.model.DNN_factory import DNNFactory

@DNNFactory.register('lenet5')
class Lenet5(nn_module):
    """Based on Lenet5 model architecture from the 
    `" Gradient-Based Learning Applied to Document Recognition..." by LeCun et al. in their 1998 <http://yann.lecun.com/exdb/publis/pdf/lecun-01a.pdf>`_ paper.

    The following changes applied, to make the model FHE-Friendly:
    - max-pooling replaced by average-pooling

    Note that the model is not fully FHE-Friendly - the Relu activations still need to be replaced
    """
    
    INPUT_SIZE = (3, 32, 32)
    def __init__(self, classes=3,**kwargs):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 6, kernel_size=(5, 5), stride=(1, 1), padding=0),
            nn.ReLU(inplace=True),
            nn.AvgPool2d(kernel_size=2, stride=2, padding=0),
            nn.Conv2d(6, 16, kernel_size=(5, 5), stride=(1, 1), padding=0),
            nn.ReLU(inplace=True),
            nn.AvgPool2d(kernel_size=2, stride=2, padding=0),
            nn.Flatten(start_dim=1, end_dim=-1),
            nn.Linear(in_features=400, out_features=120, bias=True),  # 120
            nn.ReLU(inplace=True),
            nn.Linear(in_features=120, out_features=84, bias=True),  # 120
            nn.ReLU(inplace=True),
            nn.Linear(in_features=84, out_features=10, bias=True)
        )

    def forward(self, x):
        super().forward(x)
        x = self.cnn(x)
        return x


def lenet5(**kwargs):
    model = Lenet5(**kwargs).cnn
    return model

