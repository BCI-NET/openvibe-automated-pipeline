from Statistical_analysis import *
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from matplotlib import cm
from matplotlib.colors import ListedColormap
from mne.defaults import _EXTRAPOLATE_DEFAULT, _BORDER_DEFAULT

import mne
from mne.io.meas_info import Info
from mne.viz import topomap

def add_colorbar(ax, im, cmap, side="right", pad=.05, title=None,
                  format=None, size="5%"):
    """Add a colorbar to an axis."""
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(side, size=size, pad=pad)
    cbar = plt.colorbar(im, cax=cax, format=format)


    return cbar, cax


def plot_topomap_data_viz(data, pos, vmin=None, vmax=None, cmap=None, sensors=True,
                 res=64, axes=None, names=None, show_names=False, mask=None,
                 mask_params=None, outlines='head',
                 contours=6, image_interp='bilinear', show=True,
                 onselect=None, extrapolate=_EXTRAPOLATE_DEFAULT,
                 sphere=None, border=_BORDER_DEFAULT,
                 ch_type='eeg',freq='10',Stat_method='R_square signed'):
    """Plot a topographic map as image.

    Parameters
    ----------
    data : array, shape (n_chan,)
        The data values to plot.
    pos : array, shape (n_chan, 2) | instance of Info
        Location information for the data points(/channels).
        If an array, for each data point, the x and y coordinates.
        If an Info object, it must contain only one data type and
        exactly ``len(data)`` data channels, and the x/y coordinates will
        be inferred from this Info object.
    vmin : float | callable | None
        The value specifying the lower bound of the color range.
        If None, and vmax is None, -vmax is used. Else np.min(data).
        If callable, the output equals vmin(data). Defaults to None.
    vmax : float | callable | None
        The value specifying the upper bound of the color range.
        If None, the maximum absolute value is used. If callable, the output
        equals vmax(data). Defaults to None.
    cmap : matplotlib colormap | None
        Colormap to use. If None, 'Reds' is used for all positive data,
        otherwise defaults to 'RdBu_r'.
    sensors : bool | str
        Add markers for sensor locations to the plot. Accepts matplotlib plot
        format string (e.g., 'r+' for red plusses). If True (default), circles
        will be used.
    res : int
        The resolution of the topomap image (n pixels along each side).
    axes : instance of Axes | None
        The axes to plot to. If None, the current axes will be used.
    names : list | None
        List of channel names. If None, channel names are not plotted.
    %(topomap_show_names)s
        If ``True``, a list of names must be provided (see ``names`` keyword).
    mask : ndarray of bool, shape (n_channels, n_times) | None
        The channels to be marked as significant at a given time point.
        Indices set to ``True`` will be considered. Defaults to None.
    mask_params : dict | None
        Additional plotting parameters for plotting significant sensors.
        Default (None) equals::

           dict(marker='o', markerfacecolor='w', markeredgecolor='k',
                linewidth=0, markersize=4)
    %(topomap_outlines)s
    contours : int | array of float
        The number of contour lines to draw. If 0, no contours will be drawn.
        If an array, the values represent the levels for the contours. The
        values are in µV for EEG, fT for magnetometers and fT/m for
        gradiometers. Defaults to 6.
    image_interp : str
        The image interpolation to be used. All matplotlib options are
        accepted.
    show : bool
        Show figure if True.
    onselect : callable | None
        Handle for a function that is called when the user selects a set of
        channels by rectangle selection (matplotlib ``RectangleSelector``). If
        None interactive selection is disabled. Defaults to None.
    %(topomap_extrapolate)s

        .. versionadded:: 0.18
    %(topomap_sphere)s
    %(topomap_border)s
    %(topomap_ch_type)s

    Returns
    -------
    im : matplotlib.image.AxesImage
        The interpolated data.
    cn : matplotlib.contour.ContourSet
        The fieldlines.
    """
    sphere = topomap._check_sphere(sphere)
    return _plot_topomap_test(data, pos, vmin, vmax, cmap, sensors, res, axes,
                         names, show_names, mask, mask_params, outlines,
                         contours, image_interp, show,
                         onselect, extrapolate, sphere=sphere, border=border,
                         ch_type=ch_type,freq=freq,Stat_method=Stat_method)[:2]
