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

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import namedtuple
from scipy.stats import hmean
from pyhelayers.mltoolbox.he_dl_lib.my_logger import get_logger
from sklearn.metrics import confusion_matrix
logger = get_logger()
def make_confusion_matrix(cf,
                          val_metrics,
                          epoch,
                          categories='auto',
                          group_names=None,
                          count=True,
                          percent=True,
                          cbar=True,
                          xyticks=True,
                          xyplotlabels=True,
                          sum_stats=True,
                          figsize=None,
                          cmap='Blues',
                          title=False):
    '''
    This function will make a pretty plot of an sklearn Confusion Matrix cm using a Seaborn heatmap visualization.
    Arguments
    ---------
    cf:            confusion matrix to be passed in
    group_names:   List of strings that represent the labels row by row to be shown in each square.
    categories:    List of strings containing the categories to be displayed on the x,y axis. Default is 'auto'
    count:         If True, show the raw number in the confusion matrix. Default is True.
    normalize:     If True, show the proportions for each category. Default is True.
    cbar:          If True, show the color bar. The cbar values are based off the values in the confusion matrix.
                   Default is True.
    xyticks:       If True, show x and y ticks. Default is True.
    xyplotlabels:  If True, show 'True Label' and 'Predicted Label' on the figure. Default is True.
    sum_stats:     If True, display summary statistics below the figure. Default is True.
    figsize:       Tuple representing the figure size. Default will be the matplotlib rcParams value.
    cmap:          Colormap of the values displayed from matplotlib.pyplot.cm. Default is 'Blues'
                   See http://matplotlib.org/examples/color/colormaps_reference.html

    title:         Title for the heatmap. Default is None.
    '''

    # CODE TO GENERATE TEXT INSIDE EACH SQUARE
    blanks = ['' for i in range(cf.size)]

    if group_names and len(group_names) == cf.size:
        group_labels = ["{}".format(value) for value in group_names]
    else:
        group_labels = blanks

    if count:
        group_counts = ["{0:0.0f}\n".format(value) for value in cf.flatten()]
    else:
        group_counts = blanks

    if percent:
        accuracyMetrics = get_accuracy_metrics(cf)

        percentages = []
        for i, (p, r) in enumerate(zip(accuracyMetrics.precision_mat, accuracyMetrics.recall_mat)):
            for j, (pj, rj) in enumerate(zip(p, r)):
                if i == j:
                    percentages.append(f"P: {pj:.2}\n(R: {rj:.2})\n (F1: {accuracyMetrics.f1_list[j]:.2})")
                else:
                    percentages.append(f"{pj:.2}\n({rj:.2})\n-")
        # precision_percentages = ["P: {0:.2}\n".format(value) for value in (cf / np.sum(cf, axis=0)).flatten()]
        # recall_percentages = ["(R: {0:.2})\n".format(value) for value in (cf / np.sum(cf, axis=1)).flatten()]
    else:
        percentages = blanks

    box_labels = [f"{v1}{v2}{v3}".strip() for v1, v2, v3 in zip(group_labels, group_counts, percentages)]
                                                                        # precision_percentages, recall_percentages)]
    box_labels = np.asarray(box_labels).reshape(cf.shape[0], cf.shape[1])

    # CODE TO GENERATE SUMMARY STATISTICS & TEXT FOR SUMMARY STATS
    if sum_stats:
        # if it is a binary confusion matrix, show some more stats
        if len(cf) == 2:
            # Metrics for Binary Confusion Matrices
            precision = accuracyMetrics.precision_list[1]
            recall =accuracyMetrics.recall_list[1]
            f1_score = accuracyMetrics.f1_list[1]
            stats_text = "\n\nAccuracy={:0.3f}\nPrecision={:0.3f}\nRecall={:0.3f}\nF1 Score={:0.3f}".format(
                accuracyMetrics.accuracy, precision, recall, f1_score)
            # FIXME: why f1_score is used for harmonic_f1? it is confusing and not consistent
            harmonic_f1 = f1_score
        else:
            harmonic_f1 = accuracyMetrics.harmonic_f1
            harmonic_f1 = float(f"{harmonic_f1:.2}")
            stats_text = ""
    else:
        stats_text = ""
        harmonic_f1 = 0

    # SET FIGURE PARAMETERS ACCORDING TO OTHER ARGUMENTS
    if figsize == None:
        # Get default figure size if not set
        figsize = plt.rcParams.get('figure.figsize')

    if xyticks == False:
        # Do not show categories if xyticks is False
        categories = False
    try:
        # MAKE THE HEATMAP VISUALIZATION
        fig = plt.figure(figsize=figsize)

        ax = sns.heatmap((cf / np.sum(cf, axis=0)), annot=box_labels, fmt="", cmap=cmap, cbar=cbar, xticklabels=categories,
                    yticklabels=categories, annot_kws={"size": 15})
        ax.collections[0].colorbar.ax.annotate(f'---H_F1:{harmonic_f1:.2}', (0.9, harmonic_f1), color='red', fontsize=12, fontweight='bold')

        if xyplotlabels:
            plt.ylabel('True label')
            plt.xlabel(f'Predicted label\n')
        else:
            plt.xlabel(stats_text)

        if title:
            plt.title(stats_text)

        if val_metrics:
            val_metrics.update_figure('confusion_matrix', fig, writer_step=epoch - 1)
        else:
            plt.show()
        # return fig
    except Exception as e:
        print("Failed to create confusion matrix",e)


