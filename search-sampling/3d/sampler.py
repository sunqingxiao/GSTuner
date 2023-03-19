import numpy as np
import random
import sys
import time

def load_data(arch, stencil, numoc, cv):
    paras, real, pred = [], [], []
    for i in range(numoc):
        try:
            ocdata = np.load('result/{}_{}_oc{}_cv{}_scores.npz'.format(arch, stencil, i, cv))
        except:
            paras.append(np.array([]))   
            real.append(np.array([]))
            pred.append(np.array([]))
        else:
            paras.append(ocdata['paras'])
            real.append(ocdata['scores'][0])
            pred.append(ocdata['scores'][1])

    return paras, real, pred


def reset_ratio(iter_ratio, opt_oc, smpratio, lower, adjust):
    sumratio = 0.0
    for i in range(len(iter_ratio)):
        if i == opt_oc or iter_ratio[i] == 0.0:
            continue
        if iter_ratio[i] - adjust >= lower:   # assume lower >= adjust
            iter_ratio[i] -= adjust
        sumratio += iter_ratio[i]
    iter_ratio[opt_oc] = smpratio - sumratio  # total ratio remains the same
    
    return iter_ratio


def get_opt(pred, iter_list):
    oc_best = np.full((len(iter_list)), 10000.0, dtype='float32')
    for i in range(len(iter_list)):
        if len(iter_list[i]) == 0:
            continue
        oc_best[i] = pred[i][iter_list[i]].min()
    opt_oc = np.argmin(oc_best)

    return opt_oc


def sample_data(pred, numoc, smpratio, ratio, lower, adjust):
    oc_setting = np.zeros((numoc), dtype='int32')
    iter_ratio = np.zeros((numoc), dtype='float32')
    oc_idle = np.zeros((numoc), dtype='int32')

    oc_list, sample_list = [], []
    for i in range(numoc): # initial sampling
        oc_setting[i] = pred[i].shape[0]
        if oc_setting[i] == 0:
            oc_idle[i] = 1
        sample_list.append([])
        oc_list.append(list(range(oc_setting[i])))

    num_setting, num_sampled = np.sum(oc_setting), 0
    iter_ratio = smpratio * (oc_setting / num_setting)

    while num_sampled < num_setting * ratio:
        iter_list, iter_sampled = [], 0
        for ocId in range(numoc):
            tmplist, tmpsmp = [], int(num_setting * iter_ratio[ocId] + 1)
            if tmpsmp >= len(oc_list[ocId]):
                tmplist = random.sample(oc_list[ocId], len(oc_list[ocId]))
                iter_ratio[ocId] = 0.0
            else:
                tmplist = random.sample(oc_list[ocId], tmpsmp)
            iter_list.append(tmplist)
            sample_list[ocId].append(tmplist)
            iter_sampled += len(tmplist)
            for i in range(len(tmplist)):
                oc_list[ocId].remove(tmplist[i])

        opt_oc = get_opt(pred, iter_list)
        iter_ratio = reset_ratio(iter_ratio, opt_oc, smpratio, lower, adjust)
        num_sampled += iter_sampled
    
    for ocId in range(numoc): # list flattening
        if oc_idle[ocId]:
            sample_list[ocId] = []
        else:
            sample_list[ocId] = list(eval(str(sample_list[ocId]).replace('[', '').replace(']', '').replace(' ,', '')))

    return sample_list


def main():
    if len(sys.argv) < 4:
        print("usage: {} arch stencil cv")
        exit()

    arch, stencil, cv, numoc = sys.argv[1], sys.argv[2], int(sys.argv[3]), 8
    paras, real, pred = load_data(arch, stencil, numoc, cv)
    # 0.4 0.04 0.001 0.001 -> 0.1 *** 0.8 0.08 0.002 0.002
    ratio, smpratio, lower, adjust = 0.4, 0.04, 0.001, 0.001
    start_time = time.time()
    sample_list = sample_data(pred, numoc, smpratio, ratio, lower, adjust)
    print('{} {}'.format(stencil, (time.time()-start_time) * 1000))

    for ocId in range(numoc):
        smpparas = paras[ocId][sample_list[ocId]]
        smpdurations = real[ocId][sample_list[ocId]]
        np.savez('searched/{}_{}_oc{}_sampled.npz'.format(arch, stencil, ocId), paras=smpparas, durations=smpdurations)


if __name__=='__main__':
    main()
