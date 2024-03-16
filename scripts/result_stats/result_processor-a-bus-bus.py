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
    if len(parts) >= 4:
        number = parts[2]
        # middle = parts[-2].split('.')[0]
        boolean = parts[-1].split('.')[0]
        return number, boolean
    return None

data = []
solved = {}
for file_name in file_names:
    parts = split_file_name(file_name)
    if parts:
        number, flag = parts
        data.append([number, flag])
        solved[number] = flag
    else:
        print("Invalid file name format")
    print()  # Separator between file names

df = pd.DataFrame(data, columns=["Number", "Augmented"])
#df = df.sort_values(["Number", "Name", "Augmented"])  # Sort the DataFrame based on multiple columns
df = df.sort_values(["Number", "Augmented"], key=lambda x: pd.to_numeric(x, errors='coerce'))

df.to_csv(directory + "result_table.csv", index=False)


unique_numbers = df["Number"].unique()

# Print the unique numbers
for number in unique_numbers:
    print(number)

# print the name with 1 to 5 that are not in solved
not_solved = []
for i in range(1, 90):
    if str(i) not in solved:
        not_solved.append(str(i))

print('Not solved:\n', not_solved)


# convert the not_solved_model to bash format as model_task_dict
model_task_dict = ' '.join(not_solved)
print('model_task_dict:\n', model_task_dict)

