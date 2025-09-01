## NOT YET IMPLEMENTED ##
# --------------------------------------------
# IMPORTS 
# --------------------------------------------

from collections import OrderedDict


def add_to(file):
  while True:
    y = (yield)
    with open(file, 'a') as f:
      f.write(y)

def log_cls_fn_exec(func):
  def inner(*arg, **kwarg):
    #
    try:
      gen_func = arg[0].g
    except:
      gen_func = None
      print(f'No logging defined. please check parent code..')
    #
    if gen_func:
      # before function
      gen_func.send(f"Debug: Starting function execution {func.__name__}(), with arguments {arg}, kw-arguments: {kwarg}\n")
    #
    # function execution
    result = func(*arg, **kwarg)
    #
    if gen_func:
      # after function
      gen_func.send(f"Debug: Done with {func.__name__} function with result : {result}\n")
    #
    return result
  return inner
