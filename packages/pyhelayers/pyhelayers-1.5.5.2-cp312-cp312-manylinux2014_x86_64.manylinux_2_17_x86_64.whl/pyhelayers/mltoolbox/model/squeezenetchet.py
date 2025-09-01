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
import torch.nn.functional as F
from pyhelayers.mltoolbox.model.nn_module import nn_module
from pyhelayers.mltoolbox.model.DNN_factory import DNNFactory

class Fire(nn.Module):
    def __init__(self, inplanes: int, squeeze_planes: int, expand1x1_planes: int, expand3x3_planes: int) -> None:
        super().__init__()
        self.inplanes = inplanes
        self.squeeze = nn.Conv2d(inplanes, squeeze_planes, kernel_size=1)
        self.squeeze_activation = nn.ReLU(inplace=True)
        self.expand1x1 = nn.Conv2d(squeeze_planes, expand1x1_planes, kernel_size=1)
        self.expand1x1_activation = nn.ReLU(inplace=True)
        self.expand3x3 = nn.Conv2d(squeeze_planes, expand3x3_planes, kernel_size=3, padding=1)
        self.expand3x3_activation = nn.ReLU(inplace=True)
        self.concat_activation = nn.ReLU(inplace=True)  # unified relus

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.squeeze_activation(self.squeeze(x))
        x = torch.cat([self.expand1x1_activation(self.expand1x1(x)), self.expand3x3_activation(self.expand3x3(x))], 1)  # separated ReLUs
        # x = self.concat_activation(torch.cat([self.expand1x1(x), self.expand3x3(x)], 1))  # unified ReLUs
        return x


@DNNFactory.register('squeezenet_CHET')
class SqueezeNetCHET(nn_module):
    """Based on 'CHET: An Optimizing Compiler for Fully-Homomorphic Neural-Network Inferencing' <https://www.cs.utexas.edu/~roshan/CHET.pdf> paper

    Note that the model is not fully FHE-Friendly - contains Relu activations, that still need to be replaced
    """
    INPUT_SIZE = (3, 32, 32)
    def __init__(self, add_bn=False, num_classes: int = 10, dropout: float = 0.5, **kwargs) -> None:
        super().__init__()
        self.num_classes = num_classes
        
        self.features = nn.Sequential(
                nn.Conv2d(3, 64, kernel_size=3, stride=1,padding=1),
                nn.ReLU(inplace=True),
                nn.AvgPool2d(kernel_size=3, stride=2, padding=1, ceil_mode=False),
                Fire(64, 32, 64, 64),  # Fire(64, 16, 64, 64),
                Fire(128, 32, 64, 64),  # Fire(128, 16, 64, 64),
                nn.AvgPool2d(kernel_size=3, stride=2, padding=1, ceil_mode=False),
                Fire(128, 32, 128, 128),
                Fire(256, 32, 128, 128),
            )

        self.classifier = nn.Sequential(
            nn.Conv2d(256, self.num_classes, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.AvgPool2d((8, 8), stride=1)
        )

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.xavier_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)

        self.cnn = nn.Sequential(
            self.features,
            self.classifier
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        super().forward(x)
        x = self.cnn(x)
        x = torch.flatten(x, 1)
        return x
        
def squeezenet_chet(**kwargs):
    model = SqueezeNetCHET(**kwargs)
    return model


if __name__=="__main__":
    from torchsummary import summary
    summary(squeezenet_chet(), (3, 32, 32))

