#!/bin/bash

# Directories creation
if [ ! -d "./logs" ]; then
    mkdir ./logs
fi
## Store all experiment results in a common directory
timestamp=$(date +%s)
mkdir ./logs/$timestamp


# Benchmarking loop
#array=(1 200 400 600 800 1000 1200 1400 1600 1800 2000 2200 2400 2600 2800 2970 2985 2993 2996 2997) #Random series (leaves only 3 points in the end)
array=(1 2 4 8 16 32 64 128 256 512 1024 2048 2500 3000 3500 4096 4500 5000 5500 6000 6500 7000 7500 8192 16384 32768) #FLI coefficients
#array=$(seq 0 20)
for p in "${array[@]}"
do

## Compute power of 2
#p=$((2 ** $p))

## Compression method
#method=cb$p     # keep X first points
#method=ce$p     # keep X last points
method=fli$p     # uses a FLI model with a tolerated error of 0.01 * X
#method=rdm$p    # randomly removes X points from dataset
#method=stairs$p # compress in a stairway fashion
#method=avg$p     # averages frame values, grouping them by windows of X points
#method=cavg$p    # averages frame values, cutting dataset in X windows

repetition_array=$(seq 0 0)
if [[ $method == *"rdm"* ]]; then
echo "Repeating compression experiment 10 times for each step."
repetition_array=$(seq 0 19)
fi

for r in $repetition_array
do

echo
echo \=\=\>\ Compression method: $method

## Output log file
filename=(logs/$timestamp/$method.log)

if [[ $method == *"rdm"* ]]; then
filename=(logs/$timestamp/$method.$r.log)
fi

## Start time
echo "Started at:" $(date) >$filename
echo "" >>$filename

## Preprocess
python preprocess.py SWaT --$method >>$filename

## Training
echo
echo "Starting training at:" $(date) >>$filename
echo
python main.py --model TranAD --dataset SWaT --retrain >>$filename

## End time
echo "" >>$filename
echo "Finished at:" $(date) >>$filename

done
done
