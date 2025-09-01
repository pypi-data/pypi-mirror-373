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
from datetime import datetime
import numpy as np
import torch
import torch.optim as optim
import warnings
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
import csv
import torch.nn as nn

logger = get_logger()


def create_log_title(args, date_str: str, uniq_id: str):
    """Convinience function that creates a string of most of the arguments, together with date and unique-id
    This can be used to distinguish the run
    Args:
            args (Arguments): The user arguments
            date_str (String): A string representing the current date and time in 'Ymd_HM' format
            uniq_id (String): Some unique id
    Returns:
        String: the generated string
    """
    arg_list = []

    arg_list.append(f"{date_str}")
    arg_list.append(uniq_id)

    if args.log_string != '':
        if args.log_string.find('-') > -1:
            warnings.warn("args.log_string cannot contain '-'. changes to '_' instead.")
            args.log_string = args.log_string.replace('-', '_')

        arg_list.append(args.log_string)

    arg_list.append(f"{args.pooling_type}pool")
    arg_list.append(f"{args.activation_type}")

    arg_list.append(args.dataset_name)

    log_title = '-'.join(arg_list)

    return log_title


def is_cuda_available(print=False):
    if torch.cuda.device_count() > 0 and os.getenv("CUDA_VISIBLE_DEVICES"):
        if print: logger.info(f"available cuda devices: {torch.cuda.device_count()}")
        return True
    else:
        if print: logger.info(f"No available cuda devices, not using cuda")
        return False


def has_nan(tensor: torch.Tensor):
    """Returns Tensor(True) if the input tensor has any Nan values, and Tensor(False) otherwise

    Args:
        tensor (Tensor): tensor

    Returns:
        Tensor: Tensor(True) if the input tensor has any Nan values, and Tensor(False) otherwise
    """
    return torch.any(tensor != tensor)


def date_str():
    """Creates a string from the current date

    Returns:
        String: 'Ymd_HM' string
    """
    return datetime.utcnow().strftime('%Y%m%d_%H%M')


def load_checkpoint(args):
    """Loads the checkpoint into memory, if the args.from_checkpoint is set to a valid checkpoint path

    Args:
        args (Arguments): user arguments

    Returns:
        nn.Module: saved model
        torch.optim:  optimizer
        SimpleNamespace: train_state
        float: loss
        MetricsTracker: metrics
        bool: is_complete state (should be True if there are no Relu activations in the model)
    """
    if args.ddp:
        #Input type (torch.cuda.FloatTensor) and weight type (torch.FloatTensor) should be the same
        #why don't need the cuda if not ddp?..
        #the input is on GPU, so we need the model to also be sent to GPU
        checkpoint = torch.load(os.path.join(args.from_checkpoint), map_location=f'cuda:{args.local_rank}')
        #checkpoint['model'].cuda(args.local_rank)
    elif is_cuda_available():
        checkpoint = torch.load(os.path.join(args.from_checkpoint), map_location=f'cuda:{args.local_rank}')
    else:
        checkpoint = torch.load(os.path.join(args.from_checkpoint), map_location=torch.device('cpu'))

    model = checkpoint['model']
    # because the updates of optimizer create new groups, the "optimizer.load_state_dict" doesn't work
    try:
        optimizer = checkpoint['optimizer']
    except Exception as e:
        logger.info(f"Loading optimizer from checkpoint process failed - using default {e}")
        optimizer = get_optimizer(args, model)

    train_state = checkpoint.get('train_state', None)
    loss = checkpoint.get("loss", 1000)
    metrics = checkpoint.get('metrics', None)
    is_complete = checkpoint.get('is_complete', True)

    return model, optimizer, train_state, loss, metrics, is_complete


def save_checkpoint(chp: set, path: str, filename: str):
    """Saves the input checkpoint chp into a file

    Args:
        chp (set): state object
        path (String): path location to save to
        filename (String): filename prefix
    """
    file_name = os.path.join(path, filename + '_checkpoint.pth.tar')
    logger.info(file_name)
    torch.save(chp, file_name)
    return file_name