def _plot_topomap_test(data, pos, vmin=None, vmax=None, cmap=None, sensors=True,res=64, axes=None, names=None, show_names=False, mask=None,mask_params=None, outlines='head',contours=6, image_interp='bilinear', show=True,onselect=None, extrapolate=_EXTRAPOLATE_DEFAULT, sphere=None,border=_BORDER_DEFAULT, ch_type='eeg',freq = '10',Stat_method = 'R square signed'):
    data = np.asarray(data)
    top = cm.get_cmap('YlOrRd_r', 128) # r means reversed version
    bottom = cm.get_cmap('YlGnBu_r', 128)
    newcolors2 = np.vstack((bottom(np.linspace(0, 1, 128)),top(np.linspace(1, 0, 128))))
    double = ListedColormap(newcolors2, name='double')
    if isinstance(pos, Info):  # infer pos from Info object
        picks = topomap._pick_data_channels(pos, exclude=())  # pick only data channels
        pos = topomap.pick_info(pos, picks)

        # check if there is only 1 channel type, and n_chans matches the data
        ch_type = topomap._get_channel_types(pos, unique=True)
        info_help = ("Pick Info with e.g. mne.pick_info and "
                     "mne.io.pick.channel_indices_by_type.")
        if len(ch_type) > 1:
            raise ValueError("Multiple channel types in Info structure. " +
                             info_help)
        elif len(pos["chs"]) != data.shape[0]:
            raise ValueError("Number of channels in the Info object (%s) and "
                             "the data array (%s) do not match. "
                             % (len(pos['chs']), data.shape[0]) + info_help)
        else:
            ch_type = ch_type.pop()

        if any(type_ in ch_type for type_ in ('planar', 'grad')):
            # deal with grad pairs
            picks = topomap._pair_grad_sensors(pos, topomap_coords=False)
            pos = topomap._find_topomap_coords(pos, picks=picks[::2], sphere=sphere)
            data, _ = topomap._merge_ch_data(data[picks], ch_type, [])
            data = data.reshape(-1)
        else:
            picks = list(range(data.shape[0]))
            pos = topomap._find_topomap_coords(pos, picks=picks, sphere=sphere)

    extrapolate = topomap._check_extrapolate(extrapolate, ch_type)
    if data.ndim > 1:
        raise ValueError("Data needs to be array of shape (n_sensors,); got "
                         "shape %s." % str(data.shape))

    # Give a helpful error message for common mistakes regarding the position
    # matrix.
    pos_help = ("Electrode positions should be specified as a 2D array with "
                "shape (n_channels, 2). Each row in this matrix contains the "
                "(x, y) position of an electrode.")
    if pos.ndim != 2:
        error = ("{ndim}D array supplied as electrode positions, where a 2D "
                 "array was expected").format(ndim=pos.ndim)
        raise ValueError(error + " " + pos_help)
    elif pos.shape[1] == 3:
        error = ("The supplied electrode positions matrix contains 3 columns. "
                 "Are you trying to specify XYZ coordinates? Perhaps the "
                 "mne.channels.create_eeg_layout function is useful for you.")
        raise ValueError(error + " " + pos_help)
    # No error is raised in case of pos.shape[1] == 4. In this case, it is
    # assumed the position matrix contains both (x, y) and (width, height)
    # values, such as Layout.pos.
    elif pos.shape[1] == 1 or pos.shape[1] > 4:
        raise ValueError(pos_help)
    pos = pos[:, :2]

    if len(data) != len(pos):
        raise ValueError("Data and pos need to be of same length. Got data of "
                         "length %s, pos of length %s" % (len(data), len(pos)))

    norm = min(data) >= 0
    vmin, vmax = topomap._setup_vmin_vmax(data, vmin, vmax, norm)


    outlines = topomap._make_head_outlines(sphere, pos, outlines, (0., 0.))
    assert isinstance(outlines, dict)

    ax = axes if axes else plt.gca()
    topomap._prepare_topomap(pos, ax)

    mask_params = topomap._handle_default('mask_params', mask_params)

    # find mask limits
    extent, Xi, Yi, interp = topomap._setup_interp(
        pos, res, extrapolate, sphere, outlines, border)
    interp.set_values(data)
    Zi = interp.set_locations(Xi, Yi)()

    # plot outline
    patch_ = topomap._get_patch(outlines, extrapolate, interp, ax)

    # plot interpolated map
    im = ax.imshow(Zi, cmap=cmap, vmin=vmin, vmax=vmax, origin='lower',
                   aspect='equal', extent=extent)
    cbar,cax = add_colorbar(ax, im, cmap, side="right", pad=.1, title=None,
                      format=None, size="5%")
    cbar.set_label('Signed R^2', rotation=270,labelpad = 15)
    ax.set_title(freq +'(Hz)',fontsize = 'large')
    # gh-1432 had a workaround for no contours here, but we'll remove it
    # because mpl has probably fixed it
    linewidth = mask_params['markeredgewidth']
    cont = True
    if isinstance(contours, (np.ndarray, list)):
        pass
    elif contours == 0 or ((Zi == Zi[0, 0]) | np.isnan(Zi)).all():
        cont = None  # can't make contours for constant-valued functions
    if cont:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter('ignore')
            cont = ax.contour(Xi, Yi, Zi, contours, colors='k',
                              linewidths=linewidth / 2.)

    if patch_ is not None:
        im.set_clip_path(patch_)
        if cont is not None:
            for col in cont.collections:
                col.set_clip_path(patch_)

    pos_x, pos_y = pos.T
    if sensors is not False and mask is None:
        topomap._topomap_plot_sensors(pos_x, pos_y, sensors=sensors, ax=ax)
    elif sensors and mask is not None:
        idx = np.where(mask)[0]
        ax.plot(pos_x[idx], pos_y[idx], **mask_params)
        idx = np.where(~mask)[0]
        topomap._topomap_plot_sensors(pos_x[idx], pos_y[idx], sensors=sensors, ax=ax)
    elif not sensors and mask is not None:
        idx = np.where(mask)[0]
        ax.plot(pos_x[idx], pos_y[idx], **mask_params)

    if isinstance(outlines, dict):
        topomap._draw_outlines(ax, outlines)

    if show_names:
        if names is None:
            raise ValueError("To show names, a list of names must be provided"
                             " (see `names` keyword).")
        if show_names is True:
            def _show_names(x):
                return x
        else:
            _show_names = show_names
        show_idx = np.arange(len(names)) if mask is None else np.where(mask)[0]
        for ii, (p, ch_id) in enumerate(zip(pos, names)):
            if ii not in show_idx:
                continue
            ch_id = _show_names(ch_id)
            ax.text(p[0], p[1], ch_id, horizontalalignment='center',
                    verticalalignment='center', size='small',fontweight= 'bold')

    plt.subplots_adjust(top=.95)

    if onselect is not None:
        lim = ax.dataLim
        x0, y0, width, height = lim.x0, lim.y0, lim.width, lim.height
        ax.RS = RectangleSelector(ax, onselect=onselect)
        ax.set(xlim=[x0, x0 + width], ylim=[y0, y0 + height])
    #topomap.plt_show(show)
    return im, cont, interp

