import subprocess
import run_nb
import argparse
import os
import sys
import pathlib
import json

parser = argparse.ArgumentParser(description='Run benchmarks on all notebooks in nbs_to_run.py')

parser.add_argument('--lib', default='pandas', choices=["pandas", "modin", "dask", "koalas"], type=str, help='The Pandas API alternative to use. Pandas is used by default.')
parser.add_argument('--add_on', choices=['dias'], type=str, help='Add on library to include (like Dias). By default it uses no additional library.')
parser.add_argument('--num_cores', default=0, type=int, metavar='NUM_CORES', help='Pass additional argument for the library.')
parser.add_argument('--scale_file', default='scales/nbs_to_run_default.json', type=str, help='JSON file that contains the scale factor for each notebook. By default we use the file that uses a scale factor of 1.0.')
parser.add_argument('--scale_input_and_exit', action='store_true', help='Scales the benchmark. The benchmark will not properly run if the input has never been scaled.')

args = parser.parse_args()

# Some validation
default_msg = 'ERROR:\n'
msg = default_msg
if args.lib == 'modin':
  try:
    num_cores = args.num_cores
    if num_cores < 2:
      msg += '--num_cores=NUM_CORES should be an integer that is at least 2 when using --lib=modin'
  except:
    msg += 'Specify --num_cores=NUM_CORES when using --lib=modin'
elif args.lib == 'dask':
  try:
    num_cores = args.num_cores
    if num_cores < 1:
      msg += '--num_cores=NUM_CORES should be an integer that is at least 1 when using --lib=dask'
  except:
    msg += 'Specify --num_cores=NUM_CORES when using --lib=dask'
elif args.lib == 'koalas':
  try:
    num_cores = args.num_cores
    if num_cores < 1:
      msg += '--num_cores=NUM_CORES should be an integer that is at least 1 when using --lib=koalas'
  except:
    msg += 'Specify --num_cores=NUM_CORES when using --lib=koalas'

add_on = args.add_on if args.add_on != None else ''

if msg != default_msg:
  print(msg)
  parser.print_help()
  sys.exit(1)

# Put a version file into the "stats" folder
if not os.path.isdir("./stats"):
  os.mkdir('./stats')
if not os.path.isdir("./errors"):
  os.mkdir('./errors')
should_run_nb_body = not args.scale_input_and_exit

prefix = str(pathlib.Path('../notebooks').resolve())

with open(args.scale_file, 'r') as fp:
  scale_d = json.load(fp)

nb_scales = []
for pair in scale_d['notebooks']:
  nb_scales.append((pair['nb'], pair['scale-factor']))
### END FOR ###

try:
  for i, (nb, scale_factor) in enumerate(nb_scales):
    kernel_user = nb.split('/')[0]
    kernel_slug = nb.split('/')[1]
    full_path = prefix+"/"+nb
    print(i + 1)
    print(f"--- RUNNING: {kernel_user}/{kernel_slug}")
    succ = run_nb.run_nb_paper(full_path, args.lib if should_run_nb_body else '', args.num_cores, add_on, scale_factor, args.scale_input_and_exit)
    if should_run_nb_body and succ:
      res = subprocess.run(["mv", "stats.json", f"stats/{kernel_user}_{kernel_slug}.json"])
except KeyboardInterrupt:
  pass
