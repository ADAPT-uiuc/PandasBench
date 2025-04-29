import json
from pathlib import Path

def get_num_cells(lib):
  base = f'./output-stats/stats-{lib}-default/'
  directory = Path(base)
  fnames = [base + f.name for f in directory.iterdir() if f.is_file() and f.name != '.version']
  num_cells = 0
  for fname in fnames:
    with open(fname, 'r') as file:
      num_cells += len(json.load(file)['cells'])

  if lib != 'pandas':
    base = f'./output-stats/errors-{lib}-default/'
    directory = Path(base)
    fnames = [base + f.name for f in directory.iterdir() if f.is_file() and f.name.endswith('.error.txt')]
    for fname in fnames:
      with open(fname, 'r') as file:
        line = file.readlines()[2]
        num_cells += int(line[line.find(':') + 2:])
  return num_cells

print('Total / Pandas:', get_num_cells('pandas'))
print('Modin:', get_num_cells('modin'))
print('Dask:', get_num_cells('dask'))
print('Koalas:', get_num_cells('koalas'))
print('Dias:', get_num_cells('dias'))
