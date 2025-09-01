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

# Import basic libraries

import torch
import torch.nn as nn
from torch.nn.parameter import Parameter
import torch.nn.functional as F
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from pyhelayers.mltoolbox.utils.util import is_cuda_available
import math
from torch.utils.checkpoint import checkpoint

logger = get_logger()

# simply define a square function
def square_activation(input):
    return input ** 2



# create a class wrapper from PyTorch nn.Module, so
# the function now can be easily used in models
class Square(nn.Module):
    '''
    Applies the Square function element-wise:
        Square(x) = x ** 2
    Shape:
        - Input: (N, *) where * means, any number of additional
          dimensions
        - Output: (N, *), same shape as the input
    '''

    def __init__(self):
        '''
        Init method.
        '''
        super().__init__()  # init the base class

    def forward(self, input):
        '''
        Forward pass of the function.
        '''
        return square_activation(input)  # simply apply already implemented Square

class RangeAwareAct(nn.Module):
    """This class represents a range-aware activation function.
    It stores the required input range and defines a loss function for inputs that are found outside of this range.

    """
    def __init__(self, range_min=-10, range_max=10):
        super().__init__()
        #in non-sequential models, same activation may be used in multiple places (same block) and we need to acount for each
        self.loss=[]   #loss in the batch, for training loss computation
        self.min_range = range_min   #integer range to keep incide
        self.max_range = range_max
        self.init_actual_data_range()


    def forward(self, input):
        #calculate global min and max of the possible range
        min_ = torch.min(input)
        max_ = torch.max(input)
        self.__update_actual_data_range(min_, max_)
        self._update_loss(min_, max_)



    def clear_range_awareness_loss(self):
        '''Initializes the activation range awareness loss to zero
        '''
        if isinstance(self.loss, list):
            self.loss.clear()
        else:
            self.loss = []


    def init_actual_data_range(self): #init range
        '''Initializes the actual data range of the activation to zero
        '''
        self.actual_data_min=torch.tensor([0.0], requires_grad=True)
        self.actual_data_max=torch.tensor([0.0], requires_grad=True)
        if is_cuda_available():
            self.actual_data_min=self.actual_data_min.cuda()
            self.actual_data_max=self.actual_data_max.cuda()


    def __update_actual_data_range(self, min_, max_):
        #self.actual_data_min, self.actual_data_max are used for polynomial aproximation. We need the entire data global range
        if min_ < self.actual_data_min: self.actual_data_min = min_
        if max_ > self.actual_data_max: self.actual_data_max = max_


    def _update_loss(self, min_, max_):
        loss = self._get_loss(min_, max_)

        if loss>0:
            logger.debug(f'loss={loss}')

        if math.isnan(loss):
            logger.error(f'nan in loss: got [{min_},{max_}], allowed range is [{self.min_range}, {self.max_range}]')
            loss = 1000 #very large but finit number



        if self.loss == 0: self.loss = []
        self.loss.append(loss)


    def get_calculated_range(self):
        '''returns the actual data minimum and maximum of the activation, that was found during forward pass.

        Returns:
            float: actual data minimum
            float: actual data maximum
        '''
        return self.actual_data_min.item(), self.actual_data_max.item()


