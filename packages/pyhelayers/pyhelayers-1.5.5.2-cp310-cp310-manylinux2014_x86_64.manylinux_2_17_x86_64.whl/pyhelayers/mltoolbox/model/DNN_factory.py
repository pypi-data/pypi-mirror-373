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

from typing import Callable
from pyhelayers.mltoolbox.model.nn_module import nn_module
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger

class DNNFactory:

    registry = {}

    @classmethod
    def register(self, name: str) -> Callable:
        logger = get_logger()

        def inner_wrapper(wrapped_class: nn_module) -> Callable:
            if name in self.registry:
                logger.warning('Model %s already exists. Will replace it', name)
            self.registry[name] = wrapped_class
            return wrapped_class

        return inner_wrapper


    @classmethod
    def get_model(self, name: str, **kwargs):
        """ Factory command to create the model.
        This method gets the appropriate model class from the registry
        and creates an instance of it, while passing in the parameters
        given in ``kwargs``.
        Args:
            name (str): The name of the model to create.

        Raises:
            NameError: "Model doesn't exist"

        Returns:
            An instance of the model that is created.
        """
        logger = get_logger()
        logger.debug(self.registry)
        if name not in self.registry:
            logger.error('Model %s does not exist in the registry', name)
            raise NameError(f"Model name: {name} doesn't exist.")

        model_class = self.registry[name]
        model = model_class(**kwargs)
        return model

    @classmethod
    def get_model_by_name(self, args):
        """Returns one of the registered models, by the user configuration

        Args:
            args (Arguments): user arguments

        Returns:
            nn.Module: The required model
        """
        return self.get_model(args.model, **vars(args))

    @classmethod
    def print_supported_models(self):
        """
        A convenience method that prints all the registered models currently available
        """
        print(f'The supported models values are: {self.registry.keys()}')

