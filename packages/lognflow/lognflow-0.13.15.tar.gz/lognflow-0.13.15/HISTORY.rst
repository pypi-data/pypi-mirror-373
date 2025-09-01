History
=======

0.1.0 (2022-11-16)
------------------

* First release on PyPI.

0.3.0 (2022-12-19)
------------------

* Very consistent and easy-to-handle interface

0.3.2 (2022-12-27)
------------------

* log your dictionary.

0.5.2 (2023-01-11)
------------------

* logger call takes txt only for the main_log
* main_log name can have no time_stamp
* All logs can be force_flush = True.
* __del__ is well implemented.

0.5.3 (2023-03-19)
------------------

* use logger.log_single('aName', aDict) to save a dictionary using numpy.savez
* time_in_file_name has been changed to time_tag, sorry there! but early stages.
* time_tag is True in the constructor, but could always be set to False
* All tests passed!

0.6.0 (2023-03-22)
------------------
* This is a stable release
* All text files are handled by the with statement
* Renaming bug is fixed
* all tests run properly.
* lognflow has all that logviewer has. We will check if dir exists at every use

0.6.1 (2023-03-22)
------------------
* rename had a bug that is fixed

0.6.2 (2023-03-25)
------------------
* made it possible to flush_all()
* We support Python 3.7+ because of dataclasses
* printprogress now can disable printing anything and return ETA at the __call__

0.6.3 (2023-04-01)
------------------
* lognflow class does all logviewer does. Maybe it is time to remove logviewer.

0.6.4 (2023-04-06)
------------------
* Better documentation and examples for readme
* get_var is added to lognflow to get buffered variables logged by log_var

0.6.5 (2023-04-26)
------------------
* Fixed a bug in the docs to allow sphinx compile it.
* log_var will log only the valid time stamps.
* added end keyword argument to log_text

0.6.6 (2023-04-27)
------------------
* Better documentation
* added tifffile imread to logviewer and imwrite to lognflow

0.6.7 (2023-04-27)
------------------
* A bug in tifffile support was fixed

0.6.8 (2023-05-04)
------------------
* Fixing readme for PyPI.
* removed marker from log_plot. user marker and linestyle keyword arguments.
* printprogress returns proper ETA every time if print_function is set to None::

0.7.0 (2023-05-15)
------------------
* logviewer returns data by log_sigle if the full name is mentioned.

0.7.1 (2023-05-22)
------------------
* printprogress supports lognflow.
* bugs fixed in lognflow.
* For now I guess lognflow and logviewer could be separate.

0.7.2 (2023-05-25)
------------------
* bug fixed in logviewer
* text_to_object added to logviewer to read dict or list logged via log_single
* test pass for logviewer including the test for text_to_object

0.7.3 (2023-06-01)
------------------
* bug fixed in logviewer in the use of suffix in get_stack_of_files
* log_imshow takes colorbar and remove_axis_ticks flags.
* every lognflow instance has a logviewer pointing to its log_dir called logged.

0.7.4 (2023-06-26)
------------------
* critical bug fixed in log_imshow

0.7.5 (2023-06-27)
------------------
* Added complex numbers to log_imshow

0.7.6 (2023-07-17)
------------------
* printprogress can handle up to 99 days
* log_text takes any save_as
* If variable name has escape key is alright
* If variable name is splitable, we replace them with _

0.8.0 (2023-07-25)
------------------
* logger.save and savez are set to be identical to log_single.
* logged.load is set to be identical to get_single.
* utils.py is added to contain all misc functions.
* replace_all added to utils

0.8.1 (2023-07-26)
------------------
* a bug fixed in log_var

0.8.2 (2023-08-02)
------------------
* the word save_as is now replaced with suffix as is in pathlib
* all loggers can take the suffix as the extension in the parameter_name

0.8.3 (2023-08-02)
------------------
* critical bug fixed in log_var to support v0.8.2

0.8.4 (2023-08-03)
------------------
* variable names that are pecular will always be fixed first.
* suffix can be read form the file name.
* time_tag will always accompany file name unless stated otherwised.

0.8.5 (2023-08-04)
------------------
* Some functions can go to utils and be mentioned in the __init__
* a bug was fixed in printprogress.

0.8.6 (2023-08-04)
------------------
* plt_utils was not added tp 0.8.5

