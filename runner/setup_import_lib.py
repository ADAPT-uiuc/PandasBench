import os
import sys
import hook

def setup_import(lib: str, add_on: str, apply_hooks: bool):
  imports = {
    'pandas': ('''if True:
      import pandas as pd
      def evaluate_lazy(lazy):
        return lazy
    ''', hook.hookPandas),
    'modin': ('''if True:
      import os
      os.environ["MODIN_ENGINE"] = "ray"
      import ray
      ray.init(num_cpus=int(os.environ['MODIN_CPUS']), runtime_env={'env_vars': {'__MODIN_AUTOIMPORT_PANDAS__': '1'}})
      import modin.pandas as pd
      def evaluate_lazy(lazy):
        return lazy
    ''', None),
    'dask': ('''if True:
      import dask.dataframe as pd
      import dask.config
      dask.config.set(num_workers=int(os.environ['DASK_CPUS']))
      def evaluate_lazy(lazy):
        return lazy.compute()
    ''', None),
    'koalas': ('''if True:
      import pyspark.pandas as pd
      from pyspark import SparkContext
      SparkContext(f'local[{os.environ["KOALAS_CPUS"]}]')
      def evaluate_lazy(lazy):
        if isinstance(lazy, pd.DataFrame):
          lazy.to_spark().cache()
        return lazy
    ''', None)
  }
  add_ons = {
    'dias': 'import dias.rewriter'
  }
  if lib in imports:
    dynImports, libHooks = imports[lib]
    if add_on in add_ons:
      dynImports += '\n' + add_ons[add_on]
    os.environ['IREWR_IMPORTS'] = dynImports
    if libHooks is not None and apply_hooks:
      libHooks()
  else:
    print('Library', lib, 'not supported')
    sys.exit(1)

