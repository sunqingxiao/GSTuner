#!/bin/bash
name=$1$2
step=$2
mkdir ${name}
mv ${name}.idsl ${name}/
#mv ${name}.npz ${name}/
#cp stencilgen ${name}/ 
#cp -r common ${name}/
#cp 2d.driver.cpp ${name}/
cp do_test.sh ${name}/
cp tuning_2d_${step}.py ${name}/
#cp run_2d.py ${name}/

cd ${name}
while [ `ps aux | grep 'tuning_2d' | grep -v 'grep' | wc -l` -ge 8 ]
do
    sleep 10
done
python tuning_2d_${step}.py
