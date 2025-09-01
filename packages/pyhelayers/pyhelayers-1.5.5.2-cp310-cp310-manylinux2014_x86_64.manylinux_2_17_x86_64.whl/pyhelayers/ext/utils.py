#
# OCO Source Materials
# 5737-A56
# © Copyright IBM Corp. 2017
#
# The source code for this program is not published or other-wise divested
# of its trade secrets, irrespective of what has been deposited with the
# U.S. Copyright Office.
#

import os
import time


def extract_batch(x_test, y_test, batch_size, batch_num):
    num_samples = x_test.shape[0]
    num_lebels = y_test.shape[0]

    # assert same size
    assert (num_samples == num_lebels)

    # calc start and end index
    start_index = batch_num * batch_size
    if start_index >= num_samples:
        raise RuntimeError('Not enough samples for batch number ' +
                           str(batch_num) + ' when batch size is ' + str(batch_size))
    end_index = min(start_index + batch_size, num_samples)

    batch_x = x_test.take(indices=range(start_index, end_index), axis=0)
    batch_y = y_test.take(indices=range(start_index, end_index), axis=0)

    return (batch_x, batch_y)


start_time = None


def start_timer():
    global start_time
    start_time = time.perf_counter()


def report_duration(op_name, duration):
    print("Duration of " + op_name + ":", "{:.3f}".format(duration), "(s)")


def end_timer(op_name, silent=False):
    global start_time
    if start_time is None:
        raise RuntimeError('Timer was not started')

    duration = time.perf_counter() - start_time
    start_time = None

    if not silent:
        report_duration(op_name, duration)

    return duration
