import json
import os
import sys

if len(sys.argv) != 2:
  print(f'Usage: {sys.argv[0]} </path/to/notebooks/root>')
  sys.exit(0)

nb_root = sys.argv[1]
if len(nb_root) != 0 and nb_root[-1] == '/':
  nb_root = nb_root[:-1]

nbs = {}

for dir in os.listdir(nb_root):
  path = f'{nb_root}/{dir}'
  nb_name = ''
  if not os.path.isdir(path):
    continue
  for entry in os.listdir(path):
    if entry[0] != '.':
      path += f'/{entry}/input'
      nb_name = f'{dir}/{entry}'
      break
  dir_size = 0
  for input_dir, _, files in os.walk(path):
    scaled_files = {''.join(file.split('.scaled')) for file in files if '.scaled.' in file}
    for file in files:
      if '.scaled.' in file or file not in scaled_files:
        print(file)
        dir_size += os.path.getsize(f'{input_dir}/{file}')
  nbs[nb_name] = {'input size (bytes)': dir_size}

with open('dataset_input_sizes.json', 'w') as file:
  json.dump(nbs, file, indent=2)

