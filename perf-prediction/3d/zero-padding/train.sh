#!/bin/bash
## create model dir
arch=("V100" "A100")
numlayers=(2 3 4 5 6 7 8 9 10) # 9
hiddendim=(2 4 8 16 32 64 128 256 512 1024) # 9

cd model
for((gid=0;gid<2;gid++))
do
    mkdir -p ${arch[gid]}
    cd ${arch[gid]}
    for((i=0;i<5;i++))
    do
        mkdir -p cv${i}
        cd cv${i}
        for((j=0;j<9;j++))
        do
            for((k=0;k<10;k++))
            do
                mkdir -p ${numlayers[j]}_${hiddendim[k]}
            done
        done
        cd ..
    done
    cd ..
done
cd ..

## execute 5-fold training
for((gid=1;gid<2;gid++))
do
    for((i=5;i<6;i++))
    do
        for((j=9;j<10;j++))
        do
            for((k=4;k<5;k++))
            do
                python -u mlp3dNet.py train ${numlayers[i]} ${hiddendim[j]} data/${arch[gid]}_cv${k}_train.npz data/${arch[gid]}_cv${k}_test.npz model/${arch[gid]}/cv${k}/${numlayers[i]}_${hiddendim[j]}/mlp_model.h5 result/${arch[gid]}_${numlayers[i]}_${hiddendim[j]}_cv${k}_scores.npz | tee result/${arch[gid]}_${numlayers[i]}_${hiddendim[j]}_cv${k}.log
                sleep 1
            done
        done
    done
done
