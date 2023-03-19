#!/bin/bash
main_cpp=../2d.driver.cpp
name=$1
echo "testing: ${name}" 
nvcc out.cu ${main_cpp} -O3  -ccbin=g++ -std=c++11 -Xcompiler "-fPIC -fopenmp -O3 -fno-strict-aliasing" --use_fast_math -Xptxas "-dlcm=cg" 
if [ $? -ne 0 ];
then
    echo "Compilation Error!"
    echo "n/a" >> duration.csv
    exit 0
fi
rm out.cu
CUDA_VISIBLE_DEVICES=0 ncu --csv --metrics duration ./a.out | grep -P avg | cut -d\" -f 24 >> duration.csv
if [ $? -ne 0 ];
then
    echo "Running Error!"
    echo "n/a" >> duration.csv
    exit 0
fi
rm a.out