def time_frequency_map(time_freq,time,freqs,channel,fmin,fmax,fres,each_point,baseline,channel_array):
    font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 14,
        }

    fig,ax = plt.subplots()
    tf = time_freq.mean(axis=0)
    tf = np.transpose(tf[channel,:,:])
    PSD_baseline = baseline[channel,:]
    A = []
    for i in range(tf.shape[1]):
        A.append(np.divide((tf[:,i]-PSD_baseline),PSD_baseline)*100)
    tf = np.transpose(A)

    frequence = []

    time_seres = []
    print(time)
    for i in range(len(freqs)):
        if freqs[i]==fmin:
            index_fmin = i
    for i in range(len(freqs)):
        if freqs[i]==fmax:
            index_fmax = i

    tf = tf[index_fmin:index_fmax+1,:]
    top = cm.get_cmap('YlOrRd_r', 128) # r means reversed version
    bottom = cm.get_cmap('YlGnBu_r', 128)
    newcolors2 = np.vstack((bottom(np.linspace(0, 1, 128)),top(np.linspace(1, 0, 128))))
    double = ListedColormap(newcolors2, name='double')
    if np.amin(tf)<0:
        plt.imshow(tf,cmap=double,aspect='auto',origin ='lower',vmin = -np.amax(tf),vmax = np.amax(tf))
    else:
        plt.imshow(tf,cmap=double,aspect='auto',origin ='lower')
    size_time = len(time)/each_point
    for i in range(len(time)):
        if (i%(round(size_time))==0):
            time_seres.append(str((round(time[i],1))))
        else:
            time_seres.append('')

    sizing = round(len(freqs[index_fmin:(index_fmax+1)])/(each_point*1/fres))
    for i in freqs[index_fmin:(index_fmax+1)]:
        if (i%(round(sizing*1/fres))==0):
            frequence.append(str(round(i)))
        else:
            frequence.append('')
    cm.get_cmap(double)
    #plt.jet()
    ax.tick_params(axis='both', which='both', length=0)
    cbar = plt.colorbar()
    cbar.set_label('ERD/ERS', rotation=270,labelpad = 10)
    plt.yticks(range(len(freqs[index_fmin:index_fmax+1])),frequence,fontsize = 7)

    plt.xticks(range(len(time)),time_seres,fontsize = 7)
    plt.xlabel(' Time (s)', fontdict=font)
    plt.ylabel('Frequency (Hz)', fontdict=font)
    plt.title('Sensor ' + channel_array[channel],fontdict = font)
    #plt.show()


