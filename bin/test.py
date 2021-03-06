import sys
import pickle
import numpy as np
from numpy.random import *
from keras.preprocessing.image import load_img, img_to_array
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.utils.np_utils import to_categorical

seed(100)  # fixed seed


def make_data():
    '''
    make_data for multi-label classification.
    Input is N (1<=N<=100)
    output is 100-dimension vector: each value corresponds to the existance of the prime factor of N.
    For example:
    Input: 12
    Output: [1,1,1,1,0,1,0,0,0,0,0,1,0,0,0...0]  # 1,2,3,4,6,12.
    '''
    def get_factors(N):
        return [n for n in range(1, 101) if N % n == 0]  # factors_label

    N_list = randint(1, 101, 1000)  # from 1 to 100 * 1000
    factors_list = [np.array(get_factors(N)) for N in N_list]  # make_matrix.
    return N_list, factors_list


def get_labels(output_factors_vector):
    '''
    return numbers of the prob >= 0.5 as true_labels
    For example:
    Input: np [0.2, 0.3, 0,4, 0,8]
    Output: [3]
    ??? Is there functions pre-instaled.?
    '''
    output = []
    for i, each in enumerate(output_factors_vector):
        if each >= 0.5:
            output.append(i)  # Check
    return output


def to_categorical_multi(numpy_labels_list, size):
    '''
    [np.array([1, 3, 9]), np.array([1])], 10 -> np.array([0, 1, 0, 1, 0, 0, 0, 0, 1], [0, 1, 0, 0, 0, 0, 0, 0, 0])
    to_categorical is for one-hot label.
    Caution: Not considering error.
    '''
    multi_label_matrix = np.zeros(size)
    for labels in numpy_labels_list:
        array = to_categorical(labels, size)  # ([one_hot], [one_hot], [one_hot])
        multi_label_vector = np.zeros(size)
        for vector in array:
            multi_label_vector += vector
        multi_label_matrix = np.vstack((multi_label_matrix, multi_label_vector))
    return multi_label_matrix[1:]


def calc_f(gold_labels_list, output_labels_list):
    '''
    Input = [[1, 3], [4]], [[1, 3], [3]]
    gold_count, output_count = 3, 3
    cross_count = 2
    Output: f-measure: -> 2/3
    ??? Is there functions pre-instaled.?
    '''
    gold_count = sum([len(set(gold_labels)) for gold_labels in gold_labels_list])  # list -> set
    output_count = sum([len(set(output_labels)) for output_labels in output_labels_list])
    cross_count = 0
    for gold_labels, output_labels in zip(gold_labels_list, output_labels_list):
        cross_count += len(set(gold_labels).intersection(set(output_labels)))  # product set
    precision = cross_count / output_count
    recall = cross_count / gold_count
    f_measure = 2 / (1 / precision + 1 / recall)
    return precision, recall, f_measure

if __name__ == '__main__':

    N_list, factors_list = make_data()
    train_N_list, test_N_list = N_list[:800], N_list[800:]  # data split
    train_factors_list, test_factors_list = factors_list[:800], factors_list[800:]
    train_N_matrix = to_categorical(train_N_list, 101)  # sparss
    train_factors_matrix = to_categorical_multi(train_factors_list, 101)
    test_N_matrix = to_categorical(test_N_list, 101)

    model = Sequential()
    model.add(Dense(output_dim=100, input_dim=101))
    model.add(Dense(output_dim=101))
    model.add(Activation("sigmoid"))
    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
    # model.compile(loss='mean_squared_error', optimizer='sgd', metrics=['accuracy']) # Not Working.
    model.fit(train_N_matrix, train_factors_matrix, nb_epoch=1000, batch_size=16)  # Train
    print('finish')
    output_factors_matrix = model.predict_proba(test_N_matrix, batch_size=100)

    output_factors_list = [get_labels(output_factors_vector)
                           for output_factors_vector in output_factors_matrix]

    for output_factors, N in zip(output_factors_list, test_N_list):
        print(N, output_factors)

    print(calc_f(test_factors_list, output_factors_list))
