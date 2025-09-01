from lognflow import multiprocessor, printprogress
from lognflow.multiprocessor import multiprocessor_gen, loopprocessor
import numpy as np
import inspect
import time

def randgen(_):
    print(_)
    n_data =  int(10000*np.random.rand())
    randn = np.random.rand(n_data)
    return randn

def test_simple_randgen():
    print('Testing function', inspect.currentframe().f_code.co_name)
    results = multiprocessor(randgen, np.arange(100))
    print(results)
    
def multiprocessor_targetFunc(iterables_sliced, shareables):
    idx = iterables_sliced
    data, mask, op_type = shareables
    _data = data[idx]
    if(op_type=='median'):
        to_return1 = np.median(_data[mask[idx]==1])
    to_return2 = np.ones((1 + int(9*np.random.rand(1)), 2, 2))
    
    return(to_return1, 'median', to_return2)
    
def test_multiprocessor():
    print('Testing function', inspect.currentframe().f_code.co_name)
    print('-'*80, '\n', inspect.stack()[0][3], '\n', '-'*80)

    N = 10000
    D = 1000
    data = (10+100*np.random.randn(N,D)).astype('int')
    mask = (2*np.random.rand(N,D)).astype('int')
    op_type = 'median'
    shareables = (data, mask, op_type)
    stats = multiprocessor(multiprocessor_targetFunc, 
                           iterables = N,
                           shareables = shareables,
                           verbose = True)
    results = []
    for cnt in range(N):
        results.append(multiprocessor_targetFunc((cnt, ), shareables))

    medians, otherOutput, _ids = stats
    print('type(medians)', type(medians))
    print('medians.shape', medians.shape)
    print('type(otherOutput)', type(otherOutput))
    print('len(otherOutput)', len(otherOutput))
    print('otherOutput[1] ', otherOutput[1])
    print('otherOutput[1][0] ', otherOutput[1][0])
    print('type(_ids) ', type(_ids))
    print('len(_ids) ', len(_ids))
    print('type(_ids[0]) ', type(_ids[0]))
    print('_ids[0].shape ', _ids[0].shape)
    
    direct_medians = np.zeros(N)
    for cnt in range(N):
        direct_medians[cnt] = np.median(data[cnt, mask[cnt]==1])
    
    print(f'direct_medians.shape: {direct_medians.shape}')
    
    print(np.array([ medians, direct_medians] ).T)
    print('difference of results: ', (direct_medians - medians).sum())

def masked_cross_correlation(iterables_sliced, shareables):
    print('Testing function', inspect.currentframe().f_code.co_name)
    vec1, vec2 = iterables_sliced
    mask, statistics_func = shareables
    vec1 = vec1[mask==1]
    vec2 = vec2[mask==1]
    
    vec1 -= vec1.mean()
    vec1_std = vec1.std()
    if vec1_std > 0:
        vec1 /= vec1_std
    vec2 -= vec2.mean()
    vec2_std = vec2.std()
    if vec2_std > 0:
        vec2 /= vec2_std

    correlation = vec1 * vec2
    to_return = statistics_func(correlation)
    return(to_return)

def test_multiprocessor_ccorr():
    print('Testing function', inspect.currentframe().f_code.co_name)
    print('-'*80, '\n', inspect.stack()[0][3], '\n', '-'*80)
    data_shape = (1000, 2000)
    data1 = np.random.randn(*data_shape)
    data2 = 2 + 5 * np.random.randn(*data_shape)
    mask = (2*np.random.rand(data_shape[1])).astype('int')
    statistics_func = np.median
    
    iterables = (data1, data2)
    shareables = (mask, statistics_func)
    ccorr = multiprocessor(
        masked_cross_correlation, iterables, shareables,
        test_mode = False)
    print(f'type(ccorr): {type(ccorr)}')
    print(f'ccorr.shape: {ccorr.shape}')

def error_multiprocessor_targetFunc(iterables_sliced, shareables):
    print('Testing function', inspect.currentframe().f_code.co_name)
    idx = iterables_sliced
    data, mask, op_type = shareables
    _data = data[idx]
    if(op_type=='median'):
        to_return1 = np.median(_data[mask[idx]==1])
        to_return1 = np.array([to_return1])
    to_return2 = np.ones((int(10*np.random.rand(1)), 2, 2))
    
    if idx == 3000:
        raise ValueError
    
    return(to_return1, 'median', to_return2)    

