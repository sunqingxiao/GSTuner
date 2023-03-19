import collections
import numpy as np

DataSets = collections.namedtuple('DataSets', ['train', 'test'])

class DataSet(object):
    def __init__(self, paras, features, durations):
        assert paras.shape[0] == durations.shape[0], (
            'paras.shape: %s durations.shape %s' % (paras.shape, durations.shape)
        )
        assert features.shape[0] == durations.shape[0], (
            'features.shape: %s durations.shape %s' % (features.shape, durations.shape)
        )
        self._num_examples = features.shape[0]
        
        self._paras = paras
        self._features = features
        self._durations = durations
        self._epochs_completed = 0
        self._index_in_epoch = 0

    @property
    def paras(self):
        return self._paras

    @property
    def features(self):
        return self._features

    @property
    def durations(self):
        return self._durations

    @property
    def num_examples(self):
        return self._num_examples

    @property
    def epochs_completed(self):
        return self._epochs_completed

    def next_batch(self, batch_size, shuffle=True):
        start = self._index_in_epoch
        # shuffle for the first epoch
        if self._epochs_completed == 0 and start == 0 and shuffle:
            perm0 = np.arange(self._num_examples)
            np.random.shuffle(perm0)
            self._paras = self.paras[perm0]
            self._features = self.features[perm0]
            self._durations = self.durations[perm0]
        # next epoch
        if start + batch_size > self._num_examples:
            # finished epoch
            self._epochs_completed += 1
            # rest examples in this epoch
            rest_num_examples = self._num_examples - start
            paras_rest_part = self._paras[start:self._num_examples]
            features_rest_part = self._features[start:self._num_examples]
            durations_rest_part = self._durations[start:self._num_examples]
            # shuffle the data
            if shuffle:
                perm = np.arange(self._num_examples)
                np.random.shuffle(perm)
                self._paras = self.paras[perm]
                self._features = self.features[perm]
                self._durations = self.durations[perm]
            # start next epoch
            start = 0
            self._index_in_epoch = batch_size - rest_num_examples
            end = self._index_in_epoch
            paras_new_part = self._paras[start:end]
            features_new_part = self._features[start:end]
            durations_new_part = self._durations[start:end]
            return np.concatenate((paras_rest_part, paras_new_part), axis=0), np.concatenate((features_rest_part, features_new_part), axis=0), np.concatenate((durations_rest_part, durations_new_part), axis=0)
        else:
            self._index_in_epoch += batch_size
            end = self._index_in_epoch
            return self._paras[start:end], self._features[start:end], self._durations[start:end]
