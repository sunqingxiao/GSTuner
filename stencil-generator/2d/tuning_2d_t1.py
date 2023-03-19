import itertools
from functools import reduce
import os
import random
import sys
import pickle
import datetime
import time
maxThreadsPerBlockLg2 = 10 # 1024
maxShmPerBlockLg2 = 15 # 32K
order = 4

def FilterParams(paraVector):
    blockSize, streaming, streamBlock, s_unroll, mergeFactor, blockMerge, retime, prefetch = paraVector

    ## max threads per block limitation
    #if not streaming and blockSize[0] * blockSize[1] > 1024:
    #    return False
    
    # for combination 0
    #if not streaming and mergeFactor == (1, 1) and blockMerge == True:
    #    return False

    #if not streaming and (streamBlock != 8 or s_unroll != 1 or retime or prefetch):
    #    return False

    # shared memoty constrian
    if streaming and (blockSize * mergeFactor[0] + 2 * order) * 8 >= 2 ** maxShmPerBlockLg2:
        return False

    if streaming and mergeFactor[1] != 1:
        return False

    if streamBlock < s_unroll:
        return False

    if blockSize * mergeFactor[0] <= order * 2:
        return False

    #if blockSize[1] * mergeFactor[1] <= order * 2:
    #    return False


    return True


def cfgToCommandLine(paraVector):
    
    blockSize, streaming, streamBlock, s_unroll, mergeFactor, blockMerge, retime, prefetch = paraVector
    cmd = ""

    if not streaming:
        #cmd += " --blockdim x={0},y={1}".format(blockSize[0], blockSize[1])
        cmd += " --unroll i={0},j={1}".format(mergeFactor[0], mergeFactor[1])
        if blockMerge:
            cmd += " --blocked-loads"
    else:
        cmd += " --blockdim x={0},y={1}".format(blockSize, streamBlock)

        cmd += " --unroll i={0},j={1}".format(mergeFactor[0], s_unroll)

        cmd += " --stream j"

        if blockMerge:
            cmd += " --blocked-loads"
        if retime:
            cmd += " --retime"
        if prefetch:
            cmd += " --prefetch"

    return cmd
    

def cfgToString(paraVector):
    blockSize, streaming, streamBlock, s_unroll, mergeFactor, blockMerge, retime, prefetch = paraVector
    cmd = ""

    if not streaming:
        #cmd += "bx{0}y{1}".format(blockSize[0], blockSize[1])
        if blockMerge:
            cmd += "bm"
        else:
            cmd += "cm"
        cmd += "x{0}y{1}".format(mergeFactor[0], mergeFactor[1])
    else:
        cmd += "bx{0}sb{1}".format(blockSize, streamBlock)

        if blockMerge:
            cmd += "bm"
        else:
            cmd += "cm"
        cmd += "x{0}".format(mergeFactor[0])
        cmd += "u{0}".format(s_unroll)

        if retime:
            cmd += "r"
        if prefetch:
            cmd += "p"

    return cmd
    

def writePara(paraVector, i):
    blockSize, streaming, streamBlock, s_unroll, mergeFactor, blockMerge, retime, prefetch = paraVector
    csv = open('duration.csv', 'a')
    csv.write(str(i) + "," + cfgToString(paraVector))
    csv.write(",{0},".format(blockSize))
    if not streaming:
    #    csv.write("{0},0,".format(blockSize[1]))
    #    csv.write("n/a,n/a,")
    #    csv.write("{0},{1},".format(mergeFactor[0], mergeFactor[1]))
    #    if blockMerge == False:
    #        csv.write("0,")
    #    else:
    #        csv.write("1,")
    #    csv.write("n/a,")
        csv.write("n/a,")
    else:
        csv.write("n/a,1,")
        csv.write("{0},{1},".format(streamBlock, s_unroll))
        csv.write("{0},n/a,".format(mergeFactor[0]))
        if blockMerge == False:
            csv.write("0,")
        else:
            csv.write("1,")
        if retime == False:
            csv.write("0,")
        else:
            csv.write("1,")
        if prefetch == False:
            csv.write("0,")
        else:
            csv.write("1,")
    csv.close() 



