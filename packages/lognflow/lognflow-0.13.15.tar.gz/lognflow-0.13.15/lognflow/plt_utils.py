import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec
from   matplotlib.colors import hsv_to_rgb
from   matplotlib.widgets import RangeSlider, TextBox, Button
from   mpl_toolkits.mplot3d import Axes3D
from   mpl_toolkits.axes_grid1 import make_axes_locatable
from   itertools import cycle as itertools_cycle
from   itertools import product as itertools_product

matplotlib_lines_Line2D_markers_keys_cycle = itertools_cycle([
    's', '*', 'd', 'X', 'v', '.', 'x', '|', 'D', '<','^',  '8','p',  
    '_','P','o','h', 'H', '>', '1', '2','3', '4',  '+', 'x', ])

matplotlib_colors_list = [
    'green', 'blue', 'cyan', 'red', 'magenta', 'yellow', 
    'orange', 'purple', 'brown', 'pink', 'lime', 
    'indigo', 'violet', 'turquoise', 'teal', 'gold', 
    'silver', 'lavender', 'maroon', 'coral', 'navy', 
    'beige', 'chocolate', 'olive', 'skyblue', 'rose', 
    'crimson', 'plum', 'orchid', 'chartreuse', 'tan',
]

def plt_colorbar(mappable, colorbar_aspect=3, 
                 colorbar_pad_fraction=0.05, colorbar_invisible=False, 
                 fontsize=10, tick_labels=None):
    """
    Add a colorbar to the current axis with consistent width.

    Parameters:
        mappable (AxesImage): The image to which the colorbar applies.
        colorbar_aspect (int): The aspect ratio of the colorbar width relative 
            to the axis width. Default is 3.
        colorbar_pad_fraction (float): The fraction of padding between the 
            axis and the colorbar. Default is 0.05.
        colorbar_invisible (bool): Whether to make the colorbar invisible. Default is False.
        fontsize (int): Font size for the colorbar tick labels. Default is 10.
        tick_labels (list or None): Custom labels for the colorbar ticks. 
        If None, default tick labels are used.

    Returns:
        Colorbar: The colorbar added to the axis.
    """

    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    width = ax.get_position().width / colorbar_aspect
    cax = divider.append_axes("right", size=width, pad=colorbar_pad_fraction)
    cbar = fig.colorbar(mappable, cax=cax)

    if colorbar_invisible:
        cbar.ax.set_visible(False)
    else:
        cbar.ax.tick_params(labelsize=fontsize)

        if tick_labels is not None:
            ticks = cbar.get_ticks()
            if len(tick_labels) == len(ticks):
                ticks = np.linspace(
                    mappable.get_clim()[0], mappable.get_clim()[1], len(tick_labels))
                cbar.set_ticks(ticks)
                cbar.set_ticklabels(tick_labels)

    return cbar

def complex2hsv(data_complex, vmin=None, vmax=None):
    """ complex2hsv
        Routine to visualise complex array as 2D image with color conveying
        phase information
        data_complex must be a complex 2d image
    """
    sx, sy = data_complex.shape

    data_abs = np.abs(data_complex)
    if vmin is None: vmin = data_abs.min()
    if vmax is None: vmax = data_abs.max()
    sat = (data_abs - vmin) / (vmax - vmin)
    data_angle = np.angle(data_complex) % (2 * np.pi)
    hue = data_angle / (2 * np.pi)
    a, b = np.divmod(hue, 1.0)

    H = np.zeros((sx, sy, 3))
    H[:, :, 0] = b
    H[:, :, 1] = np.ones([sx, sy])
    H[:, :, 2] = sat

    return hsv_to_rgb(H), data_abs, data_angle

def stack_to_frame(stack, frame_shape : tuple = None, borders = 0):
    """ turn a stack of images into a 2D frame of images
        This is very useful when lots of images need to be tiled
        against each other.
    
        Note: if the last dimension is 3, all images are RGB, if you don't wish that
        you have to add another dimension at the end by np.expand_dim(arr, axis = -1)
    
        :param stack: np.ndarray
                It must have the shape of either
                n_im x n_r x n_c
                n_im x n_r x  3  x  1
                n_im x n_r x n_c x  3
                
            In all cases n_im will be turned into a frame
            Remember if you have N images to put into a square, the input
            shape should be 1 x n_r x n_c x N
        :param frame_shape: tuple
            The shape of the frame to put n_rows and n_colmnss of images
            close to each other to form a rectangle of image.
        :param borders: literal or np.inf or np.nan
            When plotting images with matplotlib.pyplot.imshow, there
            needs to be a border between them. This is the value for the 
            border elements.
            
        output
        ---------
            Since we have N channels to be laid into a square, the side
            length would be ceil(N**0.5) if frame_shape is not given.
            it produces an np.array of shape n_f x n_r * f_r x n_c * f_c or
            n_f x n_r * f_r x n_c * f_c x 3 in case of an RGB input.
    """
    is_rgb = stack.shape[-1] == 3
    
    if(len(stack.shape) == 4):
        if((stack.shape[2] == 3) & (stack.shape[3] == 1)):
            stack = stack[..., 0]
    
    n_im, n_R, n_C = stack.shape[:3]
        
    if(len(stack.shape) == 4):
        assert is_rgb, 'For a stack of images with axis 3, it should be 1 or 3.'

    assert (len(stack.shape) == 3) | (len(stack.shape) == 4), \
        f'The stack you provided can have specific shapes. it is {stack.shape}'

    if(frame_shape is None):
        square_side = int(np.ceil(np.sqrt(n_im)))
        frame_n_r, frame_n_c = (square_side, square_side)
    else:
        frame_n_r, frame_n_c = frame_shape
    n_R += 2
    n_C += 2
    new_n_R = n_R * frame_n_r
    new_n_C = n_C * frame_n_c

    if is_rgb:
        frame = np.zeros((new_n_R, new_n_C, 3), dtype = stack.dtype)
    else:
        frame = np.zeros((new_n_R, new_n_C), dtype = stack.dtype)
    used_ch_cnt = 0
    if(borders is not None):
        frame += borders
    for rcnt in range(frame_n_r):
        for ccnt in range(frame_n_c):
            ch_cnt = rcnt + frame_n_c*ccnt
            if (ch_cnt<n_im):
                frame[rcnt*n_R + 1: (rcnt + 1)*n_R - 1,
                      ccnt*n_C + 1: (ccnt + 1)*n_C - 1] = \
                    stack[used_ch_cnt]
                used_ch_cnt += 1
    return frame

def stacks_to_frames(stack_list, frame_shape : tuple = None, borders = 0):
    """ turn a list of stack of images into a list of frame of images
        This is simply a list of calling stack_to_frame
        :param stack_list:
            It must have the shape of either
            n_f x n_im x n_r x n_c
            n_f x n_im x n_r x  3  x 1
            n_f x n_im x n_r x n_c x 3

    """    
    return np.array([stack_to_frame(stack, 
                                    frame_shape = frame_shape, 
                                    borders = borders) for stack in stack_list])

def plt_hist2(data, bins=30, cmap='viridis', use_bars = False,
              xlabel=None, ylabel=None, zlabel=None, title=None, 
              colorbar=True, fig_ax=None, colorbar_label=None,
              elev=None, azim=None):
    """
    Plot a 3D histogram with a colormap based on the height of the bars.

    Parameters:
    data (array-like): N x 2 array of (x, y) points.
    bins (int): Number of bins in each dimension.
    cmap (str): Name of the matplotlib colormap to use for the bars.
    xlabel (str): Label for the x-axis.
    ylabel (str): Label for the y-axis.
    zlabel (str): Label for the z-axis.
    title (str): Title of the plot.
    colorbar (bool): Whether to show a colorbar representing bar heights.
    fig_ax (tuple): Optional tuple (fig, ax) to specify the figure and axis to plot on.
    colorbar_label (str): Label for the colorbar, if shown.
    elev (float): Elevation angle in the z-plane for the 3D view.
    azim (float): Azimuthal angle in the x-y plane for the 3D view.

    Returns:
    tuple: (fig, ax) - The figure and axis objects.
    """
    
    assert data.shape[1] == 2, "Data must have shape (N, 2)"
    
    counts, x_edges, y_edges = np.histogram2d(data[:, 0], data[:, 1], bins=bins)

    x_pos, y_pos = np.meshgrid(x_edges[:-1] + 0.5 * (x_edges[1] - x_edges[0]),
                               y_edges[:-1] + 0.5 * (y_edges[1] - y_edges[0]))
    x_pos = x_pos.ravel()
    y_pos = y_pos.ravel()
    z_pos = np.zeros_like(x_pos)

    dx = dy = (x_edges[1] - x_edges[0])
    dz = counts.ravel()
    norm_dz = dz / dz.max() if dz.max() > 0 else dz

    colors = plt.cm.get_cmap(cmap)(norm_dz)

    if fig_ax is None:
        fig = plt.figure()
        if use_bars:
            ax = fig.add_subplot(111, projection='3d')
        else:
            ax = fig.add_subplot(111)
    else:
        fig, ax = fig_ax
    
    if use_bars:
        bars = ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, 
                         color=colors, edgecolor=colors, alpha=1)
        ax.view_init(elev=elev, azim=azim)
        if colorbar:
            mappable = plt.cm.ScalarMappable(cmap=cmap)
            mappable.set_array(dz)
            cbar = plt.colorbar(mappable, ax=ax)
            if colorbar_label is not None:
                cbar.set_label(colorbar_label)
    else:
        im = ax.imshow(
            counts.T, cmap=cmap, origin='lower', aspect='auto',
            extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]])
        if colorbar:
            plt_colorbar(im)

    if xlabel is not None: ax.set_xlabel(xlabel)
    if ylabel is not None: ax.set_ylabel(ylabel)
    if zlabel is not None: ax.set_zlabel(zlabel)
    if title  is not None: ax.set_title(title)
    
    return fig, ax

def _compute_tn_from_cm(cm):
    """
    Compute True Negatives (TN) directly from the confusion matrix (cm).
    True Negatives are the elements that are not in the row or column of the class.
    """
    n_classes = cm.shape[0]
    total_samples = np.sum(cm)
    tn_total = 0
    for i in range(n_classes):
        cm_without_class_i = np.delete(np.delete(cm, i, axis=0), i, axis=1)
        tn_class_i = np.sum(cm_without_class_i)
        tn_total += tn_class_i
    tn_normalized = tn_total / total_samples
    return tn_normalized

def compute_tp_tn_fp_fn(cm):
    """
    computes average tp, tn, fp and fn of a confusion matrix
    Example:
    ---------
    
    import numpy as np
    from sklearn.metrics import confusion_matrix
    from lognflow.plt_utils import plt_confusion_matrix
    
    N, n_classes = 10000, 20
    
    labels1 = (np.random.rand(N)*n_classes).astype('int')
    labels2 = (np.random.rand(N)*n_classes).astype('int')
    target_names = np.arange(n_classes)

    cm = confusion_matrix(labels1, labels2, normalize='all')

    TP, TN, FP, FN = compute_tp_tn_fp_fn(cm)
    print(TP, TN, FP, FN)
    
    """
    
    total_samples = np.sum(cm)
    TP = np.sum(np.diag(cm)) / total_samples
    FP = np.sum(np.sum(cm, axis=0) - np.diag(cm)) / total_samples
    FN = np.sum(np.sum(cm, axis=1) - np.diag(cm)) / total_samples
    TN = _compute_tn_from_cm(cm)
    
    return TP, TN, FP, FN

