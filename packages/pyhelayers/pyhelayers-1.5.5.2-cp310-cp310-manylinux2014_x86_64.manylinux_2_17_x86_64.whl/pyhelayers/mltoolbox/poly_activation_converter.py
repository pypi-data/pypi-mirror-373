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
import numpy as np
import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau
import pyhelayers.mltoolbox.he_dl_lib.poly_activations as poly_activations
from pyhelayers.mltoolbox.utils.util import get_optimizer
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from pyhelayers.mltoolbox.utils.util import load_checkpoint
from types import SimpleNamespace
from pyhelayers.mltoolbox.trainer import Trainer
from pyhelayers.mltoolbox.utils.util import is_cuda_available
from numpy.polynomial.polynomial import polyfit

def starting_point(args):
    """Initializes and returns the Trainer and PolyActivationConverter based on user arguments

    Args:
        args (Arguments): the user arguments

    Returns:
        Trainer: the Trainer
        PolyActivationConverter: the PolyActivationConverter
    """
    # set seed for  reproducibility
    set_seed(args)
    logger = get_logger()



    if args.from_checkpoint:
        model, optimizer, train_state, loss, metrics, was_completed = load_checkpoint(args)
            
        trainer =  Trainer(args, model,optimizer)
        act_converter = PolyActivationConverter(args, trainer.get_model(), train_state, was_completed, loss)
        if train_state:
            epoch = train_state.epoch
        else:
            epoch = 0
            
        #reset the optimizer lr to the lr argument
        for param_group in trainer.get_optimizer().param_groups:
            param_group['lr'] = args.lr
            
    else:
        trainer =  Trainer(args)
        act_converter = PolyActivationConverter(args,trainer.get_model())
        epoch = 0

    logger.info(f'current phase completeness status: {act_converter.get_was_completed()}')
    return trainer, act_converter, epoch




def _calc_relu_ratio(start_epoch: int, epoch: int, change_round: int):
    """Calculates the required ratio of the new activation in the smooth replacement strategy, based on current epoch

    Args:
        start_epoch (int): number of epoch when the replacement started
        epoch (int): current epoch number
        change_round (int): number of epochs for full replacement

    Returns:
        int: change index (relevant only for args.replace_all_at_once=False, when on each change_round a single activation is replaced, for args.replace_all_at_once=True the only possible change_index is 0 )
        float: ratio
        
    """
    change_progress = float(epoch - start_epoch) / change_round
    change_index = int(change_progress)
    change_ratio = change_progress - change_index

    return change_index, change_ratio



def _init_distillation_model(args):
    """Loads the distillation model, if it was specified in user arguments

    Args:
        args (Arguments): user arguments
    """
    if args.distillation_path:
        logger = get_logger()
        logger.info(f"Loading distillation model from {args.distillation_path}")
        
        chk_point = {}
        if args.ddp:
            #Input type (torch.cuda.FloatTensor) and weight type (torch.FloatTensor) should be the same
            #why don't need the cuda if not ddp?..
            #the input is on GPU, so we need the model to also be sent to GPU
            chk_point = torch.load(os.path.join(args.distillation_path), map_location=f'cuda:{args.local_rank}')
            chk_point['model'].cuda(args.local_rank)
        elif is_cuda_available():
            chk_point = torch.load(os.path.join(args.distillation_path), map_location=f'cuda:{args.local_rank}')
        else:
            chk_point = torch.load(os.path.join(args.distillation_path), map_location=torch.device('cpu'))

        args.distillation_model = chk_point['model']
    else:
        args.distillation_model = None



def set_seed(args):
    """Impose reproducibility

    Args:
        args (Arguments): user arguments
    """
    seed = args.seed
    torch.manual_seed(seed)

    torch.backends.cudnn.deterministic = True #default is False
    torch.backends.cudnn.benchmark = False   #default is False
    np.random.seed(seed)

    if is_cuda_available():
        torch.cuda.manual_seed_all(seed)

