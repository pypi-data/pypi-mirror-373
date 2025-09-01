""" lognflow

lognflow makes logging easy in Python. It is so simple you can code it 
yourself, so, why would you?!

lognflow logs all files into a directory by taking care of directories and 
files names. This saves you a lot of coding and makes your code readable
 when you say::

    logger = lognflow(logs_root = 'root_for_time_tagged_log_directories')
    logger.log_single('variables/variable1', variable1)
    logger('I just logged a variable.')
    
    another_logger = lognflow(log_dir = 'specific_dir')
    another_logger.log_plot('final_plot', final_plot_is_a_np_1d_array)

The next syntax is an easy way of just logging a numpy array. It will make
a new directory within the log_dir, called variables and make a npy file
named variable1 and put variable1 in it. The third line of the code above
prints the given text to the __call__ routine in the main txt file made in 
the log_dir.

As you can see, first you give it a root (logs_root) to make 
a log directory in it or give it the directory itself (log_dir). 
Then start dumping data by giving the variable name and the data with 
the type and you are set. 

Multiple processes in parallel can make as many instances as they want.

There is an option to keep the logged variables in memory for a long time and
then dump them when they reach a ceratin size. This reduces the network load.

for this the txt logs can be buffered for a chosable amount of time and 
numpy variables that don't change size can be buffered up to a certain size
before storing into the directory using log_var(name, var).

"""
import time
import atexit
import inspect
import copy
from   pathlib     import Path       as pathlib_Path
from   sys         import platform   as sys_platform
from   sys         import argv       as sys_argv
from   os          import system     as os_system
from   tempfile    import gettempdir
from   dataclasses import dataclass 
from   typing      import Union

import numpy             as np
import matplotlib.pyplot as plt

from   .utils      import (repr_raw,
                           replace_all,
                           select_directory,
                           name_from_file,
                           text_to_collection,
                           printv,
                           deepstr,
                           prepare_for_np_savez)
@dataclass
class varinlog:
    data_array          : np.ndarray      
    time_array          : np.ndarray    
    curr_index          : int
    file_start_time     : float          
    suffix              : str
    log_counter_limit   : int
    savefig             : bool
    plot_start_ago      : float
    plot_win_length     : float
    time_tag            : bool

@dataclass
class textinlog:
    to_be_logged        : str   
    log_fpath           : pathlib_Path         
    log_size_limit      : int 
    log_size            : int     
    last_log_flush_time : float
    log_flush_period    : int