def calculate_contrasting_color(value, cmap):
    """Calculate a contrasting color for a given value in the colormap."""
    r, g, b, _ = cmap(value)  # Get the RGBA values
    # Calculate luminance using the sRGB luminance formula
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # Return white for dark colors and black for light colors
    return 'white' if luminance < 0.5 else 'black'

def plt_confusion_matrix(cm, 
        target_names=None, title=None, cmap=None,
        figsize=None, fontsize = None, fontsize_title = None, show_zeros = False):
    """
    This function plots a confusion matrix and returns the figure and axis.
    Parameters:
    - cm: Confusion matrix
    - target_names: List of target names (default: None)
    - title: have any of the following options you like to see in the title
        title = YOUR_TITLE + '_truth' + '_accuracy' + '_recall' + '_precision' + '_f1_score' + '_specificity' + '_mcc'
        YOUR_TITLE could be nothing like ''
        eg. if I want to see the truth table and the f1_score I code:
            title = 'My truth table' + '_truth_f1_score'
        
    - cmap: Colormap (default: None)
    - figsize: Size of the figure (default: None)
    Returns:
    - fig: Figure object
    - ax: Axis object
    
    
    Example:
    ---------
    
    import numpy as np
    from sklearn.metrics import confusion_matrix
    from lognflow.plt_utils import plt_confusion_matrix
    
    N, n_classes = 10000, 20
    
    vec1 = (np.random.rand(N)*n_classes).astype('int')
    vec2 = (np.random.rand(N)*n_classes).astype('int')
    target_names = np.arange(n_classes)

    cm = confusion_matrix(vec1, vec2, normalize='all')

    plt_confusion_matrix(cm, target_names = target_names)
    plt.show()
    
    """
    TP, TN, FP, FN = compute_tp_tn_fp_fn(cm)

    figsize_was_None = False
    if figsize is None:
        figsize = np.ceil(cm.shape[0]**0.5)
        figsize_was_None = True
    if figsize_was_None:
        figsize = np.maximum(figsize, 5)
        figsize = (figsize + 1, figsize)
    if target_names is None:
        target_names = [chr(x + 65) for x in range(cm.shape[0])]

    if cmap is None:
        cmap = plt.get_cmap('Blues')

    fig, ax = plt.subplots(figsize=figsize)
    
    if fontsize is None:
        fontsize = 6*(np.minimum(*figsize) / cm.shape[0])**0.5
    if fontsize_title is None:
        fontsize_title = 4 * fontsize

    im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
    
    tick_marks = np.arange(len(target_names))
    ax.set_xticks(tick_marks)
    ax.set_xticklabels(target_names, rotation=45, fontsize = fontsize)
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(target_names, fontsize = fontsize)
    for i, j in itertools_product(range(cm.shape[0]), range(cm.shape[1])):
        clr = calculate_contrasting_color(cm[i, j] / cm.max(), cmap)
        if not show_zeros:
            if cm[i, j] == 0:
                continue
        ax.text(j, i, f"{cm[i, j]:2.02f}", horizontalalignment="center", color=clr,
                fontsize = fontsize)

    for i in range(cm.shape[0]):
        rect = plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False, 
                             edgecolor='darkred', lw=1, linestyle='--')
        ax.add_patch(rect)

    ax.set_ylabel('True label', fontsize = fontsize)
    ax.set_xlabel('Predicted label', fontsize = fontsize)
    if title is None:
        title_str = f'Average TP={TP:.02f}, TN={TN:.02f}, FP={FP:.02f}, FN={FN:.02f}'
    else:
        title_str = ''
        if '_truth' in title.lower():
            title_str += f'Average TP={TP:.02f}, TN={TN:.02f}, FP={FP:.02f}, FN={FN:.02f}\n'
            title = title.replace('_truth', '')
        if '_accuracy' in title.lower():
            accuracy = (TP + TN) / (TP + TN + FP + FN)
            title_str += f'Accuracy={accuracy:.04f}'
            title = title.replace('_accuracy', '')
        if '_recall' in title.lower():
            recall = TP / (TP + FN) if (TP + FN) > 0 else 0
            title_str += f', Recall={recall:.04f}'
            title = title.replace('_recall', '')
        if '_precision' in title.lower():
            precision = TP / (TP + FP) if (TP + FP) > 0 else 0
            title_str += f', Precision={precision:.04f}'
            title = title.replace('_precision', '')
        if '_f1_score' in title.lower():
            f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            title_str += f', F1-Score={f1_score:.04f}'
            title = title.replace('_f1_score', '')
        if '_specificity' in title.lower():
            specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
            title_str += f', Specificity={specificity:.04f}'
            title = title.replace('_specificity', '')
        if '_mcc' in title.lower():
            numerator = (TP * TN) - (FP * FN)
            denominator = ((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN)) ** 0.5
            mcc = numerator / denominator if denominator > 0 else 0
            title_str += f', MCC={mcc:.04f}'
            title = title.replace('_mcc', '')
            
        if len(title) > 0:
            if title[-1] != '\n':
                title += '\n'
        title_str = title + title_str
        
    ax.set_title(title_str, fontsize = fontsize_title)
    plt_colorbar(im, colorbar_invisible=False, colorbar_aspect = fontsize**0.5 * 4, 
                 fontsize = fontsize, tick_labels = target_names)
    return fig, ax

def complex2hsv_colorbar(
        fig_and_ax=None, vmin=0, vmax=1, 
        min_angle=0, max_angle=0, 
        fontsize=8, angle_threshold=np.pi / 18):
    
    xx, yy = np.meshgrid(
        np.linspace(-1, 1, 1000),
        np.linspace(-1, 1, 1000))
    conv, sat, _ = complex2hsv(xx + 1j * yy, vmax=1)

    # Set outside the circle to transparent
    mask = (xx ** 2 + yy ** 2) > 1
    conv_rgba = np.zeros((conv.shape[0], conv.shape[1], 4))
    conv_rgba[..., :3] = conv
    conv_rgba[..., 3] = 1.0  # Set alpha to 1 for everything
    conv_rgba[mask, 3] = 0  # Set alpha to 0 outside the circle
    conv_rgba[conv_rgba < 0] = 0
    conv_rgba[conv_rgba > 1] = 1
    conv_rgba = conv_rgba[::-1, :]
    if fig_and_ax is None:
        fig, ax = plt.subplots()
    else:
        try:
            fig, ax = fig_and_ax
        except Exception as e:
            print('fig_and_ax should be a two-tuple of (fig, ax). Use:')
            print('>>> fig, ax = plt.subplots()')
            raise e

    im = ax.imshow(conv_rgba, interpolation='nearest')  # Flip the image vertically
    ax.axis('off')

    diff = np.abs(max_angle - min_angle)
    # Draw lines at min and max angles if they are not too close
    if np.minimum(diff, 2 * np.pi - diff) > angle_threshold:
        for angle in [min_angle, max_angle]:
            x_end = 500 + np.cos(angle) * 500
            y_end = 500 - np.sin(angle) * 500
            ax.plot([500, x_end], [500, y_end], '--', color='gray')

    # Add text annotations for min and max values
    if int(vmin*100)/100 > 0:   #because we are going to show .2f
        ax.text(500, 500, f'{vmin:.2f}', 
                ha='center', va='center', fontsize=fontsize, color='white')

    # Calculate position for max value text and invert color for readability
    angle = 45 * np.pi / 180  # 45 degrees in radians
    x_max = int(np.cos(angle) * 500 + 300)
    y_max = int(np.sin(angle) * 500 - 200)

    bck_color = conv_rgba[y_max, x_max, :3]
    text_color = 1 - bck_color  # Invert color

    ax.text(x_max, y_max, f'{vmax:.2f}',
            ha='center', va='center', fontsize=fontsize, color=text_color)

    return fig, ax

def plt_violinplot(
        dataset:list, positions, facecolor = None, edgecolor = None, 
        alpha = 0.5, label = None, fig_and_ax : tuple = None, 
        title = None, plt_violinplot_kwargs = {}):
    
    if(fig_and_ax is None):
        fig, ax = plt.subplots(1)
    else:
        fig, ax = fig_and_ax
    violin_parts = ax.violinplot(dataset, positions, **plt_violinplot_kwargs)
    for partname in ('cbars','cmins','cmaxes','cmeans','cmedians','bodies'):
        vp = violin_parts.get(partname, [])
        if partname == 'bodies':
            for vp_body in vp:
                vp_body.set_facecolor(facecolor)
                vp_body.set_edgecolor(edgecolor)
                vp_body.set_alpha(alpha)
        else:
            if isinstance(vp, list):
                for v in vp:
                    v.set_edgecolor(facecolor)
            else:
                vp.set_edgecolor(facecolor)

    if title is not None:
        title = str(title)
        fig.suptitle(title)
        try:
            fig.canvas.manager.window.setWindowTitle(title)
        except: pass

    return fig, ax

