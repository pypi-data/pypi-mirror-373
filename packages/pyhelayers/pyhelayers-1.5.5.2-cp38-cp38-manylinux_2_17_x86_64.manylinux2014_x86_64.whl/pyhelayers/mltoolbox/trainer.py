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
from torch.utils.data import DataLoader
from tqdm.autonotebook import tqdm 
from pyhelayers.mltoolbox.he_dl_lib.distillation import nd_loss
from pyhelayers.mltoolbox.he_dl_lib.range_awareness import range_awareness_loss
from pyhelayers.mltoolbox.utils.util import accuracy, top_k_acc
from pyhelayers.mltoolbox.utils.util import get_summary, get_optimizer
from pyhelayers.mltoolbox.utils.metrics_tracker import MetricsTracker
import numpy as np

from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
#from pyhelayers.mltoolbox.he_dl_lib.timers import Timer
from pyhelayers.mltoolbox.data_loader.ds_factory import DSFactory
from pyhelayers.mltoolbox.model.DNN_factory import DNNFactory
from pyhelayers.mltoolbox.utils import util


##The following imports cause the standard datasets to get registered into factory
from pyhelayers.mltoolbox.data_loader.cifar10_dataset import Cifar10Dataset_32, Cifar10Dataset_224
from pyhelayers.mltoolbox.data_loader.cifar100_dataset import Cifar100Dataset_32, Cifar100Dataset_224
from pyhelayers.mltoolbox.data_loader.covidCT_dataset import CovidCTDataset
from pyhelayers.mltoolbox.data_loader.covidXray_dataset import CovidXrayDataset
from pyhelayers.mltoolbox.data_loader.places205_dataset import places205Dataset
from pyhelayers.mltoolbox.data_loader.places365_dataset import places365Dataset
from pyhelayers.mltoolbox.data_loader.imagenet_dataset import imagenetDataset

##the following imports cause the standard models to get registered into factory
from pyhelayers.mltoolbox.model.alexnet_fhe import alexnet_fhe
from pyhelayers.mltoolbox.model.lenet5 import Lenet5
from pyhelayers.mltoolbox.model.resnet50 import resnet50_fhe
from pyhelayers.mltoolbox.model.resnet50 import resnet18_fhe
from pyhelayers.mltoolbox.model.squeezenet import SqueezeNet1_0_FHE
from pyhelayers.mltoolbox.model.squeezenet import SqueezeNet1_1_FHE
from pyhelayers.mltoolbox.model.squeezenetchet import SqueezeNetCHET
from pyhelayers.mltoolbox.model.resnet_clip import ClipResnet50_FHE

from torch.utils.data.distributed import DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.tensorboard import SummaryWriter
import os
import sys
import pyhelayers.mltoolbox.he_dl_lib.poly_activations as poly_activations
from pyhelayers.mltoolbox.utils.util import is_cuda_available



def _create_summary_writer(args):
    """ creates SummaryWriter to report metrics to clearml, for nicer visualization
    Args:
            args (Arguments): user arguments

    Returns: either SummaryWriter or None
    """
    summary_writer_path = os.path.join(args.save_dir, 'runs')

    if not os.path.exists(summary_writer_path):
        os.makedirs(summary_writer_path)

    writer = None
    if hasattr(args, 'log_title'):
        writer = SummaryWriter(os.path.join(summary_writer_path, args.log_title))

    return writer


