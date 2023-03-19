#########################################################################
# File Name: run.sh
# Author: THU Code Farmer
# mail: thu@thu.thu
# Created Time: 2019年11月28日 星期四 01时48分56秒
#########################################################################
#!/bin/bash

arch="V100"
stencil=("star2d1r" "star2d2r" "star2d3r" "star2d4r" "box2d1r" "box2d2r" "box2d3r" "box2d4r" "cross2d1r" "cross2d2r" "cross2d3r" "cross2d4r" "star3d1r" "star3d2r" "star3d3r" "star3d4r" "box3d1r" "box3d2r" "box3d3r" "box3d4r" "cross3d1r" "cross3d2r" "cross3d3r" "cross3d4r")

PROCESS=(2 4 8 16)

stid=0
make
mpirun -np ${PROCESS[0]} ./perf-ga | tee ../log/${arch}_${stencil[stid]}.txt
