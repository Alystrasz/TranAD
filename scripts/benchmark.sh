#!/bin/bash

# Directories creation
if [ ! -d "./logs" ]; then
    mkdir ./logs
fi
## Store all experiment results in a common directory
timestamp=$(date +%s)
mkdir ./logs/$timestamp


# Benchmarking loop
array=$(seq 0 10)
for p in $array
do

## Compute power of 2
p=$((2 ** $p))

## Compression method
method=cb$p
echo
echo \=\=\>\ Compression method: $method

## Output log file
filename=(logs/$timestamp/$method.log)

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