class PolyReLU(RangeAwareAct):
    '''
    Implements a polynomial approximation of the ReLU activation function.
    The coefficients used in the polynomial can be either trainable or constants.
    If the non-trainable version is used, it is recommended to enable range-awareness by setting the `range_aware` argument to True.

    When range-awareness is enabled, the output of the polynomial defined by the `coefficients_args` must stay within (or close to)
    the range defined by the `min_range` and `max_range` arguments.
    Note that the activation function does not enforce the required range, but instead records the actual minimum and maximum
    of the processed input data and calculates the “loss” of each record relative to the required range.
    The loss is based on the deviation of a record's data from the required range.

    Shape:
        - Input: a tensor of shape (N, *) where * means, any number of additional dimensions
        - Output: (N, *), a tensor of the same shape as the input

    Parameters:
        - coefficients_args (list<<list<float>><list<float>>>): possible trainable parameters. First element is scales list second element is polynomial coefficients list
        - min_range (float): minimal range border, rellevant to the coefficients_args if trainable=False
        - max_range (float): maximal range border, rellevant to the coefficients_args if trainable=False
        - trainable (bool): If True the coefficients_args are trainable parameters
        - range_aware (bool): if True, the activation function is range-aware.
    '''
    def __init__(self, coefficients_args=None, min_range=0, max_range=0, trainable=True, range_aware = False):
        super(PolyReLU, self).__init__(min_range,max_range)

        assert isinstance(coefficients_args, list)

        if isinstance(coefficients_args[0], list):
            self.coefficients_scale = coefficients_args[0]
            coefficients = coefficients_args[1]
        else:
            self.coefficients_scale = coefficients_args 
            coefficients = [1.] * len(coefficients_args)

        logger.debug(f'parameters: {coefficients_args}')

        self.coefficients = Parameter(torch.tensor(coefficients,dtype=torch.float32))  # create a tensor out of the coefficients

        self.coefficients.requires_grad = trainable

        self.range_awareness = range_aware

        
    #requires float32 or float64 precision
    def poly_horner(self,x):
        """Horner's method used for evaluation of the polynomial defined by self.coefficients at a given point x
        coefficients order is from 0
        """
        result = self.coefficients[-1]
        for i in range(2, self.coefficients.shape[0] + 1):
            result = self.coefficients[-i] + result*x
        return result

    
    def forward(self, x):
        '''
        Forward pass of the function.
        Applies the function to the input elementwise.
        '''
        #a post-processing step should set the range_awareness to False for all poly activations
        if self.range_awareness:  #this should be true for training, and false for inference
            super().forward(x)

        # for polynomial calculation stability float32 or float64 is required
        # when run under autocast, x may be float16
        t = x.dtype
        x = x.type(torch.float32)

        if self.training:
            res = checkpoint(self.poly_horner,x)
        else:
            res = self.poly_horner(x)

        # We protect from explosions during training, by returning wrong but numerical result, where nan value is expected to (later) appear.
        # During inference of the fully fhe-friendly network, this correction will not be applied, meaning the extereme values will
        # return nan, instead of wrong numerical result.
        if self.range_awareness:
            res=res.where((res < x+10),torch.zeros_like(res,device=res.device))  #val where true and 0 where false; tensor of shape x
            res = res.where((res > x-10),torch.zeros_like(res,device=res.device))

        res = res.type(t)
        return res

    def extra_repr(self):
        return 'coefs={}'.format(
            [t.item() for t in self.get_final_coefficients()])

    def get_final_coefficients(self):
        out = []
        for i in range(len(self.coefficients_scale)):
            out.append(self.coefficients_scale[i] * self.coefficients[i])
        return out

    def remove_range_awareness(self):
        self.range_awareness = False


    def _get_loss(self, min_, max_):
        return (max((max(torch.sub(max_, self.max_range), torch.add(-min_ ,self.min_range))) , 0)) #l1 for poly. we need it to stay in the range.



class ApproxReLU(nn.Module):
    '''
    Implementation of approximated relu, as suggested at: .
    Shape:
        - Input: (N, *) where * means, any number of additional
          dimensions
        - Output: (N, *), same shape as the input
    References:
        - See related paper:
        https://arxiv.org/pdf/1911.11377.pdf
    '''

    def __init__(self):
        super().__init__()

    def forward(self, x):
        '''
        Forward pass of the function.
        Applies the function to the input elementwise.
        '''
        return 0.000469841857369822 * (x**2) + 0.500000000000008 * x



class RangeAwareReLU(RangeAwareAct):
    ''' Applies the ReLU function as usual, in addition the range awareness loss of the input is calculated
    '''
    def __init__(self):
        super().__init__()


    def forward(self, input):
        super().forward(input)  #the inputs are forced in (a small) range during train, and the actuall range of the data is calculated
        return F.relu(input)


    def _get_loss(self, min_, max_):
        return (max((max(torch.sub(max_, self.max_range), torch.add(-min_ ,self.min_range))) , 0))  #l1



class WeightedRelu(nn.Module):
    '''
    Applies the Square function element-wise:

    Shape:
        - Input: (N, *) where * means, any number of additional
          dimensions
        - Output: (N, *), same shape as the input
    '''
    def __init__(self, activation, ratio=0):
        super().__init__()  # init the base class
        self.ratio = ratio
        self.activation = activation

    def extra_repr(self):
        return 'ratio={}'.format(
            self.ratio)

    def forward(self, input):
        return (self.ratio) * self.activation(input) + (1 - self.ratio) * F.relu(input)


activation_functions_dict = {'relu': lambda x: nn.ReLU(),
                             'approx_relu': lambda x: ApproxReLU(),
                             'square': lambda x: Square(),
                             'trainable_poly': lambda x: PolyReLU(x, trainable=True, range_aware=False),
                             'non_trainable_poly': lambda coeff,min=0,max=0: PolyReLU(coeff,min,max, trainable=False, range_aware = True),
                             'weighted_relu': lambda x, y: WeightedRelu(activation=x, ratio=y),
                             'relu_range_aware': lambda *args: RangeAwareReLU(),
                             }

