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

from torchvision import models
import torch.nn as nn
from pyhelayers.mltoolbox.model.nn_module import nn_module
from pyhelayers.mltoolbox.model.DNN_factory import DNNFactory



class SqueezeNet_FHE(nn_module):
    """Based on SqueezeNet model architecture from the `"SqueezeNet: AlexNet-level
    accuracy with 50x fewer parameters and <0.5MB model size"
    <https://arxiv.org/abs/1602.07360>`_ paper, with weights pretrained on ImageNet

    The following changes applied, to make the model FHE-Friendly:
    - Adaptive average-pooling replaced by average-pooling
    - max-pooling replaced by average-pooling
    - batch normalization added after each convolution layer

    Note that the model is not fully FHE-Friendly - the Relu activations still need to be replaced
    """
    INPUT_SIZE = (3, 224, 224)
    def __init__(self, get_cnn, num_classes, pooling_type='max', add_bn=False, **kwargs):
        super().__init__()

        self.cnn = get_cnn(None)
        self.cnn.num_classes = num_classes
        self.add_bn = add_bn

        # replace adaptive avggpool by avgpool
        self.cnn.classifier[3] = nn.AvgPool2d(kernel_size=13)

        # change final_conv layer to fit the number of classes
        self.cnn.classifier[1] = nn.Conv2d(512, num_classes, kernel_size=1)

        self.make_fhe_friendly(self.add_bn, pooling_type)

    def forward(self, x):
        super().forward(x)
        return self.cnn(x)


version={'1_0': lambda x: models.squeezenet1_0(pretrained=True),
         '1_1': lambda x: models.squeezenet1_1(pretrained=True)
        }


@DNNFactory.register('squeezenet1_0')
class SqueezeNet1_0_FHE(SqueezeNet_FHE):
    """_summary_
    squeezenet1_0 partially FHE-Friendly
    """
    def __init__(self, num_classes, pooling_type='max', add_bn=False):  
        super().__init__(version['1_0'], num_classes, pooling_type, add_bn)


@DNNFactory.register('squeezenet1_1')
class SqueezeNet1_1_FHE(SqueezeNet_FHE):
    """_summary_
    squeezenet1_1 partially FHE-Friendly
    """
    def __init__(self, num_classes, pooling_type='max', add_bn=False):
         super().__init__(version['1_1'], num_classes, pooling_type, add_bn)