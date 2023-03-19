#!/bin/bash
name=$1$2
step=$2
mkdir ${name}
#cp -r common ${name}/
mv ${name}.idsl ${name}/
#mv ${name}.npz ${name}/
#cp stencilgen ${name}/ 
#cp 3d.driver.cpp ${name}/
cp do_test.sh ${name}/
cp tuning_3d_${step}.py ${name}/
#cp run_3d.py ${name}/

cd ${name}
while [ `ps aux | grep 'tuning_3d' | grep -v 'grep' | wc -l` -ge 6 ]
do
    sleep 250
done
python tuning_3d_${step}.py