def get_activation_gen(activation_type: str, *activation_args ):
    """Returns the activation function, that can be later used to generate the activation

    Args:
        activation_type (str): Activation name - one of the keys in the activation_functions_dict
        activation_args (Any, optional): Arguments to the activation, e.g coefficients. Defaults to None.

    Returns:
        lambda: A lambda function to generate an activation
    """
    activation_gen = lambda: activation_functions_dict[activation_type](*activation_args)
    return activation_gen


# TODO - remove deprecated
def set_activation_layer(model, orig_layer_name, activation_type, ratio, activation_args=None):
    if 0 < ratio < 1:  # TODO: check ratio handling
        activation = activation_functions_dict[activation_type](activation_args)
        weighted_activation = activation_functions_dict['weighted_relu']( activation, ratio)
        setattr(model, orig_layer_name, weighted_activation )
    # elif ratio == 1:
    #     setattr(model, orig_layer_name, activation_functions_dict[activation_type], ratio, activation_args))
    else:  # ratio == 0 / 1
        setattr(model, orig_layer_name, activation_functions_dict[activation_type](activation_args))


def replace_relu_activation(model: nn.Module, activation_type='square', replace_all_at_once = False, ratio=0, activation_args=None):
    """Recursively replaces all relu module to a predefined module.

    Args:
        model (nn.Module): the input model
        activation_type (str, optional): Activation layer name. Defaults to 'square'.
        replace_all_at_once (bool, optional): Replace all at once. Defaults to False.
        ratio (int, optional): Replacement ratio. Defaults to 0.
        activation_args:  Arguments for the activation layer. Defaults to None.

    Returns:
        bool: True if a replacement was performed
    """
    was_relu = False

    for child_name, child in reversed(list(model.named_children())):
        if isinstance(child, nn.ReLU) or isinstance(child, WeightedRelu):
            # if ratio == 1:
            #     set_activation_layer(model, child_name, activation_type, ratio, activation_args)

            set_activation_layer(model, child_name, activation_type, ratio, activation_args)
            was_relu = True
            if not replace_all_at_once:
                return was_relu
        else:
            was_relu |= replace_relu_activation(child, activation_type, ratio, activation_args)
    return was_relu



def find_modules_by_type(model:nn.Module, m_types:list) -> list:
    """
    Returns the list of modules satisfying the given types

    :param model: input model
    :param m_types: modules type to find
    :return: the list of (name, module) tuples satisfying the conditions
    """

    if not isinstance(m_types,list):
        m_types = [m_types]
    check_if_belong_to_types = lambda x: any([isinstance(x,m) for m in m_types])
    filt_modules = [(name,module) for name, module in model.named_modules() if check_if_belong_to_types(module)]
    return filt_modules


def get_module_by_name(model, name):

    """
    Returns the module having the passed in name

    :param model: input model
    :param name: name of module string or list of name parts
    :return: the detected module
    """
    module = model
    if isinstance(name, str):
        name = name.split(".")

    for name_part in name:
        module = getattr(module,name_part)
    return module


def change_module(model:nn.Module, name:str, new_module:nn.Module):

    """
    Replaces the module named <name> with the <new_module>

    :param model: input module
    :param name: full path for module to replace
    :param new_module: the new module name
    """
    if isinstance(name, str):
        name_parts = name.split(".")
    elif isinstance(name, list):
        name_parts = name
    else:
        raise Exception(f"Wrong input type {type(name)}")

    parent_module = get_module_by_name(model, name_parts[:-1])
    local_name = name_parts[-1]
    setattr(parent_module, local_name, new_module)


def _set_weighted_activation(model, name, activation, ratio):
    """
    Replaces the activation named <name> by new activation in the given ratio (the remaining part will be Relu)

    :param model: input model
    :param name: module to be replaced
    :param activation: new activation
    :param ratio: ratio of new activation
    """
    w_activaton = WeightedRelu(activation, ratio=ratio)
    assert not isinstance(get_module_by_name(model,name), WeightedRelu), \
        "the module is already of type WeightedRelu"
    change_module(model, name, w_activaton)
    return w_activaton


def get_range_aware_act(model):
    range_aware_act = find_modules_by_type(model, [RangeAwareAct])
    return range_aware_act


def get_weighted_relu_activations(model):
    act = find_modules_by_type(model, [WeightedRelu])
    return act

