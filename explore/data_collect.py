import glob
import sys
import re
import pathlib
import os
import pandas as pd
import json
from collections import defaultdict

sys.path.insert(1, '../')

import nbs_to_run
import bench_utils

paths_s = '../notebooks/*/*/*.ipynb'
paths = glob.glob(paths_s)

def get_df(user, base, file):
  # Special cases
  # if user == "doyouevendata" and base == './input/kiva_locations':
  #   return pd.DataFrame()
  #   # df = pd.read_csv(file, sep='\t')
  if user == 'chinstan':
    df = pd.read_csv(file, delimiter='\t', low_memory=False)
  elif user == 'wyl4417' and base == './input/multiple_choice_responses':
    df = pd.read_csv(file, low_memory=False)
  elif user == 'corazzon' and base == './input/kaggle_survey_2020_responses':
    df = pd.read_csv(file, low_memory=False)
  elif user == 'kwullum' and base == './input/UK_Traffic_Accidents_2015':
    df = pd.read_csv(file, low_memory=False)
  elif user == 'paramarthasengupta' and base == './input/Movie Dataset':
    df = pd.read_csv(file, encoding='latin1')
  elif user == 'j0thu777' and base == './input/OnlineRetail':
    df = pd.read_csv(file, encoding='ISO-8859-1')
  elif user == 'nihhaar' and base == './input/books':
    df = pd.read_csv(file, on_bad_lines='skip')
  elif user == 'grudd0' and base == './input/Mass Shootings Dataset Ver 5':
    df = pd.read_csv(file, encoding='ISO-8859-1')
  elif user == 'jirakst':
    return pd.DataFrame()
  #   df = pd.read_csv(file, on_bad_lines='skip', delimiter=';', encoding = 'ISO-8859-1', low_memory=False)
  elif user == 'robikscube':  # 1 file
    df = pd.read_csv(file, low_memory=False)
  elif user == 'maxiaoyue':  # 2 files
    df = pd.read_csv(file, low_memory=False)

  # Normal cases
  elif file.endswith('.csv'):
    df = pd.read_csv(file)
  elif file.endswith('.xlsx'):
    df = pd.read_excel(file)
  else:
    print(file)
    assert False
  
  return df

stat_dict = dict()
for i, path in enumerate(paths):
  print(i)
  
  cells = bench_utils.open_and_get_source_cells(path)

  nb_path = pathlib.Path(path)
  nb_dir = nb_path.parent

  user = str(nb_path).split('/')[3]
  print('user:', user)
  
  
  f = False
  for nb in nbs_to_run.notebooks:
    name = nb[0]
    user2, _ = name.split('/')
    if user2 == user:
      f = True
      break
  ### END FOR ###
  if not f:
    continue
  
  if user == 'roydatascience':
    # Takes up too much memory
    continue

  stat_dict[user] = {}

  # patt = re.compile(r"file_bases\s*=\s*\[(.*?)\]", re.DOTALL)
  patt = re.compile(r"file_bases\s*=\s*\[\s*(.*?)\s*\]", re.DOTALL)
  for cell in cells:
    match = patt.search(cell)
    if not match:
      continue
    
    # file_bases = [...]
    the_str = match.group(0)
    # Adds file_bases object to the global namespace
    exec(the_str)
    assert file_bases is not None

    for base in file_bases:
      base_name = base.split('/')[-1]
      stat_dict[user][base_name] = {}

      print('base:', base)
      # Use the scaled file because we can downscale it to make the process
      # faster.
      inp_file_path = os.path.join(nb_dir, f"{base}.*")
      scaled = os.path.join(nb_dir, f"{base}.scaled.*")
      match_all = glob.glob(inp_file_path)
      match_scaled = glob.glob(scaled)
      assert len(match_all) <= 2
      assert len(match_scaled) <= 1
      matching_files = [x for x in match_all if x not in match_scaled]
      assert len(matching_files) == 1
      file = matching_files[0]

      df = get_df(user, base, file)
      nrows = len(df)
      ncols = len(df.columns)
      
      tys = []
      for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]):
          if pd.api.types.is_string_dtype(df[col]):
           tys.append('str')
          else:
            tys.append('object')
        else:
          tys.append(str(df[col].dtype))
      ### END FOR ###
      
      stat_dict[user][base_name]['nrows'] = nrows
      stat_dict[user][base_name]['ncols'] = ncols
      stat_dict[user][base_name]['types'] = tys
      # END IF #
    ### END FOR ###
    break
  ### END FOR ###
### END FOR ###

with open('data_stats.json', 'w') as fp:
  json.dump(stat_dict, fp, indent=2)
