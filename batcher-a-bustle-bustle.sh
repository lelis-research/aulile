#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --mem=64G        # memory per node
#SBATCH --time=00-24:00      # time (DD-HH:MM)
#SBATCH --output=log/%N-%j.out  # %N for node name, %j for jobID

module load python/3 cuda cudnn scipy-stack
source tensorflow/bin/activate
cd src_a_bustle_a_bus/
# check if ${a} is 1 then run a-bustle.py else run bustle.py
if [ ${a} -eq 1 ]
then
    python3 a-bustle.py -t "${t}" -l "${bn}_A-Bustle_${t}_${a}_${m}.log" -m "EncodedBustleModelForPS_${m}.hdf5" -b "${b}" -bn "${bn}" -p 14000000
else
    python3 bustle.py -t "${t}" -l "${bn}_${t}_Bustle_${a}_${m}.log" -m "EncodedBustleModelForPS_${m}.hdf5" -b "${b}" -bn "${bn}"
fi