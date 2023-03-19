import sys
import sklearn
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from mlp2dDataset import DataSet

tf.enable_eager_execution()


## read numpy data
def load_data(filename):
    try:
        data = np.load(filename)
        ds = DataSet(data['features'], data['durations'])
    except:
        print("Can not find data file")
        ds = None
    finally:
        return ds


class mlpRegressor(object):
    def __init__(self, num_layers, hidden_dim, train_data, test_data, model_data, result_data):
        super(mlpRegressor, self).__init__()
        self.num_layers = num_layers
        self.hidden_dim = hidden_dim
        self.model_data = model_data
        self.result_data = result_data
        self.trainset = load_data(train_data)
        self.testset = load_data(test_data)
        self.input_shape = self.testset.features[0].shape

        self.model = Sequential()
        self.model.add(Dense(self.hidden_dim, input_shape=self.input_shape, activation='relu'))
        for i in range(0, self.num_layers-2):
            self.model.add(Dense(self.hidden_dim, activation='relu'))
        self.model.add(Dense(1, activation='linear'))

    def training(self):
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.0005)
        print(self.model.summary())
        self.model.compile(loss='mean_absolute_percentage_error', optimizer=optimizer, metrics=['mean_absolute_error', 'mean_squared_error', 'mean_absolute_percentage_error'])
        self.model.fit(self.trainset.features, self.trainset.durations, epochs=100, batch_size=256, validation_split=0.2, verbose=2)
        loss, mae, mse, mape = self.model.evaluate(self.testset.features, self.testset.durations, verbose=2)
        print("loss: {} mae: {} mse: {} mape: {}".format(loss, mae, mse, mape))
        self.model.save(self.model_data)

    def testing(self):
        saver = load_model(self.model_data)
        pred_durations = saver.predict(self.testset.features)
        print(pred_durations)
        scores = np.zeros((2, pred_durations.shape[0]), dtype='float32')
        for i in range(pred_durations.shape[0]):
            scores[0][i] = self.testset.durations[i]
            scores[1][i] = pred_durations[i]
        np.savez('{}'.format(self.result_data), scores=scores)


def main():
    if len(sys.argv) < 7:
        print("usage: {} flag{train, test} {num of layers} {hidden dimension} {train data} {test data} {model data} {result data}")
        exit()

    FLAG = sys.argv[1].lower()
    num_layers = int(sys.argv[2])
    hidden_dim = int(sys.argv[3])
    train_data = sys.argv[4]
    test_data = sys.argv[5]
    model_data = sys.argv[6]
    result_data = sys.argv[7]

    print('num_layers: {} hidden_dim: {}'.format(num_layers, hidden_dim))
    print(train_data)
    print(test_data)
    print(model_data)
    print(result_data)

    model = mlpRegressor(num_layers, hidden_dim, train_data, test_data, model_data, result_data)
    if FLAG == 'train':
        model.training()
    elif FLAG == 'test':
        model.testing()


if __name__=='__main__':
    main()
