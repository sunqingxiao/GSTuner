import os
import sys
import random
import numpy as np

def main():
    gpuArch = ['V100', 'A100']
    for gpuId in range(1, 2):
        paras = np.load('../../training-set/zero-padding/parafiles/{}_3d.npz'.format(gpuArch[gpuId]))['paras']
        datasize = paras.shape[0]

        tnslist = list(range(0, datasize))

        print(len(tnslist))

        # 5-fold cross validation
        for cvindex in range(0, 4):
            testlist = random.sample(tnslist, int(len(tnslist) / (5-cvindex)))
            for i in range(0, len(testlist)):
                tnslist.remove(testlist[i])
            np.savez('{}_rand_{}.npz'.format(gpuArch[gpuId], cvindex), sublist=testlist)
            print((len(testlist)))

        print(len(tnslist))
        np.savez('{}_rand_4.npz'.format(gpuArch[gpuId]), sublist=testlist)


if __name__=='__main__':
    main()                 
