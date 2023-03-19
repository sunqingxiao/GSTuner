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
order = 8

def FilterParams(paraVector):
    blockSize, streaming, streamBlock, s_unroll, mergeFactor, blockMerge, retime, prefetch = paraVector

    ## max threads per block limitation
    if not streaming and blockSize[0] * blockSize[1] * blockSize[2] > 1024:
        return False
    
    # for combination 0
    if not streaming and mergeFactor == (1, 1, 1) and blockMerge == True:
        return False

    if not streaming and (streamBlock != 8 or s_unroll != 1 or retime or prefetch):
        return False

    if streaming and (mergeFactor[2] != 1 or blockSize[2] != 8):
        return False

    if streamBlock < s_unroll:
        return False

    if blockSize[0] * mergeFactor[0] <= order * 2:
        return False

    if blockSize[1] * mergeFactor[1] <= order * 2:
        return False

    #if blockSize[2] * mergeFactor[2] <= order * 2:
    #    return False

    if streaming and retime  and (blockSize[0]*mergeFactor[0])*(blockSize[1]*mergeFactor[1]) * 8 >= 2 ** maxShmPerBlockLg2:
        return False

    if streaming and not retime and (blockSize[0]*mergeFactor[0])*(blockSize[1]*mergeFactor[1])*4*8 > 2 ** maxShmPerBlockLg2:
        return False

    #if streaming and retime and blockSize[0]*mergeFactor[0]*blockSize[1]*mergeFactor[1]*2 > 2 ** maxShmPerBlockLg2:
    #    return False

    return True


def cfgToCommandLine(paraVector):
    
    blockSize, streaming, streamBlock, s_unroll, mergeFactor, blockMerge, retime, prefetch = paraVector
    cmd = ""

    if not streaming:
        cmd += " --blockdim x={0},y={1},z={2}".format(blockSize[0], blockSize[1], blockSize[2])
        cmd += " --unroll i={0},j={1},k={2}".format(mergeFactor[0], mergeFactor[1], mergeFactor[2])
        if blockMerge:
            cmd += " --blocked-loads"
    else:
        cmd += " --blockdim x={0},y={1},z={2}".format(blockSize[0], blockSize[1], streamBlock)

        cmd += " --unroll i={0},j={1},k={2}".format(mergeFactor[0], mergeFactor[1], s_unroll)

        cmd += " --stream k"

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
        cmd += "bx{0}y{1}z{2}".format(blockSize[0], blockSize[1], blockSize[2])
        if blockMerge:
            cmd += "bm"
        else:
            cmd += "cm"
        cmd += "x{0}y{1}z{2}".format(mergeFactor[0], mergeFactor[1], mergeFactor[2])
    else:
        cmd += "bx{0}y{1}sb{2}".format(blockSize[0], blockSize[1], streamBlock)

        if blockMerge:
            cmd += "bm"
        else:
            cmd += "cm"
        cmd += "x{0}y{1}".format(mergeFactor[0], mergeFactor[1])
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
    csv.write(",{0},{1},".format(blockSize[0], blockSize[1]))
    if not streaming:
        csv.write("{0},0,".format(blockSize[2]))
        csv.write("n/a,n/a,")
        csv.write("{0},{1},{2},".format(mergeFactor[0], mergeFactor[1], mergeFactor[2]))
        if blockMerge == False:
            csv.write("0,")
        else:
            csv.write("1,")
        csv.write("n/a,")
        csv.write("n/a,")
    else:
        csv.write("n/a,1,")
        csv.write("{0},{1},".format(streamBlock, s_unroll))
        csv.write("{0},{1},n/a,".format(mergeFactor[0], mergeFactor[1]))
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

    blockSize = itertools.product([2**i for i in range(3, 7)], repeat=3)
    mergeFactor = itertools.product([2 ** i for i in range(0, 4)], repeat=3)

    for paraVector in filter(FilterParams, itertools.product(
      #[step for step in range (1, 2)], # time steps to fuse
      filter(lambda x: x[0] * x[1] <= 2 ** (maxThreadsPerBlockLg2),
        blockSize), # blockSize
      [True], # streaming
      [2 ** sbLg2 for sbLg2 in range (3, 7)], # length of stream block
      [1, 8, 16], # Streaming unrollFactors
      filter(lambda x: x[0] * x[1] <= 2 ** 4, mergeFactor), # merge factor
      [False, True], # False for cyclic merging, True for block merging
      [False, True], # retiming
      [False, True], # prefetching
     )):
        bsize, streaming, sb, uf, mf, blockMerge, retiming, prefetching = paraVector
        '''
        if not streaming:
            if mf == (1, 1, 1):
                group[0].append(paraVector)
            elif blockMerge == False:
                group[1].append(paraVector)
            else:
                group[2].append(paraVector)
                
            continue
        '''
        ## 5
        if (mf[0] > 1 or mf[1] > 1) and blockMerge == False and retiming == False and prefetching == True:
            group[5].append(paraVector)
        ## 6
        if (mf[0] > 1 or mf[1] > 1) and blockMerge == False and retiming == True and prefetching == True:
            group[6].append(paraVector)

        ## 7
        if (mf[0] > 1 or mf[1] > 1) and blockMerge == True and retiming == True and prefetching == True:
            group[7].append(paraVector)

    for i in range(5, 8):
        group[i] = list(set(group[i]))
        print(len(group[i]))

    csv = open("duration.csv", 'w')
    csv.write("combination,name,bx,by,bz,streaming,sb,uf,mfx,mfy,mfz,blockMerge,retiming,prefetching,Duration\n")
    csv.close()
    
    for i in range(5, 8):
        paras = group[i]
        random.shuffle (paras)

        threshold = min(30, len(paras))
        if len(paras) > 200:
            threshold = 50

        cnt = 0
        for paraVector in paras:
            cnt += 1
            print("generating: ", i, "---", cnt)
            config = cfgToCommandLine(paraVector)
            conf_str = cfgToString(paraVector)

            cmd = " ".join(["../stencilgen *.idsl", config, "--ndim L=512,M=512,N=512 >> /dev/null"])
            os.system(cmd)
        
            writePara(paraVector, i)
            os.system("./do_test.sh " + conf_str + " " + str(cnt%2))

            if cnt == threshold:
                break

    #best = getBest()
    #print("the best combination: ", best)


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
        if duration > int(seg[14]):
            duration = int(seg[14])
            comb = int(seg[0])

    return comb


if __name__ == '__main__':
    searchSpace()