0.9.0 (2023-08-09)
------------------
* copy() is now possible from a file or a variable name into another
* default suffix in get_flist is *
* logviewer.get_stack_of_files is only useful for reading data.
* more tests are added.
* moved multichannel_to_frame to utils

0.9.1 (2023-08-25)
------------------
* bug removed from plt_utils numbers_as_images_4D.
* bug removed from printprogress when number of steps is very small.

0.10.0 (2023-09-01)
-------------------
* I added multiprocessor to lognflow
* bug fixed in logviewer

0.10.1 (2023-09-12)
-------------------
* multi_channel_by_subplots bug fixed for non-square shape
* default colormap is viridis everywhere
* multiprocessor heavily debugged and made a lot easier to use
* better tests added for multiprocessor

0.10.2 (2023-10-04)
-------------------
* printprogress can be used as an iterator, test added
* time_tag is False by default for copy()
* to log MATLAB files, input must be a dictionary.
* bug fixed in get_flist to return dirs only as well
* all new features for Python 3.10 onwards are removed.

0.10.3 (2023-10-09)
-------------------
* multiprocessor handles errors with maximum speed as all processes share error_event
* multichannel_plots assume fitrst fimension is the channels not the last 
* printprogress as iterator does not take the first __next__ as a tick
* log_imshow takes meaningful input sizes to make one frame
* log_imshow_by_subplots can put images in different places
* log_imshow_series is the new name of the log_canvas
* if there are multiple images the shape should be n_f x n_r x n_c
* tests are added for all functions
* tests for lognflow.utils is added

0.10.4 (2023-10-12)
-------------------
* get_flist returns whatever search pattern means for .glob
* plt_tight_layout is removed and replaced by bbox
* You can get name from file when file is within the log_dir root

0.10.5 (2023-10-18)
-------------------
* Added new files for readthedocs
* copy() checks for proper use of arguments
* __call__ returns fpath
* loopprocessor is added

0.10.6 (2023-10-19)
-------------------
* bugs fixed in multiprocessor and loopprocessor
* tests added

0.10.7 (2023-11-01)
-------------------
* multiprocessor_gen is a generator that yields the list of arrived results
* get_flist and thus get_single do not put asterisks on their own.

0.10.8 (2023-11-03)
-------------------
* a bug fixed in get_flist

0.10.9 (2023-12-01)
-------------------
* a bug fixed in name generator when suffix is given
* copy returns destination path
* exists_ok can be given to make the log_dir of lognflow
* added get_namelist and its test
* bug fixed in plt_utils
* plt_imshow added to plt_utils

0.10.10 (2024-01-30)
--------------------
* rgb2hsv is added
* plt_imshow supports complex color map and is bug free
* added printprogress to loopprocessor

0.11.0 (2024-02-25)
-------------------
* is_builtin_collection is added for multiprocessor concatenation
* setting time_tag to 'counter' or 'counter&time' will count filenames instead of time
* plt_violinplot was added
* plt_imhist is added 

0.11.1 (2024-03-26)
-------------------
* plt_imshow_by_subplots takes stacks as well now.
* log_code is added, pass __file__ for current script to be logged.
* multiple plt_imhist is possible

0.11.2 (2024-05-03)
-------------------
* imshow_series supports both orientations
* get_stack_from_names returns np array if possible
* imshow_series now takes titles for columns and rows

0.11.3 (2024-05-17)
-------------------
* imshow_series supports titles for rows and coloumns

0.12.0 (2024-06-29)
-------------------
* plt_imshow takes portrait = True as input 
* a few other bugs are fixed
* plt-scatter3 is added
* afterall, I am removing logviewer, all functions are in lognflow
* inheriting logging is in my TODO list but 5 basic functions are added.

0.12.1 (2024-07-08)
-------------------
* animation is added to scatte3
* imshow_by_subplots is a lot better
* many other bugs are fixed

0.12.2 (2024-07-08)
-------------------
* critical bugs fixed!

0.12.3 (2024-07-08)
-------------------
* plt_imshow complex real and image will have default cmap
* transform3D_viewer is added for manipulating 3D point cloud

0.12.4 (2024-07-09)
-------------------
* transform3D_viewer is more concise
* TODO: next, I will take multiple fixed and a referenced point cloud

0.12.5 (2024-07-10)
-------------------
* transform3D_viewer supports applying the transform to others

