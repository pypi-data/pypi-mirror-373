#!/usr/bin/env python

"""Tests for `lognflow` package."""
import pytest
import inspect
import time
import numpy as np

from lognflow import lognflow, printprogress, select_directory

import tempfile
temp_dir = tempfile.gettempdir()

def test_log_index():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for putting index instead of time_stamp')
    logger.save('testa', 'testa', time_tag = False)
    logger.save('testb', 'testb', time_tag = True)
    logger.save('testb', 'test3', time_tag = True)
    logger.save('testc', 'test4', time_tag = 'index')
    logger.save('testc', 'test5', time_tag = 'index')
    logger.save('testc', 'test6', time_tag = 'index')
    logger.save('testd', 'test7', time_tag = 'time_and_index')
    logger.save('testd', 'test8', time_tag = 'time_and_index')
    logger.save('testd', 'test9', time_tag = 'time_and_index')
    
def test_lognflow_conflict_in_names():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for conflict in names')
    logger1 = lognflow(logger.log_dir)
    logger2 = lognflow(logger.log_dir)
    logger1(logger1.log_dir)
    logger2(logger2.log_dir)

def test_text():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir, print_text = False)
    logger('This is a test for text')    
    for _ in range(10000):
        logger(f'{_}')

    logger.text('not_main_script1.pdb',
           'This is a new log file for another script')
    logger.text('not_main_script2.test',
                    'For other log files you need to mention the log_name')
    logger.text('not_main_script3',
           'This is a new log file for another script', suffix = 'io')
    logger.text('test.to\not_main_script4.top',
                    'For other log files you need to mention the log_name')
    logger.text('not_main_script2',
           'This is a new log file for another script')
    logger.text('not_main_script2.test',
                    'For other log files you need to mention the log_name')
    logger.text('test.to\not_main_script4.top',
                    'To see if variable names are OK when passed properly')
    for _ in range(10000):
        logger(f'{_}')

def test_logger():
    print('Testing function', inspect.currentframe().f_code.co_name)
    ''' test the logger call funciton
        when lognflow object is made, you can call it.
        If it is called with a string as input, it will log that into the
        main_log text file.
        If a string is given and then something else is also provided afterwards
        the funciton save will be called with that while the first input
        string is going to be considered as the name of a variable.
    '''
    logger = lognflow(temp_dir)
    logger('This is a test for lognflow and logger call')

    a = 20
    b = np.array([34])
    c = 'asdf'
    
    logger(a)
    logger.save('a', a)
    logger.save('aa', a, suffix = 'txt', time_tag = False)
    logger(b)
    logger.save('b', b)
    logger.save('bb', b, suffix = 'txt', time_tag = False)
    logger(c)
    logger.save('test/c', c, suffix = 'txt')

def test_log_flush_period():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir, log_flush_period = 30)
    logger('This is a test for lognflow and record')    
    
    time_time = time.time()
    for _ in range(20):
        while(time.time() < time_time + 10):
            pass
        time_time = time.time()
        logger(f'Log{_}'*20)
        

    logger.text('not_main_script',
           'This is a new log file for another script')
    logger.text('not_main_script',
                    'For other log files you need to mention the log_name')

def test_record():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for lognflow and record')    

    for _ in range(1000):
        logger.record('vars/vec/v.to.txt', np.random.rand(10000))
        
def test_record_without_time_stamp():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for lognflow and record')    

    for _ in range(10):
        logger.save('vars/vec/v', np.random.rand(10000), time_tag = False)

def test_record_savefig():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for lognflow and record')    

    var = 0
    for _ in printprogress(range(1000)):
        time.sleep(0.001)
        var += np.random.randn(1)*_/50
        logger.record('vars/vec/v.to.txt', var, savefig = True, plot_win_length = 50)

    x = np.arange(-2, 2, 0.005)
    var = 0
    for _ in printprogress(range(len(x))):
        time.sleep(0.001)
        var = x[_]**2 + np.random.randn(1)
        logger.record('v2', var, savefig = True, plot_win_length = 100)
    
