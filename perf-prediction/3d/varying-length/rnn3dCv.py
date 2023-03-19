import os
import sys
import random
import numpy as np


def main():
    gpuArch = ['V100', 'A100']

    features = []
    durations = []
    for gpuId in range(0, 1):
        paradata = np.load('../../training-set/vary-split/parafiles/{}_3d.npz'.format(gpuArch[gpuId]))
        paras = paradata['paras']
        features = paradata['features']
        durations = paradata['durations']
        
        print(paras.shape)
        print(features.shape)
        print(durations.shape)

        max_features = np.zeros((features.shape[1]), dtype='float32')
        max_paras = np.zeros((paras.shape[1]), dtype='float32')

        for i in range(0, features.shape[1]):
            max_features[i] = features[:,i].max()
        for i in range(0, paras.shape[1]):
            max_paras[i] = paras[:,i].max()
        
        num_features = features.shape[1]
        num_paras = paras.shape[1]

        tnslist = []
        for i in range(0, 5):
            listfile = np.load('../rand-num/{}_rand_{}.npz'.format(gpuArch[gpuId], i))
            tnslist.append(listfile['sublist'])
        print(tnslist)
        
        for cvindex in range(0, 5):
            testlist = tnslist[cvindex]
            tmptrain = []
            for i in range(0, 5):
                if i == cvindex:
                    continue
                tmptrain.append(i)
            trainlist = np.concatenate((tnslist[tmptrain[0]], tnslist[tmptrain[1]], tnslist[tmptrain[2]], tnslist[tmptrain[3]]), axis=0)

            print(testlist.shape[0])
            print(trainlist.shape[0])

            train_features = np.zeros((trainlist.shape[0], num_features), dtype='float32')
            test_features = np.zeros((testlist.shape[0], num_features), dtype='float32')
            train_paras = np.zeros((trainlist.shape[0], num_paras), dtype='float32')
            test_paras = np.zeros((testlist.shape[0], num_paras), dtype='float32')
            train_durations = np.zeros((trainlist.shape[0]), dtype='float32')
            test_durations = np.zeros((testlist.shape[0]), dtype='float32')

            for i in range(0, len(trainlist)):
                train_features[i] = features[trainlist[i]]
                train_paras[i] = paras[trainlist[i]]
                train_durations[i] = durations[trainlist[i]]

            for i in range(0, len(testlist)):
                test_features[i] = features[testlist[i]]
                test_paras[i] = paras[testlist[i]]
                test_durations[i] = durations[testlist[i]]
            
            print(test_paras)
            print(test_features)
            print(test_durations)

            np.savez('data/{}_cv{}_train.npz'.format(gpuArch[gpuId], cvindex), features=train_features, paras=train_paras, durations=train_durations)
            np.savez('data/{}_cv{}_test.npz'.format(gpuArch[gpuId], cvindex), features=test_features, paras=test_paras, durations=test_durations)
            

if __name__=='__main__':
    main()                 
