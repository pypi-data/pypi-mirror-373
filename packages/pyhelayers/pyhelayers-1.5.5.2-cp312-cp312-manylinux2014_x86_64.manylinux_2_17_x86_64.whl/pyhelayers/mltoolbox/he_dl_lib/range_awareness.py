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
import math
from pyhelayers.mltoolbox.utils.util import is_cuda_available
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger

logger = get_logger()

def range_awareness_loss(act):
    """Calculates the total range awareness loss of all activations
       Params:
              - act (list<Range_aware_act>): The list of activations to calculate for
       Returns:
              - torch.tensor: total loss
    """
    loss = torch.tensor([0.0], requires_grad=True)
    if is_cuda_available():
        loss=loss.cuda()

    for a in act:
        loss=loss+sum(a[1].loss)
        if math.isnan(sum(a[1].loss)):
            logger.warning(f'nan in loss {a[0]}')
        # loss=max(loss, a[1].loss)

    logger.debug(f'range_awareness_loss={loss}')
    logger.debug(len(act))

    return loss


