lognflow
========

Log and Flow tracking made easy with Python. You can install it by::

	pip install lognflow

A simple program to use it would be similar to the following, if the root for all logs is "c:\all_logs\\"::

	from lognflow import lognflow
	import numpy as np
	
	data = np.random.rand(100)

	logger = lognflow(r'c:\all_logs\\')
	logger('This is a test for lognflow and save')
	logger.save('data', data)
	data = logger.load('data*.npy')
	
	logger.plot('data', data)

Apart form lots of easy logging and loading functionalities, lognflow provides a very nice progress bar that does not make a mess in terminals that do not support \r::

	from lognflow import printprogress
	N = 100
	pbar = printprogress(N)
	for _ in range(N):
		# do_something()
		pbar()
		
There is also a conviniant way to use multiprocessing in Python. You wish to 
provide a function name, iterable inputs and shared inputs. Then ask 
to run the function over the iterable inputs using multiprcessing. Then
The multiprocessor is for you. The following is a cross-correlation of two
masked verctors using a given ststistical function::

	from lognflow import multiprocessor
	
	def masked_cross_correlation(inputs_to_iter_sliced, inputs_to_share):
		""" Calculate the correlation of two masked vectors, then use a given
			statsitcal function to get the stat of the correlation.
		"""
	    vec1, vec2 = inputs_to_iter_sliced
	    mask, statistics_func = inputs_to_share
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
	    
	
	if __name__ == '__main__':
	    data_shape = (1000, 2000)
	    data1 = np.random.randn(*data_shape)
	    data2 = 2 + 5 * np.random.randn(*data_shape)
	    mask = (2*np.random.rand(data_shape[1])).astype('int')
	    statistics_func = np.median
	    
	    inputs_to_iter = (data1, data2)
	    inputs_to_share = (mask, statistics_func)
	    ccorr = multiprocessor(masked_cross_correlation, 
	    					   inputs_to_iter, 
	    					   inputs_to_share)
	    print(f'ccorr: {ccorr}')

In this package we use a folder on the HDD to generate files and folders in typical
formats such as numpy npy and npz, png, ... to log. A log viewer is also availble
to turn an already logged flow into variables. Obviously, it will read the folders 
and map them for you, which is something you could spend hours to do by yourself.
Also there is the nicest progress bar, that you can easily understand
and use or implement yourself when you have the time.

Looking at most logging packages online, you see that you need to spend a lot of time
learning how to use them and realizing how they work. Especially when you have to deal
with http servers and ... which will be a huge pain when working for companies
who have their own HPC. 

This is why lognflow is handy and straight forward.

Many tests are avialable in the tests directory.

* Free software: GNU General Public License v3
* Documentation: https://lognflow.readthedocs.io.

Features
--------

* lognflow puts all the logs into a directory on your pc
* lognflow makes it easy to log text or simple plots.
* lognflow makes it easy to load variables or directories
* printprogress is one of the best progress bars in Python.
* multiprocessor makes it easy to use multiprocessing in Python.

Credits
^^^^^^^^

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