class plt_imhist:
    def __init__(self, in_image, figsize=(12, 6), title=None, bins=None,
                 kwargs_for_imshow={}, kwargs_for_hist={}):
        if bins is not None:
            if not (bins in kwargs_for_hist):
                kwargs_for_hist['bins'] = bins
        
        try:
            in_image = in_image.detach().cpu().numpy()
            print('plt_imhist warning: '
                  'image converted from torch to numpy for plt!')
        except: pass

        # Adjust figsize to provide more space if needed
        self.fig, axs = plt.subplots(
            1, 2, figsize=figsize,
            gridspec_kw={'width_ratios': [5, 1], 'wspace': 0.1})
        self.fig.subplots_adjust(left=0.05, right=0.85, bottom=0.1, top=0.9)
        
        self.fig_ax = self.fig, axs[0]
        
        # Display the image
        self.im = axs[0].imshow(in_image, **kwargs_for_imshow)
        if title is not None:
            title = str(title)
            axs[0].set_title(title)
        axs[0].axis('off')
        
        cm = self.im.get_cmap()
        
        # Histogram
        im_image_ravel = in_image.ravel().copy()
        im_image_ravel = im_image_ravel[np.isnan(im_image_ravel) == False]
        im_image_ravel = im_image_ravel[np.isinf(im_image_ravel) == False]
        if len(im_image_ravel) == 0:
            im_image_ravel = in_image.ravel().copy()
        n, bins = np.histogram(im_image_ravel, **kwargs_for_hist)
        bin_centres = 0.5 * (bins[:-1] + bins[1:])
        axs[1].barh(
            bin_centres, n, height=(bins[1]-bins[0]),
            color=cm((bin_centres - bin_centres.min()) /
                         (bin_centres.max() - bin_centres.min())))
        axs[1].invert_xaxis()
        
        axs[1].yaxis.set_visible(True)
        axs[1].xaxis.set_visible(False)
        
        # Create textbox axes
        upper_text_ax = self.fig.add_axes([0.88, 0.85, 0.05, 0.05])
        lower_text_ax = self.fig.add_axes([0.88, 0.1, 0.05, 0.05])
        
        self.upper_text_box = TextBox(
            upper_text_ax, 'Max', initial=f'{in_image.max():.6f}')
        self.lower_text_box = TextBox(
            lower_text_ax, 'Min', initial=f'{in_image.min():.6f}')
        
        # Calculate the position for the slider
        slider_top = 0.85 - 0.02  # Bottom of the upper text box
        slider_bottom = 0.1 + 0.07  # Top of the lower text box
        slider_height = slider_top - slider_bottom  # Height between the two text boxes
        
        # Create slider axes on the right side of the histogram
        slider_ax = self.fig.add_axes(
            [0.895, slider_bottom, 0.02, slider_height], 
            facecolor='lightgoldenrodyellow')
        self.slider = RangeSlider(
            slider_ax, '', in_image.min(), in_image.max(),
            valinit=[in_image.min(), in_image.max()], orientation='vertical')
        self.slider.label.set_visible(False)
        self.slider.valtext.set_visible(False)
        
        self.lower_limit_line = axs[1].axhline(
            self.slider.val[0], color='k', linestyle='--')
        self.upper_limit_line = axs[1].axhline(
            self.slider.val[1], color='k', linestyle='--')
        
        # Initial text annotations for vmin and vmax
        self.vmin_text = axs[1].text(
            0.5, self.slider.val[0], f'{self.slider.val[0]:.6f}',
            transform=axs[1].get_yaxis_transform(), 
            ha='right', va='bottom', color='k')
        self.vmax_text = axs[1].text(
            0.5, self.slider.val[1], f'{self.slider.val[1]:.6f}',
            transform=axs[1].get_yaxis_transform(),
            ha='right', va='top', color='k')
        
        self.slider.on_changed(self.update)
        self.lower_text_box.on_submit(self.update_from_text)
        self.upper_text_box.on_submit(self.update_from_text)
    
    def update(self, val):
        self.im.set_clim(val[0], val[1])
        self.lower_limit_line.set_ydata([val[0], val[0]])
        self.upper_limit_line.set_ydata([val[1], val[1]])
        
        # Update text annotations to reflect the new vmin and vmax
        self.vmin_text.set_position((0.5, val[0]))
        self.vmin_text.set_text(f'{val[0]:.6f}')
        self.vmax_text.set_position((0.5, val[1]))
        self.vmax_text.set_text(f'{val[1]:.6f}')
        
        # Update text boxes to reflect the new values
        self.lower_text_box.set_val(f'{val[0]:.6f}')
        self.upper_text_box.set_val(f'{val[1]:.6f}')
        
        self.fig.canvas.draw_idle()
    
    def update_from_text(self, text):
        try:
            lower_val = float(self.lower_text_box.text)
            upper_val = float(self.upper_text_box.text)
            if lower_val < upper_val:
                self.slider.set_val([lower_val, upper_val])
        except ValueError:
            pass

def _listify_1d_list(list_of_obj):
    if list_of_obj is not None:
        if len(list_of_obj) > 1:
            it_is_1d = True
            for _ in list_of_obj:
                try:
                    if len(_) > 1:
                        it_is_1d = False
                except: pass
            if it_is_1d:
                list_of_obj = [np.array(list_of_obj).squeeze()]
    return list_of_obj

def plt_plot(y_values_list, *plt_plot_args, x_values_list = None, 
             fig_ax = None, title = None, **kwargs):
    """
        Plots multiple sets of y-values against x-values using Matplotlib, 
        with options to customize the plot.
    
        Parameters
        ----------
        y_values_list : list or iterable
            A list or iterable of y-values to plot. If a single 
            iterable is provided, it will be treated as 
            one dataset. If a list of iterables is provided, 
            each will be plotted as a separate line.
        
        x_values_list : list or iterable
            The x-values for the plot. This can either be a list 
            of the same length as `y_values_list`, 
            or a single iterable that will be reused for all y-values. 
            If `None`, y-values will be plotted 
            against their index.
        
        *plt_plot_args : tuple
            Additional positional arguments passed to the Matplotlib 
            `plot` function (e.g., line style, 
            marker type).
        
        fig_ax : tuple (figure, axes), optional
            A tuple containing a Matplotlib `figure` and `axes` object. 
            If `None`, a new figure and axes 
            will be created.
        
        title : str, optional
            The title of the plot. If `None`, no title will be set.
        
        **kwargs : dict
            Additional keyword arguments passed to the Matplotlib 
            `plot` function (e.g., `color`, `linewidth`).
        
        Returns
        -------
        tuple
            A tuple containing the Matplotlib `figure` and `axes`
             objects used for the plot.
        
        Raises
        ------
        ValueError
            If the length of `x_values_list` does not match the length of 
            `y_values_list` or if it is not 1.
        
        Notes
        -----
        - If `fig_ax` is provided, the plot will be added to the 
        given axes. Otherwise, a new figure and axes 
          will be created.
        - If `x_values_list` is `None`, y-values will be plotted against their index.
        - The function can handle multiple y-value datasets, plotting 
        each as a separate line.
        
        Example
        -------
        >>> y_values_list = [[1, 2, 3], [4, 5, 6]]
        >>> x_values_list = [1, 2, 3]
        >>> fig, ax = plt_plot(y_values_list, x_values_list)
        >>> plt.show()
    """
    y_values_list = _listify_1d_list(y_values_list)
    x_values_list = _listify_1d_list(x_values_list)
    
    if x_values_list is not None:
        assert ( (len(x_values_list) >= len(y_values_list)) | \
                 (len(x_values_list) == 1) ), \
                f'lognflow plt_plot: x_values_list has length {len(x_values_list)},'\
                ' should have length of 1 or the same as parameters list: '\
                f'{len(y_values_list)}.'
    
    if fig_ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    else:
        fig, ax = fig_ax
    
    if 'xlim' in kwargs:
        xlim = kwargs['xlim']
        kwargs.pop('xlim')
        ax.set_xlim(xlim)

    if 'ylim' in kwargs:
        ylim = kwargs['ylim']
        kwargs.pop('ylim')
        ax.set_ylim(ylim)
    
    use_grid = None
    if 'grid' in kwargs:
        use_grid = kwargs['grid']
        kwargs.pop('grid')    
    
    for list_cnt, y_values in enumerate(y_values_list):
        if(x_values_list is None):
            ax.plot(y_values, *plt_plot_args, **kwargs)
        else:
            if(len(x_values_list) == len(y_values)):
                x_values = x_values_list[list_cnt]
            else:
                x_values = x_values_list[0]
            ax.plot(x_values, y_values, *plt_plot_args, **kwargs)

    if use_grid:
        if isinstance(use_grid, dict):
            ax.grid(**use_grid)
        else:
            ax.grid(use_grid)

    if title is not None:
        title = str(title)
        ax.set_title(title)
        
    return (fig, ax)

def plt_imshow(img, 
               fig_ax = None,
               colorbar = True, 
               remove_axis_ticks = False, 
               remove_middle_axis_ticks = True,
               title = None, 
               cmap = None,
               angle_cmap = None,
               portrait = None,
               aspect = 'equal',
               figsize = None,
               title_ax_gap = 0.05,
               show_values = False,
               values_fontsize = 6,
               **kwargs):
    """
    Display an image or a complex-valued image using matplotlib's imshow.

    This function can handle real images and complex-valued data, allowing for
    visualization of magnitude and phase. The function provides options for 
    displaying a colorbar, removing axis ticks, and setting titles. If the input 
    image is complex, it will be represented in either RGB or separate real and 
    imaginary components.

    Parameters:
    ----------
    img : array_like
        The image data to be displayed. This can be a 2D array for real images or 
        a 2D complex array for complex-valued data.
        
    fig_ax : tuple, optional
        A tuple containing a figure and an axis to plot on. If None, a new figure 
        and axis will be created.
        
    colorbar : bool, optional
        Whether to display a colorbar alongside the image. Default is True.
        
    remove_axis_ticks : bool, optional
        Whether to remove ticks from the axes. Default is False.
        
    title : str, optional
        A title to be displayed above the figure. Default is None.
        
    cmap : str, optional
        The colormap to be used for displaying the image. Default is None.
        to get real and imag part separately for a xomplex image, use 
        cmap = 'complex_real_imag', if you don't provide the cmap, it will show
        the abs and angle part of the image separately.
        
    angle_cmap : str, optional
        The colormap to be used for displaying the angle of complex numbers. 
        Default is twilight_shifted. 
        
    portrait : bool, optional
        If True, the figure will be set up in portrait mode. If None, the function 
        will automatically determine the orientation based on the window dimensions.
    
    aspect : str, optional
        by default I set the aspect ratio to equal
        
    figsize: 2-tuple, optional
        figsize parameter of plt.figure
    
    **kwargs : keyword arguments
        Additional keyword arguments passed to `imshow`, such as `vmin`, `vmax`, 
        etc.

    Returns: 2-tuple
    -------
    fig : matplotlib.figure.Figure
        The figure object containing the displayed image(s).
        
    ax : matplotlib.axes.Axes or list of Axes
        The axes object(s) containing the displayed image(s). If the image is 
        complex and displayed as two separate plots, a list of axes will be returned.
    """
    
    vmin = kwargs.get('vmin', None)
    vmax = kwargs.get('vmax', None)
    
    try: img = img.detach().cpu().numpy()
    except: pass
    try: img = np.array(img)
    except: raise TypeError('plt_imshow accepts numpy or torch images only')
    
    if ( (not np.iscomplexobj(img))
         & ((cmap == 'complex') or (cmap == 'real_imag'))
         & (len(img) == 2) & (len(img.shape) == 3) ):
        img = img[0] + 1j * img[1]
        
    assert len(img.shape) == 2, 'plt_imshow accepts images only' + \
        f'TypeError: Invalid shape {img.shape} for image data.'

    if(not np.iscomplexobj(img)):
        if fig_ax is None:
            fig, ax = plt.subplots(figsize = figsize)
        else:
            fig, ax = fig_ax
        if title is not None: ax_top = ax.get_position().y1
        im = ax.imshow(img, cmap = cmap, **kwargs)
        if show_values:
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    text = f"{img[i, j]}"
                    color = 'white' if (i + j) % 2 == 0 else (0.8, 0.8, 0.8)
                    ax.text(j, i, text, ha='center', va='center', color=color, fontsize=values_fontsize)
        if(colorbar):
            plt_colorbar(im)
        if(remove_axis_ticks):
            plt.setp(ax, xticks=[], yticks=[])
        if aspect is not None:
            ax.set_aspect(aspect)
    else:
        if (cmap == 'complex'):

            complex_image, data_abs, data_angle = complex2hsv(
                img, vmin = vmin, vmax = vmax)
        
            if vmin is None: vmin = data_abs.min()
            if vmax is None: vmax = data_abs.max()
            
            try:
                min_angle = data_angle[data_abs > 0].min()
            except:
                min_angle = 0
            try:
                max_angle = data_angle[data_abs > 0].max()
            except:
                max_angle = 0
        
            if fig_ax is None:
                fig, ax = plt.subplots(figsize = figsize)
            else:
                fig, ax = fig_ax
            if title is not None: ax_top = ax.get_position().y1
            im = ax.imshow(complex_image)
            if(remove_axis_ticks):
                plt.setp(ax, xticks=[], yticks=[])

            if(colorbar):
                fig, ax_inset = complex2hsv_colorbar(
                    (fig, ax.inset_axes([0.79, 0.03, 0.18, 0.18], 
                                        transform=ax.transAxes)),
                    vmin=vmin, vmax=vmax, min_angle=min_angle, max_angle=max_angle)
                ax_inset.patch.set_alpha(0)
            if aspect is not None:
                ax.set_aspect(aspect)
        else:
            
            if fig_ax is None:
                fig = plt.figure(figsize = figsize)
            else:
                fig, _ = fig_ax
            
            try:
                window = plt.get_current_fig_manager().window
                if (window.height() > window.width()) & (portrait is None):
                    portrait = True
            except: pass
            if portrait:
                ax = [fig.add_subplot(2, 1, 1), fig.add_subplot(2, 1, 2)]
            else:
                ax = [fig.add_subplot(1, 2, 1), fig.add_subplot(1, 2, 2)]
            
            if title is not None: ax_top = ax[0].get_position().y1
            
            complex_real_imag = False
            if cmap is not None:
                if 'real_imag' in cmap:
                    complex_real_imag = True
            if complex_real_imag:
                cmap = cmap.split('real_imag')[0]
                if len(cmap) == 0: cmap = None
                else: cmap = cmap[:-1]
                if angle_cmap is None:
                    angle_cmap = cmap
                im = ax[0].imshow(np.real(img), cmap = cmap, **kwargs)
                if(colorbar):
                    plt_colorbar(im)
                ax[0].set_title('real')
                im = ax[1].imshow(np.imag(img), cmap = angle_cmap, **kwargs)
                if(colorbar):
                    plt_colorbar(im)
                ax[1].set_title('imag')
            else:
                im = ax[0].imshow(np.abs(img), cmap = cmap, **kwargs)
                if(colorbar):
                    plt_colorbar(im)
                ax[0].set_title('abs')    
                if angle_cmap is None:
                    angle_cmap = 'twilight_shifted'
                im = ax[1].imshow(np.angle(img), cmap = angle_cmap, **kwargs)
                if(colorbar):
                    plt_colorbar(im)
                ax[1].set_title('angle')
                            
            if(remove_axis_ticks):
                plt.setp(ax[0], xticks=[], yticks=[])
                ax[0].xaxis.set_ticks_position('none')
                ax[0].yaxis.set_ticks_position('none')
                plt.setp(ax[1], xticks=[], yticks=[])
                ax[1].xaxis.set_ticks_position('none')
                ax[1].yaxis.set_ticks_position('none')
            
            if remove_middle_axis_ticks:
                if portrait:
                    plt.setp(ax[0], xticks=[])
                    ax[0].xaxis.set_ticks_position('none')
                else:
                    plt.setp(ax[1], yticks=[])
                    ax[1].yaxis.set_ticks_position('none')

            
            if aspect is not None:
                ax[0].set_aspect(aspect)
                ax[1].set_aspect(aspect)
    
    if title is not None:
        title = str(title)
        fig.suptitle(title, y=ax_top + title_ax_gap)
        try: 
            fig.canvas.manager.window.setWindowTitle(title)
        except: pass
        
    return fig, ax