def save_model(trainer, act_converter, args, metrics, epoch: int, confusion_matrix, rank: int = 0):
    """Saves the model and other train-state related parameters into a file.
    last model, best model, specific epochs (by args.save_freq)

    Args:
        trainer (Trainer): the trainer object
        act_converter (PolyActivationConverter): the PolyActivationConverter object
        args (Arguments): user arguments
        metrics (MetricsTracker): current metrics
        epoch (int): current training epoch
        confusion_matrix (_type_): confusion matrix

    """
    # relevant in DDP
    if rank != 0: return

    loss = metrics.get_avg('loss')
    save_path = args.save_dir
    os.makedirs(save_path, exist_ok=True)

    args.dump_to_file(save_path)

    save_model = trainer.get_model()
    if isinstance(save_model, nn.DataParallel) or isinstance(save_model, nn.parallel.DistributedDataParallel):
        save_model = trainer.get_model().module
    
    train_state = act_converter.create_train_state(epoch)

    if args.save_freq != 0:
        state = {'train_state': train_state,
                 'model': save_model,
                 'optimizer': trainer.get_optimizer(),
                 'metrics': metrics.get_avg('loss'),
                 'loss': loss,
                 'is_complete': act_converter.get_was_completed()}
        
        # save best checkpoint (possible only if the model is fully FHE friendly)
        best_pred_loss = act_converter.get_best_found_loss()
        if best_pred_loss is None:
            best_pred_loss = 1000
        logger.debug(f'best_pred_loss: {best_pred_loss}')
        logger.debug(f'was_completed: {act_converter.get_was_completed()}')
        if (loss < best_pred_loss) and act_converter.get_was_completed():
            logger.debug("saving best")
            act_converter.set_best_found_loss_and_epoch(loss, epoch)
            save_checkpoint(state,
                            path=save_path, filename=args.model + "_best")
            np.save(os.path.join(save_path, 'best_confusion_matrix.npy'), confusion_matrix)

        if args.save_freq == -1:  # overwrite last checkpoint each period
            save_checkpoint(state,
                            save_path, args.model + f"_last")
        if args.save_freq > 0:  # write checkpoint for a given freq only
            if epoch % args.save_freq == 0:
                save_checkpoint(state,
                                save_path, args.model + f"_curr{epoch:03}")


def postproc_model(args, act_converter, rank: int = 0):
    """post-procces an FHE friendly model to replace any WeightedRelu activations by the actual activation

    Args:
        args (Arguments): user arguments
        act_converter (PolyActivationConverter): the PolyActivationConverter object
        rank (int, optional): local rank, if DDP is used. Defaults to 0.
        
    Raises:
        FileNotFoundError: The activation replacement has not completed, hence no best model to post-process.
        
    Returns:
        String: full path of the saved file
    """
    if rank != 0:
        return

    if not act_converter.get_was_completed():
        raise FileNotFoundError("The activation replacement has not completed, hence no best model to post-process.")

    save_path = args.save_dir
    os.makedirs(save_path, exist_ok=True)

    # load best model
    checkpoint = torch.load(os.path.join(save_path, args.model + "_best_checkpoint.pth.tar"))

    if not act_converter.is_fhe_friendly(checkpoint['model']):
        raise FileNotFoundError("The activation replacement has not completed, hence no best model to post-process.")

    # convert activations
    checkpoint['model'].post_process_activations()

    # save modified model as new file
    filename = args.model + "_postproc"
    full_path = save_checkpoint(checkpoint, path=save_path, filename=filename)
    return full_path


def save_onnx(args, act_converter, trainer, rank: int = 0):
    """Converts the model saved in best checkpoint file to onnx and saves the result to file.  

    Args:
        args (Arguments): user arguments
        act_converter (PolyActivationConverter): the PolyActivationConverter object
        trainer (Trainer): the trainer object
        rank (int, optional): local rank, if DDP is used. Defaults to 0.
        
    Raises:
        Exception: The activation replacement has not completed, hence no best model to post-process.
        
    Returns:
        String: full path of the saved file
    """
    
    if rank != 0:
        return
    
    # WeightedRelu activation functions must be replaced before converting
    pp_full_path = postproc_model(args, act_converter, rank)
    
    chk_point = torch.load(pp_full_path)
    torch_model = chk_point["model"]
    torch_model.cpu()
    torch_model.eval()

    model = trainer.get_model()
    if isinstance(model, nn.DataParallel) or isinstance(model, nn.parallel.DistributedDataParallel):
        model = model.module
    input_size = model.get_input_size()

    x = torch.randn(1, *input_size, requires_grad=True)
    torch_out = torch_model(x)
    logger.info(f'save_onnx:torch_out.shape: {torch_out.shape}')
    output_path = os.path.join(args.save_dir, args.model + ".onnx")
    

    torch.onnx.export(torch_model,             # model being run
                      x,                         # model input (or a tuple for multiple inputs)
                      output_path,   # where to save the model (can be a file or file-like object)
                      export_params=True,        # store the trained parameter weights inside the model file
                      training=torch.onnx.TrainingMode.PRESERVE,
                      input_names=['input'],   # the model's input names
                      output_names=['output'],  # the model's output names
                      dynamic_axes={'input': {0: 'batch_size'},    # variable length axes
                                    'output': {0: 'batch_size'}})
    print(f"ONNX model saved to {output_path}")
    return output_path, torch_model


