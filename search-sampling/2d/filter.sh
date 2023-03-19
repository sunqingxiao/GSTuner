arch=("V100" "A100")

stencil=("box2d1r" "box2d2r" "box2d3r" "box2d4r" "cross2d1r" "cross2d2r" "cross2d3r" "cross2d4r" "star2d1r" "star2d2r" "star2d3r" "star2d4r")

archid=1
cv=(4 4 4 4 4 4 4 4 4 4 4 4)

for((stid=0;stid<12;stid++))
do
    python sampler.py ${arch[archid]} ${stencil[stid]} ${cv[stid]}
done