def test_error_handling_in_multiprocessor():
    print('Testing function', inspect.currentframe().f_code.co_name)
    print('-'*80, '\n', inspect.stack()[0][3], '\n', '-'*80)
    
    N = 10000
    D = 1000
    data = (10+100*np.random.randn(N,D)).astype('int')
    mask = (2*np.random.rand(N,D)).astype('int')
    op_type = 'median'

    iterables = N
    shareables  = (data, mask, op_type)
    
    print('             ------------------------------')
    print('             NOTE: IT SHOULD RAISE AN ERROR')
    print('             ------------------------------')
    
    try:
        stats = multiprocessor(
            error_multiprocessor_targetFunc, iterables, shareables,
            verbose = True)
        raise
    except Exception as e:
        print('Error has been raised')
        print(e)
    
def noslice_multiprocessor_targetFunc(iterables_sliced, shareables):
    idx = iterables_sliced
    data, mask, op_type = shareables
    _data = data[idx]
    if(op_type=='median'):
        to_return1 = np.median(_data[mask[idx]==1])
        to_return1 = np.array([to_return1])
    to_return2 = np.ones((int(10*np.random.rand(1)), 2, 2))
    return(to_return1, 'median', to_return2)    

def test_noslice_multiprocessor():
    print('Testing function', inspect.currentframe().f_code.co_name)
    print('-'*80, '\n', inspect.stack()[0][3], '\n', '-'*80)
    
    N = 1000
    D = 1000
    data = (10+100*np.random.randn(N,D)).astype('int')
    mask = (2*np.random.rand(N,D)).astype('int')
    op_type = 'median'

    iterables = N
    shareables  = (data, mask, op_type)
    
    stats = multiprocessor(
        noslice_multiprocessor_targetFunc, iterables, shareables, verbose = True)

def compute(data, mask):
    for _ in range(400):
        res = np.median(data[mask==1])
        
    # if (data>147).sum() > 0:
    #     asdf
        
    return res, 'asdf'

def compute_arg_scatterer(iterables_sliced):
    return compute(*iterables_sliced)

def test_loopprocessor():
    print('Testing function', inspect.currentframe().f_code.co_name)
    print('-'*80, '\n', inspect.stack()[0][3], '\n', '-'*80)

    N = 16
    D = 1000000
    data = (100+10*np.random.randn(N,D)).astype('int')
    mask = (2*np.random.rand(N,D)).astype('int')

    time_of_start = time.time()
    results_mp = multiprocessor(
        compute_arg_scatterer, iterables = (data, mask), 
        shareables = None, verbose = True)
    results_mp = results_mp[0]
    mp_period = time.time() - time_of_start
    
    time_of_start = time.time()
    
    compute_lp = loopprocessor(compute)
    for cnt in printprogress(range(N)):
        results_lp = compute_lp(data[cnt], mask[cnt])
    results_lp = compute_lp()
    
    results_lp = results_lp[0]
    lp_period = time.time() - time_of_start

    time_of_start = time.time()
    results = np.zeros(N)
    for cnt in printprogress(range(N)):
        results[cnt], _ = compute(data[cnt], mask[cnt])
    sp_period = time.time() - time_of_start
    
    print((results - results_lp).sum())
    print((results - results_mp).sum())
    
    print(f'multiprocessor period: {mp_period}')
    print(f'loopprocessor period: {lp_period}')
    print(f'serial processing period: {sp_period}')
    
def test_multiprocessor_gen():
    print('Testing function', inspect.currentframe().f_code.co_name)
    N = 8
    D = 100000
    data = (100+10*np.random.randn(N,D)).astype('int')
    mask = (2*np.random.rand(N,D)).astype('int')

    for arrivals in multiprocessor_gen(compute_arg_scatterer,
                                       iterables = (data, mask), 
                                       shareables = None,
                                       verbose = True):
        
        results_mp, IDs = arrivals
        print(IDs)
    results_mp = results_mp[0]

    results = np.zeros(N)
    for cnt in printprogress(range(N)):
        results[cnt], _ = compute(data[cnt], mask[cnt])
    
    print((results - results_mp).sum())
    print('-'*80)

"""
def test_custom_parfor():
    print('-'*80, '\n', inspect.stack()[0][3], '\n', '-'*80)

    N = 16
    D = 1000000
    data = (100+10*np.random.randn(N,D)).astype('int')
    mask = (2*np.random.rand(N,D)).astype('int')

    time_of_start = time.time()
    results = np.zeros(N)
    # for cnt in range(N):
    @parfor(range(N))
    def loop_func():
        results[cnt] = np.median(data[cnt][mask[cnt]==1])
    loop_func()
    sp_period = time.time() - time_of_start
    print(f'serial processing period: {sp_period}')
"""
 
if __name__ == '__main__':
    print('lets test', flush=True)
    test_simple_randgen()
    test_loopprocessor()
    test_multiprocessor_gen()
    test_multiprocessor()
    test_noslice_multiprocessor()
    test_multiprocessor_ccorr()
    test_error_handling_in_multiprocessor()

