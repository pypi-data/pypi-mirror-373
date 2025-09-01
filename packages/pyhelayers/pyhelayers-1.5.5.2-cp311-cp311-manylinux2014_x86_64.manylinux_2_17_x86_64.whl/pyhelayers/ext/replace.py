#
# OCO Source Materials
# 5737-A56
# © Copyright IBM Corp. 2017
#
# The source code for this program is not published or other-wise divested
# of its trade secrets, irrespective of what has been deposited with the
# U.S. Copyright Office.
#

from . import utils
import numpy as np
import os
from functools import partial
import json
import sys
import keras
import tensorflow
import sklearn
from .pyfhemlimpl.pyfheml import KerasNNRequest, SKLearnLRRequest


def _hnd(lm_request, getter_func, classes_shape, *args, **kwargs):
    x_test, = args

    print("Starting FHE computation . . .")
    utils.start_timer()
    predictions = lm_request.predict(x_test)
    utils.end_timer("FHE computation")

    if classes_shape:
        if classes_shape[1] == 1:
            return np.where(predictions > 0.5, 1, 0).reshape(-1)
        else:
            return predictions.argmax(axis=1)

    return getter_func(predictions)


def _predictions_hnd_keras_nn(predictions):
    if predictions.shape[-1] > 1:
        return predictions.argmax(axis=-1)
    else:
        return (predictions > 0.5).astype('int32')


def _predictions_hnd_sklearn_lr_closure(classes):
    _clss = classes

    def _inner_func(predictions):
        if len(predictions.shape) == 1 or (len(predictions.shape) == 2 and predictions.shape[-1] == 1):
            indices = (predictions > 0.5).astype(int)
        else:
            indices = predictions.argmax(axis=1)
        return _clss[indices]

    return _inner_func


def _predictions_hnd_stub(predictions):
    return predictions


def replace(func, classes_shape=None, config_file=None, hyper_params_file=None):
    if not hasattr(func, '__call__'):
        raise TypeError

    if not hasattr(func, '__self__'):
        raise TypeError

    lm_model = func.__self__
    config = None

    if config_file is None:
        caller_name = sys._getframe(1).f_code.co_filename
        config_file = os.path.dirname(
            os.path.abspath(caller_name)) + '/fhe.json'

    try:
        with open(config_file, 'r') as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        pass

    if config and config["enable_fhe"] is False:
        return func

    requirements = config["he_run_requirements"] if config else {}
    getter_func = _predictions_hnd_stub

    # print(type(lm_model))

    if isinstance(lm_model, tensorflow.keras.models.Sequential) or isinstance(lm_model, tensorflow.keras.Sequential):
        lm_request = KerasNNRequest(lm_model, requirements, hyper_params_file)
    elif isinstance(lm_model, sklearn.linear_model.LogisticRegression):
        lm_request = SKLearnLRRequest(lm_model, requirements, hyper_params_file)
        if func.__name__ == 'predict':
            getter_func = _predictions_hnd_sklearn_lr_closure(
                lm_model.classes_)
    else:
        print(
            f"Not supported model {type(lm_model)}: the original function won't be replaced")
        return func

    return partial(_hnd, lm_request, getter_func, classes_shape)
