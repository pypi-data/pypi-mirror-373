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
import json

class Arguments:
     """This class defines the user arguments object, and sets the default values for some parameters"""
     
     def __init__(self, model, dataset_name, classes, num_epochs, data_dir):
         """
         Initializes the Arguments class, defining user-configurable parameters 
         with their default values.

         Args:
            model (str): The name or path of the model to be used.
            dataset_name (str): The name of the dataset for training and evaluation.
            classes (int): The number of classes in the dataset.
            num_epochs (int): The total number of training epochs.
            data_dir (str): The directory path where the dataset is stored.
         """
         self.model = model
         self.dataset_name = dataset_name
         self.classes = classes
         self.num_epochs = num_epochs
         self.data_dir = data_dir  #Path to dataset
         
         #defaults:
         self.seed=123            #Select seed number for reproducibility
         self.lr=0.001            #Learning rate
         self.batch_size = 200    #Training batch size
         self.opt='adam'          #Optimizer to be used in training, choices=('sgd', 'adam')
         self.save_dir='outputs/mltoolbox/'         #Path to checkpoint save directory
         self.save_freq=-1                 #How frequently save checkpoint (-1: overwrite last checkpoint each period; 0:  do not save; positive integer: write checkpoint for a given freq only)
         self.pooling_type="avg"           #Max or average pooling, choices=('max', 'avg')
         self.activation_type="relu_range_aware"   #Activation type', choices=('non_trainable_poly', 'trainable_poly', 'approx_relu', 'relu', 'square', 'relu_range_aware', 'weighted_relu'))
         self.debug_mode=False             #Breaks a training epoch after loading only a few batches.
         self.replace_all_at_once=True     #Changes the activation layers at once or layer by layer
         self.epoch_to_start_change=-1     #Epoch number to start changing the activation function (set to -1 when it is not utilized, the change is performed on the first epoch)
         self.change_round=-1              #Number of epochs per change (set to -1 when it is not utilized)
         self.smooth_transition=False      #Change each activation layer in a smooth change or at once
         self.gradient_clip=-1.0           #The threshold value for gradient clipping during training
         self.log_string='test'            #Name for ClearML 
         self.from_checkpoint=''           #Location of .pth checkpoint file to load. If empty the model will be created from scratch
         self.coeffs_scale=[[0.1, 0.1, 0],[1.,1., 1]]  #Coefficients scale for trainable poly activation optionally including initial value of coefs
         self.distillation_path=""               #Path for a distillation model file
         self.distillationT=10.0        #Temperature parameter for the distillation process. Controls the softness of the teacher's output probabilities. Higher values make the distribution softer.
         self.distillation_alpha=0.1    #Weighting factor for the distillation loss relative to the standard training loss. Higher values give more importance to the distillation loss.
         self.continue_with_nans=False  #Flag to allow training to continue even if NaN values are encountered.
         self.local_rank=0              #Required for DDP setup, this value should not be changed by the user.
         self.ddp=False                 #Whether to use Distributed Data Parallel (DDP) for multi-GPU training.
         self.ffcv=False          #Whether to use FFCV for accelerated data loading. Using ffcv improves running speed, but reqires converting the data into supported format and pointing to it in ffcv_train_data_path argument
         self.distillation_model=None    #This argument should not be changed by the user
         self.lr_new=0.0002              #Learning rate for new (replaced) activations
         self.validation_freq=1          #Defines how often (in epochs) the validation set is evaluated during training. A value of 1 means validation after every epoch.
         self.disable_scheduler=False    #Flag to disable the learning rate scheduler. If True, the scheduler is not used during training.
         self.min_lr = 1e-5         #Minimal learning rate for scheduler
         self.ffcv_train_data_path = ""    #Location of ffcv data. Required if ffcvis set to True
         self.range_aware_train = False    #A flag that makes the training be range aware. Can be turned off (The default value is False). When False, range loss is not calculated.
         self.range_awareness_loss_weight = 0     #Weight of range awareness loss term in the loss function
         self.poly_degree = 18                    #The ReLU approximation polynomial degree

     def dump_to_file(self, path):
        """Dump all the arguments of Arguments class into a file. This method is called when the model checkpoint is saved, and placed next to the checkpoint."""
        with open(os.path.join(path, 'training_arguments.json'), 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=lambda x: str(type(x)))
