#!/bin/bash

# Directories creation
if [ ! -d "./logs" ]; then
    mkdir ./logs
fi
## Store all experiment results in a common directory
timestamp=$(date +%s)
mkdir ./logs/$timestamp


# Benchmarking loop
array=$(seq 0 20)
for p in $array
do

## Compute power of 2
p=$((2 ** $p))

## Compression method
#method=cb$p     # keep X first points
#method=ce$p     # keep X last points
#method=fli$p     # uses a FLI model with a tolerated error of 0.01 * X
method=rdm$p    # randomly removes X points from dataset
#method=stairs$p # compress in a stairway fashion
#method=avg$p     # averages frame values, grouping them by windows of X points
#method=cavg$p    # averages frame values, cutting dataset in X windows

repetition_array=$(seq 0 0)
if [[ $method == *"rdm"* ]]; then
echo "Repeating compression experiment 10 times for each step."
repetition_array=$(seq 0 9)
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
