arch=("V100" "A100")

stencil=("box3d1r" "box3d2r" "box3d3r" "box3d4r" "cross3d1r" "cross3d2r" "cross3d3r" "cross3d4r" "star3d1r" "star3d2r" "star3d3r" "star3d4r")

archid=1
cv=(4 4 4 4 4 4 4 4 4 4 4 4)

for((stid=0;stid<12;stid++))
do
    python sampler.py ${arch[archid]} ${stencil[stid]} ${cv[stid]}
done
