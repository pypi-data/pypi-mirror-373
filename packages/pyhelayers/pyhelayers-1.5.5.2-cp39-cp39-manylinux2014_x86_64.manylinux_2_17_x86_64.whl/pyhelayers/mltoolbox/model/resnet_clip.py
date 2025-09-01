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
import os
import clip
from tqdm import tqdm
import json
from pyhelayers.mltoolbox.utils.util import is_cuda_available
from pyhelayers.mltoolbox.model.nn_module import nn_module
from pyhelayers.mltoolbox.model.DNN_factory import DNNFactory
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
import importlib

logger = get_logger()


@DNNFactory.register('CLIPresnet50')
class ClipResnet50_FHE(nn_module):
    INPUT_SIZE = (3, 224, 224)

    def __init__(self, dataset_name, save_dir, pooling_type='avg', add_bn=False, **kwargs):
        '''
        Args:
            pooling_type: max or avg
            add_bn: whether or not to add batch normalization in specific locations
            dataset_name: dataset name
            save_dir: parent directory for output data
        '''
        save_dir = save_dir.split("/")
        save_dir = '/'.join(save_dir[:-1])

        logger.debug(f"save dir: {save_dir}, dataset_name: {dataset_name}")

        super().__init__()
        self.models_path = os.path.join(save_dir, "clip_models")
        clip_model, self.transform = clip.load('RN50', device="cpu", download_root=self.models_path)
        self.cnn = clip_model.visual
        self.logit_scale = clip_model.logit_scale.exp().detach()

        try:
            json_data = self.__get_template_json(dataset_name)
            classnames = json_data["classes"]
            templates = json_data["templates"]

            self.classes_encoded = self.encode_classes(classnames, templates, clip_model, dataset_name)

            self.make_fhe_friendly(False, pooling_type)
        except:
            return

    def __get_template_json(self, dataset_name):
        package_name = "pyhelayers.mltoolbox.data_loader"
        module_name = os.path.join("class_templates", f"{dataset_name.lower()}_classes_templates.json")
        template_file_name = os.path.join(os.path.dirname(importlib.import_module(package_name).__file__), module_name)

        if not os.path.exists(template_file_name):
            logger.error(f"The dataset {dataset_name} can't be used with CLIPresnet50 - the templates file {template_file_name} is missing. Please add the templates file and try again.")
            raise Exception("template file is missing") 
            
        with open(template_file_name, "r") as f:
            data = f.read()
            
        json_data = json.loads(data)
        return json_data

    def encode_classes(self, classnames, templates, clip_model, dataset_name):
        with torch.no_grad():
            zeroshot_weights_path = os.path.join(self.models_path, f"zeroshot_weights/{dataset_name}/class_weights.pt")
            if os.path.exists(zeroshot_weights_path):
                zeroshot_weights = torch.load(zeroshot_weights_path, map_location=torch.device('cpu'))
                logger.info("Loaded encoded textual labels matrix")
            else:
                logger.info(f"Creating class embeddings for the {dataset_name} dataset")
                zeroshot_weights = []
                for classname in tqdm(classnames):
                    texts = [template.format(classname) for template in templates]  # format with class
                    texts = clip.tokenize(texts).cpu()  # tokenize
                    class_embeddings = clip_model.encode_text(texts)  # embed with text encoder
                    class_embeddings /= class_embeddings.norm(dim=-1, keepdim=True)
                    class_embedding = class_embeddings.mean(dim=0)
                    class_embedding /= class_embedding.norm()
                    zeroshot_weights.append(class_embedding)
                zeroshot_weights = torch.stack(zeroshot_weights, dim=1)  # .cuda()

                weights_dir = os.path.dirname(zeroshot_weights_path)
                if not os.path.exists(weights_dir):
                    os.makedirs(weights_dir)
                torch.save(zeroshot_weights, zeroshot_weights_path)
                print(f"{dataset_name} class templates saved.")

            print(f"prompts_shape: {zeroshot_weights.shape}")

        return zeroshot_weights

    def classifier(self, image_features):
        # normalized features
        image_features = image_features / image_features.norm(dim=1, keepdim=True)

        # cosine similarity as logits
        device = image_features.device

        cosine_sim_image_text = self.logit_scale.to(device) * image_features @ self.classes_encoded.to(device)

        return cosine_sim_image_text

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not hasattr(self, "classes_encoded"):
            raise AssertionError (f"The model is not ready and cannot be ran.")
        
        super().forward(x)
        x = self.cnn(x)
        x = self.classifier(x)
        return x

    def get_obj_device(self, obj):
        return obj.device