def relu(x):
    return np.maximum(0, x)

##TODO: do we need the scale??
def aprox_poly(minv,maxv,degree):
    """Aproximates ReLU by a polynomial of given degree in the range given by [minv,maxv]
    Args:
            minv (float): range minimum value
            maxv (float): range maximum value
            degree (int): polynomial required degree

    Returns:
            list<list<float>>: first item is list of scales, second item is list of coefficients, the same structure as the coeffs_scale user argument
                               The scales are always returned as a list of ones, and are here only to fit the coeffs_scale structure.

    """
    logger = get_logger()
    logger.info(f'aprox_poly {minv}, {maxv}, {degree}')
    x = np.linspace(minv,maxv,2000)
    np.append(x,0)
    y=relu(x)
    p = polyfit(x,y,degree)  #Since version 1.4
    logger.info(p)

    scale = list(np.ones(degree+1))
    coeffs_scale = [scale, p]
    logger.debug(coeffs_scale)

    return coeffs_scale


class PolyActivationConverter:
    """This class helps in the FHE conversion of the model; namely the activation replacement. 
    It holds the current model conversion state. The initialization can be either from scratch, or from some given point - this can be
    usefull when loading a mnodel from a checkpoint.

    Our assumption is that a model's activation functions can only be either relu or relu_range_aware, but not both at the same time.
    Furthermore, we assume that the non-trainable PolyRelu activation function is only utilized as a substitute for relu_range_aware activations.

    Supported replacement flows:
     1)   relu -> relu_range_aware -> non_trainable_poly
     2)   relu -> weighted_relu (for smooth_transition, usually for the trainable_poly activation)
    """
    def __init__(self, args, model, train_state=None, chp_was_completed=None,  loss=None):
        """
        Initializes the PolyActivationConverter, managing the activation function 
        replacement process for Fully Homomorphic Encryption (FHE) conversion.

        Args:
            args (Arguments): A set of user-defined arguments for the conversion process.
            model (torch.nn.Module): The model to be converted.
            train_state (SimpleNamespace, optional): A dictionary holding the training state, if resuming from a checkpoint. Defaults to None.
            chp_was_completed (bool, optional): Indicates whether the checkpoint conversion was fully completed. True if there are no Relu activations in the model.
            loss (float, optional): Loss value at train_state.epoch
        """
        self.__init_from_scratch(args)
        self.was_completed = self.__find_is_complete(model)
        self.cuda = is_cuda_available(True)
        self.logger.debug(f'current phase completenes status: {self.was_completed}')

        if train_state is not None:
            #TODO: add continue_training arg instead of this if?
            #we may want to redefine those values in new phase, but keep if we continue training(for smooth and one-by-one it is crutial)
            if (not chp_was_completed) and (not self.was_completed): #continue from where stopped using train_state
                self.best_loss = loss
                self.best_epoch = train_state.epoch
                self.start_epoch = train_state.start_epoch
                self.wait_before_change = train_state.wait_before_change
            
            self.logger.debug("init from checkpoint")
        
        self.__validate(model, args.activation_type, args.epoch_to_start_change, args.num_epochs)

    def __validate(self, model, activation_type, epoch_to_start_change, num_epochs):
        num_relu = len(poly_activations.get_relu_activations(model))
        num_relu_range_aware = len(poly_activations.get_relu_range_aware_activations(model))
        num_weighted_relu = len(poly_activations.get_weighted_relu_activations(model))

        if (num_relu > 0) and (num_relu_range_aware > 0):
            self.logger.warning("Warning: The model contains both relu and relu_range_aware activation types, which is ambiguous. Please ensure that only one of these activation types is used in the model.")
            raise Exception("Unsupported flow")

        elif (num_weighted_relu > 0) and (num_relu_range_aware > 0):
            self.logger.warning("Warning: The model contains both weighted_relu and relu_range_aware activation types, which is ambiguous. Please ensure that only one of these activation types is used in the model.")
            raise Exception("Unsupported flow")

        elif (num_relu_range_aware > 0):
            self.logger.info("relu_range_aware activations found in the model, and will be replaced in the current run.")

            if ((activation_type != "non_trainable_poly") and (activation_type != "relu_range_aware") and (epoch_to_start_change < num_epochs)):
                self.logger.warning(f"Warning: relu_range_aware activation type cannot be replaced by activation of type {activation_type}. Only non_trainable_poly activation type can be used to replace relu_range_aware activation. Please modify the activation_type user argument to `non_trainable_poly`, or use a model that has relu activations, and does not include relu_range_aware activations.")
                raise Exception("Unsupported flow")

    def __init_from_scratch(self, args):
        self.logger = get_logger()
        if is_cuda_available():
            self.logger.info("Visible gpu devices: " + os.environ["CUDA_VISIBLE_DEVICES"])

        # coefficients scale for trainable poly activation
        assert isinstance(args.coeffs_scale, list)
        self.logger.debug(f"loaded coeffs_scale is {args.coeffs_scale}")

        _init_distillation_model(args)

        self.start_epoch = 0
        self.wait_before_change = args.epoch_to_start_change
        self.best_loss = None
        self.best_epoch = None
        self.args = args
        self.poly_degree = args.poly_degree


    def get_start_epoch(self):
        """A getter for the start_epoch class argument"""
        return self.start_epoch
    
    def get_wait_before_change(self):
        """A getter for the wait_before_change class argument"""
        return self.wait_before_change
    
    def get_was_completed(self):
        """A getter for the was_completed class argument"""
        return self.was_completed
       
    def set_best_found_loss_and_epoch(self, loss, epoch):
        """A setter for the best_loss and best_epoch class arguments"""
        self.best_loss = loss
        self.best_epoch = epoch
        
        
    def get_best_found_loss(self):
        """A getter for the best_loss class argument"""
        return self.best_loss
    
    
    def create_train_state(self, epoch: int):
        """Returns a namespace that groups start_epoch, current epoch and wait_before_change together

        Args:
            epoch (int): the current epoch

        Returns:
            SimpleNamespace: a namespace that groupps the passed in arguments together
        """
        return SimpleNamespace(start_epoch=self.start_epoch, epoch=epoch, wait_before_change=self.wait_before_change)


    def is_fhe_friendly(self,model):
        """
        Args:
            model (nn.Model): model
        Returns:
            bool: True if the model has no ReLU activations
        """
        num_relu = len(poly_activations.get_relu_activations(model))
        num_relu_range_aware = len(poly_activations.get_relu_range_aware_activations(model))
        num_weighted_relu = len(poly_activations.get_weighted_relu_activations(model))
        if num_relu==0 and num_relu_range_aware==0 and num_weighted_relu==0:
            return True

        ##also check avg_pooling?

        return False


    def __find_is_complete(self, model):
        """
        Calculates the current completion state of the model.
        If the model has any relu/relu_range_aware/weighted_relu activations - then a convertion may be still required.

        Note the assumptions:
        1. We assume all relu activations are replaced at first step.
        2. If relu was replaced by relu_range_aware, than all the relu_range aware must be replaced by non_trainable_poly at the second step.

        as a result, if any relu present in the model, and the activation_type != 'relu' - False is returned
        if any relu_range_aware is present in the model, and the activation_type != 'relu_range_aware' - False is returned
        if weighted_relu is present in the model (smooth transition was not finished for some activation/s) - False is returned
        any other situation will return True.

        Args:
            model (nn.Model): model to be converted
        Returns:
            bool: True if there nothing to be done in the current phase (based on the model and the user arguments)

        Supported flows:
        relu -> relu_range_aware -> non_trainable_poly
        relu -> weighted_relu (smooth_transition, usually to trainable_poly activation)
        """
        num_relu = len(poly_activations.get_relu_activations(model))
        if num_relu > 0:
            if self.args.activation_type == 'relu':  return True
            else: return False

        #num_relu=0
        num_relu_range_aware = len(poly_activations.get_relu_range_aware_activations(model))
        if num_relu_range_aware > 0:
            if self.args.activation_type == 'relu_range_aware': return True
            else: return False

        #num_relu = num_relu_range_aware = 0
        num_weighted_relu = len(poly_activations.get_weighted_relu_activations(model))
        if num_weighted_relu > 0:
            return False

        return True



    #aproximates either first relu_range_aware or global (by replace_all_at_once) to poly
    def __aprox_relu_by_poly(self, model, trainer, degree):
        delta = 3
        relu_act = poly_activations.get_relu_range_aware_activations(model)
        if len(relu_act) > 0:
            trainer.approximate_input_range_from_data(self.args) #each relu_range_aware will have min and max calculated at instance
        else:
            self.logger.info("nothing to aproximate")
            return [(None, 0, 0)]


        if self.args.replace_all_at_once: #all layers, each individually
            res=[]
            for act in relu_act:
                minv, maxv = act[1].get_calculated_range()
                self.logger.info(f'replacing relu in range {minv}:{maxv} by:')
                coeffs_scale = aprox_poly(float(minv)-delta,float(maxv)+delta,degree) #polyfit (on extended range)
                res.append((coeffs_scale, minv, maxv))
            return res

        else: #one by one
            #replace first activation, using its range
            minv, maxv = relu_act[0][1].get_calculated_range()

        self.logger.info(f'replacing relu in range {minv}:{maxv} by:')

        coeffs_scale = aprox_poly(float(minv)-delta,float(maxv)+delta,degree) #polifit (on extended range)

        return [(coeffs_scale, minv, maxv)]


        
    def __get_activation_gen_params(self, model, trainer):
        """Returns the parameter list, depending on the target activation:
         - for non_trainable_poly it approximates a polynomial per activation
         - for other activation types it uses the user argument coeff_scale, returning a sinle tuple item in a list

         Returns:
            list<tuple>: A list of tuples of the form: (coeffs_scale, minv, maxv), where minv is the minimum range and maxv is the maximum range
        """
        poly_aprox_activation_types = ["non_trainable_poly"]

        if self.args.activation_type in poly_aprox_activation_types:
            poly_list = self.__aprox_relu_by_poly(model,trainer,self.poly_degree)
            return poly_list
        else:
            return [self.args.coeffs_scale]

            
            
    def replace_activations(self, trainer, epoch, scheduler):
        """Handles the entire replacement logic - depending on the arguments values and current epoch

        Args:
            trainer (Trainer): trainer instance
            epoch (int): current epoch number
            scheduler (ReduceLROnPlateau): Learning rate reduction schedualer
        """
        self.logger.debug("replace_activations")
        # condition to start activation modification
        model = trainer.get_model()
        is_time_to_change = (epoch > self.start_epoch + self.wait_before_change) and (not self.__find_is_complete(model))
        self.logger.debug(f"is_time_to_change {is_time_to_change}")
        self.logger.debug(f"epoch {epoch}")
        self.logger.debug(f"start_epoch {self.start_epoch}")
        self.logger.debug(f"wait_before_change {self.wait_before_change}")
        self.logger.debug(f"was_completed {self.was_completed}")


        if is_time_to_change:
            optimizer = trainer.get_optimizer()
            # two main cases - smooth and not smooth
            # 1 - smooth
            if self.args.smooth_transition: #no per_activation_approximation support: only all_at_once=True/False
                self.logger.debug("going to change")
                self.__replace_activations_smooth(model, epoch, optimizer, scheduler)
            # 2 - not smooth
            else: #all_at_once/one by one/per_activation_approximation
                scheduler = self.__replace_activations(model, trainer, scheduler)
                self.start_epoch = epoch
            
            self.best_loss = None
            self.was_completed = self.__find_is_complete(model)

        


    def __replace_activations(self, model, trainer, scheduler):
        """Replaces relu activations in a non-smooth manner, either all at once or one by one. Updates the was_completed and wait_before_change states
            Starts a new scheduler.

            If any relu_range_aware activations are present in the passed in model - one or all ot them are replaced at single call,
            depnding on the replace_all_at_once user argument.
            If no relu_range_aware activations are present - we attempt to replace one or all relu activations at single cal (depnding on the replace_all_at_once user argument).
            If no relu_range_aware and no relu activations are present in the model, exception is raised.
        Args:
            model(nn.Module) : Input model
            activation_gen (lambda): A lambda fumction to generate the required activation

        Raises:
            Exception: There are no ReLU activations to replace - check configuration and the model

        Returns:
            ReduceLROnPlateau: Handles reduction of learning rate when a metric has stopped improving
        """
        params = self.__get_activation_gen_params(model, trainer) #one or all, depending on replace_all_at_once flag
        num_relu_range_aware = len(poly_activations.get_relu_range_aware_activations(model))
        if (num_relu_range_aware>0): #replace relu_range_aware
            for poly in params:
                activation_gen = poly_activations.get_activation_gen(self.args.activation_type, *poly)
                self.logger.debug(activation_gen)
                self.logger.debug (poly)
                new_activations = poly_activations.replace_relu_range_aware_activation(model, activation_gen)

        else:  ###replace relu
            activation_gen = poly_activations.get_activation_gen(self.args.activation_type, *params[0])
            new_activations = poly_activations.replace_relu_activations(model, activation_gen, self.args.replace_all_at_once)

        if len(new_activations) == 0: #if no replacement was performed 
            raise Exception("There are no ReLU activations to replace - check configuration and the model")

        if self.cuda:
            model = model.cuda()
        self.logger.info(model)
        self.logger.info(f"restart optimizer and scheduler for activation {new_activations}")
        optimizer = get_optimizer(self.args, model)
        scheduler = ReduceLROnPlateau(optimizer, factor=0.5, patience=2, min_lr=self.args.min_lr, verbose=True)
        self.wait_before_change = self.args.change_round


        return scheduler


    def __replace_activations_smooth(self, model, epoch, optimizer, scheduler):
        """Replaces relu activations in a smooth manner, updates the was_completed state . Updates the scheduler.

        Args:
            model (nn.Module): the input model
            activation_gen (lambda): A lambda function to generate the required activation
            epoch (int): current epoch
            optimizer (torch.optim): optimizer
            scheduler (ReduceLROnPlateau): scheduler

        Note: only ReLU activations are replaced
        Note: non_trainable_poly activation type is not supported in the smooth replacement
        """
        params = [self.args.coeffs_scale]
        activation_gen = poly_activations.get_activation_gen(self.args.activation_type, *params)
        change_index, change_ratio = _calc_relu_ratio(self.start_epoch + self.wait_before_change, epoch, self.args.change_round)
        new_activations, is_missing = poly_activations.create_or_update_weighted_activations(model, activation_gen,
                                                                                            change_index, change_ratio,
                                                                                            self.args.replace_all_at_once)

        if len(new_activations) == 0: #if no replacement was performed 
            self.logger.info(f"Transition phase: {change_index}:{change_ratio}" )
        else:
            if self.cuda:
                model = model.cuda()
            for name, activation in new_activations:
                # add new parameters to optimizer and scheduler
                optimizer.add_param_group({'params': activation.parameters(), 'lr': self.args.lr_new, 'momentum' : 0.9, 'weight_decay': 5e-4, 'maximize': False, 'foreach': None})
                scheduler.min_lrs.append(self.args.min_lr)
            self.logger.info(model)
            self.logger.debug(optimizer)
            self.logger.info(f"Started changing {change_index} with ratio {change_ratio}")