def test_get_record():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for lognflow and record')    

    var = 0
    for _ in printprogress(range(500)):
        time.sleep(0.001)
        var += np.random.rand(10000)
        logger.record('vars/vec/v.to.txt', var)
        
    time_arr, data_arr = logger.get_record('vars/vec/v.to.txt')
    logger.plot('vars/vec/v', data_arr[:, 0], '-*', x_values_list = [time_arr])
    
def test_log_animation():
    print('Testing function', inspect.currentframe().f_code.co_name)
    var1 = np.random.rand(32, 100, 100)
    logger = lognflow(temp_dir)
    logger('This is a test for log_animation')    
    logger.log_animation('var1',var1)

def test_save_matlab():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for saving MATLAB files using a dictionary')    
    data_to_save = dict(data1 = np.random.rand(3,3),
                        data2 = 'test',
                        data3 = [1, 2, 4])
    logger.save('MATLAB_test.mat', data_to_save)

def test_save():
    print('Testing function', inspect.currentframe().f_code.co_name)
    var1 = np.random.rand(100)
    
    logger = lognflow(temp_dir)
    logger('This is a test for save')    
    logger.save('var1/var1.txt', var1)
    logger.save('var1/var1.npy', var1)
    a_dict = dict({'str_var': 'This is a string',
                   'var1': var1})
    logger.save('a_dict', a_dict)
    logger.save('a_dict.txt', a_dict)
    logger.save('a_dict2', a_dict, suffix = 'txt')

def test_plot():
    print('Testing function', inspect.currentframe().f_code.co_name)
    var1 = np.random.rand(100)
    var2 = 3 + np.random.rand(100)
    var3 = 6 + np.random.rand(100)
    
    logger = lognflow(temp_dir)
    logger('This is a test for plot')    
    
    logger.plot('var1', var1)
    
    logger.plot('vars', [var1, var2, var3], '-*')
    
def test_hist():
    print('Testing function', inspect.currentframe().f_code.co_name)
    var1 = np.random.rand(1000)
    var2 = 3 + np.random.rand(1000)
    var3 = 6 + np.random.rand(1000)
    
    logger = lognflow(temp_dir)
    logger('This is a test for hist')    
    
    logger.hist(parameter_name = 'var1', 
                parameter_value_list = [var1],
                bins = 20)
    
    logger.hist(parameter_name = 'vars', 
                parameter_value_list = [var1, var2, var3],
                bins = 20)
    
def test_scatter3():
    print('Testing function', inspect.currentframe().f_code.co_name)
    var1 = np.random.rand(100)
    var2 = 3 + np.random.rand(100)
    var3 = 6 + np.random.rand(100)

    var3d = np.array([var1, var2, var3])
    
    logger = lognflow(temp_dir)
    logger('This is a test for scatter3')    
    
    logger.scatter3('var3d', var3d.T)
    logger.scatter3('var3d_animation', var3d.T, make_animation=True,
                    elev_list = [45],
                    azim_list = np.arange(0, 360, 2),
                    log_animation_kwargs = {'interval' : 100})
    
def test_savefig():
    print('Testing function', inspect.currentframe().f_code.co_name)
    from lognflow.plt_utils import plt_imshow
    plt_imshow(np.random.rand(100, 100))
    logger = lognflow(temp_dir)
    logger('This is a test for savefig')    
    logger.savefig('var3d')        
    
def test_hexbin():
    print('Testing function', inspect.currentframe().f_code.co_name)
    var1 = np.random.randn(10000)
    var2 = 3 + np.random.randn(10000)

    logger = lognflow(temp_dir)
    logger('This is a test for hexbin')    
    
    logger.hexbin('hexbin', [var1, var2])    

def test_imshow():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for imshow')    
    logger.imshow('var2d', np.random.rand(100, 100))    
    logger.imshow('var2d_100_of_them', np.random.rand(25, 100, 100))

def test_surface():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for surface')    
    logger.surface('var3d', np.random.rand(100, 100))    

