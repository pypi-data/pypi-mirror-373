"""Top-level package for lognflow."""

__author__ = 'Alireza Sadri'
__email__ = 'arsadri@gmail.com'
__version__ = '0.13.15'

from .lognflow import lognflow, getLogger
from .printprogress import printprogress
from .plt_utils import (
    np, plt, plt_imshow, plt_imhist, plt_hist2, plt_colorbar, 
    plt_imshow_series, plt_imshow_subplots)
from .utils import (select_directory, 
                    select_file, 
                    is_builtin_collection, 
                    text_to_collection, 
                    printv,
                    block_runner)

from .multiprocessor import multiprocessor

def basicConfig(*args, **kwargs):
    ...