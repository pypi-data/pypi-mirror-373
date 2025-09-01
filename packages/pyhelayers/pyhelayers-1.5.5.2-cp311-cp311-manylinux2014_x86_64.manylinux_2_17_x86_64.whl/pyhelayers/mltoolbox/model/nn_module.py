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

from torch import tensor
import torch.nn as nn
import pyhelayers.mltoolbox.he_dl_lib.poly_activations as poly_activations
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
import torch

logger = get_logger()

class nn_module(nn.Module):
    """This class serves as a wrapper for all the mltoolbox models.

    The steps to extend the mltoolbox with an additional model:
    1. Extend the nn_module class, implementing the forward method.
    2. Register the new class to DNNFactory using the @DNNFactory.register decoration

    Example:
        import torch.nn as nn
        from pyhelayers.mltoolbox.model.nn_module import nn_module
        from pyhelayers.mltoolbox.model.DNN_factory import DNNFactory

        @DNNFactory.register('new_model')
        class newModel(nn_module):
            def __init__(self, **kwargs):
                super().__init__()

                #define your torch.nn model
                self.cnn = ...

            def forward(self, x):
                super().forward(x)
                x = self.cnn(x)
                return x



    3. Add an import to the new class in your main (so that the new class gets registered on start)

    Example:
        import newModel

    """

    def __init__(self):
            """
            Initializes an instance of the nn_module class.
            """
            super(nn_module, self).__init__()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """The forward method of the wrapper class. It should be called by any subclass (by super().forward(x)) as
        shown in the class documentation example. This asserts the size of the input image and also clears any accumulated range_awareness_loss
        from any previous model forward calls (this happens for every batch calculation)"""
        
        self.assertSize(x)
        self.clear_range_awareness_loss()
        return x

    def clear_range_awareness_loss(self):
        """Clears the accumulated range awareness loss in all range-aware activations of the model."""
        act = poly_activations.get_range_aware_act(self.cnn)
        for a in act:
            a[1].clear_range_awareness_loss()


    #this needs to happen once before each train epoch / validation/ test / aprox
    def init_actual_data_range(self):
        """Zeroize the actual data range of all range-aware activations."""
        act = poly_activations.get_range_aware_act(self.cnn)
        for a in act:
            a[1].init_actual_data_range()

    def set_max_pooling_to_avg(self):
        """ Replaces each max-pooling by an average-pooling 
        """
        maxpool_activations = poly_activations.find_modules_by_type(self.cnn, nn.MaxPool2d)

        for i, (name, module) in enumerate(maxpool_activations):
            target_pooling = nn.AvgPool2d(module.kernel_size, module.stride, module.padding,
                                          ceil_mode=module.ceil_mode)
            poly_activations.change_module(self.cnn, name, target_pooling)


    def add_batch_norm_after_conv(self):
        """Adds batch normalization after each convolutional layer
        """
        conv_activations = poly_activations.find_modules_by_type(self.cnn, nn.Conv2d)

        for i, (name, module) in enumerate(conv_activations):
            conv_with_bn = nn.Sequential(nn.Conv2d(module.in_channels, module.out_channels,
                                                                   module.kernel_size, module.stride,
                                                                   module.padding),
                                                                   nn.BatchNorm2d(module.out_channels))
            poly_activations.change_module(self.cnn, name, conv_with_bn)


    def add_batch_norm_before_conv(self):
        """Adds batch normalization before each convolutional layer, except for the first one
        """
        conv_activations = poly_activations.find_modules_by_type(self.cnn, nn.Conv2d)

        for i, (name, module) in enumerate(conv_activations):
            if i > 0:
                conv_with_bn = nn.Sequential(nn.BatchNorm2d(module.in_channels), nn.Conv2d(module.in_channels,
                                                                                           module.out_channels,
                                                                                           module.kernel_size,
                                                                                           module.stride,
                                                                                           module.padding))
                poly_activations.change_module(self.cnn, name, conv_with_bn)


    #TODO: evaluate the number of channels for each layer of the model automatically, instead of manually passing the relevant sizes.
    class bn_info:
        """Defines a layer data element for adding batch normalization after a layer
        """
        def __init__(self, after_layer_name: str, channels: int):
            """
            Args:
                after_layer_name (str): Name of the layer, after which the batch normalization should be added
                channels (int): batch normalization channels
            """
            self.after_layer_name = after_layer_name
            self.channels = channels

    # adds bn after pooling.
    def addBatchNormAfterActivation(self, bn_info):
        """Adds batch normalization after specific layers, specified by the user

        Args:
            bn_info (list[bn_info]): list of layers after which batch normalization should be added
        """
        for info in bn_info:
            module = poly_activations.get_module_by_name(self.cnn, info.after_layer_name)
            poly_activations.change_module(self.cnn, info.after_layer_name,
                                           nn.Sequential(module, nn.BatchNorm2d(info.channels)))




    @staticmethod
    def get_pooling_by_type(type):
        """Returns a string of the asked torch class (average or max pooling)"""
        dict = {
            'avg': nn.AvgPool2d,
            'max': nn.MaxPool2d
        }
        return dict[type]

    def make_fhe_friendly(self, add_bn: bool, pooling_type: str = 'max', bn_list=None):
        """Applies changes to the given model towards making it FHE-Friendly. This is the first step. The model may still contain Relu activations after the call to this function.

        Args:
            add_bn (bool): If True batch normalization will be added
            pooling_type (str, optional): Required pooling type: 'avg' or 'max'. Average pooling is considered FHE-Friendly, Max is not. Defaults to 'max'.
            bn_list (list[bn_info], optional): If not None - the batch normalization will be added after the specified layers, if None the batch normalization will be added after each convolutional layer . Defaults to None.
        """
        if add_bn:
            if bn_list:
                self.addBatchNormAfterActivation(bn_list)
            else:
                self.add_batch_norm_after_conv()

        if not pooling_type == 'max':
            self.set_max_pooling_to_avg()

    def assertSize(self, x: tensor):
        """Asserts the required image size for the model

        Args:
            x (tensor): data tensor

        Raises:
            AssertionError: Please resize the images to the matching size
        """
        inputSize=(x.shape[1], x.shape[2],x.shape[3])
        if (inputSize != self.INPUT_SIZE):
            raise AssertionError (f'Model expects images of size {self.INPUT_SIZE}. Please resize the images to the matching size.')
        
    def remove_range_awareness(self):
        """Unset the range awareness for all CNN and PolyReLU activations"""
        activations = poly_activations.find_modules_by_type(self.cnn, poly_activations.PolyReLU)
        for name, module in activations:
            module.remove_range_awareness()

    def post_process_weighted_relu_act(self):
        """Replaces each WeightedRelu activation in the given model, by the WeightedRelu.activation:
        
        Example: 
            WeightedRelu( ratio=1.0
                (activation): TrainablePolyReLU(coefs=[0.09679805487394333, 0.13760216534137726]))

            will be replaced by the plain

            TrainablePolyReLU(coefs=[0.09679805487394333, 0.13760216534137726])
        """
        activations = poly_activations.get_weighted_relu_activations(self.cnn)
        for name, module in activations:
            poly_activations.change_module(self.cnn, name, module.activation)

    def post_process_activations(self):
        """The method post-process an FHE friendly model before converting it into an ONNX file: 
        It replaces WeightedRelu activations by the actual activation and removes range awareness"""
       
        self.post_process_weighted_relu_act()
        self.remove_range_awareness()

    def get_input_size(self):
        """Returns the input size expected by the model

        Returns:
            tuple: the input size expected by the model: (channels, height, width)
        """
        return self.INPUT_SIZE
  

