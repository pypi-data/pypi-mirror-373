#
# OCO Source Materials
# 5737-A56
# © Copyright IBM Corp. 2017
#
# The source code for this program is not published or other-wise divested
# of its trade secrets, irrespective of what has been deposited with the
# U.S. Copyright Office.
#

from abc import ABC, abstractmethod
from .pyfhe import PYFHE
import os
import tempfile
import math
from . import utils
import numpy as np
import sklearn_json as skljson


class IRequest(ABC):
    @abstractmethod
    def __create_context(self):
        raise NotImplementedError

    @abstractmethod
    def __encrypt_input(self, plain_samples):
        raise NotImplementedError

    @abstractmethod
    def __encrypt_model(self):
        raise NotImplementedError

    @abstractmethod
    def __decrypt(self, enc_model, predictions):
        raise NotImplementedError


class IMLConfigHandler(ABC):
    def __init__(self):
        self._temp_dir = tempfile.TemporaryDirectory()

    @abstractmethod
    def get_model(self, model):
        pass

    @abstractmethod
    def get_weights(self):
        pass

    def cleanup(self):
        self._temp_dir.cleanup()


class AbstractMLComputationRequest(IRequest):
    isAbstractMLComputationRequest = True

    def __init__(self, model_architecture, requirements, hyper_params_file = None, init_files = []):
        self.__fhewrap = PYFHE(
            model_architecture, requirements, hyper_params_file, init_files)

    def predict(self, plain_samples):
        self._IRequest__create_context()
        sampleSize = plain_samples.shape[0]
        batchSize = self.__fhewrap.get_profile().get_optimal_batch_size()
        numBatches = math.ceil(sampleSize / batchSize)
        # print(f"Batch size: {batchSize}")
        # print(f"Number of batches: {numBatches}")

        all_plain = None

        enc_model = self._IRequest__encrypt_model()

        for i in range(numBatches):
            batchSamples, _ = utils.extract_batch(
                plain_samples, plain_samples, batchSize, i)
            print(f"Running encrypted batch {i+1}/{numBatches}")
            enc_samples = self._IRequest__encrypt_input(batchSamples)
            predictions = self.__fhewrap.get_empty_encrypted_data()
            self.__predict(enc_model, enc_samples, predictions)
            plain = self._IRequest__decrypt(predictions)

            if all_plain is None:
                if len(plain.shape) > 1:
                    all_plain = np.empty(shape=(0, *plain.shape[1:]))
                else:
                    all_plain = np.empty(shape=(0, 1))   

            all_plain = np.append(all_plain, plain, 0)
            #all_plain = np.append(all_plain, plain)

        return all_plain

    def _IRequest__create_context(self):
        self.__fhewrap.init_context()

    @property
    def _context(self):
        return self.__fhewrap.get_context()

    @property
    def _private_context(self):
        return self.__fhewrap.get_context(True)

    @property
    def _public_context(self):
        return self.__fhewrap.get_context(False)

    def _IRequest__encrypt_input(self, plain_samples):
        return self.__fhewrap.encrypt_input(plain_samples)

    def _IRequest__encrypt_model(self):
        return self.__fhewrap.encrypt_model()

    # def _IRequest__encrypt(self, plain_samples):
    #     enc_model = self.__fhewrap.encrypt_model()
    #     enc_samples = self.__fhewrap.encrypt_input(plain_samples)
    #     return enc_model, enc_samples

    def _IRequest__decrypt(self, predictions):
        return self.__fhewrap.decrypt_output(predictions)

    @abstractmethod
    def __predict(self, enc_model, enc_samples, predictions):
        raise NotImplementedError


class KerasMLConfigHandler(IMLConfigHandler):
    def __init__(self, model):
        IMLConfigHandler.__init__(self)
        self.__model = model

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def get_model(self):
        model_json = self.__model.to_json()
        json_file_name = os.path.join(self._temp_dir.name, 'model.json')
        with open(json_file_name, 'w') as (json_file):
            json_file.write(model_json)

        return json_file_name

    def get_weights(self):
        weights_file_name = os.path.join(self._temp_dir.name, 'model.h5')
        self.__model.save_weights(weights_file_name)
        return weights_file_name


class SKLearnConfigHandler(IMLConfigHandler):
    def __init__(self, model):
        IMLConfigHandler.__init__(self)
        self.__model = model

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def get_model(self):
        json_file_name = os.path.join(self._temp_dir.name, 'model.json')
        skljson.to_json(self.__model, json_file_name)

        return json_file_name

    def get_weights(self):
        pass