def test_imshow_series():
    print('Testing function', inspect.currentframe().f_code.co_name)
    """ 
        When we have 8 set of images, each is 100x100 and there are 9 of them 
        which will appear as 3x3 tile.
    """
    logger = lognflow(temp_dir)
    logger('This is a test for prepare_stack_of_images')

    stack_1 = np.random.rand(8, 9, 100, 100)
    from lognflow.plt_utils import stacks_to_frames
    
    stack_1 = stacks_to_frames(stack_1)
    stack_2 = np.random.rand(8, 100, 100)
    stack_3 = np.random.rand(8, 9, 100, 100, 3)
    stack_3 = stacks_to_frames(stack_3)
    
    list_of_stacks123 = [stack_1, stack_2, stack_3]
    
    logger.imshow_series('imshow_series_before_handling', list_of_stacks123)
    
    stack_4 = np.random.rand(1, 32, 32, 16)
    stack_4 = stacks_to_frames(stack_4)
    list_of_stacks = [stack_4]
    logger.imshow_series('just_one_series', list_of_stacks, cmap = 'cool')
    
    imgs=[]
    for _ in range(5):
        _imgs = np.random.rand(5, 100, 100)
        _imgs[:, 50, 50] = 2
        imgs.append(_imgs)
    
    logger = lognflow(temp_dir)
    logger('This is a test for imshow_series')    
    logger(f'imgs.shape: {imgs[0].shape}')

    logger.imshow_series(parameter_name = 'imshow_series\\', 
                             list_of_stacks = imgs, 
                             text_as_colorbar = True)
    
    data = [1 + np.random.rand(10, 100, 100),
            1 + np.random.rand(10, 10, 10)]
    mask0 = data[0][0]*0 + 1
    mask0[::2, ::2] = 0
    mask1 = data[1][0] != 0
    list_of_masks = [mask0, mask1]
    logger.imshow_series(parameter_name = 'imshow_series2\\',
        list_of_stacks = data, 
        list_of_masks = list_of_masks,
        list_of_titles_columns = np.arange(10),
        list_of_titles_rows = np.arange(2),
        colorbar_last_only = True,
        colorbar_labelsize = 10,
        )

def test_names_with_slashes_and_backslashes():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for test_names_with_slashes_and_backslashes')   

    _imgs = np.random.rand(10, 10)
    logger.save(r'test_param1', _imgs)
    logger.save(r'test_param2/', _imgs)
    logger.save(r'test_param3\\', _imgs)
    logger.save(r'test_param4\d', _imgs)
    logger.save(r'test_param4\d2\\', _imgs)
    logger.save(r'test_param4\d2/', _imgs)
    logger.save(r'test_param4\d2/e', _imgs)

def test_log_confusion_matrix():
    print('Testing function', inspect.currentframe().f_code.co_name)
    from sklearn.metrics import confusion_matrix
    
    n_classes = 52
    vec1 = (np.random.rand(10000)*n_classes).astype('int')
    vec2 = (np.random.rand(10000)*n_classes).astype('int')
    target_names = np.arange(n_classes)
    
    cm = confusion_matrix(vec1, vec2, normalize='all')
    logger = lognflow(temp_dir)
    logger('This is a test for log_confusion_matrix')
    logger.log_confusion_matrix('cm1', cm, target_names = target_names, 
                         title = 'Test_truth_accuracy_recall_precision')

def test_rename():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for test_rename')
    logger.rename(logger.log_dir.name + '_new_name')
    logger('This is another test for test_rename')
    
def test_save_text():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for test_save_text', flush = True)
    var = 2
    logger.save('text_log\a\t/\b/\b//\\/b', 'hello\n', suffix='txt', time_tag = False)
    logger.save('text_log\a', 'bye\n', suffix='json', time_tag = False)
    logger.save('text_log\a', var, suffix='pdb', time_tag = False)
    
def test_imshow_complex():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for test_imshow_complex', flush = True)
    
    mat = np.random.rand(100, 100) + 10 * 1j * np.random.rand(100, 100)
    
    logger(f'mat is complex? {np.iscomplexobj(mat)}')
    logger.imshow('mat', mat)
    