def searchSpace():

    #startTime = datetime.datetime.now()
    #best = 1e12
    group = []
    for i in range(11):
        group.append([])

    #blockSize = itertools.product([2**i for i in range(3, 8)], repeat=2)
    mergeFactor = itertools.product([2 ** i for i in range(0, 4)], repeat=2)

    for paraVector in filter(FilterParams, itertools.product(
      #[step for step in range (1, 2)], # time steps to fuse
      #filter(lambda x: x[0] * x[1] <= 2 ** (maxThreadsPerBlockLg2),
      #  blockSize), # blockSize
      [2 ** bs for bs in range(3, 9)],
      [True], # streaming
      [8, 32, 128, 512, 1024], # length of stream block
      [1, 8, 16], # Streaming unrollFactors
      filter(lambda x: x[0] * x[1] <= 2 ** 4, mergeFactor), # merge factor
      [False, True], # False for cyclic merging, True for block merging
      [False, True], # retiming
      [False, True], # prefetching
     )):
        bsize, streaming, sb, uf, mf, blockMerge, retiming, prefetching = paraVector
        '''
        if not streaming:
            if mf == (1, 1):
                group[0].append(paraVector)
            elif blockMerge == False:
                group[1].append(paraVector)
            else:
                group[2].append(paraVector)
                
            continue
        '''
        ## 0
        if (mf[0] > 1) and blockMerge == False and retiming == False and prefetching == False:
            #print (type(mf))
            group[0].append(paraVector)

        ## 1
        if (mf[0] > 1) and blockMerge == False and retiming == True and prefetching == False:
            group[1].append(paraVector)

        #if (mf[0] > 1) and blockMerge == False and retiming == False and prefetching == True:
        #    group[5].append(paraVector)
        
        ## 2
        if (mf[0] > 1) and blockMerge == False and retiming == True and prefetching == True:
            group[2].append(paraVector)

        ## 3
        if (mf[0] > 1) and blockMerge == True and retiming == False and prefetching == False:
            group[3].append(paraVector)

        #if (mf[0] > 1) and blockMerge == True and retiming == True and prefetching == False:
        #    group[8].append(paraVector)

        ## 4
        if (mf[0] > 1) and blockMerge == True and retiming == False and prefetching == True:
            group[4].append(paraVector)

        ##if (mf[0] > 1) and blockMerge == True and retiming == True and prefetching == True:
        #    group[10].append(paraVector)

    for i in range(5):
        print(len(group[i]))

    csv = open("duration.csv", 'w')
    csv.write("combination,name,bx,by,streaming,sb,uf,mfx,mfy,blockMerge,retiming,prefetching,Duration\n")
    csv.close()
    
    for i in range(5):
        paras = group[i]
        random.shuffle (paras)

        threshold = min(30, len(paras))
        if len(paras) > 200:
            threshold = 50

        cnt = 0
        for paraVector in paras:
            cnt += 1
            print("testing: ", i, "---", cnt)
            config = cfgToCommandLine(paraVector)
            conf_str = cfgToString(paraVector)

            cmd = " ".join(["../stencilgen *.idsl", config, "--ndim M=8192,N=8192 >> /dev/null"])
            os.system(cmd)
        
            writePara(paraVector, i)
            os.system("./do_test.sh " + conf_str + " " + str((1+cnt)%2))

            if cnt == threshold:
                break

    # best = getBest()
    # print("the best combination: ", best)


def getBest():
    csv = open("duration.csv", 'r')
    cnt = 0
    duration = 1e10
    comb = 0
    for line in csv:
        if cnt == 0:
            cnt = cnt + 1
            continue
        seg = line.split(',')
        if duration > int(seg[12]):
            duration = int(seg[12])
            comb = seg[0]

    return comb


if __name__ == '__main__':
    searchSpace()
