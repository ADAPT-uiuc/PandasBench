# This is based on log_times.py from dias-benchmarks:
# https://github.com/ADAPT-uiuc/dias-benchmarks/blob/1fd6276b147fb666a2f56a3c0d47c099aca4e3c0/runner/log_times.py

from IPython import *

def main():
  import json
  import sys
  import time
  import os
  import subprocess
  import re
  import psutil

  # It may get overshadowed by the notebook
  _PBENCH_builtin_max = max
  _PBENCH_builtin_sum = sum

  def _PBENCH_get_memory_of_proc(proc):
    try:
      return proc.memory_full_info().pss
    except:
      return 0

  def _PBENCH_measure_mem():
    curProc = psutil.Process()
    return curProc.memory_full_info().pss + _PBENCH_builtin_sum([_PBENCH_get_memory_of_proc(proc) for proc in curProc.children(True)])

  from setup_import_lib import setup_import
  import hook as PBENCH_HOOK

  _PBENCH_ipython = get_ipython()
  if _PBENCH_ipython is None:
    print("[ERROR]: Run with `ipython` not `python`")
    sys.exit(1)
  # assert isinstance(_PBENCH_ipython, InteractiveShell)


  _PBENCH_run_config_filename = sys.argv[1]

  _PBENCH_f = open(_PBENCH_run_config_filename)
  try:
    _PBENCH_run_config = json.load(_PBENCH_f)
  except:
    _PBENCH_f.close()
    sys.exit(1)
  _PBENCH_f.close()


  if _PBENCH_run_config['scale_input']:
    os.environ['INPUT_SCALE_FACTOR'] = str(_PBENCH_run_config['scale_factor'])

  # Set enviromental variables used in the notebooks
  # and the rewriter to run code conditionally.
  if _PBENCH_run_config['library'] == 'modin':
    # See: https://modin.readthedocs.io/en/stable/getting_started/using_modin/using_modin_locally.html#advanced-configuring-the-resources-modin-uses
    # But also: https://github.com/modin-project/modin/issues/1666
    # It seems to me this applies only in a distributed setting, so we should be ok.
    os.environ["MODIN_CPUS"] = _PBENCH_run_config['num_cores']
  elif _PBENCH_run_config['library'] == 'dask':
    os.environ['DASK_CPUS'] = _PBENCH_run_config['num_cores']
  elif _PBENCH_run_config['library'] == 'koalas':
    os.environ['KOALAS_CPUS'] = _PBENCH_run_config['num_cores']

  _PBENCH_run_nb = _PBENCH_run_config['library'] != ''
  if _PBENCH_run_nb:
    setup_import(_PBENCH_run_config['library'], _PBENCH_run_config['add_on'], False)

  _PBENCH_use_dias = _PBENCH_run_config['add_on'] == 'dias'

  import bench_utils
  if _PBENCH_use_dias:
    # Use the rewriter as a lib. Note, however, that importing the rewriter will
    # overwrite apply().
    os.environ["_IREWR_USE_AS_LIB"] = "True"
    import dias.rewriter

  _PBENCH_error_file = _PBENCH_run_config['error_file']
  _PBENCH_times_file = _PBENCH_run_config['output_times_json']
  _PBENCH_measure_modin_mem = _PBENCH_run_config['library'] == 'modin'
  _PBENCH_measure_koalas_mem = _PBENCH_run_config['library'] == 'koalas'

  def _PBENCH_err_txt(ctx):
    return \
