import os
import re
import pandas as pd
import sys

target = sys.argv[1]

directory = '../../results/' + target  # Replace with the directory path you want to explore

file_names = []
for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)):
        file_names.append(filename)

print(file_names[0])

def split_file_name(file_name):
    parts = file_name.split('_')
    # print(parts)
    if len(parts) >= 6:
        number = int(parts[2])
        model = int(parts[-2].split('.')[0])
        boolean = int(parts[-1].split('.')[0])
        return number, model, boolean
    return None

data = []
solved = {}
for file_name in file_names:
    parts = split_file_name(file_name)
    if parts:
        number, model, flag = parts
        data.append([number, model, flag])
        if number not in solved:
            solved[number] = []
        solved[number].append(model)
    else:
        print("Invalid file name format")
    print()  # Separator between file names

df = pd.DataFrame(data, columns=["Number", "Model Number", "Augmented"])
#df = df.sort_values(["Number", "Name", "Augmented"])  # Sort the DataFrame based on multiple columns
df = df.sort_values(["Number", "Model Number", "Augmented"], key=lambda x: pd.to_numeric(x, errors='coerce'))

df.to_csv(directory + "result_table.csv", index=False)


unique_numbers = df["Number"].unique()

# Print the unique numbers
for number in unique_numbers:
    print(number)


# Count the frequency of each unique number
frequency_count = df["Number"].value_counts()

#model freq
model_frequency_count = df["Model Number"].value_counts()

# Print the frequency count
frequency_count.to_csv(directory + "freq_count.csv")

#print the model_frequency_count
model_frequency_count.to_csv(directory + "model_freq_count.csv")

# print the name with 1 to 5 that are not in solved
not_solved = {}
for i in range(1, 90):
    if i not in solved.keys():
        not_solved[i] = []
        for j in range(1, 6):
            not_solved[i].append(j)
    else:
        for j in range(1, 6):
            if j not in solved[i]:
                if i not in not_solved:
                    not_solved[i] = []
                not_solved[i].append(j)

print('Not solved:\n', not_solved)

# revert the dictionary where the key is the model number and the value is the number of the not solved
not_solved_model = {}
for key, value in not_solved.items():
    for v in value:
        if v not in not_solved_model:
            not_solved_model[v] = []
        not_solved_model[v].append(key)
print('Not solved model:\n', not_solved_model)

# convert the not_solved_model to bash format as model_task_dict
model_task_dict = {}
for key, value in not_solved_model.items():
    model_task_dict[key] = ' '.join(str(x) for x in value)
print('model_task_dict:\n', model_task_dict)