class lognflow:
    """Initialization
        
        lognflow creates a directory called and puts all logs in there.
        
        Where?
        1: if logs_root is given, it makes a log_dir in it with a time_stamp.
        2: if log_dir is given, it uses it directly.        
        3: If you type::
            logger = lognflow()
        it will try to open a dialog to select a directory, if error occurs,
        it will get a temp directory from the os and continues.
        
        The lognflow allows setting global settings that can  be overridden
        later by calling each of its methods as follows.
    
        :param logs_root: 
            This is the root directory for all logs.
            We will use the time.time() to create a log directory for each 
            instance of the lognflow. 
        :type logs_root: pathlib.Path
        
        :param log_dir: 
            This is the final directory path for the log files. 
        :type log_dir: pathlib.Path
    
        :param log_prefix:
            this string will be put before the time tag for log_dir, when
            only logs_root is given.
        :type log_prefix: str
        
        :param log_suffix:
            if given, time tag will not be used and this string will be 
            put at the end of the log_dir name.
        :type log_prefix: str
        
        :param exist_ok:
            if False, if any logging directory exists, it raises an error.
        
        :param print_text: 
            If True, everything that is logged as text will be printed as well
        :type print_text: bool
        
        :param main_log_name: 
            main log file name, by default: 'main_log'
        :type main_log_name: str
                
        :param log_flush_period:
            The period between flushing the log files into HDD. By not
            flushing, you can reduce network or HDD overhead.
        :type log_flush_period: int
                
        :param time_tag:
            File names can carry time_tags in time.time() format or indices. This 
            is pretty much the most fundamental contribution of lognflow beside
            carrying the folders and files paths around. By default it is True and
            all file names will not have time tags if you set it to False. so,
            you can give time_tag argument for all logger functions, whose 
            default is this default. It can also be a string: options
            are 'index' or 'time_and_index'. If you use index, instead of time
            stamps, it will simply put an index that counts up after each logging.
        :type time_tag: bool
    """
    
    def __init__(self, 
                 logs_root        : pathlib_Path     = None,
                 log_dir          : pathlib_Path     = None,
                 log_dir_prefix   : str              = None,
                 log_dir_suffix   : str              = None,
                 exist_ok         : bool             = True,
                 time_tag         : Union[bool, str] = True,
                 print_text       : bool             = True,
                 main_log_name    : str              = 'log',
                 log_flush_period : int              = 10):
        atexit.register(self.flush_all)
        self._init_time = time.time()
        self.log_dir_prefix = log_dir_prefix
        self.log_dir_suffix = log_dir_suffix
        self.exist_ok = exist_ok
        
        self.time_tag = time_tag
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        if 'time_tag' in values and values['time_tag'] is not None:
            self._time_tag_provided = True
        else:
            self._time_tag_provided = False

        if(log_dir is None):
            if(logs_root is None):
                logs_root = gettempdir()
                try:
                    logs_root = select_directory(logs_root)
                except:
                    print('no logs_root was provided.'
                          + 'Could not open select_folder'
                          + f'So a folder from tmp is chosen: {logs_root}')
            new_log_dir_found = False
            while(not new_log_dir_found):
                log_dir_name = ''
                if(log_dir_prefix is not None):
                    log_dir_name = str(log_dir_prefix)
                if len(log_dir_name) > 0:
                    if log_dir_name[-1] != '_':
                        log_dir_name += '_'
                if(log_dir_suffix is None):
                    log_dir_name_ = log_dir_name + f'{int(self._init_time)}'
                    merging_log_dir = pathlib_Path(logs_root) / log_dir_name_
                    decimal_places = 0
                    while merging_log_dir.is_dir():
                        decimal_places += 1
                        if decimal_places > 3:
                            decimal_places = 3
                        self._init_time = time.time()
                        log_dir_name_ = log_dir_name + f'{self._init_time:.{decimal_places}f}'
                        merging_log_dir = pathlib_Path(logs_root) / log_dir_name_
                else:
                    log_dir_name += f'{log_dir_suffix}'
                    merging_log_dir = pathlib_Path(logs_root) / log_dir_name
                self.log_dir = merging_log_dir
                if(not self.log_dir.is_dir()):
                    new_log_dir_found = True
                else:
                    self._init_time = time.time()
            self.logs_root = logs_root
            self.log_dir_provided = False
        else:
            self.log_dir_provided = True
            self.log_dir = pathlib_Path(log_dir)

        self.logged = self
        
        self._print_text = print_text
        self._loggers_dict = {}
        self._vars_dict = {}
        self._single_var_call_cnt = 0

        self.log_name = main_log_name
        self.log_flush_period = log_flush_period
    
        self.log_dir_str = str(self.log_dir.absolute())
        self.enabled = True
        self.counted_vars = {}
        self.param_name_set = set()
        self.close = self.flush_all
        self.warning_log_dir = False
        
        #all depricated and will be removed in a few revisions
        self.log_text               = self.text
        self.log_text_flush         = self.text_flush
        self.log_var                = self.record
        self.log_var_flush          = self.record_flush
        self.log_plot               = self.plot
        self.log_hist               = self.hist
        self.log_scatter3           = self.scatter3
        self.log_surface            = self.surface
        self.log_hexbin             = self.hexbin
        self.log_imshow             = self.imshow
        self.log_imshow_by_subplots = self.imshow_subplots
        self.log_imshow_series      = self.imshow_series
        self.log_images_in_pdf      = self.images_to_pdf
        self.log_plt                = self.savefig
        self.log_torch_dict         = self.save_torch
        self.get_torch_dict         = self.load_torch
        self.log_single             = self.save
        self.get_single             = self.load
        self.get_var                = self.get_record

    def setLevel(self, level = 'info.txt'):
        self.log_name = level
        
    def assert_log_dir(self):
        if (not self.log_dir.is_dir()) & (not self.warning_log_dir):
            self.warning_log_dir = True
            print('~'*30, 'WARNING', '~'*30)
            if self.log_dir_provided:
                print(f'lognflow.logdir: No such directory: ')
                print({self.log_dir})
            elif self.logs_root.is_dir():
                self.log_dir = self.logs_root
                print('lognflow Warning: You read from the provided logs_root:')
                print(self.logs_root)
                print('to read from a log, use log_dir as the input argument:')
                print(f'logger = lognflow(log_dir = {self.log_dir}')
                print('I will assume that this logs_root is log_dir from now on')
            else:
                print('You should provide log_dir when initializing lognflow '
                      'if you wish to read the stored data first as follows:')
                print(f'logger = lognflow(log_dir = LOG_DIR_PATH')
            print('~'*67)
            return False

    def disable(self):
        self.enabled = False
        
    def enable(self):
        self.enabled = True
    
    def log_code(self, code_fpath = None):
        """ log code, pass __file__
        """
        if code_fpath is None:
            code_fpath = sys_argv[0]
        code_fpath = pathlib_Path(code_fpath)
        self.copy(code_fpath.name, code_fpath)
    
    def name_from_file(self, fpath):
        """ 
            Given an fpath inside the logger log_dir, 
            what would be its equivalent parameter_name?
        """
        return name_from_file(self.log_dir_str, fpath)
    
    def file_from_name(self, parameter_name):
        """ file from name
            given a parameter_name, it returns log_dir / parameter_name
        """
        return self.log_dir / parameter_name
    
    def copy(self, parameter_name = None, source = None, suffix = None,
             time_tag = False):
        """ copy into a new file
            Given a parameter_name, the second argument will be copied into
            the first. We will try syntaxes os_system('cp') and 'copy' for
            Windows.
            
            :param parameter_name: str
                examples: myvar or myscript/myvar
                parameter_name can be just a name e.g. myvar, or could be a
                path like name such as myscript/myvar.
            :param source: str
                if source.is_file() then it is copied into its new location.
                Otherwise, we use logger.get_flist(source, suffix) to 
                obtain a list of files matching the source and copy them into
                their new location.
        """
        if not self.enabled: return
        arg_err_msg = 'when using copy, the first argument is the final name '\
                      ' after copy is finished. The second argument is ' \
                      ' the absolute path of source file, str(fpath.absolute())'
        if parameter_name is None:
            parameter_name = ''
        else:
            assert parameter_name == str(parameter_name), arg_err_msg

        flist = []
        try:
            source_as_fpath = pathlib_Path(source)
            if source_as_fpath.is_dir():
                fpath_dest = self.log_dir / (parameter_name + source_as_fpath.stem)
                if sys_platform in ["linux", "linux2", "darwin"]:
                    os_system(f'cp -r {source_as_fpath} {fpath_dest}')
                elif sys_platform == "win32":
                    os_system(f'xcopy {source_as_fpath} {fpath_dest} /E /I /Y')
                return fpath_dest
            
            elif source_as_fpath.is_file():
                flist = [source_as_fpath]
            else:
                raise ValueError
        except:
            try:
                flist = self.get_flist(source, suffix)
            except Exception as e:
                print(str(e))
        assert flist, \
            'source could not be found to copy. \n' + arg_err_msg

        for fpath in flist:
            if len(parameter_name) == 0:
                parameter_name = fpath.name
            
            param_dir, param_name, suffix = self._param_dir_name_suffix(
                parameter_name, suffix)

            if len(param_name) == 0:
                new_param_name = fpath.stem
            else:
                new_param_name = param_name
            if suffix is None:
                suffix = fpath.suffix
            fpath_dest = self._get_fpath(
                param_dir, new_param_name, suffix, time_tag)
            
            if sys_platform in ["linux", "linux2", "darwin"]:
                os_system(f'cp {fpath} {fpath_dest}')
            elif sys_platform == "win32":
                os_system(f'copy {fpath} {fpath_dest}')
        return fpath_dest
            
    @property
    def time_stamp(self):
        """ Current time stamp
            Gives the time after the start of the lognflow
        """
        return time.time() - self._init_time
    
    def rename(self, new_name:str, append: bool = False):
        """ renaming the log directory
            It is possible to rename the log directory while logging is going
            on. This is particulary useful when at the end of an experiment,
            it is necessary to put some variables in the name of the directory,
            which is very realistic in the eyes of an experimentalist.
            
            There is only one input and that is the new name of the directory.

            :param new_name: The new name of the directory (without parent path)
            :type new_name: str
            
            :param append: keep the time tag for the folder and 
                append it to the right side of the new name. Default: False.
            :type append: bool
            
        """
        if not self.enabled: return
        
        self.flush_all()
        if(append):
            log_dir_name = ''
            if(self.log_dir_prefix is not None):
                log_dir_name = str(self.log_dir_prefix)
            if len(log_dir_name) > 0:
                if log_dir_name[-1] != '_':
                    log_dir_name += '_'
            if(self.log_dir_suffix is None):
                log_dir_name_with_suffix = log_dir_name + f'{self._init_time}'
            else:
                log_dir_name_with_suffix = \
                    log_dir_name + f'{self.log_dir_suffix}'
            if self.log_dir.name == log_dir_name_with_suffix:
                log_dir_name += new_name
                if log_dir_name[-1] != '_':
                    log_dir_name += '_'
                if(self.log_dir_suffix is None):
                    log_dir_name += f'{self._init_time}'
                else:
                    log_dir_name += f'{self.log_dir_suffix}'
            else:
                log_dir_name = self.log_dir.name + '_' + new_name
        else:
            log_dir_name = new_name        
        new_dir = self.log_dir.parent / log_dir_name
        try:
            self.log_dir = self.log_dir.rename(new_dir)
            for log_name in list(self._loggers_dict):
                curr_textinlog = self._loggers_dict[log_name]
                curr_textinlog.log_fpath = \
                    self.log_dir /curr_textinlog.log_fpath.name
        except:
            self.text(None, 'Could not rename the log_dir from:')
            self.text(None, f'{self.log_dir.name}')
            self.text(None, 'into:')
            self.text(None, f'{new_name}')
            self.text(None, 'Most probably a file was open.')
        return self.log_dir
    
    def _param_dir_name_suffix(self, parameter_name: str, suffix: str = None):
        
        assert isinstance(parameter_name, str), \
            f'lognflow: The parameter name {parameter_name} is not a string.' \
            + f' It is of type {type(parameter_name)}.' \
            + 'Perhaps you forgot to pass the name of the variable first.'
        parameter_name = ''.join(
            [_ for _ in repr(repr_raw(parameter_name))  if _ != '\''])
        parameter_name = replace_all(parameter_name, ' ', '_')
        parameter_name = replace_all(parameter_name, '\\', '/')
        parameter_name = replace_all(parameter_name, '//', '/')
        
        if(parameter_name[-1] == '/'):
            param_name = ''
            param_dir = parameter_name
        else:
            parameter_name_split = parameter_name.split('/')
            if len(parameter_name_split) == 1:
                param_name = parameter_name
                param_dir = ''
            else:
                param_name = parameter_name_split[-1]
                param_dir = '/'.join(parameter_name_split[:-1])

        if(suffix == 'mat'):
            if(len(param_name) == 0):
                param_dir_split = param_dir.split('/')
                if param_dir_split[-1] == '/':
                    param_name = param_dir_split[-2]
                else:
                    param_name = param_dir_split[-1]
                    
        if(suffix is None):
            param_name_split = param_name.split('.')
            if len(param_name_split) > 1:
                param_suffix = param_name_split[-1]
                #Here you can check if it is a valid extention
                param_name = '.'.join(param_name_split[:-1])
            else:
                param_suffix = None
        else:
            param_suffix = suffix
            param_name_split = param_name.split('.')
            if len(param_name_split) > 1:
                fname_suffix = param_name_split[-1]
                if fname_suffix == param_suffix:
                    param_name = '.'.join(param_name_split[:-1])
    
        return(param_dir, param_name, param_suffix)

    def _get_fpath(self, param_dir: pathlib_Path, param_name: str = None, 
                   suffix: str = None, time_tag: bool = None) -> pathlib_Path:
        
        if time_tag is None:
            if self._time_tag_provided:
                time_tag = self.time_tag
            elif param_name in self.param_name_set:
                time_tag = True 

        assert isinstance(time_tag, (bool, str)), \
            'Argument time_tag must be a boolean or a string.'

        if time_tag == True:
            index_tag = False
        elif time_tag == False:
            index_tag = False
        elif (time_tag.lower() == 'index'):
            time_tag = False
            index_tag = True
        elif (time_tag.lower() == 'time_and_index'):
            time_tag = True
            index_tag = True
        
        _param_dir = self.log_dir / param_dir
        if(not _param_dir.is_dir()):
            _param_dir.mkdir(parents = True, exist_ok = self.exist_ok)

        if param_name is None:
            return _param_dir
        else:
            self.param_name_set.add(param_name)

            if index_tag:
                var_fullname = param_dir + '/' + param_name
                self.counted_vars[var_fullname] = self.counted_vars.get(
                    var_fullname, 0) + 1
                index_tag_str = str(self.counted_vars[var_fullname])

                if(len(param_name) > 0):
                    param_name += '_' + index_tag_str
                else:
                    param_name = index_tag_str
            
            if time_tag:
                param_name_before_time_stamp = copy.copy(param_name)
                time_stamp_str = f'{int(self.time_stamp)}'
                if(len(param_name) > 0):
                    param_name += '_' + time_stamp_str
                else:
                    param_name += time_stamp_str
    
            if(suffix is None):
                fpath = _param_dir / param_name
            else:
                while suffix[0] == '.':
                    suffix = suffix[1:]
                fpath = _param_dir / (param_name + '.' + suffix)

            if time_tag:
                while fpath.is_file():
                    param_name = copy.copy(param_name_before_time_stamp)
                    time_stamp_str = f'{self.time_stamp:.3f}'
                    if(len(param_name) > 0):
                        param_name += '_' + time_stamp_str
                    else:
                        param_name += time_stamp_str
            
                    if suffix is None:
                        fpath = _param_dir / param_name
                    else:
                        while suffix[0] == '.': suffix = suffix[1:]
                        fpath = _param_dir / (param_name + '.' + suffix)
            
            return fpath
        
    def _get_dirnamesuffix(self, param_dir, param_name, suffix):
        log_dirnamesuffix = param_name
        if(len(param_dir) > 0):
            log_dirnamesuffix = param_dir + '/' + log_dirnamesuffix
        if(len(suffix) > 0):
            log_dirnamesuffix = log_dirnamesuffix + '.' + suffix
        return log_dirnamesuffix
            
    def _text_handler(self, log_name: str, 
                         log_size_limit: int = int(1e+7),
                         time_tag: bool = None,
                         log_flush_period = None,
                         suffix = None):
        
        if (log_flush_period is None):
            log_flush_period = self.log_flush_period
        param_dir, param_name, suffix = self._param_dir_name_suffix(
            log_name, suffix)
        if suffix is None:
            suffix = 'txt'
        
        log_dirnamesuffix = self._get_dirnamesuffix(
            param_dir, param_name, suffix)
        
        fpath = self._get_fpath(param_dir, param_name, suffix, time_tag)
        self._loggers_dict[log_dirnamesuffix] = textinlog(
            to_be_logged=[],      
            log_fpath=fpath,         
            log_size_limit=log_size_limit,    
            log_size=0,          
            last_log_flush_time=0,
            log_flush_period=log_flush_period)  

    def text_flush(self, log_name = None, flush = False, suffix = None):
        """ Flush the text logs
            Writing text to open(file, 'a') does not constantly happen on HDD.
            There is an OS buffer in between. This funciton should be called
            regularly. lognflow calls it once in a while when text is
            called multiple times. but use needs to also call it once in a
            while.
            In later versions, a timer will be used to call it automatically.
            :param flush:
                force the flush regardless of when the last time was.
                default: False
            :type flush: bool
        """
        if not self.enabled: return
        log_name = self.log_name if (log_name is None) else log_name
        
        param_dir, param_name, suffix = self._param_dir_name_suffix(
            log_name, suffix)
        if suffix is None:
            suffix = 'txt'
        log_dirnamesuffix = self._get_dirnamesuffix(
            param_dir, param_name, suffix)
        
        curr_textinlog = self._loggers_dict[log_dirnamesuffix]
        
        if((self.time_stamp - curr_textinlog.last_log_flush_time \
                                           > curr_textinlog.log_flush_period)
           | flush):
            
            with open(curr_textinlog.log_fpath, 'a+') as f:
                f.writelines(curr_textinlog.to_be_logged)
                f.flush()
            curr_textinlog.to_be_logged = []
            curr_textinlog.last_log_flush_time = self.time_stamp

    def text(self, 
                 log_name: str = None,
                 to_be_logged = '', 
                 log_time_stamp = True,
                 print_text = None,
                 log_size_limit: int = int(1e+7),
                 time_tag: bool = None,
                 log_flush_period: int = None,
                 flush = False,
                 end = '\n',
                 new_file = False,
                 suffix = None):
        """ log a string into a text file
            You can shose a name for the log and give the text to put in it.
            Also you can pass a small numpy array. You can ask it to put time
            stamp in the log and in the log file name, you can disable
            printing the text. You can set the log size limit to split it into
            another file with a new time stamp.
            
            :param log_name: str
                   examples: mylog or myscript/mylog
                   log_name can be just a name e.g. mylog, or could be a
                   pathlike name such as myscript/mylog.
            :param to_be_logged: str, nd.array, list, dict
                   the string to be logged, could be a list
                   or numpy array or even a dictionary. It uses str(...).
            :param log_time_stamp: bool
                   Put time stamp for every entry of the log
            :param print_text: bool
                   if False, what is logged will not be printed.
            :param log_size_limit: int
                   log size limit in bytes.
            :param time_tag: bool
                   put time stamp in file names.
            :param log_flush_period: int
                   How often flush the log in seconds, if time passes this
                   given period, it will flush the first time a text is logged,
                   or if the logger is finilized.
            :param flush: bool
                   force flush into the log file
            :param end: str
                   The last charachter for this call.
            :param new_file: bool
                   if a new file is needed. If time_tag is True, it will make
                   a new file with a new name that has a time tag. If False,
                   it closees the current text file and overwrites on it.
            :param suffix: str
                   suffix is the extension of the file name.
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
        log_flush_period = self.log_flush_period \
            if (log_flush_period is None) else log_flush_period
        log_name = self.log_name if (log_name is None) else log_name

        param_dir, param_name, suffix = self._param_dir_name_suffix(
            log_name, suffix)
        if suffix is None:
            suffix = 'txt'
        log_dirnamesuffix = self._get_dirnamesuffix(
            param_dir, param_name, suffix)

        if ( (not (log_dirnamesuffix in self._loggers_dict)) or new_file):
            self._text_handler(log_dirnamesuffix, 
                                   log_size_limit = log_size_limit,
                                   time_tag = time_tag,
                                   suffix = suffix)

        if((print_text is None) | (print_text is True)):
            print_text = self._print_text
        if(print_text):
            if(log_time_stamp):
                print(f'T:{self.time_stamp:>6.6f}| ', end='')
            print(to_be_logged, end = end)

        curr_textinlog = self._loggers_dict[log_dirnamesuffix]
        _logger = []
        if(log_time_stamp):
            _time_str = f'T:{self.time_stamp:>6.6f}| '
            _logger.append(_time_str)
        if(isinstance(to_be_logged, list)):
            for _ in to_be_logged:
                _tolog = str(_)
                _logger.append(_tolog)
        else:
            _tolog = str(to_be_logged)
            _logger.append(_tolog)
        if(len(_logger[-1]) > 0):
            if(_logger[-1][-1] != end):
                _logger.append(end)
        else:
            _logger.append(end)
        log_size = 0
        for _logger_el in _logger:
            curr_textinlog.to_be_logged.append(_logger_el)
            log_size += len(_logger_el)
        curr_textinlog.log_size += log_size
        
        self.text_flush(log_dirnamesuffix, flush)        

        if(log_size >= curr_textinlog.log_size_limit):
            self._text_handler(
                log_dirnamesuffix, 
                log_size_limit = curr_textinlog.log_size_limit,
                time_tag = curr_textinlog.time_tag,
                suffix = suffix)
            curr_textinlog = self._loggers_dict[log_dirnamesuffix]
        return curr_textinlog.log_fpath
                        
    def _get_log_counter_limit(self, param, log_size_limit):
        cnt_limit = int(log_size_limit/(param.size*param.itemsize))
        return cnt_limit

    def record(self, parameter_name: str, parameter_value, flush = False,
                suffix = None, log_size_limit: int = int(1e+8), savefig = False,
                plot_start_ago = None, plot_win_length = 10, time_tag = False):
        """log a numpy array in buffer then dump
            It can be the case that we need to take snapshots of a numpy array
            over time. The size of the array would not change and this is hoing
            to happen frequently.
            This log_ver makes a buffer in RAM and keeps many instances of the
            array along with their time stamp and then when the size of the 
            array reaches a threhshold flushes it into HDD with a file that
            has an initial time stamp.
            The benefit of using this function over save is that it
            does not use the connection to the directoy all time and if that is
            on a network, there will be less overhead.
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param parameter_value: np.array
                    An np array whose size doesn't change
            :param suffix: str
                    can be 'npz' or 'txt' which will save it as text.
            :param log_size_limit: int
                    log_size_limit in bytes, default: 1e+8.
                    
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
        try:
            _ = parameter_value.shape
        except:
            parameter_value = np.array([parameter_value])
        
        param_dir, param_name, suffix = self._param_dir_name_suffix(
            parameter_name, suffix)
        if(suffix is None):
            suffix = 'npz'
        log_dirnamesuffix = self._get_dirnamesuffix(
            param_dir, param_name, suffix)
        
        log_counter_limit = self._get_log_counter_limit(\
            parameter_value, log_size_limit)

        if(log_dirnamesuffix in self._vars_dict):
            _var = self._vars_dict[log_dirnamesuffix]
            data_array, time_array, curr_index, \
                file_start_time, suffix, log_counter_limit = \
                    (_var.data_array, _var.time_array, _var.curr_index, \
                    _var.file_start_time, _var.suffix, _var.log_counter_limit)
            curr_index += 1
        else:
            file_start_time = self.time_stamp
            curr_index = 0

        if(curr_index >= log_counter_limit):
            self.record_flush(log_dirnamesuffix, **flush_kwargs)
            file_start_time = self.time_stamp
            curr_index = 0
        elif flush:
            self.record_flush(log_dirnamesuffix, **flush_kwargs)

        if(curr_index == 0):
            data_array = np.zeros((log_counter_limit, ) + parameter_value.shape,
                                  dtype = parameter_value.dtype)
            time_array = np.zeros(log_counter_limit)
        
        try:
            time_array[curr_index] = self.time_stamp
        except: pass
        if(parameter_value.shape == data_array[curr_index].shape):
            data_array[curr_index] = parameter_value
        else:
            data_array[curr_index] = data_array[curr_index - 1] * 0 + np.nan
        
        self._vars_dict[log_dirnamesuffix] = varinlog(data_array, 
                                                      time_array, 
                                                      curr_index,
                                                      file_start_time,
                                                      suffix,
                                                      log_counter_limit,
                                                      savefig,
                                                      plot_start_ago,
                                                      plot_win_length,
                                                      time_tag)

    def record_flush(self, parameter_name: str, suffix: str = None):
        """ Flush the buffered numpy arrays
            If you have been using log_ver, this will flush all the buffered
            arrays. It is called using log_size_limit for a variable and als
            when the code that made the logger ends.
            :param parameter_name: str
                examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
        """
        if not self.enabled: return
        param_dir, param_name, suffix = self._param_dir_name_suffix(
            parameter_name, suffix)
        if(suffix is None):
            suffix = 'npz'
        log_dirnamesuffix = self._get_dirnamesuffix(
            param_dir, param_name, suffix)
        
        _param_dir = self._get_fpath(param_dir)
        
        _var = self._vars_dict[log_dirnamesuffix]
        savefig  = _var.savefig
        time_tag = _var.time_tag
        _var_data_array = _var.data_array[_var.time_array > 0]
        _var_time_array = _var.time_array[_var.time_array > 0]
        
        if _var.suffix == 'npz':
            fpath = _param_dir / f'{param_name}_{_var.file_start_time:.6f}.npz'
            np.savez(fpath,
                time_array = _var_time_array,
                data_array = _var_data_array)
        else:
            fpath = _param_dir / f'{param_name}_time_{_var.file_start_time:.6f}.txt'
            np.savetxt(fpath, _var_time_array)
            fpath = _param_dir / f'{param_name}_data_{_var.file_start_time:.6f}.txt'
            np.savetxt(fpath, _var_data_array)
        
        _var_data_array = _var_data_array.squeeze()
        if savefig & (len(_var_data_array.squeeze().shape) == 1):
            plot_start_ago = _var.plot_start_ago
            plot_win_length = _var.plot_win_length

            tmax = _var_time_array.max()

            if plot_start_ago is None:
                plot_start_ago = 0
                
            if plot_start_ago < len(_var_time_array):
                _var_time_array = _var_time_array[plot_start_ago:]
                _var_data_array = _var_data_array[plot_start_ago:]
                
                from .plt_utils import plt_plot
                fig_ax = plt_plot(
                    [_var_data_array], '.', x_values_list = [_var_time_array])
                n_stamps = len(_var_time_array)
                if (n_stamps > 4) & (plot_win_length is not None):
                    n_wins = int(n_stamps // plot_win_length)
                    ending = plot_win_length * n_wins
                    v1 = _var_data_array[
                        :ending].reshape(n_wins, plot_win_length).mean(1)
                    t1 = _var_time_array[
                        :ending].reshape(n_wins, plot_win_length).mean(1)
                    fname = f'{param_dir}/{param_name}_{_var.file_start_time:.6f}'
                    self.plot(fname, 
                              [v1], '--',fig_ax = fig_ax, x_values_list = [t1],
                              time_tag = time_tag)
        return fpath
    
    def get_record(self, parameter_name: str, suffix: str = None) -> tuple:
        """ Get the buffered numpy arrays
            If you need the buffered variable back.
            :param parameter_name: str
                examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            
            :return: 
                A tuple including two np.ndarray. The first on is 1d time
                and the second one is nd buffered data.
            :rtype: 
                tuple of two nd.arrays
        
        """
        if not self.enabled: return
        param_dir, param_name, suffix = self._param_dir_name_suffix(
            parameter_name, suffix)
        if(suffix is None):
            suffix = 'npz'
        log_dirnamesuffix = self._get_dirnamesuffix(
            param_dir, param_name, suffix)
        
        _var = self._vars_dict[log_dirnamesuffix]
        data_array = _var.data_array[_var.time_array>0].copy()
        time_array = _var.time_array[_var.time_array>0].copy()
        return(time_array, data_array)

    def save(self, parameter_name: str, 
                   parameter_value,
                   suffix = None,
                   mat_field = None,
                   time_tag: bool = None):
        """log a single variable
            The most frequently used function would probably be this one.
            
            if you call the logger object as a function and give it a parameter
            name and something to be logged, the __call__ referes to this
            function.
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param parameter_value: np.array
                    Could be anything and np.save will be used. If it is a
                    dictionary, np.savez will be used. As you may know, np.save
                    can save all pickalables.
            :param suffix: str
                    can be 'npz', 'npy', 'mat', 'pth' for pytorch models
                    or 'txt' or anything else which will save it as text.
                    This includes 'json', 'pdb', or ...
            :param mat_field: str
                    when saving as 'mat' file, the field can be set.
                    otherwise it will be the parameter_name
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
                    
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
        
        if ((not '.' in parameter_name) 
            & (suffix is None) 
            & isinstance(parameter_value, np.ndarray) ):
            suffix = 'npy'

        param_dir, param_name, suffix = self._param_dir_name_suffix(
            parameter_name, suffix)
        if(suffix is None):
            if isinstance(parameter_value, (np.ndarray, int, float)):
                suffix = 'npy'
            elif (isinstance(parameter_value, dict)):
                suffix = 'npz'
            else:
                suffix = 'txt'
        fpath = self._get_fpath(param_dir, param_name, suffix, time_tag)
        
        try:
            if(suffix == 'npy'):
                np.save(fpath, parameter_value)
            elif(suffix == 'npz'):
                parameter_value_dict = prepare_for_np_savez(parameter_value)
                np.savez(fpath, **parameter_value_dict)
            elif((suffix == 'tif') | (suffix == 'tiff')):
                from tifffile import imwrite
                imwrite(fpath, parameter_value)
            elif(suffix == 'mat'):
                from scipy.io import savemat
                if(mat_field is None):
                    if isinstance(parameter_value, dict):
                        savemat(fpath, parameter_value)
                    else:
                        mat_field = param_name
                if(mat_field is not None):
                    savemat(fpath, {f'{mat_field}':parameter_value})
            elif(suffix == 'pth'):
                from torch import save as torch_save
                torch_save(parameter_value, fpath)
            elif(suffix == 'json'):
                import json
                obj_str = deepstr(parameter_value)
                with open(fpath,'a') as fdata: 
                    json.dump(obj_str, fdata)
            else:
                with open(fpath,'a') as fdata: 
                    fdata.write(str(parameter_value))
        except Exception as e:
            fpath = None
            print(f"An error occurred: {e}")
        return fpath
    
    def savefig(self, 
                parameter_name: str, 
                image_format='jpg', dpi=1200,
                time_tag: bool = None,
                close_plt = True):
        """log a single plt
            log a plt that you have on the screen.
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
                    
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
            
        param_dir, param_name, image_format = \
            self._param_dir_name_suffix(parameter_name, image_format)
        fpath = self._get_fpath(param_dir, param_name, image_format, time_tag)
        
        try:
            plt.savefig(fpath, format=image_format, dpi=dpi,
                        bbox_inches='tight')
            if(close_plt):
                plt.close()
            return fpath
        except:
            if(close_plt):
                plt.close()
            self.text(
                None, f'Cannot save the plt instance {parameter_name}.')
            return None
    
    def plot(self, parameter_name: str, 
                   parameter_value_list,
                   *plt_plot_args,
                   x_values_list = None,
                   image_format='jpg',
                   dpi=1200,
                   title = None,
                   time_tag: bool = None,
                   fig_ax = None,
                   return_figure = False,
                   **kwargs):
        """log a single plot
            If you have a numpy array or a list of arrays (or indexable by
            first dimension, an array of 1D arrays), use this to log a plot 
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param parameter_value_list: np.array
                    An np array or a list of np arrays or indexable-by-0th-dim
                    np arrays
            :param x_values_list: np.array
                    if set, must be a list of one or many np.array of same size of 
                    all y values or a list for each vector in y values where 
                    every element of x-values list is the same as the 
                    y-values element in their list
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
                    
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
        from .plt_utils import plt_plot
        plt_plot(
            parameter_value_list, *plt_plot_args, 
            x_values_list = x_values_list, fig_ax = fig_ax, **kwargs)
            
        if not return_figure:
            fpath = self.savefig(
                parameter_name = parameter_name, 
                image_format=image_format, dpi=dpi,
                time_tag = time_tag)
            return fpath
        else:
            return fig, ax
    
    def printv(self, *args, **kwargs):
        if 'logger' in kwargs:
            kwargs.pop('logger')
        printv(*args, logger = self, **kwargs)
    
    def hist(self, parameter_name: str, 
                   parameter_value_list,
                   bins = 10,
                   alpha = 0.5,
                   labels_list = None,
                   normalize = False,
                   image_format='jpg', 
                   dpi=1200, 
                   title = None,
                   time_tag = None, 
                   return_figure = False,
                   **kwargs):
        """log a single histogram
            If you have a numpy array or a list of arrays (or indexable by
            first dimension, an array of 1D arrays), use this to log a hist
            if multiple inputs are given they will be plotted on top of each
            other using the alpha opacity. 
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param parameter_value_list: np.array
                    An np array or a list of np arrays or indexable-by-0th-dim
                    np arrays
            :param bins: number or np.array
                    used to set the bins for making of the histogram
            :param alpha: float 
                    the opacity of histograms, a flot between 0 and 1. If you
                    have multiple histograms on top of each other,
                    use 1/number_of_your_variables.
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
                    
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
            
        from .plt_utils import plt_hist
        fig, ax = plt_hist(parameter_value_list, 
                           bins = bins, alpha = alpha, 
                           normalize = normalize, 
                           labels_list = labels_list, **kwargs)
        if title is not None:
            ax.set_title(title)
        if not return_figure:
            fpath = self.savefig(
                parameter_name = parameter_name, 
                image_format=image_format, dpi=dpi,
                time_tag = time_tag)
            return fpath
        else:
            return fig, ax
    
    
    def scatter3(self, parameter_name: str,
                     data_N_by_3,
                     elev_list = None,
                     azim_list = None,
                     image_format='jpg', 
                     dpi=300,
                     title = None,
                     time_tag: bool = None, 
                     return_figure = False,
                     make_animation = False,
                     log_animation_kwargs = {},
                     **kwargs):
        """log a single scatter in 3D
            Scatter plotting in 3D
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param data_N_by_3: np.array
                    An np array of size 3 x n, to sctter n data points in 3D
            :param elev_list: list
                    Must be an iterable even if has only one number for elev
            :param azim_list: list
                    Must be an iterable even if has only one number for azim
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
                    
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag

        if data_N_by_3.shape[0] == 3:
            if data_N_by_3.shape[1] != 3:
                data_N_by_3 = data_N_by_3.T
                self.text(
                    None, 'lognflow.scatter3> input dataset is transposed.')
        from .plt_utils import plt_scatter3
        fig_ax_opt_stack = plt_scatter3(data_N_by_3, title = title,
                     elev_list = elev_list, azim_list = azim_list,
                     make_animation = make_animation, **kwargs)
            
        if not return_figure:
            if make_animation:
                self.log_animation(parameter_name, fig_ax_opt_stack[2], 
                                   dpi=dpi, time_tag = time_tag,
                                   **log_animation_kwargs) 
            else:
                return self.savefig(
                    parameter_name = parameter_name, 
                    image_format = image_format, dpi=dpi,
                    time_tag = time_tag)
        else:
            return fig_ax_opt_stack
    
    def surface(self, parameter_name: str,
                       parameter_value, image_format='jpg', 
                       dpi=1200, title = None,
                       time_tag: bool = None, return_figure = False, **kwargs):
        """log a surface in 3D
            surface plotting in 3D exactly similar to imshow but in 3D
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param parameter_value: np.array
                    An np array of size n x m, to plot surface in 3D
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
            rest of the parameters (**kwargs) will be passed to plot_surface() 
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
            
        from .plt_utils import plt_surface
        fig, ax = plt_surface(parameter_value)
        
        if title is not None:
            ax.set_title(title)
            
        if not return_figure:
            fpath = self.savefig(
                parameter_name = parameter_name, 
                image_format=image_format, dpi=dpi,
                time_tag = time_tag)
            return fpath
        else:
            return fig, ax
    
    def hexbin(self, parameter_name: str, parameter_value,
                   gridsize = 20, image_format='jpg', dpi=1200, title = None,
                   time_tag: bool = None, return_figure = False):
        """log a 2D histogram 
            The 2D histogram is made out of hexagonals
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param parameter_value: np.array
                    An np array of size 2 x n, to make the 2D histogram
            :param gridsize: int
                    grid size is the number of bins in 2D
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hexbin(parameter_value[0], 
                   parameter_value[1], 
                   gridsize = gridsize)
        if title is not None:
            ax.set_title(title)
            
        if not return_figure:
            fpath = self.savefig(
                    parameter_name = parameter_name, 
                    image_format=image_format, dpi=dpi,
                    time_tag = time_tag)
            return fpath
        else:
            return fig, ax
    
    def imshow(self, 
                   parameter_name: str, 
                   parameter_value, 
                   frame_shape : tuple = None,
                   colorbar = True,
                   remove_axis_ticks = True,
                   image_format='jpg', dpi=1200, cmap = 'viridis',
                   title = None, time_tag: bool = None, borders = 0, 
                   return_figure = False, figsize = None, **kwargs):
        """log an image
            The image is logged using plt.imshow
            Accepted shapes are:
                * (n, m) 
                * (n, m,  3)
                * (n_im, n_r, n_c)
                * (n_im, n_r,  3,  1)
                * (n_im, n_r, n_c, 3)
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param parameter_value: np.array
                    An np array of shape amongst the following:
                    * (n, m) 
                    * (n, m,  3)
                    * (n_im, n_r, n_c)
                    * (n_im, n_r,  3,  1)
                    * (n_im, n_r, n_c, 3)
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
            
        parameter_value_shape = parameter_value.shape
        n_dims = len(parameter_value_shape)
        
        FLAG_img_ready = False
        use_stack_to_frame = False
        if(n_dims == 2):
            FLAG_img_ready = True
        elif(n_dims == 3):
            if(parameter_value_shape[2] != 3):
                use_stack_to_frame = True
            else:
                #warning that 3 dimensions as the last axis is RGB
                FLAG_img_ready = True
        elif(n_dims == 4):
                use_stack_to_frame = True
        
        if(use_stack_to_frame):
            from .plt_utils import stack_to_frame
            parameter_value = stack_to_frame(
                parameter_value, frame_shape = frame_shape, 
                borders = borders)
            if parameter_value is not None:
                FLAG_img_ready = True

        if(FLAG_img_ready):
            from .plt_utils import plt_imshow
            plt_imshow(parameter_value, 
                       colorbar = colorbar, 
                       remove_axis_ticks = remove_axis_ticks, 
                       title = title,
                       cmap = cmap,
                       figsize = figsize,
                       **kwargs)
                
            if not return_figure:
                fpath = self.savefig(
                        parameter_name = parameter_name, 
                        image_format=image_format, dpi=dpi,
                        time_tag = time_tag)
                return fpath
            else:
                return fig, ax
        else:
            self.text(
                self.log_name,
                f'Cannot imshow variable {parameter_name} with shape' + \
                f'{parameter_value.shape}')
            return

    def imshow_subplots(self, 
        parameter_name: str, 
        images: np.ndarray,
        frame_shape = None,
        grid_locations = None,
        figsize = None,
        image_format='jpg', 
        dpi=1200, 
        time_tag: bool = None,
        colorbar = False,
        remove_axis_ticks = True,
        titles = None,
        cmaps = None,
        return_figure = False,
        **kwargs):
        """log multiple images in a tiled frame
            The frame image is logged using plt.imshow
            
            Accepted shapes are:
                * (n, m) 
                * (n, m,  3)
                * (n_im, n_r, n_c)
                * (n_im, n_r,  3,  1)
                * (n_im, n_r, n_c, 3)
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param images: np.array
                    An np array of size n_f x n_r x n_c, to be shown by imshow
                    as a square tile of side length of n_ch**0.5
            :param frame_shape:
                n_f images will be tiles according to thi tuple as shape.
            :param grid_locations:
                if this is of shape n_images x 2, then each subplot will be 
                located at a specific given location.
                To make it beautiful, you better proveide figsize and im_sizes
                or  im_size_factor to merely scale them to cover a small region 
                between 0 and 1.
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag

        from .plt_utils import plt_imshow_subplots
        fig, ax = plt_imshow_subplots(images = images,
                                     frame_shape = frame_shape, 
                                     grid_locations = grid_locations,
                                     figsize = figsize,
                                     colorbar = colorbar,
                                     remove_axis_ticks = remove_axis_ticks,
                                     titles = titles,
                                     cmaps = cmaps,
                                     **kwargs)
                
        if not return_figure:
            fpath = self.savefig(
                    parameter_name = parameter_name, 
                    image_format=image_format, dpi=dpi,
                    time_tag = time_tag)
            return fpath
        else:
            return fig, ax
    
    def imshow_series(self, 
                      parameter_name: str,
                      list_of_stacks, 
                      list_of_masks = None,
                      figsize = None,
                      text_as_colorbar = False,
                      colorbar = False,
                      cmap = 'viridis',
                      list_of_titles_columns = None,
                      list_of_titles_rows = None,
                      fontsize = None,
                      vmin = None,
                      vmax = None,
                      title = None,
                      colorbar_last_only = True,
                      colorbar_fraction = 0.046,
                      colorbar_pad = 0.04,
                      colorbar_labelsize = 1,
                      grid_width_space = 0.0,
                      remove_axis_ticks = True,
                      aspect = 'equal',
                      image_format='jpg', 
                      dpi=1200,
                      time_tag: bool = None,
                      return_figure = False,
                      **kwargs):
                          
        """log a cavas of stacks of images
            One way to show many images and how they change is to make
            stacks of images and put them in a list. Then each
            element of the list is supposed to be iteratable by the first
            dimension, which should be the same size for all elements in 
            the list. This function will start putting them in rows of a canvas.
            If you have an image with many channels.
            
            Each element of the list must appear as either:
            n_frm x n_row x n_clm if there are n_frm images 
                                  for all elements of stack
            n_frm x n_row x n_clm x 3 if channels are in RGB
            
            if you have multiple images as channels such as the following,
            call the prepare_stack_of_images.
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.

            Displays a grid of image series for comparison with optional customization for annotations, colorbars, and formatting.
            
            Parameters:
                list_of_stacks (list): 
                    A list of 3D or 4D arrays, each representing a stack of images. 
                    All stacks must have the same number of images.
                    
                list_of_masks (list, optional): 
                    A list of masks corresponding to the stacks. Each mask should have the same shape 
                    as the images in its respective stack. If provided, masked areas will be ignored 
                    when calculating statistics. Defaults to None.
                    
                figsize (tuple, optional): 
                    The overall size of the figure in inches. If None, it is determined based on 
                    the number of stacks and images. Defaults to None.
                    
                text_as_colorbar (bool, optional): 
                    If True, displays the maximum, mean, and minimum values of each image as text 
                    in place of a colorbar. Defaults to False.
                    
                colorbar (bool, optional): 
                    If True, displays a colorbar for each subplot. Defaults to False.
                    
                cmap (str, optional): 
                    The colormap to use for displaying the images. Defaults to 'viridis'.
                    
                list_of_titles_columns (list, optional): 
                    Titles for each column in the grid. Must have a length equal to the number 
                    of images in each stack. Defaults to None.
                    
                list_of_titles_rows (list, optional): 
                    Titles for each row in the grid. Must have a length equal to the number of stacks. 
                    Defaults to None.
                    
                fontsize (int, optional): 
                    Font size for the text annotations. If None, it is determined based on the figure size. 
                    Defaults to None.
                    
                vmin (float, optional): 
                    The minimum value for image normalization. If None, it is automatically calculated 
                    from the image data. Defaults to None.
                    
                vmax (float, optional): 
                    The maximum value for image normalization. If None, it is automatically calculated 
                    from the image data. Defaults to None.
                    
                title (str, optional): 
                    The title for the entire figure. Defaults to None.
                    
                colorbar_last_only (bool, optional): 
                    If True, displays a colorbar only for the last column. Defaults to False.
                    
                colorbar_fraction (float, optional): 
                    Fraction of the original axis allocated for the colorbar. Defaults to 0.046.
                    
                colorbar_pad (float, optional): 
                    Padding between the image and colorbar. Defaults to 0.04.
                    
                colorbar_labelsize (int, optional): 
                    Label size for the colorbar. Defaults to 1.
                    
                grid_width_space (float, optional): 
                    Horizontal spacing between grid columns. Defaults to 0.0.
                    
                remove_axis_ticks (bool, optional): 
                    If True, removes axis ticks from all subplots. Defaults to True.
                    
                aspect (str, optional): 
                    Aspect ratio of the displayed images. Defaults to 'equal'.
                    
                **kwargs: 
                    Additional keyword arguments to pass to the `imshow` function.

            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
                    
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
        
        from .plt_utils import plt_imshow_series
        fig, ax = plt_imshow_series(
            list_of_stacks          = list_of_stacks, 
            list_of_masks           = list_of_masks,
            figsize                 = figsize,
            text_as_colorbar        = text_as_colorbar,
            colorbar                = colorbar,
            cmap                    = cmap,
            list_of_titles_columns  = list_of_titles_columns,
            list_of_titles_rows     = list_of_titles_rows,
            fontsize                = fontsize,
            vmin                    = vmin,
            vmax                    = vmax,
            title                   = title,
            colorbar_last_only      = colorbar_last_only,
            colorbar_fraction       = colorbar_fraction,
            colorbar_pad            = colorbar_pad,
            colorbar_labelsize      = colorbar_labelsize,
            grid_width_space        = grid_width_space,
            remove_axis_ticks       = remove_axis_ticks,
            aspect                  = aspect,
            **kwargs)
            
        if not return_figure:
            fpath = self.savefig(
                    parameter_name = parameter_name, 
                    image_format=image_format, dpi=dpi,
                    time_tag = time_tag)
            return fpath
        else:
            return fig, ax

    def images_to_pdf(self,
        parameter_name: str, 
        parameter_value: list,
        time_tag: bool = None,
        dpi=1200, 
        **kwargs):
        
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
            
        param_dir, param_name, suffix = self._param_dir_name_suffix(
            parameter_name, 'pdf')
        fpath = self._get_fpath(param_dir, param_name, suffix, time_tag)
        
        try:
            from PIL import Image
        except Exception as e:
            print('install PIL by: --> pip install Pillow')
            raise e
        images = [Image.fromarray(_) for _ in parameter_value]
        images[0].save(
            fpath, "PDF" , 
            resolution=dpi, 
            save_all=True, 
            append_images=images[1:],
            **kwargs)
        
    def variables_to_pdf(self,
                         parameter_name: str, 
                         parameter_value: list,
                         time_tag: bool = None,
                         dpi = 1200,
                         **kwargs):
        images = self.get_stack_from_names(parameter_value)
        self.images_to_pdf(
            parameter_name, images, time_tag, dpi, **kwargs)

    def log_confusion_matrix(self,
                             parameter_name: str,
                             cm,
                             target_names = None,
                             title='Confusion matrix',
                             cmap=None,
                             figsize = None,
                             image_format = 'jpg',
                             dpi = 1200,
                             time_tag = False,
                             close_plt = True):
        """log a confusion matrix
            given a sklearn confusion matrix (cm), make a nice plot
        
            :param cm:
                confusion matrix from sklearn.metrics.confusion_matrix
            
            :param target_names: 
                given classification classes such as [0, 1, 2]
                the class names, for example: ['high', 'medium', 'low']
            
            :param title:        
                the text to display at the top of the matrix
            
            :param cmap: 
                the gradient of the values displayed from matplotlib.pyplot.cm
                (http://matplotlib.org/examples/color/colormaps_reference.html)
                plt.get_cmap('viridis') or plt.cm.Blues
                
            :param time_tag: 
                if True, the file name will be stamped with time
        
            Usage::
            -----
                from lognflow import lognflow
                logger = lognflow(log_roots or log_dir)
                logger.plot_confusion_matrix(\
                    cm           = cm,        # confusion matrix created by
                                              # sklearn.metrics.confusion_matrix
                    target_names = y_labels_vals, # list of names of the classes
                    title        = best_estimator_name) # title of graph
                        
        
            Credit
            ------
                http://scikit-learn.org/stable/auto_examples/
                    model_selection/plot_confusion_matrix.html
    
        """
        if not self.enabled: return
        from .plt_utils import plt_confusion_matrix
        plt_confusion_matrix(
            cm, target_names=target_names, title=title, 
            cmap=cmap, figsize=figsize)
        
        fpath = self.savefig(
                parameter_name = parameter_name, 
                image_format=image_format, dpi=dpi,
                time_tag = time_tag,
                close_plt = close_plt)
        return fpath

    def log_animation(
        self, parameter_name: str, stack, interval=50, blit=False, 
        repeat_delay = None, dpi=100, time_tag: bool = None):
        
        """Make an animation from a stack of images
            
            :param parameter_name: str
                    examples: myvar or myscript/myvar
                    parameter_name can be just a name e.g. myvar, or could be a
                    path like name such as myscript/myvar.
            :param stack: np.array of shape 
                    n_f x n_r x n_c or n_f x n_r x n_c x 3
                    stack[cnt] needs to be plotable by plt.imshow()
            :param time_tag: bool
                    Wheather if the time stamp is in the file name or not.
        """
        if not self.enabled: return
        time_tag = self.time_tag if (time_tag is None) else time_tag
            
        param_dir, param_name, suffix = self._param_dir_name_suffix(
            parameter_name, 'gif')
        fpath = self._get_fpath(param_dir, param_name, suffix, time_tag)

        fig, ax = plt.subplots()
        ims = []
        for img in stack:    
            im = ax.imshow(img, animated=True)
            ax.axis('off')
            ims.append([im])

        from matplotlib import animation as matplotlib_animation
        ani = matplotlib_animation.ArtistAnimation(\
            fig, ims, interval = interval, blit = blit, repeat_delay = repeat_delay)
        try:
            ani.save(fpath, dpi = dpi, 
                 writer = matplotlib_animation.PillowWriter(fps=int(1000/interval)))
            plt.close()
            return fpath
        except Exception as e:
            plt.close()
            print('lognflow: cannot save the animation. Here is the unraised error:')
            print(e)
            print('-'*79)
        
    def flush_all(self):
        if not self.enabled: return
        for log_name in list(self._loggers_dict):
            self.text_flush(log_name, flush = True)
        for parameter_name in list(self._vars_dict):
            self.record_flush(parameter_name)

    def savez(self, parameter_name: str, 
                    parameter_value,
                    time_tag: bool = None):
        return self.save(parameter_name = parameter_name, 
                               parameter_value = parameter_value,
                               suffix = 'npz',
                               time_tag = time_tag)

    #towards supporting all that logging supports
    def debug(self, text_to_log):
        self.text('debug', text_to_log, time_tag = False)
    def info(self):
        self.text('info', text_to_log, time_tag = False)
    def warning(self):
        self.text('warning', text_to_log, time_tag = False)
    def error(self):
        self.text('error', text_to_log, time_tag = False)
    def critical(self):
        self.text('critical', text_to_log, time_tag = False)
    def exception(self):
        self.text('exception', text_to_log, time_tag = False)

    def save_torch(self, name, x):
        if isinstance(x, dict):
            for key in x.keys():
                self.save_torch(name+'/'+key, x[key])
        else:
            self.save(name, x.detach().cpu().numpy())

    def load_torch(self, name):
        self.assert_log_dir()
        flist = self.get_flist(name)
        for fpath in flist:
            if fpath.is_file():
                vname = self.name_from_file(fpath)
                out = self.load(vname)
                return torch.from_numpy(out).cuda()
            if fpath.is_dir():
                fpath_str = str(fpath.absolute())
                vname = fpath_str.split(str(self.log_dir))[1][1:]
                flist_dir = self.get_flist(vname + '/*')
                output = {}
                for fpath_inner in flist_dir:
                    key = fpath_inner.stem
                    output[key] = self.load_torch(
                        vname + '/' + fpath_inner.name)
                return output
        return None    
    
    def get_flist(self, var_name, suffix = None):
        """ get list of files
            return the list of files for a saved variable.

            Parameters
            ----------
            :param var_name:
                variable name
            :param suffix:
                If there are different suffixes availble for a variable
                this input needs to be set. npy, npz, mat, and torch are
                supported.
        """
        self.assert_log_dir()
        var_name = var_name.replace('\t', '\\t').replace('\n', '\\n')\
            .replace('\r', '\\r').replace('\b', '\\b')

        flist = list((self.log_dir).glob(var_name))
        
        if not flist:
            if suffix is None:
                if len(var_name.split('.')) > 1:
                    suffix = var_name.split('.')[-1]
                    name_before_suffix = var_name.split('.')[:-1]
                    if((len(name_before_suffix) == 1) & 
                       (name_before_suffix[0] == '')):
                        var_name = '*'
                    else:
                        var_name = ('.').join(var_name.split('.')[:-1])
                else:
                    suffix = '*'
    
            suffix = suffix.strip('.')        
    
            flist = []            
            if((self.log_dir / var_name).is_file()):
                flist = [self.log_dir / var_name]
            elif((self.log_dir / f'{var_name}.{suffix}').is_file()):
                flist = [self.log_dir / f'{var_name}.{suffix}']
            else:
                _var_name = (self.log_dir / var_name).name
                _var_dir = (self.log_dir / var_name).parent
                search_patt = f'{_var_name}.{suffix}'
                search_patt = replace_all(search_patt, '**', '*')
                flist = list(_var_dir.glob(search_patt))
        if(flist):
            try:
                flist_tags = np.array([float(fpath_v.stem.split('_')[-1]) for fpath_v in flist])
                sortinds = np.argsort(flist_tags)
                flist = [flist[_] for _ in sortinds]
            except:
                flist.sort()
        else:
            var_dir = self.log_dir / var_name
            if(var_dir.is_dir()):
                flist = list(var_dir.glob('*'))
            if(len(flist) > 0):
                flist.sort()
        return flist

    def get_namelist(self, var_name, suffix = None):
        """ get logger names of files
            return the list of names for a saved variable.

            Parameters
            ----------
            :param var_name:
                variable name
            :param suffix:
                If there are different suffixes availble for a variable
                this input needs to be set. npy, npz, mat, and torch are
                supported.
        """
        self.assert_log_dir()
        nlist = self.get_flist(var_name, suffix)
        if nlist:
            nlist = [name_from_file(self.log_dir_str, fpath) for fpath in nlist]
        return nlist

    def get_common_files(self, var_name_A, var_name_B, suffix = None,
                               flist_A = None, flist_B = None):
        """ get common files in two directories
        
            It happens often in ML that there are two directories, A and B,
            and we are interested to get the flist in both that is common 
            between them. returns a tuple of two lists of files.
            
            Parameters
            ----------
            :param var_name_A:
                directory A name
            :param var_name_B:
                directory B name
        """
        self.assert_log_dir()
        if not flist_A:
            flist_A = self.get_flist(var_name_A, suffix)
        if not flist_B:
            flist_B = self.get_flist(var_name_B, suffix)
        
        suffix_A = flist_A[0].suffix
        suffix_B = flist_B[0].suffix 
        parent_A = flist_A[0].parent
        parent_B = flist_B[0].parent
        
        fstems_A = [_fst.stem for _fst in flist_A]
        fstems_B = [_fst.stem for _fst in flist_B]
        
        fstems_A_set = set(fstems_A)
        fstems_B_set = set(fstems_B)
        common_stems = list(fstems_A_set.intersection(fstems_B_set))

        flist_A_new = [parent_A / (common_stem + suffix_A) \
                          for common_stem in common_stems]
        flist_B_new = [parent_B / (common_stem + suffix_B) \
                          for common_stem in common_stems]

        return(flist_A_new, flist_B_new)

    def get_text(self, log_name='main_log', flist = None, suffix = 'txt',
                       file_index = -1):
        """ get text log files
            Given the log_name, this function returns the text therein.

            Parameters
            ----------
            :param log_name:
                the log name. If not given then it is the main log.
            :param flist:
                you can give a file list in Posix paths, for text files
            :param suffix: str
                to search for specifi files
            :param file_index: int or list[int]
                a number or a list of numbers for the index of the file 
                to include, default: -1

        """
        self.assert_log_dir()
        if isinstance(file_index, int):
            file_index = [file_index]
        if not flist:
            flist = self.get_flist(log_name, suffix)
        n_files = len(flist)
        if (n_files>0):
            txt = []
            for fcnt in file_index:
                with open(flist[int(fcnt)]) as f_txt:
                    txt.append(f_txt.readlines())
            if(n_files == 1):
                txt = txt[0]
            return txt

    def is_file(self, var_name, file_index = None, suffix = None, verbose = False):
        """ check if a single variable file exists
            returns True is available else returns False

            Parameters
            ----------
            :param var_name:
                variable name
            :param file_index:
                If there are many snapshots of a variable, this input can
                limit the returned to a set of indices.
            :param suffix:
                If there are different suffixes availble for a variable
                this input needs to be set. npy, npz, mat, and torch are
                supported.
        """
        self.assert_log_dir()
        assert file_index == int(file_index), \
                    f'file_index {file_index} must be an integer'
        flist = self.get_flist(var_name, suffix)
        if flist:
            if len(flist) == 1:
                var_path = flist[0]
            else:
                if file_index is not None:
                    if verbose:
                        self.text(None, 
                            f'There are {len(flist)} files, logged with'
                            + f' name {var_name}.'
                            + f' The given index is {file_index}.')
                    var_path = flist[file_index]
                else:
                    self.text(None, '-'*60)
                    self.text(None, 
                        f'There are {len(flist)} files, logged with'
                        + f' name {var_name} but the index is not given.')
                    self.text(None, '-'*60)
                    return None
            try:
                if var_path.is_file(): return True
            except: pass
        return False

    def _load(self, var_name, file_index = None, 
                   suffix = None, read_func = None, verbose = False,
                   return_collection = False):
        """ get a single variable
            return the value of a saved variable.

            Parameters
            ----------
            :param var_name:
                variable name
            :param file_index:
                If there are many snapshots of a variable, this input can
                limit the returned to a set of indices.
            :param suffix:
                If there are different suffixes availble for a variable
                this input needs to be set. npy, npz, mat, and torch are
                supported.
            :param read_func:
                a function that takes the Posix path and returns data
            :param return_collection:
                if True, then tries to read the text as if a list/dict/tuple had been
                logged.
            .. note::
                when reading a MATLAB file, the output is a dictionary.
                Also when reading a npz except if it is made by record
        """
        self.assert_log_dir()
        assert file_index == int(file_index), \
                    f'file_index {file_index} must be an integer'
        flist = self.get_flist(var_name, suffix)
        var_path = None
        if flist:
            if len(flist) == 1:
                var_path = flist[0]
            else:
                if file_index is not None:
                    if verbose:
                        self.text(None, 
                            f'There are {len(flist)} files, logged with'
                            + f' name {var_name}.'
                            + f' The given index is {file_index}.')
                    var_path = flist[file_index]
                else:
                    self.text(None, '-'*60)
                    self.text(None, 
                        f'There are {len(flist)} files, logged with'
                        + f' name {var_name} but the index is not given.')
                    self.text(None, '-'*60)
                    return None
    
            if(var_path.is_file()):
                if verbose:
                    self.text(None, f'Loading {var_path}')
                if read_func is not None:
                    return (read_func(var_path), var_path)
                if(var_path.suffix == '.npz'):
                    buf = np.load(var_path)
                    try: #check if it is made by record
                        assert len(buf.files) == 2
                        time_array = buf['time']
                        data_array = buf['data']
                        data_array = data_array[time_array > 0]
                        time_array = time_array[time_array > 0]
                        return((time_array, data_array), var_path)
                    except:
                        return(buf, var_path)
                if(var_path.suffix == '.npy'):
                    try: return(np.load(var_path), var_path)
                    except: pass
                if(var_path.suffix == '.mat'):
                    try: 
                        from scipy.io import loadmat
                        return(loadmat(var_path), var_path)
                    except: pass
                if(var_path.suffix == '.dm4'):
                    try:
                        from hyperspy.api import load as hyperspy_api_load
                        return (hyperspy_api_load(var_path).data, var_path)
                    except: pass
                if((var_path.suffix == '.tif') | (var_path.suffix == '.tiff')):
                    try:
                        from tifffile import imread as tifffile_imread
                        return(tifffile_imread(var_path), var_path)
                    except: pass
                if (var_path.suffix == '.pth'):
                    try:
                        from torch import load as torch_load 
                        return(torch_load(var_path), var_path)
                    except: pass
                try:    #png, jpg, ...
                    from matplotlib.pyplot import imread
                    img = imread(var_path)
                    return(img, var_path)
                except: pass
                try:
                    txt = var_path.read_text(errors = 'ignore')
                    if (var_path.suffix == '.json'):
                        return_collection = True
                    if return_collection:
                        txt = text_to_collection(txt)
                    return(txt, var_path)
                except: pass
                var_path = None
            else:
                var_path = None
                
        if (var_path is None) & verbose:
            self.text(None, f'Looking for {var_name} failed. ' + \
                        f'{var_path} is not in: {self.log_dir}')
        return None, None
    
    def load(self, var_name, file_index = -1, 
                   suffix = None, read_func = None, verbose = False,
                   return_fpath = False, return_collection = False):
        """ get a single variable
            return the value of a saved variable.

            Parameters
            ----------
            :param var_name:
                variable name
            :param file_index:
                If there are many snapshots of a variable, this input can
                limit the returned to a set of indices.
            :param suffix:
                If there are different suffixes availble for a variable
                this input needs to be set. npy, npz, mat, and torch are
                supported.
            :param read_func:
                a function that takes the Posix path and returns data
            .. note::
                when reading a MATLAB file, the output is a dictionary.
                Also when reading a npz except if it is made by record
        """
        self.assert_log_dir()
        loaded_data, fpath = self._load(
            var_name = var_name, file_index = file_index, suffix = suffix, 
            read_func = read_func, verbose = verbose,
            return_collection = return_collection)   
        if return_fpath:
            return loaded_data, fpath
        else:
            return loaded_data
        
    def get_stack_from_files(self, 
        var_name = None, flist = [], suffix = None, read_func = None,
        return_flist = False):
       
        """ Get list or data of all files in a directory
       
            This function gives the list of paths of all files in a directory
            for a single variable.

            Parameters
            ----------
            :param var_name:
                The directory or variable name to look for the files
            :type var_name: str
           
            :param flist:
                list of Paths, if data is returned, this flist input can limit
                the data requested to this list.
            :type flist: list
           
            :param suffix:
                the suffix of files to look for, e.g. 'txt'
            :type siffix: str
           
            :param read_func:
                the function that takes the posix path of a file and returns
                the data in there.
           
            Output
            ----------
                It returns a list of data in all files or a numpy array if 
                concatenation of all is possible.
        """
        self.assert_log_dir()
        if not flist:
            flist = self.get_flist(var_name, suffix)
        else:
            flist = list(flist)
            assert pathlib_Path(flist[0]).is_file(), \
                f'File not found: {flist[0]}. You can use get_flist'
        
        if flist:
            n_files = len(flist)
            if(read_func is None):
                try:
                    fdata = np.load(flist[0])
                    read_func = np.load
                except: pass
            if(read_func is None):
                try:
                    from matplotlib.pyplot import imread
                    fdata = imread(flist[0])
                    read_func = imread
                except: pass
            try:
                read_func(flist[0])
            except Exception as e:
                if flist[0].is_file():
                    self.text(None, 
                        f'lognflow: The data file {flist[0]} could not be read.'
                        'Please provide a read_function for this file.')
                else:
                    self.text(
                        None, f'File {flist[0]} does not exist.')
                raise e
            dataset = [read_func(fpath) for fpath in flist]
            try:
                dataset_array = np.array(dataset, dtype=dataset[0].dtype)
            except:
                dataset_array = dataset
            
            if return_flist:
                return(dataset_array, flist)
            else:
                return(dataset_array)

    def get_stack_from_names(self, 
             var_names = None, read_func = None, return_flist = False):
        self.assert_log_dir()
        try:
            var_names_str = str(var_names)
        except: pass
        else:
            var_names = [var_names]
        assert var_names == list(var_names), \
            'input should be a list of variable names'
        dataset = []
        flist = []
        for name in var_names:
            images_flist = self.get_flist(name)
            if images_flist:
                for file_index in range(len(images_flist)):
                    data, fpath = self.load(
                        name, file_index = file_index,
                        read_func = read_func, return_fpath = True)
                    if data is not None:
                        dataset.append(data)
                        flist.append(fpath)

        try:
            dataset = np.array(dataset, dtype=dataset[0].dtype)
        except: pass
                        
        if return_flist:
            return dataset, flist
        else:
            return dataset

    def replace_time_with_index(self, var_name, verbose = False):
        """ index in file var_names
            lognflow uses time stamps to make new log files for a variable.
            That is done by putting time stamp after the name of the variable.
            This function changes all of the time stamps, sorted ascendingly,
            by indices.
            
            :param var_name:
                variable name
        """
        self.assert_log_dir()
        var_dir = self.log_dir / var_name
        if(var_dir.is_dir()):
            var_fname = None
            flist = list(var_dir.glob(f'*.*'))
        else:
            var_fname = var_dir.name
            var_dir = var_dir.parent
            flist = list(var_dir.glob(f'{var_fname}'))
            if (len(flist) == 0) & (not ('*' in var_fname)):
                self.text(None, 
                    'lognflow, replace_time_with_index:' +\
                    'the given pattern has no * and no files were found')
        if flist:
            flist.sort()
            fcnt_width = len(str(len(flist)))
            for fcnt, fpath in enumerate(flist):
                f_time_stamp = fpath.stem.split('_')[-1]
                try:
                    if int(f_time_stamp) == float(f_time_stamp):
                        fname_old = fpath.name.split(f_time_stamp)
                        f_time_stamp = float(f_time_stamp)
                        fname_new = fname_old[0] + f'{f_time_stamp:0.1f}' + fname_old[1]
                        fpath_new = flist[fcnt].parent / fname_new
                        flist[fcnt].rename(fpath_new)
                        flist[fcnt] = fpath_new
                except: pass

            for fcnt, fpath in enumerate(flist):
                if verbose:
                    self.text(None, f'Changing {flist[fcnt].name}')
                f_time_stamp = fpath.stem.split('_')[-1]
                fname_old = fpath.name.split(f_time_stamp)
                fname_new = \
                    fname_old[0] + f'{fcnt:0{fcnt_width}d}' + fname_old[1]
                fpath_new = flist[fcnt].parent / fname_new
                if verbose:
                    self.text(None, f'To {fpath_new.name}')
                flist[fcnt].rename(fpath_new)

    def __call__(self, *args, **kwargs):
        """calling the object
            In the case of the following code::
                logger = lognflow()
                logger('Hello lognflow')
            The text (str(...)) will be passed to the main log text file.
        """
        fpath = self.text(None, *args, **kwargs)
        return fpath

    def __repr__(self):
        return f'{self.log_dir}'

    def __bool__(self):
        return self.log_dir.is_dir()

getLogger = lognflow