def plot_psd(Power_MI, Power_Rest, freqs, channel, channel_array, each_point, fmin, fmax, fres):
    font = {'family': 'serif',
            'color': 'black',
            'weight': 'normal',
            'size': 14,
            }

    fig, ax = plt.subplots()
    frequence = []
    Aver_MI = 10 * np.log10(Power_MI[:, channel, :])
    Aver_MI = Aver_MI.mean(0)
    STD_MI = 10 * np.log10(Power_MI[:, channel, :])
    STD_MI = STD_MI.std(0)

    Aver_Rest = 10 * np.log10(Power_Rest[:, channel, :])
    Aver_Rest = Aver_Rest.mean(0)
    STD_Rest = 10 * np.log10(Power_Rest[:, channel, :])
    STD_Rest = STD_Rest.std(0)

    for idx, f in enumerate(freqs):
        if f == fmin:
            index_fmin = idx
            break

    for idx, f in enumerate(freqs):
        if f == fmax:
            index_fmax = idx
            break

    # plt.plot(Aver_MI,freqs,Aver_Rest,freqs)
    # index_fmin = np.where(np.abs(freqs-fmin)<0.00001)
    # index_fmax = np.where(np.abs(freqs-fmax)<0.00001)
    # print(index_fmin)
    Selected_MI = (Aver_MI[index_fmin:index_fmax])
    Selected_Rest = (Aver_Rest[index_fmin:index_fmax])

    Selected_MI_STD = (STD_MI[index_fmin:index_fmax] / Power_MI.shape[0])
    Selected_Rest_STD = (STD_Rest[index_fmin:index_fmax] / Power_MI.shape[0])

    plt.plot(freqs[index_fmin:index_fmax], Selected_MI, label='Motor Imagery', color='blue')

    plt.fill_between(freqs[index_fmin:index_fmax], Selected_MI - Selected_MI_STD, Selected_MI + Selected_MI_STD,
                     color='blue', alpha=0.3)
    plt.plot(freqs[index_fmin:index_fmax], Selected_Rest, label='Resting state', color='red')
    plt.fill_between(freqs[index_fmin:index_fmax], Selected_Rest - Selected_Rest_STD,
                     Selected_Rest + Selected_Rest_STD,
                     color='red', alpha=0.3)
    sizing = round(len(freqs[index_fmin:(index_fmax + 1)]) / (each_point * 1 / fres))
    for i in freqs[index_fmin:(index_fmax + 1)]:
        if (i % (round(sizing * 1 / fres)) == 0):
            frequence.append(str(round(i)))
        else:
            frequence.append('')
    ax.tick_params(axis='both', which='both', length=0)

    plt.title('Sensor: ' + channel_array[channel], fontsize='large')
    plt.xticks(range(len(freqs[index_fmin:(index_fmax + 1)])), frequence, fontsize=12)
    plt.xlabel(' Frequency (Hz)', fontdict=font)
    plt.ylabel('Power spectrum (db)', fontdict=font)
    plt.margins(x=0)
    ax.set_xticks(np.arange(fmin, fmax, sizing))
    ax.grid(axis='x')
    plt.axis('square')

    plt.legend()
    # plt.show()

