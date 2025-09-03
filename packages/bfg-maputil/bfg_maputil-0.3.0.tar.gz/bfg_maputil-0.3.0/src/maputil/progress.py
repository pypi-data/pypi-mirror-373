in_notebook = False
try:
    from IPython import get_ipython  # type: ignore

    if get_ipython() is not None and "IPKernelApp" in get_ipython().config:
        in_notebook = True
except ImportError:
    pass

if in_notebook:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm
