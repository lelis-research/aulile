#!/bin/bash

benchmark_name="38"
benchmark_filename="bustle_38.txt"

for ((aug = 1; aug <= 1; aug++))
	do
	for ((model = 1; model <= 5; model ++))
		do
		for ((taskId = 1; taskId <=38; taskId ++))
			do
				echo "Augment : ${aug}"
				echo "Model : ${model}"
				echo "TaskID : ${taskId}"
				echo "Benchmark Name : ${benchmark_name}"
				echo "Benchmark Filename : ${benchmark_filename}"
				sbatch --export=m="${model}",t="${taskId}",a="${aug}",bn="${benchmark_name}",b="${benchmark_filename}" batcher-a-bustle-bustle.sh
			done
		done
	done