def read_filepaths(file):
    paths, labels = [], []
    with open(file, 'r') as f:
        lines = f.read().splitlines()

        for line in lines:
            if ('/ c o' in line):
                break
            try:
                splitted_line = line.split(' ')
                if len(splitted_line) == 4:
                    subjid, path, label, source =splitted_line
                else: # for sirm
                    subjid = splitted_line[0] + ' ' + splitted_line[1]
                    path, label,source = splitted_line[2:]
            except:
                logger.info(f"{file} {splitted_line}")
            paths.append(path)
            labels.append(label)
    return paths, labels


def get_optimizer(args, model: torch.nn.Module):
    """Return the user defined optimizer object

    Args:
        args (Arguments): user arguments
        model (nn.Module): model

    Returns:
        torch.optim: optimizer object
    """
    weight_decay = 5e-4
    if args.opt == 'sgd':
        return optim.SGD(model.parameters(), lr=args.lr, momentum=0.9, weight_decay=weight_decay)
    elif args.opt == 'adam':
        return optim.Adam(model.parameters(), lr=args.lr, weight_decay=weight_decay)


def get_summary(args, epoch: int, num_samples: int, metrics, mode: str):
    """Prints the epoch summary

    Args:
        args (Arguments): user arguments
        epoch (int): epoch number
        num_samples (int): number of processed sumples
        metrics (MetricsTracker): current metrics
        mode (String): "Train"/"Test"/"Validation"
    """
    msg = (
    f'\n {mode}:\n EPOCH: {epoch}\t'
    f'Samples: {num_samples}\t'
    f'Loss: {metrics.get_avg("loss"):.4f}\t'
    f'Accuracy: {metrics.get_avg("accuracy"):.2f}\t'
    f'Top5_Acc: {metrics.get_avg("top_5_acc"):.2f}\n'
    )

    return msg


def accuracy(output: torch.Tensor, target: torch.Tensor):
    """Accuracy classification score. This metric computes the number of times where the correct label is equal to the predicted label

    Args:
        output (list): List of predictions
        target (list): True labels
    Returns:
        int: number of correct predictions
        int: number of samples
        float: The top-1 accuracy score
    """
    '''returns: number of correct classifications, total number of clussifications, accuracy (correct divided by total)'''
    samples = len(target)
    
    with torch.no_grad():
        pred = torch.argmax(output, dim=1)
        correct = torch.sum(pred == target).item()
        
    return correct, samples, correct / samples


def top_k_acc(output: torch.Tensor, target: torch.Tensor, k: int =3):
    """Top-k Accuracy classification score. 
    This metric computes the number of times where the correct label is among the top k labels predicted (ranked by predicted scores)

    Args:
        output (list): List of predictions
        target (list): True labels
        k (int, optional): Number of most likely outcomes considered to find the correct label. Defaults to 3.

    Returns:
        float: top_k accuracy: The top-k accuracy score
    """
    if output.shape[1] < k:
        k = 1

    with torch.no_grad():
        pred = torch.topk(output, k, dim=1)[1]
        correct = 0
        for i in range(k):
            correct += torch.sum(pred[:, i] == target).item()
        
    return correct / len(target)
    
                
    
def write_to_csv(rowData: list, dir: str, fname: str, header:list =[]):
    """Write data row into CSV file

    Args:
        rowData (list): data
        dir (String): path to write to
        fname (String): file name
        header (list, optional): headers row. Defaults to [].
    """
    os.makedirs(dir, exist_ok=True)
    full_path = os.path.join(dir, fname)
    
    with open(full_path, 'a+') as f:
        writer = csv.writer(f, delimiter=',')
        
        file_is_empty = os.stat(full_path).st_size == 0
        if file_is_empty and header != []:
            writer.writerow(header)
            
        writer.writerow(rowData)