def plot_psd2(Rsigned, Power_MI, Power_Rest, freqs, channel, channel_array, each_point, fmin, fmax, fres):
    font = {'family': 'serif',
            'color': 'black',
            'weight': 'normal',
            'size': 14,
            }

    fig, ax = plt.subplots()
    frequence = []
    Aver_MI = 10 * np.log10(Power_MI[:, channel, :])
    Aver_MI = Aver_MI.mean(0)
    STD_MI = 10 * np.log10(Power_MI[:, channel, :])
    STD_MI = STD_MI.std(0)

    Aver_Rest = 10 * np.log10(Power_Rest[:, channel, :])
    Aver_Rest = Aver_Rest.mean(0)
    STD_Rest = 10 * np.log10(Power_Rest[:, channel, :])
    STD_Rest = STD_Rest.std(0)

    for idx, f in enumerate(freqs):
        if f == fmin:
            index_fmin = idx
            break

    for idx, f in enumerate(freqs):
        if f == fmax:
            index_fmax = idx
            break

    # plt.plot(Aver_MI,freqs,Aver_Rest,freqs)
    # index_fmin = np.where(np.abs(freqs-fmin)<0.00001)
    # index_fmax = np.where(np.abs(freqs-fmax)<0.00001)
    # print(index_fmin)
    Selected_MI = (Aver_MI[index_fmin:index_fmax])
    Selected_Rest = (Aver_Rest[index_fmin:index_fmax])

    Selected_MI_STD = (STD_MI[index_fmin:index_fmax]/Power_MI.shape[0])
    Selected_Rest_STD = (STD_Rest[index_fmin:index_fmax]/Power_MI.shape[0])

    plt.plot(freqs[index_fmin:index_fmax], 100*Rsigned[channel, index_fmin:index_fmax], label='r2', color='black')
    plt.plot(freqs[index_fmin:index_fmax], Selected_MI, label='Motor Imagery', color='blue')

    plt.fill_between(freqs[index_fmin:index_fmax], Selected_MI - Selected_MI_STD, Selected_MI + Selected_MI_STD,
                     color='blue', alpha=0.3)
    plt.plot(freqs[index_fmin:index_fmax], Selected_Rest, label='Resting state', color='red')
    plt.fill_between(freqs[index_fmin:index_fmax], Selected_Rest - Selected_Rest_STD,
                     Selected_Rest + Selected_Rest_STD,
                     color='red', alpha=0.3)
    sizing = round(len(freqs[index_fmin:(index_fmax + 1)]) / (each_point * 1 / fres))
    for i in freqs[index_fmin:(index_fmax + 1)]:
        if (i % (round(sizing * 1 / fres)) == 0):
            frequence.append(str(round(i)))
        else:
            frequence.append('')
    ax.tick_params(axis='both', which='both', length=0)

    plt.title('Sensor: ' + channel_array[channel], fontsize='large')
    plt.xticks(range(len(freqs[index_fmin:(index_fmax + 1)])), frequence, fontsize=12)
    plt.xlabel(' Frequency (Hz)', fontdict=font)
    plt.ylabel('Power spectrum (db)', fontdict=font)
    plt.margins(x=0)
    ax.set_xticks(np.arange(fmin, fmax, sizing))
    ax.grid(axis='x')
    plt.axis('square')

    plt.legend()
    # plt.show()