class Trainer:
    """This class represents a training object, that has all the needed components for a training, like dataLoaders, optimizer, model etc.
    
    """
    def __get_normed_weights(self, args, datasetSplit):
        """For an imbalanced dataset, returns a list of weights, to be used to normalize the data distribution. 
        For an imbalanced dataset, the samples_per_cls attribute should contain a list of integers, representing the number of samples 
        in each of the classes. 

        Args:
            args (Arguments): user arguments
            datasetSplit (dataLoader.dataset): The data to be normalized

        Returns:
            list<float>: A list of weights
        """
        if self.ds.is_imbalanced():
            samples_per_class = np.array(self.ds.get_samples_per_class(datasetSplit))

            normed_weights = 1.0 / samples_per_class
            normed_weights = normed_weights / normed_weights.sum()

            return torch.FloatTensor(normed_weights).cuda(args.local_rank if self.cuda else  None)
        return None

    
    def get_model(self):
        """Returns the model to be trained

        Returns:
            nn.model: the model to be trained
        """
        return self.model
        
    def get_optimizer(self):
        """Returns the optimizer of the training

        Returns:
            optimizer: the optimizer of the training
        """
        return self.optimizer

           
    def __init__(self, args, model=None, optimizer=None):
        """Initializes the model, optimizer and data generators, based on user defined arguments.
        In case model and optimizer are passed - they are used, In case any of those arguments is None, the values are initialized from scratch, based on user arguments

        Args:
            args (Arguments): user defined arguments
            model (nn.Model, optional): Either a partually trained model (loaded from check point) or None. In case no model is passed, the model is loaded based on user arguments, by name
            optimizer (Optimizer, optional): The optimizer to use during training (loaded from check point) or None. In case no model is passed, the optimizer is loaded based on user arguments
        """
        self.logger = get_logger()
        self.writer = _create_summary_writer(args)
        self.cuda = is_cuda_available()

        if self.cuda:
            self.device = "cuda"
        else: self.device = "cpu"

        if model is not None:
            self.logger.debug("model from chp")
            self.model = model
        else:
            self.model = DNNFactory.get_model_by_name(args)

        if optimizer is not None:
            self.optimizer = optimizer
        else:
            self.optimizer = get_optimizer(args, self.model)
            
        self.__init_data(args)
        

    def __init_data_ffcv(self,args):
        """
        Creates ffcv training_generator
        """
        from ffcv.loader import Loader, OrderOption
        import numba
        
        #setting num workers as cpu cores number (the maximum possible)
        num_cpu_cores = numba.config.NUMBA_DEFAULT_NUM_THREADS

        if args.ddp:
            torch.cuda.set_device(args.local_rank)
            self.model = self.model.to(memory_format=torch.channels_last)
            self.model = DDP(self.model.cuda(args.local_rank))

            #setting os_cache to False for single gpu ; True for multi-gpu
            os_cache = torch.cuda.device_count() > 1
            self.training_generator = Loader(args.ffcv_train_data_path, batch_size=args.batch_size, num_workers=num_cpu_cores, distributed = True,
                        order=OrderOption.RANDOM, drop_last=True, pipelines = self.ds.get_train_pipe_ffcv(args), os_cache=os_cache)

        else:
            self.model = nn.DataParallel(self.model)
            if self.cuda:
                self.model = self.model.cuda()

            self.training_generator = Loader(args.ffcv_train_data_path, batch_size=args.batch_size, num_workers=num_cpu_cores, distributed = False, seed =args.seed,
                        order=OrderOption.RANDOM, drop_last=True, pipelines = self.ds.get_train_pipe_ffcv(args), os_cache=True)




    #https://github.com/pytorch/pytorch/issues/73603
    #Multiworker dataloader with persistent workers is non-deterministic after first epoch
    def __init_data(self, args):
        self.ds = DSFactory.get_ds(args.dataset_name, classes=args.classes, path=args.data_dir, args=args)
        self.logger.debug(self.ds)

        val_data = self.ds.get_val_data()
        test_data = self.ds.get_test_data()
        approx_data = self.ds.get_approximation_set()

        test_params = {'batch_size': args.batch_size,
                    'shuffle': False,
                    'num_workers': 4,
                    'pin_memory': True,
                    'drop_last': True,
                    'persistent_workers': True
                    }

        self.val_generator = DataLoader(val_data, **test_params)
        self.test_generator = DataLoader(test_data, **test_params)
        self.approx_generator = DataLoader(approx_data, **test_params)

        #create spetial ffcv loader for train data only
        #the test and validation are fast as they are, so no ffcv special data pre-processing is used
        if (args.ffcv):
            self.__init_data_ffcv(args)
            return

        train_data = self.ds.get_train_data()

        ##Setting persistent_workers to True will improve performances when you call into the dataloader multiple times in a row (as creating the workers is expensive).
        #But it also means that the dataloader will have some persistent state even when it is not used (which can use some RAM depending on your dataset).
        #If the persistent state is not an issue for you, you should definitly enable it.
        train_params = {'batch_size': args.batch_size,
                        'shuffle': False,#True,
                        'num_workers': 4,
                        'pin_memory': True,
                        'drop_last': True,
                        'persistent_workers': True
                        }

        if args.ddp:
            torch.cuda.set_device(args.local_rank)
            self.model = DDP(self.model.cuda(args.local_rank)) 
            train_sampler = DistributedSampler(train_data,shuffle=True)
            train_params['sampler'] = train_sampler
            #if the test is ddp, use dist.all_gather and dist.all_gather_object to gather results from all instances
            #test_sampler = DistributedSampler(test_data,shuffle=False)
            #test_params['sampler'] = test_sampler
        elif self.cuda:
            self.model = nn.DataParallel(self.model).cuda()
            train_params['shuffle'] = True
        

        self.training_generator = DataLoader(train_data, **train_params)


    #used for calculating the range loss term
    def get_range_aware_act(self, args):
        """Returns a list of activations in the current trained model that are range awared. """
        if args.range_aware_train:
            return poly_activations.get_range_aware_act(self.model)

        else: return []


    def get_all_ranges(self, args):
        """Lists all activations ranges (min and max) in a single list

        Args:
            args (Arguments): user arguments

        Returns:
            list<float>: ranges (two numbers for each activation, that represent minimum and maximum of the activation range)
        """
        all_ranges_lst = []
        act = self.get_range_aware_act(args)
        for n, module in act:
            all_ranges_lst = all_ranges_lst + [module.get_calculated_range()]
        return all_ranges_lst


    def __init_actual_data_range(self):
        """Sets the actual_data_range of each range aware activation to zero
        """
        if isinstance(self.model, nn.DataParallel) or isinstance(self.model, nn.parallel.DistributedDataParallel):
            self.model.module.init_actual_data_range()
        else:
            self.model.init_actual_data_range()


    def train_step(self, args, epoch: int, t: tqdm):
        """Performs a single train step (a single forward and backward pass)

        Args:
            args (Arguments): user arguments
            epoch (int): the current epoch number (for epoch summary printing)
            t (tqdm): training progress (the progress is updated after each epoch)
        Raises:
            Exception: Exit because of NaNs, if Nan values are present in the output, and args.continue_with_nans=False

        Returns:
            MetricsTracker: metrics
            np.array: confusion matrix
        """
        self.model.train()

        self.__init_actual_data_range()
  
        scaler = torch.cuda.amp.GradScaler(enabled=is_cuda_available())

        confusion_matrix = torch.zeros((args.classes, args.classes), dtype=int)
        normed_weights = self.__get_normed_weights(args, self.ds.get_train_data())

        criterion = nn.CrossEntropyLoss(reduction='mean', weight=normed_weights)

        metric_ftns = ['loss', 'accuracy', 'top_5_acc']
        train_metrics = MetricsTracker(*[m for m in metric_ftns], mode='train', writer = self.writer)
        train_metrics.reset()

        sum_correct = 0.0
        sum_total = 0.0
        sum_loss = 0.0
        sum_acc = 0.0
        sum_top5_acc = 0.0
        preds = []
        gt = []
        self.logger.debug(f"Starting training epoch {epoch}")
        iterator = tqdm(self.training_generator, file=sys.stdout)
        for batch_idx, input_tensors in enumerate(iterator):
            if args.debug_mode:
                if batch_idx > 10:
                    break

            self.optimizer.zero_grad(set_to_none=True) #performance
            input_data, target = input_tensors
            if self.cuda and not args.ffcv:
                input_data = input_data.cuda(args.local_rank if args.ddp else  None) #this is already cuda for ffcv loader
                target = target.cuda(args.local_rank if args.ddp else  None)

            with torch.autocast(self.device):
                output = self.model(input_data)
                if util.has_nan(output):
                    self.logger.info(f"Nans in training {epoch}/{batch_idx} {(output != output).any(axis=1).sum()}")
                    if not args.continue_with_nans:
                        raise Exception("Exit because of NaNs")

                loss1 = criterion(output, target)
                loss2 = range_awareness_loss(self.get_range_aware_act(args))

                loss = loss1 + args.range_awareness_loss_weight * loss2
                self.logger.debug(f'range_aware_weight:{args.range_awareness_loss_weight}')
                self.logger.debug(f'loss1: {loss1:.3f}, loss2: {float(loss2):.3f}, tot {loss.item():.3f}')

                if args.distillation_model:
                    in_t = args.distillation_model(input_data)
                    loss = loss + args.distillation_alpha * nd_loss(output, in_t, T=args.distillationT)

            sum_loss += loss.item()

            max_output = output.detach().abs().max().item()
            scaler.scale(loss).backward()

            if args.gradient_clip > 0:
                # Unscales the gradients of optimizer's assigned params in-place
                scaler.unscale_(self.optimizer)
                # optimizer's gradients are already unscaled, so scaler.step does not unscale them,
                # although it still skips optimizer.step() if the gradients contain infs or NaNs.
                torch.nn.utils.clip_grad_value_(self.model.parameters(), args.gradient_clip)

            scaler.step(self.optimizer)
            scaler.update()

            correct, total, acc = accuracy(output, target)
            _, preds_t = torch.max(output, 1)
            top_5_acc = top_k_acc(output, target, 5)

            gt.extend(target)
            preds.append(preds_t)

            sum_acc += acc
            sum_correct += correct
            sum_total += total
            sum_top5_acc += top_5_acc

            num_samples = batch_idx * args.batch_size + 1
            
            t.set_description('T {} loss={:.3f}, acc={:.3f}, avr_acc={:.3f}, max_out={:.2f}, top5={:.2f}'.
                                format(batch_idx, loss.item(), acc, sum_correct / float(num_samples) ,max_output, top_5_acc))

        self.logger.debug(f"Finished training epoch {epoch}")
        preds = torch.cat(preds).cpu()

        for t, p in zip(gt, preds):
            confusion_matrix[t.long(), p.long()] += 1

        train_metrics.update_all({
                                        'loss': sum_loss/(batch_idx+1),
                                        'accuracy': sum_acc/(batch_idx+1),
                                        'top_5_acc': sum_top5_acc / (batch_idx + 1)
                                        }, writer_step=epoch)
        self.logger.info(get_summary(args, epoch, num_samples, train_metrics, mode="Training"))
        confusion_matrix_numpy = confusion_matrix.cpu().numpy()


        train_metrics.report_ranges(epoch, self.get_all_ranges(args))

        return train_metrics, confusion_matrix_numpy


    def test(self, args, epoch: int):
        """Tests the model on the given data

        Args:
            args (Arguments): user arguments
            epoch (int): epoch number

        Raises:
            Exception: Exit because of NaNs, if Nan values are present in the output, and args.continue_with_nans=False

        Returns:
            MetricsTracker: metrics
            np.array: confusion matrix
        """
        return self.__validation( args, self.test_generator, epoch, mode='test')
    
    def validation(self, args, epoch: int):
        """Tests the model on the given data

        Args:
            args (Arguments): user arguments
            epoch (int): epoch number

        Raises:
            Exception: Exit because of NaNs, if Nan values are present in the output, and args.continue_with_nans=False

        Returns:
            MetricsTracker: metrics
            np.array: confusion matrix
        """
        return self.__validation(args, self.val_generator, epoch, mode='val')
            
    def __validation(self, args, dataGenerator, epoch: int, mode: str ='val'):
        """Tests the model on the given data

        Args:
            args (Arguments): user arguments
            dataGenerator (dataLoader): the data to test the model
            epoch (int): epoch number
            mode (str, optional): A short label (can be 'test' or 'val') . Defaults to 'val'.

        Raises:
            Exception: Exit because of NaNs, if Nan values are present in the output, and args.continue_with_nans=False

        Returns:
            MetricsTracker: metrics
            np.array: confusion matrix
        """
        self.logger.debug(f"Start {mode} phase")
        self.model.eval()

        self.__init_actual_data_range()

        normed_weights = self.__get_normed_weights(args, dataGenerator.dataset)

        criterion = nn.CrossEntropyLoss(reduction='mean', weight=normed_weights)

        metric_ftns = ['loss', 'accuracy', 'auc', 'top_5_acc']
        val_metrics = MetricsTracker(*[m for m in metric_ftns], mode=mode, writer = self.writer)
        val_metrics.reset()
        confusion_matrix = torch.zeros(args.classes, args.classes, dtype=int)

        sum_correct = 0.0
        sum_total = 0.0
        sum_loss = 0.0
        sum_acc = 0.0
        sum_top5_acc = 0.0
        gt = []
        pred_probs = []
        preds = []

        self.logger.debug("Start validation batch loop")
        with torch.no_grad():
            for batch_idx, input_tensors in enumerate(dataGenerator):
                if args.debug_mode:
                    if batch_idx > 10:
                        break

                input_data, target_l = input_tensors
                target = target_l
                if (self.cuda):
                    input_data = input_data.cuda(args.local_rank if args.ddp else  None)
                    target = target_l.cuda(args.local_rank if args.ddp else  None)

                output = self.model(input_data)
                if util.has_nan(output):
                    self.logger.warning(f"Nans in {mode}  {epoch}/{batch_idx}")
                    if not args.continue_with_nans:
                        raise Exception("Exit because of NaNs")
                    return val_metrics, confusion_matrix

                loss = criterion(output, target)
                sum_loss += loss.item()

                correct, total, acc = accuracy(output, target)
                sum_acc += acc
                sum_correct += correct
                sum_total += total
                top_5_acc = top_k_acc(output, target, 5)
                sum_top5_acc += top_5_acc

                num_samples = batch_idx * args.batch_size + 1
                _, preds_t = torch.max(output, 1)
                pred_probs_t = nn.functional.softmax(torch.clamp(output, max=20), dim=1)
                preds.append(preds_t)
                pred_probs.append(pred_probs_t)
                gt.extend(target_l)

            self.logger.debug("Done validation batch loop")
            preds = torch.cat(preds).cpu()
            for t, p in zip(gt, preds):
                confusion_matrix[t.long(), p.long()] += 1

            #self.logger.debug("Threading to make_confusion_matrix start")


            values_to_update_dict = {'loss': sum_loss / (batch_idx + 1),
                                    'accuracy': sum_acc / (batch_idx + 1),
                                    'top_5_acc': sum_top5_acc / (batch_idx + 1)
                                    }
            val_metrics.update_all(values_to_update_dict, writer_step=epoch)
        self.logger.info(get_summary(args, epoch, num_samples, val_metrics, mode=mode))
        confusion_matrix_numpy = confusion_matrix.cpu().numpy()

        self.logger.debug('Confusion Matrix\n{}'.format(confusion_matrix_numpy))

        val_metrics.report_ranges(epoch, self.get_all_ranges(args))
        return val_metrics, confusion_matrix_numpy


    def approximate_input_range_from_data(self, args):
        """Runs the model on the given data. As the result, each range aware activation in the model (if any)
        will hold the correct actual data range - minimum and maximum values of all inputs it recieved during the approximation run
        on the approximation data set.
        This ranges are used when approximation the range aware relu by range aware polynomial, as polynomial approximation requires a range

        Args:
            args (Arguments): user arguments

        """
        self.model.eval()

        self.__init_actual_data_range()

        self.logger.debug("aprox")
        #subset of the training generator.
        data_generator = self.approx_generator

        with torch.no_grad():
            for batch_idx, input_tensors in enumerate(data_generator):
                if args.debug_mode:
                    if batch_idx > 10:
                        break

                input_data, target_l = input_tensors
                if (self.cuda):
                    input_data = input_data.cuda(args.local_rank if args.ddp else  None)
                    self.model.cuda(args.local_rank if args.ddp else  None)

                self.model(input_data)
