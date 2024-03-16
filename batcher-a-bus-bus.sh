#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G        # memory per node
#SBATCH --time=00-24:00      # time (DD-HH:MM)
#SBATCH --output=log/%N-%j.out  # %N for node name, %j for jobID

module load python/3 cuda cudnn scipy-stack
source tensorflow/bin/activate
cd src_a_bustle_a_bus/
# check if ${a} is 1 then run a-bus.py else run bus.py
if [ ${a} -eq 1 ]
then
    python3 a-bus.py -t ${t} -l ${bn}_A-BUS_${t}_${a}_${f}.log -b "${b}" -bn "${bn}" -p 14000000 -f "${f}"
else
    python3 bus.py -t ${t} -l ${bn}_BUS_${t}_${a}.log -b "${b}" -bn "${bn}"
fi