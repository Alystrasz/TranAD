#!/bin/bash

# Parameters check
if [ $# != 1 ]; then
    echo " Usage: ./scripts/benchmark.sh [MSDS|SWaT|SMD]"
    exit
fi

dataset=$1
supported=("MSDS" "SWaT" "SMD")
if [[ $(echo ${supported[@]} | fgrep -w $dataset) ]]
then
    echo
else
    echo "Unsupported dataset (\"$dataset\")."
    exit
fi


## Compression method
#method=cb     # keep X first points
#method=ce     # keep X last points
#method=fli     # uses a FLI model with a tolerated error of 0.01 * X
method=rdm    # randomly removes X points from dataset
#method=stairs # compress in a stairway fashion
#method=avg     # averages frame values, grouping them by windows of X points
#method=cavg    # averages frame values, cutting dataset in X windows


# Directories creation
if [ ! -d "./logs" ]; then
    mkdir ./logs
fi
## Store all experiment results in a common directory
timestamp=$dataset.$method.$(date +%s)
mkdir ./logs/$timestamp


# Benchmarking loop
#array=(1 200 400 600 800 1000 1200 1400 1600 1800 2000 2200 2400 2600 2800 2970 2985 2993 2996 2997) #Random series (leaves only 3 points in the end)
#array=(1 2 4 8 16 32 64 128 256 512 1024 2048 2500 3000 3500 4096 4500 5000 5500 6000 6500 7000 7500 8192 16384 32768) #FLI coefficients
array=(1000 2000 5000 10000 20000 50000 100000 110000 120000 130000 140000 143000 146000)
#array=$(seq 0 20)
for p in "${array[@]}"
do

## Compute power of 2
#p=$((2 ** $p))

m=$method$p

repetition_array=$(seq 0 0)
if [[ $m == *"rdm"* ]]; then
repetition_count=10
echo "Repeating compression experiment $repetition_count times for each step."
repetition_array=$(seq 0 $((repetition_count-1)))
fi

for r in $repetition_array
do

echo
echo \=\=\>\ Compression method: $m

## Output log file
filename=(logs/$timestamp/$m.log)

if [[ $m == *"rdm"* ]]; then
filename=(logs/$timestamp/$m.$r.log)
fi

## Start time
echo "Started at:" $(date) >$filename
echo "" >>$filename

## Preprocess
python preprocess.py $dataset --$m >>$filename

## Training
echo
echo "Starting training at:" $(date) >>$filename
echo
python main.py --model TranAD --dataset $dataset --retrain >>$filename

## End time
echo "" >>$filename
echo "Finished at:" $(date) >>$filename

done
done
