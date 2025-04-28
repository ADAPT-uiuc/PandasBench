import pandas as pd
import inspect
import traceback
import time
import types
import sys

funcs = []
newfuncs = []

externalCallTimes = {}
allCallCounts = {}
inCall = False

# This actually increases running time by _a lot_!
def _PandasBench_is_at_top_of_call_stack():
  current_frame = inspect.currentframe()
  caller_frame = current_frame.f_back
  stack = inspect.stack()

  # Check if the caller frame is the top frame in the stack
  stack_len = len(stack)
  # MAGIC_NUMBER = len(stack with a top-level call) - 1
  # 
  # TODO: We need a more reliable magic number, that works in different systems.
  # I'm not sure the stacks look the same in different systems.
  MAGIC_NUMBER = 19
  is_top = caller_frame == stack[stack_len - MAGIC_NUMBER].frame

  # Clean up to avoid reference cycles
  del current_frame, caller_frame, stack

  return is_top

def _make_prologue(attr):
  return f'''
  global inCall
  _PBENCH_start = None
  if _PandasBench_is_at_top_of_call_stack():
    if '{attr}' in allCallCounts:
      allCallCounts['{attr}'] += 1
    else:
      allCallCounts['{attr}'] = 1
    if not inCall:
      inCall = True
      _PBENCH_start = time.perf_counter_ns()
  '''

def _make_epilogue(attr):
  return f'''
  if _PBENCH_start is not None:
    _PBENCH_end = time.perf_counter_ns()
    if '{attr}' in externalCallTimes:
      externalCallTimes['{attr}'].append(_PBENCH_end - _PBENCH_start)
    else:
      externalCallTimes['{attr}'] = [_PBENCH_end - _PBENCH_start]
    inCall = False
  '''

def hookCalls(objStr, ignores):
  obj = eval(objStr)
  obj_name = objStr.replace('.', '_')
  for attr in dir(obj):
    if attr in ignores or attr.startswith('_'):
      continue
    func_name = obj_name+'__'+attr
    original_method = getattr(obj, attr)
    if type(original_method) == types.MethodType or type(original_method) == types.FunctionType:
      funcs.append(original_method)
      exec(f'''
def new_{func_name}_method(*args, **kwargs):
  {_make_prologue(func_name)}
  res = funcs[{len(funcs) - 1}](*args, **kwargs)
  {_make_epilogue(func_name)}
  return res
newfuncs.append(new_{func_name}_method)
{objStr}.{attr} = newfuncs[{len(newfuncs)}]
      ''', globals())
    elif type(original_method) == property:
      funcs.append(original_method)
      exec(f'''
def new_{func_name}_property(*args, **kwargs):
  {_make_prologue(func_name)}
  res = funcs[{len(funcs) - 1}].__get__(*args, **kwargs)
  {_make_epilogue(func_name)}
  return res
newfuncs.append(new_{func_name}_property)
{objStr}.{attr} = property(newfuncs[{len(newfuncs)}])
      ''', globals())

def hookPandas():
  hookCalls('pd.DataFrame', {'query', 'eval'})
  # `name` is used dynamically. We don't need it and it causes problems.
  hookCalls('pd.Series', {'name'})
  hookCalls('pd', {})
