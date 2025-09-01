#depricated file
from multiprocessing import Process, Queue, cpu_count, Event
from numpy import __name__    as np___name__
from numpy import array       as np_array
from numpy import zeros       as np_zeros
from numpy import argsort     as np_argsort
from numpy import unique      as np_unique
from .utils import is_builtin_collection

def _to_collection(returned_obj):
    if not is_builtin_collection(returned_obj):
        return [returned_obj]
    return returned_obj

def _loopprocessor_function_test_mode(
         targetFunction, theQ, procID_range, error_event, args, kwargs):
    results = targetFunction(*args, **kwargs)
    results = _to_collection(results)
    theQ.put([procID_range, [results], False])

def _loopprocessor_function(
        targetFunction, theQ, procID_range, error_event, args, kwargs):
    try:
        results = targetFunction(*args, **kwargs)
        results = _to_collection(results)
        theQ.put([procID_range, [results], False])
    except Exception as e:
        if not error_event.is_set():
            error_event.set()
        theQ.put([procID_range, None, True])

class loopprocessor():
    def __init__(self, 
            targetFunction, n_cpu = None, test_mode = False, logger = print,
            concatenate_outputs = True, verbose = True, n_processes = 0):
        self.targetFunction = targetFunction
        self.test_mode = test_mode
        self.aQ = Queue()
        self.concatenate_outputs = concatenate_outputs
        if(n_cpu is None):
            self.n_cpu = cpu_count()
        else:
            self.n_cpu = n_cpu
        self.verbose = verbose
        self.n_processes = n_processes
        if self.verbose:
            self.logger = logger
            self.logger(f'lognflow loopprocessor initialized with {self.n_cpu} CPUs.')
            if self.n_processes:
                assert self.n_processes > 0
                assert self.n_processes == int(self.n_processes)
                from .printprogress import printprogress
                self.pBar = printprogress(self.n_processes)

        self.outputs_is_given = False
        self.outputs = []
        self.Q_procID = []
    
        self.numBusyCores = 0
        self.procID = 0
        self.numProcessed = 0

        self.any_error = False
        self.error_event = Event()
        self.empty_queue = False
    
    def __call__(self, *args, **kwargs):
        if (len(args) == 0) & (len(kwargs) == 0):
            self.empty_queue = True
        
        release_a_cpu = False
        if (len(args) > 0) | (len(kwargs) > 0):
            if(self.numBusyCores >= self.n_cpu):
                release_a_cpu = True
                
        single_queue_access = True
        while(single_queue_access | release_a_cpu | self.empty_queue):
            single_queue_access = False
        
            if (not self.aQ.empty()):
                aQElement = self.aQ.get()
                ret_procID_range = aQElement[0]
                ret_result = aQElement[1]
                if ((not self.any_error) & aQElement[2]):
                    self.any_error = True
                    if self.n_processes:
                        del self.pBar
                    self.empty_queue = True
                    error_ret_procID = ret_procID_range.copy()
                    self.logger('')
                    self.logger('lognflow, loopprocessor: An exception'\
                                ' has been raised. signaling all processes'\
                                ' to stop and join, please wait...')
                if (not self.any_error):
                    for ret_procID, result in zip(ret_procID_range, ret_result):
                        self.Q_procID.append(ret_procID)
                        self.outputs.append(result)
                        if self.n_processes:
                            self.pBar()
                elif(self.numBusyCores):
                    self.logger(f'Number of busy cores: {self.numBusyCores}')
    
                self.numProcessed += 1
                self.numBusyCores -= 1
                release_a_cpu = False
                if(self.any_error & (self.numBusyCores == 0)):
                    self.logger(f'Number of busy cores: {self.numBusyCores}')
                    self.logger(f'All cores are free')
                    self.empty_queue = False
                    break
            if(self.numProcessed >= self.procID):
                self.empty_queue = False
                
        if(not self.any_error):
            if (len(args) > 0) | (len(kwargs) > 0):
                procID_range = [self.procID]
                _args = (
                    self.targetFunction, self.aQ, procID_range, 
                    self.error_event, args, kwargs)
                if(self.test_mode):
                    _loopprocessor_function_test_mode(*_args)
                else:
                    Process(target = _loopprocessor_function, 
                            args = _args).start()
                self.procID += 1
                self.numBusyCores += 1
    
        if(self.any_error):
            self.logger('-'*79)
            self.logger('An exception occured during submitting jobs.')
            self.logger('Here we try to reproduce it but will raise '
                  'ChildProcessError regardless.')
            self.logger(f'We will call {self.targetFunction} ')
            self.logger('with the following index to slice the inputs:'
                  f' {error_ret_procID[0]}')
            self.logger('to avoid seeing this message, pass the argument called '\
                   'logger, it is print by default.')
            self.logger('-'*79)
            _loopprocessor_function_test_mode(
                self.targetFunction, self.aQ, 
                error_ret_procID, self.error_event, args, kwargs)
            raise ChildProcessError
        
        if (len(args) == 0) & (len(kwargs) == 0):
            sortArgs = np_argsort(self.Q_procID)
            ret_list = [self.outputs[i] for i in sortArgs]
            
            return_as_is = False
            ret_entries_lens = []
            for ret_entry in ret_list:
                try:
                    _len = len(ret_entry)
                except:
                    try:
                        _len = ret_entry.size
                    except:
                        return_as_is = True
                    else:
                        ret_entries_lens.append(_len)
                else:
                    ret_entries_lens.append(_len)
            ret_entries_lens_unique = np_unique(ret_entries_lens)
            if len(ret_entries_lens_unique) != 1:
                return_as_is = True
            
            if return_as_is | (not self.concatenate_outputs):
                self.outputs = ret_list
                return self.outputs
            else:
                n_entries = ret_entries_lens_unique[0]
                self.outputs = []
                for element_cnt in range(n_entries):
                    element_all = []
                    is_not_nparray = False
                    is_numpy = False
                    shapes_are_not_the_same = False
                    shapes_are_the_same = False
                    for entry in ret_list:
                        instance = entry[element_cnt]
                        try:
                            instance_size = instance.size
                        except:
                            is_not_nparray = True
                        else:
                            if instance_size == 0:
                                is_not_nparray = True
                            else:
                                if not is_numpy:
                                    numpy_shape = instance.shape
                                else:
                                    if numpy_shape == instance.shape:
                                        shapes_are_the_same = True
                                    else:
                                        shapes_are_not_the_same = True
                                is_numpy = True
                        element_all.append(instance)
                    if ((not is_not_nparray) & 
                        is_numpy & 
                        (not shapes_are_not_the_same) &
                        shapes_are_the_same):
                        element_all = np_array(element_all)
                    self.outputs.append(element_all)  
                if n_entries == 1:
                    return self.outputs[0]
                else:
                    return self.outputs