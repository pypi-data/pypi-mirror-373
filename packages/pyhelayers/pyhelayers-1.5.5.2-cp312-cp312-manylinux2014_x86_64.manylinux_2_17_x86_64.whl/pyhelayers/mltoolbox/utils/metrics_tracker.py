import pandas as pd


class MetricsTracker:
    def __init__(self, *metrics, mode, writer=None):
        self.metrics = metrics
        self.mode = mode
        self.writer = writer
        self._df = pd.DataFrame(index=metrics, columns=['total', 'num'])
        self.reset()

    def get_avg(self, key):
        return self._df.total[key] / self._df.num[key]

    def reset(self):
        for col in self._df.columns:
            self._df[col].values[:] = 0

    def update(self, key, value, writer_step=1):
        if self.writer is not None:
            self.writer.add_scalar(self.mode + "/" + key, value, writer_step)

        self._df.total[key] += value
        self._df.num[key] += 1

    def update_all(self, values_dict, writer_step=1):
        for key in values_dict:
            self.update(key, values_dict[key], writer_step)

    def print_all(self):
        s = ''
        d = dict(self._df.avg)
        for key in d:
            s += "{} {:.4f}\t".format(key, d[key])

        return s


    def __range_lst_to_global(self,lst):
        """finds global min ang global max over all activations ranges
        """
        global_min = 0
        global_max = 0
        for (mi, mx) in lst:
            global_min = min(global_min, mi)
            global_max = max(global_max, mx)
        return global_min, global_max

    # reports ranges to clearml
    def report_ranges(self, epoch, ranges):
        """reports ranges to clearml
        Args:
            - epoch (int): current epoch number
            - ranges (list<float>): list of maximum and minimum values. The list is ordered - first 2 numbers represent
            ranges of first layer, and so on.
        """
        if (not ranges) or (not self.writer): return
        global_min, global_max = self.__range_lst_to_global(ranges)
        # Global Range Graphs
        self.writer.add_scalar(f'Global Ranges/{self.mode}-min', global_min, epoch)
        self.writer.add_scalar(f'Global Ranges/{self.mode}-max', global_max, epoch)

        # Range Per Layer Graphs
        for i, n in enumerate(ranges):
            min_val, max_val = n
            self.writer.add_scalar(f'Range per Layer-{self.mode}/-min-{str(i)}', min_val, epoch)
            self.writer.add_scalar(f'Range per Layer-{self.mode}/-max-{str(i)}', max_val, epoch)

