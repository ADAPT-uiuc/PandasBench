
import re
import json
import sys
import subprocess
import os
from enum import Enum
import glob

import bench_utils

def run_nb_file(nb_path: str, library: str, num_cores: int, add_on: str, scale_factor: float, scale_input: bool):
  source_cells = bench_utils.open_and_get_source_cells(nb_path)

  # Don't do the following. You'll mess the cell index (i.e., we won't know that it is the nth cell)
  # source_cells = [s for s in source_cells if s.strip() != ""]

  src_dir = os.path.dirname(nb_path)

  def run_config(source_cells, error_file, times_file, library,
                 num_cores, add_on, scale_factor, scale_input):
    config = dict()
    config['src_dir'] = src_dir
    config['cells'] = source_cells
    config['error_file'] = error_file
    config['output_times_json'] = times_file
    config['library'] = library
    config['num_cores'] = str(num_cores)
    config['add_on'] = add_on
    config['scale_factor'] = scale_factor
    config['scale_input'] = scale_input

    config_filename = 'run_config.json'
    f = open(config_filename, 'w')
    json.dump(config, f, indent=2)
    f.close()

    # We measure memory usage with GNU time -v. We will only take that into account later if Modin
    # is not enabled, because this is unreliable for Modin.
    res = subprocess.run(["ipython", "log_times.py", f"{config_filename}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.returncode == 0, res
  
  # END run_config() #

  def load_json(file):
    f = open(file, 'r')
    jd = json.load(f)
    f.close()
    return jd

  pwd = os.getcwd()

  nb_path_split = nb_path.split('/')
  file_base = 'errors/' + nb_path_split[-3] + '.' + nb_path_split[-2]
  err_file = pwd + '/' + file_base + '.' + 'error.txt'
  times_file = pwd + '/' + 'times.json'
  succ, res = run_config(source_cells, err_file, times_file, library,
                         num_cores, add_on, scale_factor, scale_input)
  the_stdout = res.stdout.decode()
  # We may have an exception which is not denoted as error unfortunately. We have to search the stdout.
  if "Traceback" in the_stdout:
    succ = False
  if not succ:
    stdout_file_name = file_base + '.stdout.txt'
    stderr_file_name = file_base + '.stderr.txt'
    print(f"There was an error while running {nb_path}. See {err_file}, {stderr_file_name} and {stdout_file_name}")
    bench_utils.write_to_file(stdout_file_name, res.stdout.decode())
    bench_utils.write_to_file(stderr_file_name, res.stderr.decode())
    return False
  os.remove('run_config.json')
  if library == '':
    return True
  times = load_json(times_file)
  os.remove(times_file)

  if 'max-mem-in-mb' not in times:
    times['max-mem-in-mb'] = 0
  if 'max-disk-in-mb' not in times:
    times['max-disk-in-mb'] = 0

  f = open('stats.json', 'w')
  json.dump(times, f, indent=2)
  f.close()

  return True

def run_nb_paper(nb_dir: str, library: str, num_cores: int, add_on: str, scale_factor: float, scale_input: bool):
  updated_nb = "/".join((nb_dir, "updated.ipynb"))
  if os.path.exists(updated_nb):
    nb_path = updated_nb
  else:
    nb_path = "/".join((nb_dir, "old.ipynb"))

  return run_nb_file(nb_path, library, num_cores, add_on, scale_factor, scale_input)