def get_poly_activations(model):
    act = find_modules_by_type(model, [PolyReLU])
    return act


def get_relu_range_aware_activations(model):
    act = find_modules_by_type(model, [RangeAwareReLU])
    return act

def replace_relu_range_aware_activation(model, activation_gen) -> list:
    """
    Replaces the first relu_range_aware activation in the model by the given <activation_gen>

    :param model: input model
    :param activation_gen: function to generate activation
    :param replace_all_at_once: if true all activation should be replaced, otherwise only first
    :return: the list of (name, activations) tuples of created activations
    """

    relu_activations = get_relu_range_aware_activations(model)
    new_activations = []

    logger.debug(len(relu_activations))
    if len(relu_activations) == 0:
        logger.debug("returning []")
        return []

    name = relu_activations[0][0]
    new_activation = activation_gen()
    change_module(model, name, new_activation)
    new_activations.append((name, new_activation))

    return new_activations


def get_relu_activations(model):
    relu_activations = find_modules_by_type(model, [nn.ReLU])
    return relu_activations

def replace_relu_activations(model, activation_gen, replace_all_at_once = False) -> list:
    """
    Replaces either the first, or all relu activations in the model by the given <activation_gen>

    :param model: input model
    :param activation_gen: function to generate activation
    :param replace_all_at_once: if true all activation should be replaced, otherwise only the first
    :return: the list of (name, activations) tuples of created activations
    """

    relu_activations = get_relu_activations(model)
    new_activations = []
    if len(relu_activations) == 0:
        return []
    if replace_all_at_once:
        for name, _ in relu_activations:
            new_activation = activation_gen()
            change_module(model, name, new_activation)
            new_activations.append((name,new_activation))
    else:
        index = -1
        name = relu_activations[index][0]
        new_activation = activation_gen()
        change_module(model, name, new_activation)
        new_activations.append((name, new_activation))
    return new_activations


def create_or_update_weighted_activations(model, activation_gen,
                                          change_index, change_ratio,
                                          replace_all_at_once)->(list, bool):

    """
    Either changes Relu activations to WeightedRelu activations, or updates the ratio of WeightedRelu activations

    :param model: input model
    :param activation_gen: function to generate activation
    :param change_index: index of activation to be replaced or updated
    :param change_ratio: the ratio of new activation
    :param replace_all_at_once: if true all activation should be replaced, otherwise only first
    :return: list of (name, module) tuples of created activations and
            boolean indicating if the change_required index exceed the available list of  activations
    """
    activations_init = find_modules_by_type(model, [nn.ReLU, WeightedRelu])

    activations = []
    # to skip activations when ReLu is part of WeightedRelu
    for name, activation in activations_init:
        potential_parent_name = name.split(".")[:-1]
        potential_parent_module = get_module_by_name(model,potential_parent_name)
        if not isinstance(potential_parent_module,WeightedRelu):
            activations.append((name, activation))

    new_activations =[]
    is_missing = False

    if replace_all_at_once:
        # for replace_all_at_once by finishing the first cycle all activation should replaced with weight =1
        if change_index > 0:
            change_ratio = 1
            is_missing = True

        for name, activation in activations:
            if isinstance(activation, WeightedRelu):
                activation.ratio = change_ratio
            else:
                w_activaton = _set_weighted_activation(model,name,activation_gen(),ratio=change_ratio)
                new_activations.append((name, w_activaton))
    else:
        activations = activations[-1::-1]

        if change_index >= len(activations):
            is_missing = True
            # to make sure all previous activations are changed
            change_index = len(activations)
        else:
            target_name, target_activation = activations[change_index]
            if isinstance(target_activation, nn.ReLU):
                w_activaton = _set_weighted_activation(model, target_name, activation_gen(), ratio=change_ratio)
                new_activations.append((target_name, w_activaton))
            else:
                assert isinstance(target_activation, WeightedRelu)
                target_activation.ratio = change_ratio

        # validate/update all previous activations
        for _i in range(change_index):
            name, activation = activations[_i]
            if not isinstance(activations[_i][1], WeightedRelu):
                logger.debug(f"warning: previous activation[{_i}] {name} is not WeightedRelu ({activation}) - replacing with")
                w_activaton = _set_weighted_activation(model, name, activation_gen(), ratio=1.0)
                new_activations.append((name, w_activaton))
            elif activation.ratio < 1.0:
                logger.debug(f"warning: previous activation[{_i}] {name} ratio ({activation.ratio}) - replacing with ratio = 1.0")
                activation.ratio = 1.0

    return new_activations,is_missing