def plot_Rsquare_calcul_welch(Rsquare,channel_array,freq,smoothing,fres,each_point,fmin,fmax):
    fig,ax = plt.subplots()
    font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 14,
        }
    frequence = []

    for idx, f in enumerate(freq):
        if f == fmin:
            index_fmin = idx
            break

    for idx, f in enumerate(freq):
        if f == fmax:
            index_fmax = idx
            break

    Rsquare_reshape = Rsquare[0:64,index_fmin:index_fmax+1]

    top = cm.get_cmap('YlOrRd_r', 128) # r means reversed version
    bottom = cm.get_cmap('YlGnBu_r', 128)
    newcolors2 = np.vstack((bottom(np.linspace(0, 1, 128)),top(np.linspace(1, 0, 128))))
    double = ListedColormap(newcolors2, name='double')

    if np.amin(Rsquare_reshape) < 0:
        plt.imshow(Rsquare_reshape,cmap='bwr',aspect='auto',vmin = -np.amax(abs(Rsquare_reshape)),vmax = np.max(abs(Rsquare_reshape)))
    else:
        plt.imshow(Rsquare_reshape,cmap='bwr',aspect='auto')
    cm.get_cmap(double)
    #plt.jet()
    cbar = plt.colorbar()
    cbar.set_label('Signed R^2', rotation=270,labelpad = 10)
    plt.yticks(range(len(channel_array)),channel_array)
    freq_real = range(0,round(freq[len(freq)-1]),2)
    sizing = round(len(freq[index_fmin:(index_fmax+1)])/(each_point*1/fres))
    for i in freq[index_fmin:(index_fmax+1)]:
        if (i%(round(sizing*1/fres))==0):
            frequence.append(str(round(i)))
        else:
            frequence.append('')

    if smoothing == True:
        plt.xlim(0,80)
    if smoothing == False:
        # plt.xticks(range(0,len(freq)-1,round(2/fres)),freq_real)
        #plt.xlim(0,round(70/fres))

        ax.tick_params(axis='both', which='both', length=0)
        plt.xticks(range(len(freq[index_fmin:index_fmax+1])),frequence,fontsize = 10)
        # plt.xlim(0,round(72/fres))
    plt.xlabel('Frequency (Hz)', fontdict=font)
    plt.ylabel('Sensors', fontdict=font)

    # Major ticks
    ax.set_xticks(np.arange(0, len(freq[index_fmin:index_fmax+1]), 1))
    ax.set_yticks(np.arange(0, len(channel_array), 1))

    # Labels for major ticks
    ax.set_xticklabels(frequence)
    ax.set_yticklabels(channel_array)

    # Minor ticks
    
    ax.set_yticks(np.arange(-.5, len(channel_array), 1), minor=True)
    ax.set_xticks(np.arange(-.5, len(freq[index_fmin:index_fmax+1]), 1), minor=True)
    # Gridlines based on minor ticks
    ax.grid(which='minor', color='black', linestyle='-', linewidth=1)
    #(ax.grid(axis ='minor',color = 'black',linewidth=1)
    #Hplt.yticks(range(len(channel_array)),channel_array)
    #plt.show()


def Reorder_Rsquare(Rsquare, electrodes_orig, powerLeft, powerRight):
    if len(electrodes_orig) >= 64:
        electrodes_target = ['FP1','AF7','AF3','F7','F5','F3','F1','FT9','FT7','FC5','FC3','FC1','T7','C5','C3','C1','TP9','TP7','CP5','CP3','CP1','P7','P5','P3','P1','PO9','PO7','PO3','O1','AFz','Fz','FCz','Cz','CPz','Pz','POz','Oz','FP2','AF8','AF4','F8','F6','F4','F2','FT10','FT8','FC6','FC4','FC2','T8','C6','C4','C2','TP10','TP8','CP6','CP4','CP2','P8','P6','P4','P2','PO10','PO8','PO4','O2']
    else:
        electrodes_target = ['Fp1','F7','F3','FC5','FC1','T7','C3','CP5','CP1','P7','P3','PO9','O1','AFz','Fz','FCz','Cz','Pz','Oz','Fp2','F8','F4','FC6','FC2','T8','C4','CP6','CP2','P8','P4','PO10','O2']
    index_elec = []
    for i in range(len(electrodes_orig)):
        for k in range(len(electrodes_target)):
            if electrodes_orig[i] == electrodes_target[k]:
                index_elec.append(k)
                break

    Rsquare_final = np.copy(Rsquare)
    powerLeft_final = np.copy(powerLeft)
    powerRight_final = np.copy(powerRight)

    for l in range(len(index_elec)):
        # print("index "+str(l)+" replaced by "+str(index_elec[l]))
        powerLeft_final[:, l, :] = powerLeft[:, index_elec[l], :]
        powerRight_final[:, l, :] = powerRight[:, index_elec[l], :]
        Rsquare_final[l] = Rsquare[index_elec[l], :]

    return Rsquare_final, electrodes_target, powerLeft_final, powerRight_final


