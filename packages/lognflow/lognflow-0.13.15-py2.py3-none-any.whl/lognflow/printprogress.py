from math import ceil
from time import time

def needs_s(number):
    return 's' if not ( (number == 1) or (number == -1) ) else ''

class printprogress:
    """
    While there are packages that use \r to show a progress bar, 
    there are cases e.g. a print_function or an ssh terminal that does not 
    support \r. In such cases, if something is typed at the end of 
    the line, it cannot be deleted. The following code provides a good 
    looking progress bar with a simple title and limits and 
    is very simple to use. Define the object with number of steps of the loop 
    and then call it in every iteration of the loop. If you'd like it
    to go faster, call it with give number of steps that have passed.
    """
    def __init__(self, 
                 int_or_iterable, 
                 numTicks = 78,
                 title = None,
                 desc = None,
                 method = 'linear',
                 print_function = print,
                 **print_function_kwargs):
        """
            int_or_iterable: int or iterable
                Number of iterations in the for loop or iterable
                n_steps = int(it) or n_steps = len(it)
            numTicks: int
                The number of charachters in a row of the screen - 2
                default: 78 for old screens that have 80 coloumns
            title : str 
                The title of progress bar.
                default: f'Progress bar for {n_steps} steps in {numTicks} ticks'
            desc : str
                it is the same as title used by tqdm
            print_function:
                print_function must be callable with a string and should not add
                \n to the its input.
                If you pass None as the print_function, nothing will be printed.
                yet the output of the __call__ will be the remaining time in
                seconds.
            method: options how to calculate the remaining time are
                'linear':
                       p                   x      
                |-----------|--------------------------|
                           ck                       n_steps
                As such  x/(n-c) = p/c => x = p(n/c - 1)
                more options to come
        """
        assert method in ['linear', 'linear_robust']
        if desc is not None:
            if title is not None:
                assert desc == title, 'either give me title or desc' 
            title = desc
        self.yielding_data = False
        try:
            n_steps = int(int_or_iterable)
        except:
            n_steps = len(int_or_iterable)
            self.iterable = int_or_iterable
            if n_steps > 0:
                self.yielding_data = True
                self.yielding_data_call_warning = False

        if(n_steps<2):
            print_function = None

        self.FLAG_first_tick = True
        
        self.print_function_kwargs = print_function_kwargs
        self.method = method
        self.print_function = print_function
        
         ############################################################################### what happens in case of [1] as input
        
        if (title is None):
            needs_s(n_steps)
            title = f'Progress for {n_steps} step{needs_s(n_steps)}'
        self.FLAG_ended = False
        self.FLAG_warning = False
        self.startTime = time()
        self.ck = 0
        self.prog = 0
        self.n_steps = n_steps
        if(numTicks < len(title) + 2 ):
            self.numTicks = len(title)+2
        else:
            self.numTicks = numTicks
        
        self._print_func(' ', end='')
        self._print_func('_'*self.numTicks, end='')
        self._print_func(' ')
        
        self._print_func('/', end='')
        self._print_func(' '*int((self.numTicks - len(title))/2), end='')
        self._print_func(title, end='')
        self._print_func(' '*int(ceil((self.numTicks-len(title))/2)-1), end='')
        self._print_func(' \\')
        
        self._print_func(' ', end = '')
        self.len_prog_text = 0
        self.remTimeS_perv = 0
        self.average_filter_coeff = 0
    
    def _print_func(self, text, end='\n'):
        if (self.print_function is not None):
            if (self.print_function == print):
                print(text, end = end, flush = True)
            else:
                self.print_function(text, end = end,
                                       **self.print_function_kwargs)
        
    def _calc_ETA(self):
        if(self.method == 'linear'):
            passedTime = time() - self.startTime
            if self.ck > 0:
                remTimeS = passedTime * ( self.n_steps / self.ck - 1)
                if(self.average_filter_coeff):
                    if (self.remTimeS_perv > 5) & (remTimeS > 5):
                        remTimeS = (1 - self.average_filter_coeff)*remTimeS + \
                                    self.average_filter_coeff*self.remTimeS_perv
                
                self.remTimeS_perv = remTimeS
            else:
                remTimeS = 1e+7
        return remTimeS
    
    def _make_progress(self, ck = 1):
        
        remTimeS = 0
        if(self.FLAG_ended):
            if(not self.FLAG_warning):
                self.FLAG_warning = True
                self._print_func('-' * (self.numTicks + 2))
        else:
            self.ck += ck
            if(self.ck <= self.n_steps):
                remTimeS = self._calc_ETA() # useful when print_function is None
                try: cProg = int(self.numTicks*self.ck/(self.n_steps-1)/3)
                except: cProg = int(self.numTicks/3)
                #3: because 3 charachters are used
                while((self.prog < cProg) & (not self.FLAG_ended)):
                    self.prog += 1
                    remTimeS = self._calc_ETA()
                    if remTimeS < 86400*100:
                        if(remTimeS>356400): # less than 99d and more than 99h
                            progStr = "%02d" % int(ceil(remTimeS/86400))
                            self._print_func(progStr, end='')
                            self._print_func('d', end='')
                            self.len_prog_text += 3
                        elif(remTimeS>5940): # less than 99h and more than 99m
                            progStr = "%02d" % int(ceil(remTimeS/3600))
                            self._print_func(progStr, end='')
                            self._print_func('h', end='')
                            self.len_prog_text += 3
                        elif(remTimeS>99): # less than 99m and more than 99s
                            progStr = "%02d" % int(ceil(remTimeS/60))
                            self._print_func(progStr, end='')
                            self._print_func('m', end='')
                            self.len_prog_text += 3
                        elif(remTimeS>=0): # less than 99s and more than 0
                            progStr = "%02d" % int(ceil(remTimeS))
                            self._print_func(progStr, end='')
                            self._print_func('s', end='')
                            self.len_prog_text += 3
                        else:
                            self._end()
            if((self.ck >= self.n_steps) | 
               (self.len_prog_text >= self.numTicks)):
                self._end()
        return remTimeS
    
    def __call__(self, ck=1):
        """ ticking the progress bar
            just call the object and the progress bar moves ck steps
            ahead when ready.
            
            output
            ~~~~~~
            :param ETA:
                the remaining time in seconds will be provided at the output
        """
        if(self.yielding_data):
            if not self.yielding_data_call_warning:
                print('printprogress is used as an Iterator,'
                      ' You can not call it. Perhaps you gave it a list,'
                      ' rather than the length of the list as the first arg.')
                self.yielding_data_call_warning = True
        else:
            return self._make_progress(ck)

    # Supporting iterator type usage
    def __iter__(self):
        self.FLAG_iter_ended = False
        self.iter_ck = 0
        return self
  
    def __next__(self):
        if(self.yielding_data):
            if not self.FLAG_iter_ended:
                if self.FLAG_first_tick:
                    self._make_progress(0)
                    self.FLAG_first_tick = False
                else:
                    self._make_progress()
                if self.iter_ck == self.n_steps - 1:
                    self.FLAG_iter_ended = True
                toret = self.iterable[self.iter_ck]
                self.iter_ck += 1
                return toret
            else:
                self.FLAG_iter_ended = True
                self.FLAG_ended = True
                raise StopIteration
        else:
            if self.n_steps:
                print('printprogress is used as a Generator, e.g. to a for loop'
                      ' but the first argument does not have length via __len__'
                      ' perhaps you gave it a number or the length of a list as'
                      ' the first argument. To use it in a for loop '
                      ' (specifically as a generator), provide the list itself.'
                      ' If you wish to give a number of steps, define the pbar'
                      ' before the for loop via pbar = printprogress(n_steps)'
                      ' then call the pbar() inside the for loop when a step is'
                      ' carried out.'
                      )
            self.FLAG_iter_ended = True
            self.FLAG_ended = True
            raise StopIteration
    
    def _end(self):
        if(not self.FLAG_ended):
            self._print_func('')
            self.FLAG_ended = True

    def __del__(self):
        self._end()