#!/bin/bash
## create model dir
arch=("V100" "A100")

numlayers=(2 3 4 5 6 7 8 9 10) # 9
hiddendim=(2 4 8 16 32 64 128 256 512 1024) # 9

## execute 5-fold training
for((gid=0;gid<1;gid++))
do
    for((i=5;i<6;i++))
    do
        for((j=8;j<9;j++))
        do
            for((k=3;k<5;k++))
            do
                python rnn2dNet.py test ${numlayers[i]} ${hiddendim[j]} data/${arch[gid]}_cv${k}_train.npz data/${arch[gid]}_cv${k}_test.npz model/${arch[gid]}/cv${k}/${numlayers[i]}_${hiddendim[j]}/rnn_model.h5 result/${arch[gid]}_${numlayers[i]}_${hiddendim[j]}_cv${k}_scores.npz
                sleep 1
            done
        done
    done
done