def topo_plot(Rsquare, freq, electrodes, fres, fs, Stat_method):
    fig,ax = plt.subplots()
    size_dim = mne.channels.make_standard_montage('standard_1020')
    if len(electrodes) >32:
        biosemi_montage = mne.channels.make_standard_montage('standard_1020')
    else:
        biosemi_montage_inter = mne.channels.make_standard_montage('standard_1020')
        ind = [i for (i, channel) in enumerate(biosemi_montage_inter.ch_names) if channel in electrodes]
        biosemi_montage = biosemi_montage_inter.copy()
        # Keep only the desired channels
        biosemi_montage.ch_names = [biosemi_montage_inter.ch_names[x] for x in ind]
        kept_channel_info = [biosemi_montage_inter.dig[x+3] for x in ind]
        # Keep the first three rows as they are the fiducial points information
        biosemi_montage.dig = biosemi_montage_inter.dig[0:3]+kept_channel_info
        #biosemi_montage = mne.channels.make_standard_montage('standard_1020')
    n_channels = len(biosemi_montage.ch_names)
    fake_info = mne.create_info(ch_names=biosemi_montage.ch_names, sfreq=fs/2,
                                ch_types='eeg')

    rng = np.random.RandomState(0)
    data = rng.normal(size=(n_channels, 1)) * 1e-6
    fake_evoked = mne.EvokedArray(data, fake_info)
    fake_evoked.set_montage(biosemi_montage)

    # first we obtain the 3d positions of selected channels
    chs = ['Iz', 'Cz', 'T9', 'T10']
    pos = np.stack([size_dim.get_positions()['ch_pos'][ch] for ch in chs])


    # now we calculate the radius from T7 and T8 x position
    # (we could use Oz and Fpz y positions as well)
    radius = np.abs(pos[[2, 3], 0]).mean()

    # then we obtain the x, y, z sphere center this way:
    # x: x position of the Oz channel (should be very close to 0)
    # y: y position of the T8 channel (should be very close to 0 too)
    # z: average z position of Oz, Fpz, T7 and T8 (their z position should be the
    #    the same, so we could also use just one of these channels), it should be
    #    positive and somewhere around `0.03` (3 cm)
    x = pos[0, 0]
    y = pos[-1, 1]
    z = pos[:, -1].mean()
    sizer = np.zeros([n_channels])
    print(x)
    print(y)
    print(z)
    for i in range(n_channels):
        for j in range(len(electrodes)):
            if(biosemi_montage.ch_names[i]==electrodes[j]):
                sizer[i] = Rsquare[:,freq][j]
    freq = str(freq)
    top = cm.get_cmap('YlOrRd_r', 128) # r means reversed version
    bottom = cm.get_cmap('YlGnBu_r', 128)
    newcolors2 = np.vstack((bottom(np.linspace(0, 1, 128)),top(np.linspace(1, 0, 128))))
    double = ListedColormap(newcolors2, name='double')
    plot_topomap_data_viz(sizer, fake_evoked.info,sensors = False,names = biosemi_montage.ch_names,show_names = True,res = 256,mask_params = dict(marker='', markerfacecolor='w', markeredgecolor='k',linewidth=0, markersize=0),contours = 0,image_interp='gaussian',show=True, extrapolate='head',cmap=double,freq = freq,Stat_method=Stat_method)




