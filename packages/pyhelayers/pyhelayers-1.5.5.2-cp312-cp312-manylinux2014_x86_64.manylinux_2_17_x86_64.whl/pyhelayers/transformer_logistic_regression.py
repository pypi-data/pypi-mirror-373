#
# OCO Source Materials
# 5737-A56
# © Copyright IBM Corp. 2017
#
# The source code for this program is not published or other-wise divested
# of its trade secrets, irrespective of what has been deposited with the
# U.S. Copyright Office.
#

import importlib.util

# TransformerLogisticRegression requires the heaan_sdk wheel to be installed in the environment
heaan_sdk_spec = importlib.util.find_spec("heaan_sdk")
if heaan_sdk_spec is not None:
    import pyhelayers
    import heaan_sdk
    import shutil
    import os
    import numpy as np

    class TransformerLogisticRegressionEncryptedData():
        def __init__(self, heaan_context, data_set = None):
            self.heaan_context = heaan_context
            self.data_set = data_set

        def save_to_buffer(self):
            raise Exception('TransformerLogisticRegressionEncryptedData.save_to_buffer - not implemented. Use save_to_file.')

        def load_from_buffer(self, buff):
            raise Exception('TransformerLogisticRegressionEncryptedData.load_from_buffer - not implemented. Use load_from_file.')

        def save_to_file(self, path):
            self.data_set.save(path)

        def load_from_file(self, path):
            self.data_set = heaan_sdk.DataSet.from_path(self.heaan_context, path)       

    class TransformerLogisticRegressionIoEncoder():
        def __init__(self, heaan_context, heaan_lr):
            self.heaan_context = heaan_context
            self.heaan_lr = heaan_lr

        def encode_encrypt(self, tensors):
            data_set = None
            if len(tensors) == 2:
                data_set = heaan_sdk.ml.linear_model.preprocessor.encode_data.encode_train_data(self.heaan_context, tensors[0], np.squeeze(tensors[1]), self.heaan_lr.unit_shape)
            elif len(tensors) == 1:
                data_set = self.heaan_lr.encode_encrypt(self.heaan_context, tensors[0], self.heaan_lr.unit_shape, self.heaan_lr.num_classes)
            else:
                raise Exception('TransformerLogisticRegressionIoEncoder.encode_encrypt - Unexpected number of tensors to encrypt.')

            return TransformerLogisticRegressionEncryptedData(self.heaan_context, data_set)

        def decrypt_decode_output(self, encrypted_data):
            return encrypted_data.data_set.decrypt_decode()

    class TransformerLogisticRegression():
        def __init__(self, he_context = None):
            self.heaan_lr = None
            self.he_context = he_context
            self.heaan_context = None
            self.keys_path = '/tmp/heaan_keys/'

            if he_context is not None:
                self._load_heaan_context()

        def _load_heaan_context(self):
            public_keys_dir = 'public_keypack/'
            secret_key_dir = 'secret_keypack/'

            if os.path.exists(self.keys_path):
                shutil.rmtree(self.keys_path)
            os.mkdir(self.keys_path)
            os.mkdir(self.keys_path + public_keys_dir)

            self.he_context.save_public_keys_to_dir(self.keys_path + public_keys_dir)

            if self.he_context.has_secret_key():
                self.he_context.save_secret_key_to_dir(self.keys_path + secret_key_dir)

            self.heaan_context = heaan_sdk.Context.from_args(
                self.he_context.get_parameter_preset_str(),
                key_dir_path=self.keys_path,
                load_keys=("all" if self.he_context.has_secret_key() else "pk")
                )

            # We should keep the directory with the keys until the end of the run (it is deleted in the d'tor)

        def encode_encrypt(self, files, he_run_req, hyper_params):
            if not hyper_params.trainable:
                raise Exception('TransformerLogisticRegression.encode_encrypt - Currently supported only in trainable mode.')

            # TODO: This is hard-coded for now, but consider selecting this dynamically in some way. 
            # However, we must use one of the pre-made heaan presets (and not a custom preset)
            req = pyhelayers.HeConfigRequirement(2**15, 12, 42, 18) # ParameterPreset::FGb
            req.bootstrappable = True
            self.he_context = pyhelayers.HeaanContext()
            self.he_context.init(req)
            self.he_context.set_default_device(he_run_req.get_optimized_device())
            self._load_heaan_context()

            if hyper_params.fit_hyper_params.fit_batch_size is None:
                hyper_params.fit_hyper_params.fit_batch_size = 1

            unit_shape = (hyper_params.fit_hyper_params.fit_batch_size, 0)

            self.heaan_lr = heaan_sdk.LogisticRegression(
                self.heaan_context,
                unit_shape,
                hyper_params.number_of_features,
                hyper_params.number_of_classes,
                num_epoch=hyper_params.fit_hyper_params.number_of_epochs,
                batch_size=hyper_params.fit_hyper_params.fit_batch_size,
                lr=hyper_params.fit_hyper_params.learning_rate,
                verbose=hyper_params.verbose
                #TODO: we can also set the activation here, but it requires adding the activations types from heaan
            )

        def get_created_he_context(self):
            return self.he_context

        def predict(self, inputs):
            predictions = self.heaan_lr.predict(inputs.data_set)
            return TransformerLogisticRegressionEncryptedData(self.heaan_context, predictions)

        def fit(self, inputs):
            self.heaan_lr.fit(inputs.data_set)

        def save_to_buffer(self):
            raise Exception('TransformerLogisticRegression.save_to_buffer - not implemented. Use save_to_file.')

        def load_from_buffer(self, buff):
            raise Exception('TransformerLogisticRegression.load_from_buffer - not implemented. Use load_from_file.')

        def save_to_file(self, path):
            self.heaan_lr.save(path)

        def load_from_file(self, path):
            self.heaan_lr = heaan_sdk.LogisticRegression.from_path(self.heaan_context, path)

        def create_model_io_encoder(self):
            return TransformerLogisticRegressionIoEncoder(self.heaan_context, self.heaan_lr)

        def load_encrypted_data(self, buf):
            raise Exception('TransformerLogisticRegression.load_encrypted_data - not implemented. Use load_encrypted_data_from_file.')

        def load_encrypted_data_from_file(self, file_path):
            res = TransformerLogisticRegressionEncryptedData(self.heaan_context)
            res.load_from_file(file_path)
            return res