def plt_hist(vectors_list, fig_ax = None,
             bins = 10, alpha = 0.5, normalize = False, 
             labels_list = None, **kwargs):
    
    try:
        vectors_list_shape = vectors_list.shape
        if len(vectors_list_shape == 1):
            vectors_list = [vectors_list]
    except: pass
    
    assert len(vectors_list) > 0, \
        f'lognflow.plt_hist: input should be a list or an array or an array of arrays'
    
    if fig_ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
    else:
        fig, ax = fig_ax
    
    for vec_cnt, vec in enumerate(vectors_list):
        bins_, edges = np.histogram(vec, bins)
        if normalize:
            bins_ = bins_ / bins_.max()
        ax.bar(edges[:-1], bins_, 
                width =np.diff(edges).mean(), alpha=alpha)
        if labels_list is None:
            ax.plot(edges[:-1], bins_, **kwargs)
        else:
            assert len(labels_list) == len(vectors_list)
            ax.plot(edges[:-1], bins_, 
                     label = f'{labels_list[vec_cnt]}', **kwargs)
    return fig, ax

def plt_hist_subplots(arrays, bins = 10, frame_shape=None, alpha=0.7, 
                      kwargs_bar = {} , kwargs_plot = {}):
    """
    Function to plot histograms of multiple arrays in subplots.
    
    Parameters:
    - arrays (list of np.ndarray): List of arrays to plot histograms for.
    - bins (int or sequence of scalars): Bin specification for the histograms.
    - frame_shape (tuple or None): If provided, specify the number of rows and columns for the subplots.
    - alpha (float): The transparency of the bars.
    - color (str): The color of the bars.
    - **kwargs: Additional arguments passed to the plot.
    """
    
    N = len(arrays)
    if frame_shape is None:
        cols = int(np.ceil(np.sqrt(N)))
        rows = int(np.ceil(N / cols))
    else:
        rows, cols = frame_shape
        N = min(N, rows * cols)
        
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 5))
    axes = axes.flatten()
    
    for cnt, data in enumerate(arrays):
        ax = axes[cnt]
        bins_data, edges = np.histogram(data, bins=bins)
        
        ax.bar(edges[:-1], bins_data, width=np.diff(edges).mean(), 
               alpha=alpha, **kwargs_bar)
        
        ax.plot(edges[:-1], bins_data, **kwargs_plot)
        
        ax.set_title(f"Histogram {cnt + 1}")

    # Hide unused axes if any
    for ax in axes[N:]:
        ax.set_visible(False)

    plt.tight_layout()
    

def plt_scatter3(
        data_N_by_3, fig_ax = None, title = None, 
        elev_list = [20, 70], azim_list = np.arange(0, 360, 20),
        make_animation = False, **kwargs):
    assert (len(data_N_by_3.shape)==2) & (data_N_by_3.shape[1] == 3), \
        'The first argument must be N x 3'
    if fig_ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
    else:
        fig, ax = fig_ax
    ax.scatter(data_N_by_3[:, 0], 
               data_N_by_3[:, 1], 
               data_N_by_3[:, 2], **kwargs)
    
    if title is not None:
        title = str(title)
        ax.set_title(title)
        try:
            fig.canvas.manager.window.setWindowTitle(title)
        except: pass

    try: elev_list = [int(elev_list)]
    except: pass
    try: azim_list = [int(azim_list)]
    except: pass

    if make_animation:
        stack = []
        for elev in elev_list:
            for azim in azim_list:
                ax.view_init(elev=elev, azim=azim)
                img = plt_fig_to_numpy_3ch(fig)
                stack.append(img)
        return fig, ax, stack
    else:
        elev = None if elev_list is None else elev_list[0]
        azim = None if azim_list is None else azim_list[0]
        if (elev is not None) | (azim is not None):
            ax.view_init(elev=elev, azim=azim)
        return fig, ax

def plt_surface(stack, fig_ax = None, **kwargs):
    n_r, n_c = stack.shape

    if fig_ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
    else:
        fig, ax = fig_ax

    X, Y = np.meshgrid(np.arange(n_r, dtype='int'), 
                       np.arange(n_c, dtype='int'))
    ax.plot_surface(X, Y, stack, **kwargs)
    return fig, ax

def plt_fig_to_numpy_3ch(fig):
    """Convert a matplotlib figure to a numpy 2D array (RGB)."""
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (h, w, 4)  # Shape should be (height, width, 4) for RGBA
    buf = np.copy(buf)  # Ensure we have a copy, not a view
    return buf

def plt_fig_to_numpy(fig):
    """ from https://www.icare.univ-lille.fr/how-to-
                    convert-a-matplotlib-figure-to-a-numpy-array-or-a-pil-image/
    """
    fig.canvas.draw()
    w,h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.ubyte)
    buf.shape = (w, h, 4)
    return buf.sum(2)