def plot_Pmapsigned_calcul_welch(Rsquare,channel_array,freq,smoothing,fres,each_point,fmin,fmax):
    fig,ax = plt.subplots()
    font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 14,
        }
    frequence = []
    for idx, f in enumerate(freq):
        if f == fmin:
            index_fmin = idx
            break

    for idx, f in enumerate(freq):
        if f == fmax:
            index_fmax = idx
            break

    Rsquare_reshape = Rsquare[0:64,index_fmin:index_fmax]
    for i in range(Rsquare_reshape.shape[0]):
        for k in range(Rsquare_reshape.shape[1]):
            if Rsquare_reshape[i,k] >=0:
                Rsquare_reshape[i,k] = 1-Rsquare_reshape[i,k]
            else:
                Rsquare_reshape[i,k] = -1-Rsquare_reshape[i,k]
    plt.imshow(Rsquare_reshape,cmap='bwr',aspect='auto')
    cm.get_cmap(name = 'bwr')
    #plt.jet()
    cbar = plt.colorbar()
    cbar.set_label('Confidence level', rotation=270,labelpad = 10)
    plt.yticks(range(len(channel_array)),channel_array)
    freq_real = range(0,round(freq[len(freq)-1]),2)
    for i in range(len(freq)):
        if (i%(round(each_point*1/fres))==0):
            frequence.append(str(round(freq[i])))
        else:
            frequence.append('')

    if smoothing == True:
        plt.xlim(0,80)
    if smoothing == False:
        # plt.xticks(range(0,len(freq)-1,round(2/fres)),freq_real)
        #plt.xlim(0,round(70/fres))
        ax.tick_params(axis='both', which='both', length=0)
        plt.xticks(range(len(freq[index_fmin:index_fmax])),frequence[index_fmin:index_fmax],fontsize = 10)
        # plt.xlim(0,round(72/fres))
    plt.xlabel('Frequency (Hz)', fontdict=font)
    plt.ylabel('Sensors', fontdict=font)

    plt.show()



def time_frequency_map_between_cond(time_freq,time,freqs,channel,fmin,fmax,fres,each_point,baseline,channel_array):
    font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 14,
        }

    fig,ax = plt.subplots()
    rsquare_signed = Compute_Signed_Rsquare(time_freq[:,channel,:,:],baseline[:,channel,:,:])
    rsquare_signed = np.transpose(rsquare_signed)
    frequence = []

    time_seres = []
    print(time)
    for idx, f in enumerate(freqs):
        if f == fmin:
            index_fmin = idx
            break

    for idx, f in enumerate(freqs):
        if f == fmax:
            index_fmax = idx
            break

    rsquare_signed = rsquare_signed[index_fmin:index_fmax+1,:]
    top = cm.get_cmap('YlOrRd_r', 128) # r means reversed version
    bottom = cm.get_cmap('YlGnBu_r', 128)
    newcolors2 = np.vstack((bottom(np.linspace(0, 1, 128)),top(np.linspace(1, 0, 128))))
    double = ListedColormap(newcolors2, name='double')
    if np.amin(rsquare_signed)<0:
        plt.imshow(rsquare_signed,cmap=double,aspect='auto',origin ='lower',vmin = -np.amax(rsquare_signed),vmax = np.amax(rsquare_signed))
    else:
        plt.imshow(rsquare_signed,cmap=double,aspect='auto',origin ='lower') 
    size_time = len(time)/each_point
    for i in range(len(time)):
        if (i%(round(size_time))==0):
            time_seres.append(str((round(time[i],1))))
        else:
            time_seres.append('')

    sizing = round(len(freqs[index_fmin:(index_fmax+1)])/(each_point*1/fres))
    for i in freqs[index_fmin:(index_fmax+1)]:
        if (i%(round(sizing*1/fres))==0):
            frequence.append(str(round(i)))
        else:
            frequence.append('')
    cm.get_cmap(double)
    #plt.jet()
    ax.tick_params(axis='both', which='both', length=0)
    cbar = plt.colorbar()
    cbar.set_label('Signed R^2', rotation=270,labelpad = 10)
    plt.yticks(range(len(freqs[index_fmin:index_fmax+1])),frequence,fontsize = 7)

    plt.xticks(range(len(time)),time_seres,fontsize = 7)
    plt.xlabel(' Time (s)', fontdict=font)
    plt.ylabel('Frequency (Hz)', fontdict=font)
    plt.title('Sensor ' + channel_array[channel],fontdict = font)