def test_replace_time_with_index():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for reading using logger')
    
    for _ in range(5):
        logger.save('test_param', np.array([_]))
        logger.save('testy/t', np.array([_]))
    
    flist = logger.get_flist('test_param*')
    data_in = logger.get_stack_from_files('test_param*')
    
    logger(flist)

    logger.replace_time_with_index('test_param*')
    
    flist = logger.get_flist('test_param*')
    data_out = logger.get_stack_from_files(flist = flist)
    
    logger(flist)
    
    logger(data_in)
    logger(data_out)

def test_copy_file():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for copying files')
    
    var = np.random.rand(10)
    fpath = logger.save('var', var, suffix = 'txt')
    
    logger.copy('myvar/varvar', fpath, suffix = 'pdb', 
             time_tag= True)
    
    var_check = logger.load('myvar/varvar*')
    assert str(var) == var_check
    
def test_copy_list_of_files():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for copy list of files')
    
    logger.save('test/var', np.random.rand(10), suffix = 'txt')
    logger.save('test/var', np.random.rand(10), suffix = 'fasta')
    logger.save('test/var', np.random.rand(10), suffix = 'json')
    logger.save('test/var', np.random.rand(10), suffix = 'txt')
    
    logger.copy('myvar/', 'test/var*', suffix = 'pdb', time_tag = False)
    
    for test_cnt in range(4):
        var_check1 = logger.load('test/var', file_index = test_cnt)
        var_check2 = logger.load('myvar/var', file_index = test_cnt)
        assert var_check1 == var_check2
    
def test_imshow_subplots():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for imshow_subplots')
    images = np.random.rand(20, 100, 100)
    logger.imshow_subplots('images', images, frame_shape = (4, 5))

def test_copy():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger1 = lognflow(temp_dir)
    fpath = logger1('This is a test for test_copy', flush = True)

    logger2 = lognflow(temp_dir)
    logger2.copy('some_text.txt', fpath)

def test_log_images_to_pdf():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('test log images in pdf')
    
    logger.imshow('im1', np.random.randn(30, 30))
    logger.imshow('im1', np.random.randn(20, 40))
    
    images = logger.get_stack_from_names('im1*.*')
    logger.images_to_pdf(
        'im1_all', parameter_value = images, time_tag = False)
    
def test_variables_to_pdf():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('test log variables in pdf')
    
    logger.imshow('im1', np.random.randn(30, 30))
    logger.imshow('im1', np.random.randn(20, 40))
    logger.variables_to_pdf('im1_all', 'im1*.*', time_tag = False)

def test_log_code():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('test log variables in pdf')
    
    logger.log_code(__file__)

def test_get_flist_multiple_directories():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('This is a test for test_multiple_directories_get_flist')
    
    logger.save('dir1/dir/var', np.random.rand(100))
    logger.save('dir2/dir/var', np.random.rand(100))
    logger.save('dir3/dir/var', np.random.rand(100))
    
    flist = logger.get_flist('dir*/dir/var*.npy')
    [print(_) for _ in flist]
    [print(logger.name_from_file(_)) for _ in flist]
        
def test_get_stack_from_files():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    
    logger('This is a test for get_stack_from_files')

    for _ in range(5):
        logger.save('A/img', np.random.rand(100, 100))
        logger.save('B/img', np.random.randn(100, 100))

    flist_A = logger.get_flist('A/*')
    flist_B = logger.get_flist('B/*')
    
    logger(flist_A)
    logger(flist_B)
    
    logger.replace_time_with_index('A/img')
    logger.replace_time_with_index('B/img')

    flist_A = logger.get_flist('A/*')
    flist_B = logger.get_flist('B/*')
    
    logger(flist_A)
    logger(flist_B)
    
    stack_A = logger.get_stack_from_files(flist = flist_A)
    stack_B = logger.get_stack_from_files(flist = flist_B)

    logger(f'stack_A.shape: {stack_A.shape}')
    logger(f'stack_B.shape: {stack_B.shape}')
    
    logger.imshow_series('data_samples', [stack_A, stack_B], dpi = 300)

    flist_A_AB, flist_B_AB = logger.get_common_files('A/*', 'B/*')
    logger(f'flist_A_AB: {flist_A_AB}')
    logger(f'flist_B_AB: {flist_B_AB}')
    
    if(flist_A_AB):
        
        dataset_A = logger.get_stack_from_files('A/*', flist = flist_A_AB)
        dataset_B = logger.get_stack_from_files('B/*', flist = flist_B_AB)
        
        logger.imshow_series('data_samples', 
                                 [dataset_A, dataset_B], dpi = 300)
        _ = logger._loggers_dict['log.txt'].log_size
        logger('Size of the log file in bytes is: ' \
               + f'{_}')