def numbers_as_images_3D(data3D_shape: tuple,
                         fontsize: int, 
                         text_loc: tuple = None,
                         verbose: bool = True):
    """ Numbers3D
    This function generates a 4D dataset of images with shape
    (n_x, n_r, n_c) where in each image the value "x" is written as a text
    that fills the image. As such, later when working with such a dataset you can
    look at the image and know which index it had before you use it.
    
    Follow this recipe to make good images:
    
    1- set n_x to 10, Set the desired n_r, n_c and width. 
    2- find fontsize that is the largest and still fits
    3- Increase n_x to desired size.
    
    You can provide a logs_root, log_dir or simply select a directory to save the
    output 3D array.
    
    """
    n_x, n_r, n_c = data3D_shape
    
    if text_loc is None:
        text_loc = (n_r//2 - fontsize, n_c//2 - fontsize)
    
    dataset = np.zeros(data3D_shape)    
    txt_width = int(np.log(n_x)/np.log(n_x)) + 1
    number_text_base = '{ind_x:0{width}}}'
    if(verbose):
        from lognflow import printprogress
        pBar = printprogress(n_x)
    for ind_x in range(n_x):
        mat = np.ones((n_r, n_c))
        number_text = number_text_base.format(ind_x = ind_x, 
                                              width = txt_width)
        fig = plt.figure(figsize = (n_rr, n_cc), dpi = n_rc)
        ax = fig.add_subplot(111)
        ax.imshow(mat, cmap = 'gray', vmin = 0, vmax = 1)
        ax.text(text_loc[0], text_loc[1],
                number_text, fontsize = fontsize)
        ax.axis('off')
        buf = plt_fig_to_numpy(fig)
        plt.close()
        dataset[ind_x] = buf.copy()
        if(verbose):
            pBar()
    return dataset

def numbers_as_images_4D(data4D_shape: tuple,
                         fontsize: int, 
                         text_loc: tuple = None,
                         verbose: bool = True):
    """ Numbers4D
    This function generates a 4D dataset of images with shape
    (n_x, n_y, n_r, n_c) where in each image the value "x, y" is written as a text
    that fills the image. As such, later when working with such a dataset you can
    look at the image and know which index it had before you use it.
    
    Follow this recipe to make good images:
    
    1- set n_x, n_y to 10, Set the desired n_r, n_c and width. 
    2- try fontsize that is the largest
    3- Increase n_x and n_y to desired size.
    
    You can provide a logs_root, log_dir or simply select a directory to save the
    output 4D array.
    
    :param text__loc:
        text_loc should be a tuple of the location of bottom left corner of the
        text in the image.
    
    """
    n_x, n_y, n_r, n_c = data4D_shape

    if text_loc is None:
        text_loc = (n_r//2 - fontsize, n_c//2 - fontsize)
    
    dataset = np.zeros((n_x, n_y, n_r, n_c))    
    txt_width = int(np.log(np.maximum(n_x, n_y))
                    / np.log(np.maximum(n_x, n_y))) + 1
    number_text_base = '{ind_x:0{width}}, {ind_y:0{width}}'
    if(verbose):
        from lognflow import printprogress
        pBar = printprogress(n_x * n_y)
    for ind_x in range(n_x):
        for ind_y in range(n_y):
            mat = np.ones((n_r, n_c))
            number_text = number_text_base.format(
                ind_x = ind_x, ind_y = ind_y, width = txt_width)
            n_rc = np.minimum(n_r, n_c)
            n_rr = n_r / n_rc
            n_cc = n_c / n_rc
            fig = plt.figure(figsize = (n_rr, n_cc), dpi = n_rc)
            ax = fig.add_subplot(111)
            ax.imshow(mat, cmap = 'gray', vmin = 0, vmax = 1)
            ax.text(text_loc[0], text_loc[1], number_text, fontsize = fontsize)
            ax.axis('off')
            buf = plt_fig_to_numpy(fig)
            plt.close()
            dataset[ind_x, ind_y] = buf.copy()
            if(verbose):
                pBar()
    return dataset

class plot_gaussian_gradient:
    """ Orignally developed for RobustGaussinFittingLibrary
    Plot curves by showing their average, and standard deviatoin
    by shading the area around the average according to a Gaussian that
    reduces the alpha as it gets away from the average.
    You need to init() the object then add() plots and then show() it.
    refer to the tests.py
    """
    def __init__(self, xlabel = None, ylabel = None, num_bars = 100, 
                       title = None, xmin = None, xmax = None, 
                       ymin = None, ymax = None, fontsize = 14):
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.num_bars = num_bars
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        LWidth = 1
        font = {
                'weight' : 'bold',
                'size'   : fontsize}
        plt.rc('font', **font)
        params = {'legend.fontsize': 'x-large',
                 'axes.labelsize': 'x-large',
                 'axes.titlesize':'x-large',
                 'xtick.labelsize':'x-large',
                 'ytick.labelsize':'x-large'}
        plt.rcParams.update(params)
        plt.figure(figsize=(8, 6), dpi=50)
        self.ax1 = plt.subplot(111)
    
    def addPlot(self, x, mu, std, gradient_color, label, 
                snr = 3.0, mu_color = None, general_alpha = 1,
                mu_linewidth = 1):

        for idx in range(self.num_bars-1):
            y1 = ((self.num_bars-idx)*mu + idx*(mu + snr*std))/self.num_bars
            y2 = y1 + snr*std/self.num_bars
            
            prob = np.exp(-(snr*idx/self.num_bars)**2/2)
            plt.fill_between(
                x, y1, y2, 
                color = (gradient_color + (prob*general_alpha,)), 
                edgecolor=(gradient_color + (0,)))

            y1 = ((self.num_bars-idx)*mu + idx*(mu - snr*std))/self.num_bars
            y2 = y1 - snr*std/self.num_bars
            
            plt.fill_between(
                x, y1, y2, 
                color = (gradient_color + (prob*general_alpha,)), 
                edgecolor=(gradient_color + (0,)))
        if(mu_color is None):
            mu_color = gradient_color
        plt.plot(x, mu, linewidth = mu_linewidth, color = mu_color, 
                 label = label)
        
    def show(self, show_legend = True):
        if(self.xmin is not None) & (self.xmax is not None):
            plt.xlim([self.xmin, self.xmax])
        if(self.ymin is not None) & (self.ymax is not None):
            plt.ylim([self.ymin, self.ymax])
        if(self.xlabel is not None):
            plt.xlabel(self.xlabel, weight='bold')
        if(self.ylabel is not None):
            plt.ylabel(self.ylabel, weight='bold')
        if(self.title is not None):
            plt.title(self.title)
        if(show_legend):
            plt.legend()
        plt.grid()
        
        plt.show()
        
    def __call__(self, *args, **kwargs):
        self.addPlot(*args, **kwargs)

def plt_imshow_series(list_of_stacks, 
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
                      **kwargs,
                      ):
    
    """
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
    
    Returns:
        tuple:
            - fig (matplotlib.figure.Figure): The created figure.
            - None: Placeholder for potential additional return values.
            
    Raises:
        AssertionError: 
            If the input lists do not meet the expected shapes or lengths.
    """
    
    if colorbar:
        colorbar_last_only = False
        
    n_stacks = len(list_of_stacks)
    if(list_of_masks is not None):
        assert len(list_of_masks) == n_stacks, \
            f'the number of masks, {len(list_of_masks)} and ' \
            + f'stacks {n_stacks} should be the same'
     
    n_imgs = len(list_of_stacks[0])
    for ind, stack in enumerate(list_of_stacks):
        assert len(stack) == n_imgs, \
            'All members of the given list should have same number of images.' \
            f' while the stack indexed as {ind} has length {len(stack)}.'
        assert (len(stack.shape) == 3) | (len(stack.shape) == 4), \
            f'The shape of the stack {ind} must have length 3 or 4, it has '\
            f'shape of {stack.shape}. Perhaps you wanted to have only '\
             'one set of images. If thats the case, put that single '\
             'image in a list.'

    if (list_of_titles_columns is not None):
        assert len(list_of_titles_columns) == n_imgs, \
            f'len(list_of_titles_columns): {len(list_of_titles_columns)}, ' \
            + f'should be len(list_of_stacks[0]): {n_imgs}'

    if (list_of_titles_rows is not None):
        assert len(list_of_titles_rows) == n_stacks, \
            f'len(list_of_titles_rows): {len(list_of_titles_rows)}, ' \
            + f'should be len(list_of_stacks): {n_stacks}'
            
    if figsize is None:
        if(colorbar):
            figsize = (n_imgs* 2, n_stacks)
        else:
            figsize = (n_imgs, n_stacks)

    if fontsize is None:
        fontsize = int(max(figsize)/10)
        if fontsize > 8: fontsize = 8
    
    fig = plt.figure(figsize = figsize)
    if colorbar_last_only:
        gs1 = matplotlib.gridspec.GridSpec(n_stacks, n_imgs + 1)
    else:
        gs1 = matplotlib.gridspec.GridSpec(n_stacks, n_imgs)
    if grid_width_space:
        gs1.update(wspace=grid_width_space, hspace=0)
    
    for stack_cnt in range(n_stacks):
        
        if(list_of_masks is not None): mask = list_of_masks[stack_cnt]
        else: mask = None

        for img_cnt in range(n_imgs):
            ax = plt.subplot(gs1[stack_cnt, img_cnt])
            
            data_canvas = list_of_stacks[stack_cnt][img_cnt]
            try: data_canvas = data_canvas.detach().cpu().numpy()
            except: data_canvas = data_canvas.copy()

            if(mask is not None):
                if(data_canvas.shape == mask.shape):
                    data_canvas[mask==0] = 0
                    data_canvas_stat = data_canvas[mask>0].copy()
            else:
                data_canvas_stat = data_canvas.copy()
            data_canvas_stat = data_canvas_stat[
                (np.isnan(data_canvas_stat) + np.isinf(data_canvas_stat) == 0)]
            
            if vmin is None: vmin_ = data_canvas_stat.min()
            else: vmin_ = copy.copy(vmin)
            if vmax is None: vmax_ = data_canvas_stat.max()
            else: vmax_ = copy.copy(vmax)

            im = ax.imshow(data_canvas, 
                           cmap = cmap, vmin = vmin_, vmax = vmax_, **kwargs)
            if(remove_axis_ticks):
                plt.setp(ax, xticks=[], yticks=[])
            
            if aspect is not None:
                ax.set_aspect(aspect)
            
            if colorbar | colorbar_last_only:
                if colorbar_last_only:
                    colorbar_invisible = img_cnt != n_imgs - 1
                else:
                    colorbar_invisible = 0
                plt_colorbar(im, colorbar_invisible = colorbar_invisible)
                                            
            if(text_as_colorbar):
                ax.text(data_canvas.shape[0]*0,
                         data_canvas.shape[1]*0.05,
                         f'{data_canvas.max():.6f}', 
                         color = 'yellow',
                         fontsize = fontsize)
                ax.text(data_canvas.shape[0]*0,
                         data_canvas.shape[1]*0.5, 
                         f'{data_canvas.mean():.6f}', 
                         color = 'yellow',
                         fontsize = fontsize)
                ax.text(data_canvas.shape[0]*0,
                         data_canvas.shape[1]*0.95, 
                         f'{data_canvas.min():.6f}', 
                         color = 'yellow',
                         fontsize = fontsize)
            
            if (list_of_titles_rows is not None):
                if img_cnt == 0:
                    ax.set_ylabel(list_of_titles_rows[stack_cnt], fontsize = fontsize)
            if (list_of_titles_columns is not None):
                if stack_cnt == 0:
                    ax.set_title(list_of_titles_columns[img_cnt], fontsize = fontsize)
            
    if title is not None:
        title = str(title)
        fig.suptitle(title)
        try:
            fig.canvas.manager.window.setWindowTitle(title)
        except: pass
    return fig, None

def plt_imshow_subplots(
        images, grid_locations=None, frame_shape = None, title = None,
        titles=[], cmaps=[], colorbar=True, margin = 0.025,
        inter_image_margin = 0.01,
        colorbar_aspect=2, colorbar_pad_fraction=0.05, title_ax_gap = 0.05,
        figsize=None, remove_axis_ticks=True, **kwargs):
    """
    Plots a list of 2D images at specified 2D grid_locations with titles 
    and colormaps.
    
    Parameters:
    images (list of 2D arrays): List of 2D images to plot.
    grid_locations (list of tuples or None): List of subplot grid_locations 
        in (rows, cols, index) format or None to generate a grid.
    titles (list of str): List of titles for each image.
    cmaps (list of str): List of colormaps for each image.
    colorbar (bool): Whether to add a colorbar beside each image. 
        Default is True.
    colorbar_aspect (int): Aspect ratio for the colorbars. Default is 2.
    colorbar_pad_fraction (float): Padding fraction for the colorbars. 
        Default is 0.05.
    figsize (tuple): Size of the figure.
    remove_axis_ticks (bool): Whether to remove axis ticks. Default is True.
    """
    if colorbar:
        margin = np.maximum(margin, 0.4)
        inter_image_margin = np.maximum(margin, 0.4)
    
    N = len(images)
    # Determine the maximum image size
    max_width = max(img.shape[1] for img in images)
    max_height = max(img.shape[0] for img in images)
    
    if grid_locations is None:
        if frame_shape is None:
            cols = int(np.ceil(np.sqrt(N)))
            rows = int(np.ceil(N / cols))
        else:
            rows, cols = frame_shape
            N = np.minimum(N, rows * cols)
        
        # Generate grid locations with dynamic spacing
        spacing = max(max_width, max_height) * (1 + inter_image_margin)
        grid_locations = np.array([[col * spacing, 1 - row * spacing] for row in range(rows) for col in range(cols)])
        grid_locations = grid_locations[:N]  # Trim to number of images
            
    lefts = grid_locations[:, 0]
    bottoms = grid_locations[:, 1]
    rights = lefts + np.array([img.shape[1] for img in images])
    tops = bottoms + np.array([img.shape[0] for img in images])
    min_left = lefts.min() - margin * max_width
    min_bottom = bottoms.min() - margin * max_height
    max_right = rights.max() + margin * max_width
    max_top = tops.max() + margin * max_height
    lefts = (lefts - min_left) / (max_right - min_left)
    bottoms = (bottoms - min_bottom) / (max_top - min_bottom)
    rights = (rights - min_left) / (max_right - min_left)
    tops = (tops - min_bottom) / (max_top - min_bottom)

    fig = plt.figure(figsize = figsize)
    axes = []
    if cmaps:
        assert len(cmaps) == N, \
            'The length of cmaps should be equal to the number of images.'
    for cnt in range(N):
        gs = matplotlib.gridspec.GridSpec(1, 1, left=lefts[cnt], right=rights[cnt], 
                                          top=tops[cnt], bottom=bottoms[cnt])
        ax = fig.add_subplot(gs[0])
        axes.append(ax)
        image = images[cnt]
        
        try:
            image = image.detach().cpu().numpy()
        except: pass
        
        if image is not None:
            if np.iscomplexobj(image):
                complex_image, data_abs, data_angle = complex2hsv(image)
                try: min_angle = data_angle[data_abs > 0].min()
                except: min_angle = 0
                try: max_angle = data_angle[data_abs > 0].max()
                except: max_angle = 0
                cax = ax.imshow(complex_image)
                
                if(colorbar):
                    vmin = kwargs.get('vmin', np.abs(image).min())
                    vmax = kwargs.get('vmax', np.abs(image).max())
                    
                    fig, ax_inset = complex2hsv_colorbar(
                        (fig, ax.inset_axes([0.79, 0.03, 0.18, 0.18], 
                                            transform=ax.transAxes)),
                        vmin=vmin, vmax=vmax, min_angle=min_angle, max_angle=max_angle)
                    ax_inset.patch.set_alpha(0)
                
            else:
                if cmaps:
                    assert not ('cmap' in kwargs), \
                        'cmap should not be in kwargs if you want to provide cmaps list'
                    cax = ax.imshow(image, cmap=cmaps[cnt], **kwargs)
                else:
                    cax = ax.imshow(image, **kwargs)
                if colorbar:
                    plt_colorbar(cax, colorbar_aspect=colorbar_aspect,
                                 colorbar_pad_fraction=colorbar_pad_fraction)
            
            try: ax.set_title(titles[cnt])
            except: pass
            
            if remove_axis_ticks:
                ax.axis('off')    
            
    if title is not None:
        title = str(title)
        fig.suptitle(title, y=tops.max() + title_ax_gap)
        try:
            fig.canvas.manager.window.setWindowTitle(title)
        except: pass
    
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.margins(margin)
    return fig, axes

def subplots_grid(plots_shape,
    grid_locations=None, frame_shape = None, title = None,
    titles=[], margin = 0.025, inter_image_margin = 0.01,
    figsize=None, remove_axis_ticks=True, **kwargs):
    
    """
        Create a grid of subplots within a single figure with customizable spacing and layout.
    
        Parameters:
        -----------
        plots_shape : tuple
            A tuple (N, max_width, max_height) where:
            - N is the number of subplots.
            - max_width and max_height define the size of each subplot.
        grid_locations : array-like, optional
            An array specifying the locations of subplots. If None, 
            locations are computed automatically.
        frame_shape : tuple, optional
            A tuple (rows, cols) specifying the layout of subplots in 
            terms of rows and columns.
            If None, a square-like layout is estimated.
        title : str, optional
            The title of the figure.
        titles : list, optional
            A list of titles for each subplot.
        margin : float, default=0.025
            The margin around the figure.
        inter_image_margin : float, default=0.01
            The spacing between subplots.
        figsize : tuple, optional
            The overall figure size in inches.
        remove_axis_ticks : bool, default=True
            Whether to remove axis ticks from subplots.
        **kwargs : dict
            Additional keyword arguments passed to `matplotlib` functions.
    
        Returns:
        --------
        fig : matplotlib.figure.Figure
            The created figure.
        axes : list of matplotlib.axes.Axes
            A list containing the subplot axes.
    """
        
    N, max_width, max_height = plots_shape
    
    if grid_locations is None:
        if frame_shape is None:
            cols = int(np.ceil(np.sqrt(N)))
            rows = int(np.ceil(N / cols))
        else:
            rows, cols = frame_shape
            N = np.minimum(N, rows * cols)
        
        spacing = max(max_width, max_height) * (1 + inter_image_margin)
        grid_locations = np.array([
            [col * spacing, 1 - row * spacing] for row in range(rows) for col in range(cols)])
        grid_locations = grid_locations[:N]
            
    lefts = grid_locations[:, 0]
    bottoms = grid_locations[:, 1]
    rights = lefts + np.array([max_width] * N)
    tops = bottoms + np.array([max_height] * N)
    min_left = lefts.min() - margin * max_width
    min_bottom = bottoms.min() - margin * max_height
    max_right = rights.max() + margin * max_width
    max_top = tops.max() + margin * max_height
    lefts = (lefts - min_left) / (max_right - min_left)
    bottoms = (bottoms - min_bottom) / (max_top - min_bottom)
    rights = (rights - min_left) / (max_right - min_left)
    tops = (tops - min_bottom) / (max_top - min_bottom)

    fig = plt.figure(figsize = figsize)
    axes = []
    for cnt in range(N):
        gs = matplotlib.gridspec.GridSpec(1, 1, left=lefts[cnt], right=rights[cnt], 
                                          top=tops[cnt], bottom=bottoms[cnt])
        ax = fig.add_subplot(gs[0])
        axes.append(ax)
        try: ax.set_title(titles[cnt])
        except: pass
        if remove_axis_ticks:
            ax.axis('off')    
            
    if title is not None:
        title = str(title)
        fig.suptitle(title)
        try:
            fig.canvas.manager.window.setWindowTitle(title)
        except: pass
    
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.margins(margin)
    return fig, axes

class transform3D_viewer:
    """
    A 3D viewer for point cloud transformations using matplotlib.

    Attributes:
        in_pointcloud (numpy.ndarray): The input point cloud.
        pt_cls (numpy.ndarray): there must be a class for each point.
            class 0 is movable others will only have different colors
    """
    def __init__(self, in_pointcloud, pt_cls = None):
        error_msg = 'input point cloud must be Nx3, where N >= 3'
        assert len(in_pointcloud.shape) == 2, error_msg
        assert in_pointcloud.shape[0] >= 3, error_msg
        assert in_pointcloud.shape[1] == 3, error_msg
        self.PC = in_pointcloud
    
        if pt_cls is None:
            pt_cls = np.zeros(len(in_pointcloud), dtype='int')
        self.pt_cls = pt_cls
        self.moving_inds = np.where(self.pt_cls == 0)[0]
        assert len(self.moving_inds) > 3, \
            'at least 3 data points must have class 0'
        self.params = {}
        self.figure()
        self.textboxevalues = np.array([
            float(self.params["Tx_text_box"].text),
            float(self.params["Ty_text_box"].text),
            float(self.params["Tz_text_box"].text),
            float(self.params["Sx_text_box"].text),
            float(self.params["Sy_text_box"].text),
            float(self.params["Sz_text_box"].text),
            float(self.params["Rx_text_box"].text),
            float(self.params["Ry_text_box"].text),
            float(self.params["Rz_text_box"].text)])

    def figure(self):
        from functools import partial

        self.Theta_init, self.Vt_init = self.get_Theta(self.PC[self.moving_inds])
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(left=0.05, right=0.5, bottom=0.1, top=0.9)
        
        # Create step size text boxes
        self.create_text_box("T_step", 0.75, 0.88, 1.0, self.update_steps)
        # Create transformation widgets
        self.create_text_box("Tx", 0.75, 0.81, self.Theta_init["Tx"], self.update_from_text)
        self.create_text_box("Ty", 0.75, 0.74, self.Theta_init["Ty"], self.update_from_text)
        self.create_text_box("Tz", 0.75, 0.67, self.Theta_init["Tz"], self.update_from_text)

        self.create_buttons("Tx", 0.70, 0.81, partial(self.update_value, "Tx", "T_step", -1), partial(self.update_value, "Tx", "T_step", 1))
        self.create_buttons("Ty", 0.70, 0.74, partial(self.update_value, "Ty", "T_step", -1), partial(self.update_value, "Ty", "T_step", 1))
        self.create_buttons("Tz", 0.70, 0.67, partial(self.update_value, "Tz", "T_step", -1), partial(self.update_value, "Tz", "T_step", 1))
        
        self.create_text_box("S_step", 0.75, 0.59, 0.1, self.update_steps)
        self.create_text_box("Sx", 0.75, 0.52, self.Theta_init["Sx"], self.update_from_text)
        self.create_text_box("Sy", 0.75, 0.45, self.Theta_init["Sy"], self.update_from_text)
        self.create_text_box("Sz", 0.75, 0.38, self.Theta_init["Sz"], self.update_from_text)
        
        self.create_buttons("Sx", 0.70, 0.52, partial(self.update_value, "Sx", "S_step", -1), partial(self.update_value, "Sx", "S_step", 1))
        self.create_buttons("Sy", 0.70, 0.45, partial(self.update_value, "Sy", "S_step", -1), partial(self.update_value, "Sy", "S_step", 1))
        self.create_buttons("Sz", 0.70, 0.38, partial(self.update_value, "Sz", "S_step", -1), partial(self.update_value, "Sz", "S_step", 1))
        
        self.create_text_box("R_step", 0.75, 0.3, 5.0, self.update_steps)
        self.create_text_box("Rx", 0.75, 0.23, self.Theta_init["Rx"], self.update_from_text)
        self.create_text_box("Ry", 0.75, 0.18, self.Theta_init["Ry"], self.update_from_text)
        self.create_text_box("Rz", 0.75, 0.13, self.Theta_init["Rz"], self.update_from_text)
        
        self.create_buttons("Rx", 0.70, 0.23, partial(self.update_value, "Rx", "R_step", -1), partial(self.update_value, "Rx", "R_step", 1))
        self.create_buttons("Ry", 0.70, 0.18, partial(self.update_value, "Ry", "R_step", -1), partial(self.update_value, "Ry", "R_step", 1))
        self.create_buttons("Rz", 0.70, 0.13, partial(self.update_value, "Rz", "R_step", -1), partial(self.update_value, "Rz", "R_step", 1))

        self.draw()
        
    def draw(self):
        # Display the point cloud
        self.ax.cla()
        for cls_cnt in np.unique(self.pt_cls):
            self.ax.scatter(self.PC[self.pt_cls == cls_cnt, 0],
                            self.PC[self.pt_cls == cls_cnt, 1],
                            self.PC[self.pt_cls == cls_cnt, 2], 
                            label=f'cls_{cls_cnt}')
        cls_values = np.unique(self.pt_cls)
        if len(cls_values) > 1:
            for cls_cnt in cls_values[:-1] :
                self.ax.plot([self.PC[self.pt_cls == cls_cnt, 0][-1], self.PC[self.pt_cls == cls_cnt + 1, 0][0]],
                             [self.PC[self.pt_cls == cls_cnt, 1][-1], self.PC[self.pt_cls == cls_cnt + 1, 1][0]],
                             [self.PC[self.pt_cls == cls_cnt, 2][-1], self.PC[self.pt_cls == cls_cnt + 1, 2][0]], 
                             color = 'black', linewidth = 2)
    
        # Calculate the bounding box for the moving_inds using SVD
        points = self.PC[self.moving_inds]
        mean = points.mean(axis=0)
        centered_points = points - mean
        U, S, Vt = np.linalg.svd(centered_points)
    
        # Project points onto principal axes
        projections = centered_points @ Vt.T
    
        # Get the min and max along each principal axis
        min_proj = projections.min(axis=0)
        max_proj = projections.max(axis=0)
    
        # Define the bounding box corners in the projected space
        bbox_proj = np.array([[min_proj[0], min_proj[1], min_proj[2]],
                              [max_proj[0], min_proj[1], min_proj[2]],
                              [max_proj[0], max_proj[1], min_proj[2]],
                              [min_proj[0], max_proj[1], min_proj[2]],
                              [min_proj[0], min_proj[1], max_proj[2]],
                              [max_proj[0], min_proj[1], max_proj[2]],
                              [max_proj[0], max_proj[1], max_proj[2]],
                              [min_proj[0], max_proj[1], max_proj[2]]])
    
        # Rotate bounding box corners back to the original coordinate system
        bbox = bbox_proj @ Vt + mean
    
        # Draw bounding box lines
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), # Bottom square
                 (4, 5), (5, 6), (6, 7), (7, 4), # Top square
                 (0, 4), (1, 5), (2, 6), (3, 7)] # Vertical lines
    
        for edge in edges:
            self.ax.plot3D(*zip(bbox[edge[0]], bbox[edge[1]]), '--', color='blue')
    
        self.fig.canvas.draw()

    def get_Theta(self, PC):
        from   scipy.spatial.transform import Rotation as scipy_rotation
        Theta = {}
        mean_vec = PC.mean(0)
        Theta["Tx"], Theta["Ty"], Theta["Tz"] = mean_vec
        PC_moving_centered = PC - mean_vec
        U, S_vec, Vt = np.linalg.svd(PC_moving_centered.T)
        Theta["Sx"], Theta["Sy"], Theta["Sz"] = S_vec
        r = scipy_rotation.from_matrix(U)
        Theta["Rx"], Theta["Ry"], Theta["Rz"] = r.as_euler('xyz', degrees=True)
        return Theta, Vt[:3]
    
    def apply(self, PC):
        from   scipy.spatial.transform import Rotation as scipy_rotation
        Theta_in, Vt_in = self.get_Theta(PC)
        Theta, _ = self.get_Theta(self.PC[self.moving_inds])
        
        translation = np.array(
            [Theta_in['Tx'] + Theta["Tx"] - self.Theta_init['Tx'],
             Theta_in['Ty'] + Theta["Ty"] - self.Theta_init['Ty'],
             Theta_in['Tz'] + Theta["Tz"] - self.Theta_init['Tz']])
        new_S = np.diag(
            [Theta_in["Sx"] * Theta["Sx"] / self.Theta_init["Sx"],
             Theta_in["Sy"] * Theta["Sy"] / self.Theta_init["Sy"],
             Theta_in["Sz"] * Theta["Sz"] / self.Theta_init["Sz"]])
        r = scipy_rotation.from_euler('xyz',
            np.array([Theta_in["Rx"] + Theta["Rx"] - self.Theta_init["Rx"],
                      Theta_in["Ry"] + Theta["Ry"] - self.Theta_init["Ry"],
                      Theta_in["Rz"] + Theta["Rz"] - self.Theta_init["Rz"]]),
            degrees=True)
        new_U = r.as_matrix()
        PC_transformed = (new_U @ new_S @ Vt_in).T + translation
        return PC_transformed
        
    def create_text_box(self, label, x, y, initial_val, on_submit):
        text_ax = self.fig.add_axes([x, y, 0.13, 0.05])
        text_box = TextBox(text_ax, label + '         ', 
                           initial=f'{initial_val:.6f}')
        text_box.on_submit(on_submit)
        self.params[f"{label}_text_box"] = text_box
    
    def create_buttons(self, label, x, y, on_click_minus, on_click_plus):
        minus_ax = self.fig.add_axes([x, y, 0.04, 0.05])
        plus_ax = self.fig.add_axes([x + 0.19, y, 0.04, 0.05])
        minus_button = Button(minus_ax, '-')
        plus_button = Button(plus_ax, '+')
        minus_button.on_clicked(on_click_minus)
        plus_button.on_clicked(on_click_plus)
        self.params[f"{label}_minus_button"] = minus_button
        self.params[f"{label}_plus_button"] = plus_button
    
    def update_steps(self, text):
        try:
            self.params["T_step"] = float(self.params["T_step_text_box"].text)
            self.params["S_step"] = float(self.params["S_step_text_box"].text)
            self.params["R_step"] = float(self.params["R_step_text_box"].text)
        except ValueError:
            pass

    def update_from_text(self, text):
        from   scipy.spatial.transform import Rotation as scipy_rotation
        try: # Read new transformation values
            self.textboxevalues = np.array([
                float(self.params["Tx_text_box"].text),
                float(self.params["Ty_text_box"].text),
                float(self.params["Tz_text_box"].text),
                float(self.params["Sx_text_box"].text),
                float(self.params["Sy_text_box"].text),
                float(self.params["Sz_text_box"].text),
                float(self.params["Rx_text_box"].text),
                float(self.params["Ry_text_box"].text),
                float(self.params["Rz_text_box"].text)])
        except ValueError:
            pass
            
        translation = self.textboxevalues[:3].copy()
        new_S = np.diag(self.textboxevalues[3:6].copy())
        r = scipy_rotation.from_euler(
            'xyz',self.textboxevalues[6:].copy(), degrees=True)
        new_U = r.as_matrix()
        PC_transformed = (new_U @ new_S @ self.Vt_init).T + translation
        # Update the movable part of the point cloud
        self.PC[self.moving_inds] = PC_transformed
        
        self.draw()

    def update_value(self, label, step_label, direction, event):
        current_val = float(self.params[f"{label}_text_box"].text)
        step_size = float(self.params[f"{step_label}_text_box"].text)
        new_val = current_val + direction * step_size
        self.params[f"{label}_text_box"].set_val(f"{new_val:.6f}")

