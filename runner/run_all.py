import subprocess
import run_nb
import argparse
import os
import sys
import pathlib
import nbs_to_run

parser = argparse.ArgumentParser(description='Run benchmarks on all notebooks in nbs_to_run.py')

parser.add_argument('--lib', default='pandas', type=str, metavar='API_IMPLEMENTATION', help='The Pandas API implementation to use. Pandas by default. Other options are modin (pass in --lib_args=NUM_CORES), dask, and koalas.')
parser.add_argument('--add_on', default='', type=str, metavar='LIBRARY', help='Add on library to include (like Dias), default is to use no additional library.')
# For the default number of cores in Modin: https://github.com/modin-project/modin/blob/b998925d9e34bdb5c0752abb85a7a5769e0826f1/modin/config/envvars.py#L215)
parser.add_argument('--lib_args', default='', type=str, metavar='LIB_ARGS', help='Pass additional argument for the library.')
parser.add_argument('--scale_input', action='store_true', help='Scale the inputs based off of nbs_to_run.py. Otherwise, the previously scaled inputs will be used. The benchmark will not properly run if the input has never been scaled.')
parser.add_argument('--scale_input_and_exit', action='store_true', help='Scale the inputs based off of nbs_to_run.py, but does not run the benchmark. The benchmark will not properly run if the input has never been scaled.')

args = parser.parse_args()

# Some validation
default_msg = 'ERROR:\n'
msg = default_msg
if args.lib == 'modin':
  try:
    num_cores = int(args.lib_args)
    if num_cores < 2:
      msg += '--lib_args=NUM_CORES should be an integer that is at least 2 when using modin'
  except:
    msg += 'Specify --lib_args=NUM_CORES when using modin'
elif args.lib == 'dask':
  try:
    num_cores = int(args.lib_args)
    if num_cores < 1:
      msg += '--lib_args=NUM_CORES should be an integer that is at least 1 when using dask'
  except:
    msg += 'Specify --lib_args=NUM_CORES when using dask'
elif args.lib == 'koalas':
  try:
    num_cores = int(args.lib_args)
    if num_cores < 1:
      msg += '--lib_args=NUM_CORES should be an integer that is at least 1 when using koalas'
  except:
    msg += 'Specify --lib_args=NUM_CORES when using koalas'

if args.scale_input and args.scale_input_and_exit:
  msg += 'At most one of --scale_input and --scale_input_and_exit should be set'

if msg != default_msg:
  print(msg)
  parser.print_help()
  sys.exit(1)

# Put a version file into the "stats" folder
if not os.path.isdir("./stats"):
  os.mkdir('./stats')
if not os.path.isdir("./errors"):
  os.mkdir('./errors')
ver_file = open('stats/.version', 'w+')
should_run_nb_body = not args.scale_input_and_exit
VER_lib = args.lib
VER_add_on = args.add_on
VER="-".join((VER_lib, VER_add_on))
ver_file.write(VER)
ver_file.close()

prefix = str(pathlib.Path('../notebooks').resolve())

good = []
bad = []
start = 0
end = len(nbs_to_run.notebooks)

nbs_to_ignore = set()
try:
  for i, (nb, scale_factor) in enumerate(nbs_to_run.notebooks):
    if nb in nbs_to_ignore:
      continue
    kernel_user = nb.split('/')[0]
    kernel_slug = nb.split('/')[1]
    full_path = prefix+"/"+nb
    print(i + 1)
    print(f"--- RUNNING: {kernel_user}/{kernel_slug}")
    scale_input = args.scale_input or args.scale_input_and_exit
    succ = run_nb.run_nb_paper(full_path, args.lib if should_run_nb_body else '', args.lib_args, args.add_on, scale_factor, scale_input)
    if should_run_nb_body:
      if succ:
        res = subprocess.run(["mv", "stats.json", f"stats/{kernel_user}_{kernel_slug}.json"])
        good.append(nb)
      else:
        bad.append(nb)
except KeyboardInterrupt:
  pass