def make_1d_labels(y):
    if len(y.shape) ==2:
        y = np.argmax(y, axis=1)
        print("shape y=", y.shape)
    elif len(y.shape) > 2:
        raise Exception(f"Wrong shape of y labels {y.shape} ")
    return y

def comp_confusion_matrix(y_true, y_pred):
    y_true_1d = make_1d_labels(y_true)
    y_pred_1d = make_1d_labels(y_pred)

    cfm = confusion_matrix(y_true_1d, y_pred_1d)
    return cfm


def format_acc_results(accuracyMetrics):
    acc_dict = accuracyMetrics._asdict()
    print("Accuracy results:")
    for key, value in acc_dict.items():
        if key.endswith("mat"):
            continue
        print("\t"+key+":", np.round(value,3))

def get_accuracy_metrics(cf):
    eps = 1e-9
    precision_mat = cf / np.maximum(np.sum(cf, axis=0),eps)
    recall_mat = (cf.T / np.maximum(np.sum(cf, axis=1),eps)).T
    precision_list = [precision_mat[i, i] for i in range(len(cf))]
    recall_list = [recall_mat[i, i] for i in range(len(cf))]
    f1_list = [2.0 * p_i * r_i / (p_i + r_i) if p_i + r_i > 0 else 0.0
               for p_i, r_i in zip(precision_list, recall_list)]
    accuracy = np.trace(cf) / float(np.sum(cf))
    harmonic_f1 = hmean(f1_list)
    total_samples = np.sum(cf)

    AccuracyMetrics = namedtuple("AccuracyMetrics",
                                 ["total_samples","f1_list","precision_list",
                                  "recall_list","accuracy",
                                  "harmonic_f1", "precision_mat",
                                  "recall_mat",])

    accuracyMetrics= AccuracyMetrics(total_samples=total_samples, f1_list=f1_list,
                    precision_mat=precision_mat,
                    recall_mat=recall_mat,
                    precision_list=precision_list,
                    recall_list=recall_list,
                    accuracy=accuracy,
                    harmonic_f1 = harmonic_f1)

    return accuracyMetrics


if __name__ == '__main__':

    cf = np.array([[553, 37, 4], [39, 839, 7], [31, 4, 48]])
    print(cf)
    metrics = get_accuracy_metrics(cf)
    print(metrics)

    make_confusion_matrix(cf, epoch=0, val_metrics=None, categories=["pneumonia", "negative", "covid19"])