class _questdiag:
    def __init__(self, question, buttons, figsize, question_hratio):
        
        assert isinstance(buttons, dict), \
            ('buttons arg must be a dictionary of texts appearing on '
             'the buttons values to be returned.')
        
        self.buttons = buttons
        self.result = None

        # Calculate the number of rows and columns for the buttons
        N = len(self.buttons)
        n_rows = int(np.ceil(N ** 0.5))  # Number of rows for buttons
        n_cols = int(np.ceil(N / n_rows))  # Number of columns for buttons
        
        if N == 1: n_rows, n_cols = 1, 1
        if N == 2: n_rows, n_cols = 1, 2
        if N == 3: n_rows, n_cols = 1, 3
        if N == 6: n_rows, n_cols = 2, 3
        
        if question_hratio is None:
            if isinstance(question, np.ndarray):
                question_hratio = 10
            else:
                question_hratio = 1
        
        if figsize is None:
            if isinstance(question, np.ndarray):
                figsize = (7.5, 7.5)
            else:
                figsize = (5, 2.5)
            
        # Create the figure and GridSpec layout
        fig = plt.figure(figsize=figsize)
        gs = matplotlib.gridspec.GridSpec(n_rows + 2, n_cols, 
                      figure=fig, 
                      height_ratios=[question_hratio] + [1] * (n_rows + 1))  
        # First row (3x height) for the question, remaining rows for buttons
        
        # Top section for the question (span the entire width)
        ax_question = fig.add_subplot(gs[0, :])
        
        # Handle different types of questions
        if isinstance(question, np.ndarray):
            if len(question.shape) == 1:
                ax_question.plot(question)
            elif len(question.shape) == 2:
                plt_imshow(question, fig_ax=(fig, ax_question))
            plt.axis('on')  # Keep axis on for plots and images
        else:
            ax_question.text(0.5, 0.5, str(question), 
                             ha='center', va='center', fontsize=12)
            ax_question.set_axis_off()  # No axis for text questions

        # Create buttons and place them on the grid
        button_objects = []
        for i, (label, val) in enumerate(self.buttons.items()):
            row = 2 + i // n_cols
            col = i % n_cols
            button_ax = fig.add_subplot(gs[row, col])
            button = Button(button_ax, label)
            button.on_clicked(self.button_click)
            button_objects.append(button)
    
        plt.show()
    
    def button_click(self, event):
        ind = event.inaxes.texts[0].get_text()  # Get text of the clicked button
        self.result = self.buttons[ind]  # Return the corresponding output
        plt.close()  # Close the plot after a button is clicked