def test_text_to_object():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir, time_tag = False)
    test_list = ['asdf', 1243, "dd"]
    logger.save('test_list', test_list, suffix = 'txt')
    
    test_dict = {"one": "asdf", 'two': 1243, 'thre': "dd"}
    logger.save('test_dict', test_dict, suffix = 'txt')
    
    flist = logger.get_flist('*')
    print(flist)
    from lognflow.utils import text_to_collection
    for file_name_input in flist:
        print('='*60)
        print(f'file name: {file_name_input}')
        with open(file_name_input, 'r') as opened_txt:
            txt = opened_txt.read()
        print('text read from the file:')
        print(txt)
        print('- '*30)


        ext_obj = text_to_collection(txt)
        print(f'Extracted object is of type {type(ext_obj)}:')
        print(ext_obj)

def test_load_specific_fname():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('test get single specific fname')
    
    vec = np.array([1])
    logger.save('vec', vec, time_tag = False)

    vec2 = np.array([2])
    logger.save('vec2', vec2, time_tag = False)
    
    vec_out = logger.load('vec.npy')
    
    assert vec_out == vec

def test_get_stack_from_names():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('test get single specific fname')
    
    logger.imshow('im1', np.random.randn(30, 30))
    logger.imshow('im1', np.random.randn(20, 40))
    
    images = logger.get_stack_from_names('im1*')
    
    print(len(images))

def test_depricated_logviewer():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir)
    logger('testing the depricated logviewer')
    
    logger.save('test', 1)
    print(logger.logged.load('test*'))

def test_log_json():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(temp_dir, time_tag = False)
    logger('testing the save for list and dict')

    import pathlib
    from lognflow import printv

    CFG = dict(
        fpath = pathlib.Path('.'),
        length = 23)
    logger.save('CFG.json', CFG)
    CFG2 = logger.load('CFG.json', return_collection=True)
    
    printv(CFG)
    printv(CFG2)

    try:
        import torch
        vec3 = torch.tensor([6,7,8])
    except:
        vec3 = np.array([6,7,8])
    input_list = ['test', 2, np.array([[3],[4],[5]]),
                  vec3, [9, 10, 11], {'a': 12, 'b': [13, 14, 15]}]
    logger.save('var.txt', input_list)
    var_readback = logger.load('var.txt', return_collection=True)
    
    for x, y in zip(input_list, var_readback): 
        print(f'{x} --> {y}')
    
def test_lognflow_here():
    print('Testing function', inspect.currentframe().f_code.co_name)
    logger = lognflow(log_dir = './')
    logger('test')

if __name__ == '__main__':
    #-----IF RUN BY PYTHON------#
    temp_dir = select_directory()
    #===========================#
    test_replace_time_with_index()
    test_log_json()
    test_record_savefig()
    test_copy()
    test_variables_to_pdf()
    test_copy_file()
    test_log_code()    
    test_log_index()
    test_copy_list_of_files()
    test_text()
    test_save_text()
    test_lognflow_conflict_in_names()
    test_rename()
    test_logger()
    test_log_flush_period()
    test_get_record()
    test_record()
    test_record_without_time_stamp()
    test_save_matlab()
    test_save()
    test_names_with_slashes_and_backslashes()
    test_log_code()
    test_get_stack_from_files()
    test_get_stack_from_names()
    test_get_flist_multiple_directories()
    test_load_specific_fname()
    test_text_to_object()
    test_depricated_logviewer()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    test_imshow()
    test_imshow_series()
    test_imshow_complex()
    test_imshow_subplots()
    test_log_images_to_pdf()
    test_log_animation()
    test_hexbin()
    test_surface()
    test_log_confusion_matrix()
    test_scatter3()
    test_plot()
    test_hist()
    test_savefig()