f"""
[START ERROR]
# Source cell idx: {ctx[0]}
# Source code:
{ctx[1]}
[END ERROR]
"""

  _PBENCH_ipython.run_line_magic('cd', _PBENCH_run_config['src_dir'])

  _PBENCH_source_cells = _PBENCH_run_config['cells']

  def _PBENCH_report_on_fail(_PBENCH_ctx):
    nonlocal _PBENCH_error_file
    bench_utils.write_to_file(_PBENCH_error_file, _PBENCH_err_txt(_PBENCH_ctx))
    sys.exit(1)

  _PBENCH_cells = []
  _PBENCH_max_mem = 0
  _PBENCH_max_disk = 0
  _PBENCH_total_time_ns = 0
  for _PBENCH_cell_idx, _PBENCH_cell in enumerate(_PBENCH_source_cells):

    # This will not catch all failures. The caller has to check the stdout
    # of this script.
    _PBENCH_ip_run_res = None
    _PBENCH_cell_idx -= 1
    if _PBENCH_cell_idx == -1:
      _PBENCH_ip_run_res = _PBENCH_ipython.run_cell(_PBENCH_cell, silent=True)
      if not _PBENCH_ip_run_res.success:
        _PBENCH_ctx = (_PBENCH_cell_idx, _PBENCH_cell)
        _PBENCH_report_on_fail(_PBENCH_ctx)
      if not _PBENCH_run_nb:
        sys.exit(0)
      continue
    elif _PBENCH_use_dias:
      ## Patt match and rewrite
      _DIAS_rewrite_start = time.perf_counter_ns()
      _DIAS_new_source, _ = dias.rewriter.rewrite_ast_from_source(_PBENCH_cell)
      _DIAS_rewrite_end = time.perf_counter_ns()
      _DIAS_rewrite_ns = _DIAS_rewrite_end - _DIAS_rewrite_start

      ## Execute
      _DIAS_exec_start = time.perf_counter_ns()
      _PBENCH_ip_run_res = _PBENCH_ipython.run_cell(_DIAS_new_source)
      _DIAS_exec_end = time.perf_counter_ns()
      _DIAS_exec_ns = _DIAS_exec_end - _DIAS_exec_start

      _PBENCH_cell_stats = dict()
      _PBENCH_cell_stats['raw'] = _PBENCH_cell
      _PBENCH_cell_stats['external_calls'] = PBENCH_HOOK.externalCallTimes
      _PBENCH_cell_stats['all_calls'] = PBENCH_HOOK.allCallCounts
      _PBENCH_cell_stats['total-ns'] = _DIAS_rewrite_ns + _DIAS_exec_ns
      _PBENCH_total_time_ns += _DIAS_rewrite_ns + _DIAS_exec_ns
      _PBENCH_cell_stats['rewritten'] = _DIAS_new_source
    else:
      _PBENCH_start = time.perf_counter_ns()
      _PBENCH_ip_run_res = _PBENCH_ipython.run_cell(_PBENCH_cell, silent=True)
      _PBENCH_end = time.perf_counter_ns()
      _PBENCH_diff_in_ns = _PBENCH_end - _PBENCH_start
      _PBENCH_cell_stats = dict()
      _PBENCH_cell_stats['raw'] = _PBENCH_cell
      _PBENCH_cell_stats['external_calls'] = PBENCH_HOOK.externalCallTimes
      _PBENCH_cell_stats['all_calls'] = PBENCH_HOOK.allCallCounts
      PBENCH_HOOK.externalCallTimes = {}
      PBENCH_HOOK.allCallCounts = {}
      _PBENCH_cell_stats['total-ns'] = _PBENCH_diff_in_ns
      _PBENCH_total_time_ns += _PBENCH_diff_in_ns
    
    if not _PBENCH_ip_run_res.success:
      _PBENCH_ctx = (_PBENCH_cell_idx, _PBENCH_cell)
      _PBENCH_report_on_fail(_PBENCH_ctx)

    modin_has_been_imported = "modin.pandas" in sys.modules
    if _PBENCH_measure_modin_mem and modin_has_been_imported:
      ray_sample = subprocess.run(["ray", "memory", "--stats-only"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      assert ray_sample.returncode == 0
      ray_sample_out = ray_sample.stdout.decode()
      match_disk = re.search("Spilled (\d+) MiB", ray_sample_out)
      if match_disk:
        _PBENCH_max_disk = _PBENCH_builtin_max(_PBENCH_max_disk, int(match_disk.group(1)))

    _PBENCH_max_mem = _PBENCH_builtin_max(_PBENCH_max_mem, _PBENCH_measure_mem())
    _PBENCH_cells.append(_PBENCH_cell_stats)

  _PBENCH_f = open(_PBENCH_times_file, 'w')
  _PBENCH_json_d = dict()
  _PBENCH_json_d['max-mem-in-mb'] = _PBENCH_max_mem // 1048576
  _PBENCH_json_d['max-mem-in-mb2'] = 0
  if _PBENCH_measure_modin_mem:
    _PBENCH_json_d['max-disk-in-mb'] = _PBENCH_max_disk
  elif _PBENCH_measure_koalas_mem:
    import time
    time.sleep(30)
    import pyspark
    context = pyspark.SparkContext.getOrCreate()
    appId = context.getConf().get('spark.app.id')
    import requests
    executors = requests.get(f'http://localhost:4040/api/v1/applications/{appId}/executors').json()
    assert len(executors) == 1
    diskUsed = executors[0]['diskUsed']
    _PBENCH_json_d['max-disk-in-mb'] = diskUsed // 1048576

  _PBENCH_json_d['cells'] = _PBENCH_cells
  _PBENCH_json_d['total-time-in-sec'] = _PBENCH_total_time_ns / 1e9
  json.dump(_PBENCH_json_d, _PBENCH_f, indent=2)
  _PBENCH_f.close()

if __name__ == '__main__':
  main()