def question_dialog(
    question = 'Yes/No/Cancel?',
    buttons={'Yes': True, 'No': False, 'Cancel': None},
    figsize = None, 
    question_hratio = None):
    """ Question dialog
    Creates a dialog with a question displayed at the top and a grid of buttons below it.
    
    The function supports displaying questions as text, 1D numpy arrays (as line plots),
    or 2D numpy arrays (as images). It displays buttons beneath the question, allowing the
    user to select one of the provided options. The buttons are organized into a grid
    layout based on the number of buttons provided. When a button is clicked, the function 
    returns the corresponding value associated with the button in the `buttons` dictionary.

    Parameters
    ----------
    question : str, np.ndarray, optional
        The question to be presented. It can be a string, a 1D numpy array (plotted as a 
        line), or a 2D numpy array (displayed as an image). Default is 'Yes/No/Cancel?'.
    
    buttons : dict, optional
        A dictionary where the keys are the text labels that will appear on the buttons, 
        and the values are the corresponding values to return when the button is clicked.
        Default is {'Yes': True, 'No': False, 'Cancel': None}.
        
    figsize : tuple, optional
        A tuple specifying the size of the figure (width, height) in inches. Default is (6, 2).

    question_hratio: int, optional
        If you are sending an image as a question, you can set the height ratio to
        buttons here, we suggest 4
    Returns
    -------
    result : any
        The value associated with the button clicked by the user. If 'Yes' is clicked, 
        returns `True`; if 'No', returns `False`; and if 'Cancel', returns `None`.
    """
    return _questdiag(question, buttons, figsize, question_hratio).result

def plt_mark(
        coords, fig_ax=None, figsize=(2, 2),
        marker=None, markersize = None, return_markersize = False):
    """
    Plots a grid of dots with a dynamic figure size to avoid overlap.
    
    Parameters:
    - coords: numpy array of shape (N, 2), where each row is [x, y] coordinates
    - fig_ax: 2-tuple of (fig, ax) or None; if None, a new figure and axis are created
    - figsize: tuple of two floats, figure size in inches (width, height)
    - marker: str, marker style (e.g., 'x', 'o', '.', etc.); if None, use the next marker in the cycle
    - marker_sizer: float, the marker size
    
    Returns:
    - 2-tuple of (fig, ax), and the markersize used for plotting
    """
    if fig_ax is None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
        if figsize is None:
            figsize = fig.get_size_inches()
    else:
        fig, ax = fig_ax
    
    if markersize is None:
        markersize = 12 * min(figsize[0], figsize[1])/ len(coords)
        markersize = np.maximum(markersize, 1)

    if marker is None:
        marker = next(matplotlib_lines_Line2D_markers_keys_cycle)
    
    ax.plot(coords[:, 0], coords[:, 1], 
            marker=marker, markersize=markersize, linestyle='')

    if return_markersize:
        return fig, ax, markersize
    else:
        return fig, ax