0.12.6 (2024-07-11)
-------------------
* transform3D_viewer improved

0.12.7 (2024-07-12)
-------------------
* some of the names of the funcitons are mroe accurate now
* plot now takes arguments that plt.plot takes and a bug has been fixed there!

0.12.8 (2024-07-27)
-------------------
* added question_dialog
* bugs fixed in transform3D_viewer
* suffix in load only sets the reader and does not disregard the current suffix
* added support to load python collections including for text_collection
* list, tuple or dict
* np.array, torch.tensor

0.12.9 (2024-07-27)
-------------------
* more like logging
* imshow_by_subplots is now fully functional

0.12.10 (2024-08-10)
-------------------
* the 3D viewer transformer shows the connection between parts
* the imshow_by_subplots had a bug that is fixed

0.12.11 (2024-08-10)
-------------------
* the bug in scatter3 without animation is fixed.

0.12.12 (2024-08-28)
-------------------
* log_dir assertion only throws a warning
* printvar try 1.
* pyrunner try 1. is added

0.12.13 (2024-08-29)
-------------------
* critical error removed

0.12.14 (2024-08-30)
-------------------
* removed dependency on dill

0.12.15 (2024-09-12)
-------------------
* added contour_overlayed
* moved loopprocessor to multiprocessor
* added printv
* added plot_marker

0.12.16 (2024-09-10)
-------------------
* added plt_confusion_matrix
* changed the name of imshow_series and imshow_by_subplots and plot_marker
* plot_marker is plt_mark
* fixes for plt_utils
* all tests passed!

0.12.17 (2024-10-17)
-------------------
* fixed a bug in plt_hist2
* added plt_plot

0.12.18 (2024-10-22)
-------------------
* allow pyrunner to be imported from lognflow itself
* bug fixed in lognflow.plot
* block_runner supports code_block_id to be int, float or string.
* block_runner supports debugging

0.12.19 (2024-10-24)
-------------------
* plt_hist2 is easier to use now
* plt_plot supports shapes N, (1, N)
* record accepts argument savefig
* block_runner reads the code before running
* time_tag is True by default again
* removed all imports from lognflow for faster loading
* all tests are passed!

0.13.00 (2024-11-8)
-------------------
* should have added a revision in the last "patch"
* allow access to plt_imhist fig_ax

0.13.01 (2024-11-14)
-------------------
* turned title into str when passing to plt_utils functions
* plt_imshow_subplots bug fixed for when fram_shape is given
* crtical bugs fixed in plt_imshow_series

0.13.02 (2024-11-15)
-------------------
* added vmin and vmax to plt_imshow_series

0.13.03 (2024-11-19)
-------------------
* plt_imshow_series updated heavily.

0.13.04 (2024-11-21)
-------------------
* more sensible printv
* added printv to getLogger
* confusion_matrix fixed

0.13.05 (2024-11-29)
-------------------
* plt_confusion_matrix puts black rectangles around diagonal elements
* confusion matrix is much more useful now
* printvar avoids printing long massages

0.13.06 (2024-11-29)
-------------------
* critical bug in plt_imshow for complex numbers
* critical bug fixed in printv

0.13.07 (2024-12-06)
-------------------
* using pyvista you can visualize 3D volumes easily by pv_volume
* another fix for text color of confusion matrix
* plt_plot xlim and ylim added
* bug fixed in plt_imshow_series

0.13.08 (2024-12-13)
-------------------
* plt_plot takes grid keyword argument

0.13.09 (2024-12-17)
-------------------
* window for plt_imshow went in a try 

0.13.10 (2024-12-19)
-------------------
* plt_imshow_subplots takes complex images too
* plt_record takes savefig and plot_time_window to plot the windowed average

0.13.11 (2025-01-03)
-------------------
* rrecord can take the arguments for plotting and not the record flush
* changing window title will not raise error any more in ipynb

0.13.12 (2025-04-01)
-------------------
* text_to_collection returns pathlib WindowsPath if it was written to a text
* log_dir Warning will be issued only once.

0.13.13 (2025-06-01)
-------------------
* fixed many bugs in plt_utils

0.13.14 (2025-06-01)
-------------------
* fixed plt_imshow_series color bars
* read json automatically

0.13.15 (2025-09-01)
-------------------
* added is_file