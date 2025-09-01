#
# OCO Source Materials
# 5737-A56
# © Copyright IBM Corp. 2017
#
# The source code for this program is not published or other-wise divested
# of its trade secrets, irrespective of what has been deposited with the
# U.S. Copyright Office.
#

import pyhelayers
import os
import json
from enum import Enum


class MODEL_ARCH(Enum):
    LR = 1
    NN = 2


class PYFHE(object):
    __requirements_setters = {"security": "set_security_level",
                              "integerPartPrecision": "set_integer_part_precision",
                              "fractPartPrecision": "set_fractional_part_precision",
                              "batchSize": "optimize_for_batch_size",
                              "modelEncrypted": "set_model_encrypted",
                              "nofixedBatchSize": "set_no_fixed_batch_size",
                              "optTarget": "set_optimization_target",
                              "exhaustiveSearch": "set_exhaustive_search",
                              "maxBatchMemory": "set_max_batch_memory",
                              "maxClientInferenceCpuTime": "set_max_client_inference_cpu_time",
                              "maxClientInferenceMemory": "set_max_client_inference_memory",
                              "maxPredictCpuTime": "set_max_predict_cpu_time",
                              "maxOutputMemory": "set_max_output_memory",
                              "maxModelMemory": "set_max_model_memory",
                              "maxInputMemory": "set_max_input_memory",
                              "maxInitModelCpuTime": "set_max_init_model_cpu_time",
                              "maxContextMemory": "set_max_context_memory",
                              "maxDecryptOutputCpuTime": "set_max_decrypt_output_cpu_time",
                              "maxEncryptInputCpuTime": "set_max_encrypt_input_cpu_time",
                              "maxInferenceCpuTime": "set_max_inference_cpu_time",
                              "maxInferenceMemory": "set_max_inference_memory",
                              "he_context_options": "set_he_context_options"
                              }

    def __init__(self, model_architecture, requirements=None, hyper_params_file = None, init_files = []):
        if not isinstance(model_architecture, MODEL_ARCH):
            raise TypeError(
                "The model_architecture parameter should be [MODEL_ARCH.LR | MODEL_ARCH.NN]")

        self.__model_architecture = model_architecture
        for file in init_files:
            assert(os.path.isfile(file))
        if hyper_params_file:
            assert(os.path.isfile(hyper_params_file))

        self.__plain = self.__init_plain(hyper_params_file, init_files)
        self.__init_default_context()
        self.__profile = None
        self.__enc_model = None
        self.__iop = None
        self.__ioe = None

        try:
            if os.path.isfile(requirements):
                with open(requirements, 'r') as f:
                    config = json.loads(f.read())
                    self.__requirements = config["he_run_requirements"]
            else:
                raise FileNotFoundError
        except TypeError:
            self.__requirements = requirements
        print(f"User model architecture is {self.__model_architecture}")
        print(f"User requirements are {self.__requirements}")

    def encrypt_model(self):
        profile = self.get_profile()
        self.__enc_model = self.__plain.get_empty_he_model(self.get_context())
        self.__enc_model.encode_encrypt(self.__plain, profile)

        return self.__enc_model

    def encrypt_input(self, plain_samples):
        # print('Encrypting input . . .')
        res = pyhelayers.EncryptedData(self.get_context())
        self.get_io_encoder().encode_encrypt(res, [plain_samples])
        return res

    def decrypt_output(self, client_predictions):
        if isinstance(client_predictions, pyhelayers.EncryptedData):
            predictions = client_predictions
        else:
            predictions = pyhelayers.EncryptedData(self.__client_context)
            predictions.load_from_buffer(client_predictions)
        
        res = self.get_io_encoder().decrypt_decode_output(predictions)
        # print('Prediction results have been decrypted')
        return res

    def init_context(self):
        if self.__profile is None:
            self.__init_profile()
        print('Generating encryption keys . . .')
        self.__client_context.init(self.__profile.get_he_config_requirement())


    def __init_default_context(self):
        self.__client_context = pyhelayers.DefaultContext()

    def __init_plain(self, hyper_params_file, init_files):
        hyper_params = pyhelayers.PlainModelHyperParams()
        if hyper_params_file:
            hyper_params.load(hyper_params_file)
        if len(init_files) > 0:
            return pyhelayers.PlainModel.create(hyper_params, init_files)
        return None

    def __init_profile(self):
        he_run_req = pyhelayers.HeRunRequirements()

        [getattr(he_run_req, PYFHE.__requirements_setters[req])(self.__requirements[req])
         for req in self.__requirements.keys() if req in PYFHE.__requirements_setters]

        print("Optimizing for FHE . . .")
        self.__profile = pyhelayers.HeModel.compile(self.__plain, he_run_req)


    def get_profile(self):
        if self.__profile is None:
            self.__init_profile()
        return self.__profile

    def get_encrypted_model(self):
        return self.__enc_model if self.__enc_model else self.encrypt_model()
    
    def get_io_processor(self):
        return self.__iop if self.__iop else self.create_io_processor()
    
    def get_io_encoder(self):
        return self.__ioe if self.__ioe else self.create_io_encoder()
    
    def create_io_encoder(self):
        he_model = self.get_encrypted_model()
        self.__ioe = pyhelayers.ModelIoEncoder(he_model)
        return self.__ioe
    
    def create_io_processor(self):
        he_model = self.get_encrypted_model()
        self.__iop = he_model.create_io_processor()
        return self.__iop

    def init_context_from_buffer(self, context_buffer, secret_key=None):
        self.__init_default_context()
        self.__client_context.load_from_buffer(context_buffer)
        if secret_key:
            self.__client_context.load_secret_key(secret_key)

    def encrypted_model_from_buffer(self, model_buffer):
        self.__enc_model = pyhelayers.load_he_model(self.get_context(), model_buffer)

        return self.__enc_model

    def get_context(self, secret_key=None):
        if secret_key is None:
            return self.__client_context
        elif secret_key == False:
            return self.__client_context.save_to_buffer()
        else:
            return self.__client_context.save_to_buffer(), self.__client_context.save_secret_key()

    def predict(self, enc_samples):
        prediction = pyhelayers.EncryptedData(self.get_context())

        if isinstance(enc_samples, pyhelayers.EncryptedData):
            self.get_encrypted_model().predict(prediction, enc_samples)
        else:
            samples = pyhelayers.EncryptedData(self.__client_context)
            samples.load_from_buffer(enc_samples)
            self.get_encrypted_model().predict(prediction, samples)

        return prediction
    
    def get_empty_encrypted_data(self):
        return pyhelayers.EncryptedData(self.get_context())
