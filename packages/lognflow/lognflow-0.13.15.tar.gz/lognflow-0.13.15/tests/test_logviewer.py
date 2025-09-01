#!/usr/bin/env python

"""Tests for `lognflow.logviewer` package."""

import pytest
import re
import numpy as np

from lognflow import (lognflow, select_directory, 
                      logviewer, printprogress,
                      text_to_collection)

import tempfile
temp_dir = tempfile.gettempdir()

def test_get_flist_multiple_directories():
    logger = lognflow(temp_dir)
    logger('Well this is a test for test_multiple_directories_get_flist')
    
    logger.log_single('dir1/dir/var', np.random.rand(100))
    logger.log_single('dir2/dir/var', np.random.rand(100))
    logger.log_single('dir3/dir/var', np.random.rand(100))
    
    flist = logger.logged.get_flist('dir*/dir/var*.npy')
    [print(_) for _ in flist]
    [print(logger.logged.name_from_file(_)) for _ in flist]
        
def test_logviewer():
    logger = lognflow(temp_dir)
    logger('Well this is a test for logviewer')
    
    logger.log_single('test_param', np.random.rand(100))
    
    logged = logviewer(logger.log_dir, logger)
    print(logged.get_single('test_param*'))
    print(logged.get_text())

def test_get_stack_from_files():
    logger = lognflow(temp_dir)
    
    logger('Well this is a test for get_stack_from_files')

    for _ in range(5):
        logger.log_single('A/img', np.random.rand(100, 100))
        logger.log_single('B/img', np.random.randn(100, 100))

    logged = logviewer(logger.log_dir, logger)

    flist_A = logged.get_flist('A/*')
    flist_B = logged.get_flist('B/*')
    
    logger(flist_A)
    logger(flist_B)
    
    logger.logged.replace_time_with_index('A/img')
    logger.logged.replace_time_with_index('B/img')

    flist_A = logged.get_flist('A/*')
    flist_B = logged.get_flist('B/*')
    
    logger(flist_A)
    logger(flist_B)
    
    stack_A = logged.get_stack_from_files(flist = flist_A)
    stack_B = logged.get_stack_from_files(flist = flist_B)

    logger(f'stack_A.shape: {stack_A.shape}')
    logger(f'stack_B.shape: {stack_B.shape}')
    
    logger.log_imshow_series('data_samples', [stack_A, stack_B], dpi = 300)

    flist_A_AB, flist_B_AB = logged.get_common_files('A/*', 'B/*')
    logger(f'flist_A_AB: {flist_A_AB}')
    logger(f'flist_B_AB: {flist_B_AB}')
    
    if(flist_A_AB):
        
        dataset_A = logged.get_stack_from_files('A/*', flist = flist_A_AB)
        dataset_B = logged.get_stack_from_files('B/*', flist = flist_B_AB)
        
        logger.log_imshow_series('data_samples', 
                                 [dataset_A, dataset_B], dpi = 300)
        _ = logger._loggers_dict['main_log.txt'].log_size
        logger('Size of the log file in bytes is: ' \
               + f'{_}')

def test_text_to_object():
    logger = lognflow(temp_dir, time_tag = False)
    test_list = ['asdf', 1243, "dd"]
    logger.log_single('test_list', test_list, suffix = 'txt')
    
    test_dict = {"one": "asdf", 'two': 1243, 'thre': "dd"}
    logger.log_single('test_dict', test_dict, suffix = 'txt')
    
    logged = logviewer(logger.log_dir)
    flist = logged.get_flist('*')
    print(flist)
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

def test_get_single_specific_fname():
    logger = lognflow(temp_dir)
    logger('test get single specific fname')
    
    vec = np.array([1])
    logger.log_single('vec', vec, time_tag = False)

    vec2 = np.array([2])
    logger.log_single('vec2', vec2, time_tag = False)
    
    logged = logviewer(logger.log_dir)
    vec_out = logged.get_single('vec.npy')
    
    assert vec_out == vec

def test_get_stack_from_names():
    logger = lognflow(temp_dir)
    logger('test get single specific fname')
    
    logger.log_imshow('im1', np.random.randn(30, 30))
    logger.log_imshow('im1', np.random.randn(20, 40))
    
    logged = logviewer(logger.log_dir)

    images = logged.get_stack_from_names('im1*')
    
    print(len(images))

if __name__ == '__main__':
    temp_dir = select_directory()
    test_get_stack_from_files()
    test_get_stack_from_names()
    test_get_flist_multiple_directories()
    test_get_single_specific_fname()
    test_logviewer()
    test_text_to_object()
