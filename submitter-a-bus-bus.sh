#!/bin/bash

benchmark_name="38"
benchmark_filename="bustle_38.txt"

for ((aug = 1; aug <= 1; aug++))
	do
	for ((taskId = 1; taskId <=38; taskId ++))
		do
		for ((f = 0.25; f <= 0.75; f += 0.25))
			do
				echo "Augment : ${aug}"
				echo "TaskID : ${taskId}"
				echo "Benchmark Name : ${benchmark_name}"
				echo "Benchmark Filename : ${benchmark_filename}"
				sbatch --export=t="${taskId}",a="${aug}",bn="${benchmark_name}",b="${benchmark_filename}",f="${f}" batcher-a-bus-bus.sh
			done
		done
	done