def plt_graph_like(adj_mat, labels, figsize = (10, 8), gridspecs = (10, 10),
                   grid_rows_divide_at = 4, grid_clms_divide_at = 9):
    assert adj_mat.shape[0] == adj_mat.shape[1], \
        'This function is for a complete graph adjacency matrix'
    pt_inds = np.arange(len(adj_mat))
    new_inds = []
    for lblcnt, lbl in enumerate(np.unique(labels)):
        points_selected = pt_inds[labels == lbl].copy()
        adj_mat_selected = adj_mat[labels == lbl][:, labels == lbl].copy()
        nodes_mean = adj_mat_selected.mean(0)
        nodes_std = adj_mat_selected.std(0)
        nodes_scores = nodes_mean.copy()
        nodes_scores[nodes_std > 0] /= nodes_std[nodes_std > 0]
        nodes_scores[nodes_std == 0] = 0
        sort_inds_selected = np.argsort(nodes_scores)
        points_selected_sorted = points_selected[sort_inds_selected]
        new_inds.append(points_selected_sorted)
    new_inds = np.concatenate(new_inds, axis = 0)

    adj_mat = adj_mat[new_inds][:, new_inds].copy()
    label = labels[new_inds].copy()

    _, for_plotting_colorbars = np.unique(label, return_counts=True)
    print(for_plotting_colorbars)
    n_classes = len(for_plotting_colorbars)
    # Parameters
    rows, cols = adj_mat.shape
    bar_shift = rows // 20  # Width of the color bars
    value_color = 1  # Starting value for color bars
    start_color = 0
    end_color = 0

    additional_matrix = np.ones((adj_mat.shape[0], bar_shift))

    for i in range(n_classes):
        end_color += for_plotting_colorbars[i]
        additional_matrix[start_color:end_color, :] = value_color
        value_color += 1
        start_color += for_plotting_colorbars[i]

    # Transpose the additional matrix for the top bar
    transposed_matrix = additional_matrix.T

    # Extend the original matrix with the side color bar
    extended_matrix = np.hstack((adj_mat, additional_matrix))

    # Pad the transposed matrix to match the width of the extended matrix
    padding_width = extended_matrix.shape[1] - transposed_matrix.shape[1]
    padding = np.zeros((transposed_matrix.shape[0], padding_width))
    padded_transposed = np.hstack((transposed_matrix, padding))

    # Stack the padded transposed matrix (top bar) and the extended matrix
    final_matrix = np.vstack((padded_transposed, extended_matrix))

    # Create a mask for the color bars
    mask = np.zeros_like(final_matrix, dtype=bool)
    mask[:bar_shift, :] = True  # Top bar
    mask[:, -bar_shift:] = True  # Side bar

    # Create a masked matrix for the overlay
    overlay_matrix = np.ma.masked_where(~mask, final_matrix)

    # Define a custom colormap for the color bars
    colors = matplotlib_colors_list[:n_classes]
    cmap_custom = ListedColormap(colors)

    # Modify the overlay_matrix to include the corner region
    corner_mask = np.zeros_like(final_matrix, dtype=bool)
    corner_mask[:bar_shift, -bar_shift:] = True  # Corner region

    # Assign a special value (e.g., -1) to the corner region in the overlay_matrix
    overlay_matrix[corner_mask] = -1

    # Extend the custom colormap to include white for the corner region
    colors_with_white = ['white'] + colors  # Add white as the first color
    cmap_custom_with_white = ListedColormap(colors_with_white)

    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(*gridspecs, figure=fig)
    # Left plot (span the full height of the left column)
    ax1 = fig.add_subplot(gs[:, :grid_clms_divide_at])
    # Top-right plot (top-right corner)
    ax2 = fig.add_subplot(gs[:grid_rows_divide_at, grid_clms_divide_at:])
    # Bottom-right plot (bottom-right corner)
    ax3 = fig.add_subplot(gs[grid_rows_divide_at:, grid_clms_divide_at])

    # Display the image
    cax = ax1.imshow(final_matrix, aspect='auto', cmap='GnBu', vmin=0, vmax=1)
    ax1.imshow(overlay_matrix, aspect='auto', cmap=cmap_custom_with_white, vmin=-1, vmax=value_color)
    ax1.set_xticks(np.cumsum(for_plotting_colorbars))  # Adjust step size as needed
    ax1.set_yticks(bar_shift + np.cumsum(for_plotting_colorbars))  # Adjust step size as needed
    ax1.set_aspect('equal')

    legend_labels = [f'Cluster {ii}' for ii in range(n_classes)]  # Replace with your actual labels
    legend_colors = colors[:n_classes]  # Use the first 3 colors for the legend
    legend_handles = [Patch(color=color, label=label) for color, label in zip(legend_colors, legend_labels)]

    ax2.axis('off')  # Turn off the axis for legend plot
    ax2.legend(loc='upper center', handles=legend_handles)

    # Add colorbar in ax3
    ax3.set_position([ax3.get_position().x0, ax3.get_position().y0, 0.03, ax3.get_position().height])
    fig.colorbar(cax, cax=ax3, use_gridspec=True)

    # plt.tight_layout()

    return fig, [ax1, ax2, ax3]

def plt_contours(
        Z_list, X_Y = None, fig_ax = None, levels = 10, colors_list = None, 
        linestyles_list = None, linewidth = 0.5, fontsize = 3, title = None,
        figsize = None):
    """
    Plot contours of multiple surfaces overlaid on the same plot.
    
    Parameters:
    - Z_list: List of 2D arrays representing the surface heights at each 
              grid point.
    - X_Y: tuple where the (X, Y) describe the meshgrid over which Z is defined
    - fig_ax: Tuple (fig, ax) where fig is the figure and ax is the axes.
              If None, creates a new figure and axes.
    - levels: Number of contour levels for all surfaces.
    - colors_list: List of colors for the contours of each surface. 
                   If None, defaults to a colormap.
    - linestyles_list: List of line styles for the contours of each surface. 
                       If None, defaults to a pattern.
    - title: Optional title for the plot.
    """
    
    # Create figure and axes if not provided
    if fig_ax is None:
        fig, ax = plt.subplots(figsize = figsize)
    else:
        fig, ax = fig_ax
    
    # Default colors and linestyles if not provided
    if colors_list is None:
        colors_list = plt.cm.jet(np.linspace(0, 1, len(Z_list)))
    if linestyles_list is None:
        linestyles_list = ['dashed', 'solid'] * (len(Z_list) // 2 + 1)
    
    # Plot contours for each surface in Z_list
    try:
        Z_list_shape = Z_list.shape
        if len(Z_list_shape) == 2:
            Z_list = [Z_list]
    except: pass
    
    for i, Z in enumerate(Z_list):
        if X_Y is None:
            Y, X = np.meshgrid(np.arange(Z.shape[1]), np.arange(Z.shape[0]))
        else:
            X, Y = X_Y
        color = colors_list[i % len(colors_list)]
        linestyle = linestyles_list[i % len(linestyles_list)]
        contour = ax.contour(X, Y, Z, levels=levels, colors=[color],
                             linestyles=linestyle, linewidths = linewidth)
        
        # Add labels to contours
        if fontsize is not None:
            ax.clabel(contour, inline=True, fontsize=fontsize, fmt='%.2f')
        
    ax.set_aspect('equal')

    if title is not None:
        title = str(title)
        ax.set_title(title)
        try:
            fig.canvas.manager.window.setWindowTitle(title)
        except: pass
    
    return fig, ax

def pv_volume(volume, volume_xyz = None, 
                   grid_size=None, grid_opacity=0.5, show_grid=True, 
                   title="volume Visualization", show_ticks = True):
    import pyvista as pv

    if volume_xyz is None:
        x, y, z = np.mgrid[:volume.shape[0],
                           :volume.shape[1],
                           :volume.shape[2]]
    else:
        x, y, z = volume_xyz
    
    x_min, x_max, y_min, y_max, z_min, z_max = (x.min(), x.max(), y.min(), y.max(), z.min(), z.max()) 
    normed_values = (volume - volume.min()) / (volume.max() - volume.min())

    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    point_cloud = pv.PolyData(points)
    point_cloud["volume"] = normed_values.ravel()

    plotter = pv.Plotter()
    plotter.add_title(title)

    plotter.add_points(point_cloud, scalars="volume", cmap="viridis", opacity="sigmoid")
    if show_ticks:
        plotter.show_bounds(
            grid='front',
            location='outer',
            all_edges=True,
        )

    return plotter

def pv_surface(data_2d, plotter=None, show_edges=True, cmap=None, zscale = None):
    """
    Create a surface plot from a 2D array using PyVista and PolyData.

    Parameters:
        data_2d (numpy.ndarray): A 2D numpy array to plot.
        plotter (pyvista.Plotter): Existing plotter instance (if any).
        show_edges (bool): Whether to show edges of the surface.
        cmap (str): Colormap to use for the surface.
    """
    import pyvista as pv
    
    if not isinstance(data_2d, np.ndarray) or len(data_2d.shape) != 2:
        raise ValueError("Input must be a 2D numpy array.")
    
    nx, ny = data_2d.shape
    x = np.arange(nx)
    y = np.arange(ny)
    yy, xx = np.meshgrid(y, x)
    z = data_2d
    points = np.c_[xx.ravel(), yy.ravel(), z.ravel()]
    faces = []

    for i in range(nx - 1):
        for j in range(ny - 1):
            idx = i * ny + j
            faces.append([4, idx, idx + 1, idx + ny + 1, idx + ny])

    faces = np.array(faces, dtype=np.int32).ravel()

    mesh = pv.PolyData(points, faces)
    mesh["scalars"] = z.ravel()
    if plotter is None:
        plotter = pv.Plotter()
    plotter.add_mesh(mesh, show_edges=show_edges, cmap=cmap, scalars="scalars",
                     scalar_bar_args={'title': "Intensity"})
    if zscale is None:
        zscale = (data_2d.shape[0] * data_2d.shape[1])**0.5 / (
            data_2d.max() - data_2d.min())
    plotter.set_scale(xscale = 1, yscale = 1, zscale = zscale)
    plotter.add_axes()
    
    return plotter

def interpolate_mse_surface(grid_locations, mse, resolution=None, method='cubic'):
    from scipy.interpolate import griddata

    x = grid_locations[:, 0]
    y = grid_locations[:, 1]

    if resolution is None:
        dx = np.diff(np.sort(np.unique(x)))
        dy = np.diff(np.sort(np.unique(y)))
        min_dx = dx[dx > 0].min() if np.any(dx > 0) else 1.0
        min_dy = dy[dy > 0].min() if np.any(dy > 0) else 1.0
        resolution = 0.1 * min(min_dx, min_dy)

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()

    grid_x, grid_y = np.meshgrid(
        np.arange(x_min, x_max + resolution, resolution),
        np.arange(y_min, y_max + resolution, resolution)
    )

    grid_z = griddata(grid_locations, mse, (grid_x, grid_y), method=method)
    extent = (x_min, x_max, y_min, y_max)
    return grid_z, extent

if __name__ == '__main__':
    plt_imshow(np.random.rand(100, 100) + 1j * np.random.rand(100, 100), portrait = True)
    plt.show()