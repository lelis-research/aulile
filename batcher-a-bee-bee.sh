#!/bin/bash
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:1
#SBATCH --mem=64G        # memory per node
#SBATCH --time=00-24:00      # time (DD-HH:MM)
#SBATCH --output=log/%N-%j.out  # %N for node name, %j for jobID

module load python/3 cuda cudnn scipy-stack
source tensorflow/bin/activate
cd src/
if [ ${a} -eq 1 ]
then
    python3 bee.py -t ${t} -d 0 -l ${bn}_A-Bee_${t}_${a}_${m}.log -m bustle_model_0${m}.hdf5 -b "${b}" -bn "${bn}" -a "${a}" -p 14000000
else
    python3 bee.py -t ${t} -d 0 -l ${bn}_Bee_${t}_${a}_${m}.log -m bustle_model_0${m}.hdf5 -b "${b}" -bn "${bn}" -a "${a}" -p 14000000
fi
