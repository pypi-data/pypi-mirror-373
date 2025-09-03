"""
Math utility functions.
"""

import re
import numpy as np



def str_isint(s, abs=True):
    """
    Tests if a ``str`` can be converted to a ``int``.

    Args:
        s: ``str``
           character string to test.
        abs: ``bool``
            ``True`` (default) to match only positive/absolute value,
            ``False`` otherwise (to match also a negative value).

    Return:
        ``True`` if ``str`` ``s`` matches a ``int`` ``False`` otherwise.

    Examples:
        >>> str_isint('10')
        True
        >>> str_isint('-5')
        False
        >>> str_isint('-5', abs=True)
        False
        >>> str_isint('-5', abs=False)
        True
        >>> str_isint('25', abs=True)
        True
        >>> str_isint('not_an_int')
        False

    .. seealso::
        str_isfloat
    """
    if abs:
        int_re = r"^[0-9]+$"
    else:
        int_re = r"^-?[0-9]+$"
    return re.fullmatch(int_re, s) is not None


def str_isfloat(s, abs=True):
    """
    Tests if a ``str`` can be converted to a ``float``.

    Args:
        s: ``str``
           character string to test.
        abs: ``bool``
            ``True`` (default) to match only positive/absolute value,
            ``False`` otherwise (to match also a negative value).

    Return:
        ``True`` if ``str`` ``s`` matches a ``float`` ``False`` otherwise.
        If ``str_isint(s) == True`` then ``str_isfloat(s) == True``.

    Examples:
        >>> str_isfloat('10.2')
        True
        >>> str_isfloat('10')
        True
        >>> str_isfloat('-5')
        False
        >>> str_isfloat('-5', abs=True)
        False
        >>> str_isfloat('-5', abs=False)
        True
        >>> str_isfloat('25', abs=True)
        True
        >>> str_isfloat('not_a_float')
        False


    .. seealso::
        str_isint
    """
    # exclude first space case (because we don't use fullmatch below)
    if re.match(r'.*\s.*', s):
        return None
    # the reason fullmatch is not used is negative numbers
    if abs:
        float_re = r"^([0-9]+)|([0-9]*\.[0-9]+)$"
    else:
        float_re = r"^-?([0-9]+)|([0-9]*\.[0-9]+)$"
    return re.match(float_re, s) is not None


def get_locmaxs(xy_tuples):
    """
    Finds local maximums in ``xy_tuples``.

    The first and last points cannot be local maximum.

    Args:
        xy_tuples: ``Sequence[tuple]``, numpy 2d array
            Sequence of pairs ``(x, y)`` (the points).
            If a numpy array, it must have two columns (``x``, ``y``), one row
            per point.
            The max points are searched on ``y`` dimension along ``x``
            dimension.

    Return:
        The list of local max found.
        If no max found, returns an empty list.

    Examples:
        >>> x1 = np.arange(10)
        >>> pts = list(zip(x1, np.cos(x1)))
        >>> get_locmaxs(pts)
        [(np.int64(6), np.float64(0.960170286650366))]
        >>> x2 = np.arange(100)
        >>> more_pts = list(zip(x2, np.cos(x2)))
        >>> np.array(get_locmaxs(more_pts))
        array([[ 6.        ,  0.96017029],
               [13.        ,  0.90744678],
               [19.        ,  0.98870462],
               [25.        ,  0.99120281],
               [31.        ,  0.91474236],
               [38.        ,  0.95507364],
               [44.        ,  0.99984331],
               [50.        ,  0.96496603],
               [57.        ,  0.89986683],
               [63.        ,  0.98589658],
               [69.        ,  0.99339038],
               [75.        ,  0.92175127],
               [82.        ,  0.9496777 ],
               [88.        ,  0.99937328],
               [94.        ,  0.96945937]])
        >>> # passing more points as a numpy array works the same
        >>> np.array(get_locmaxs(np.array(more_pts)))
        array([[ 6.        ,  0.96017029],
               [13.        ,  0.90744678],
               [19.        ,  0.98870462],
               [25.        ,  0.99120281],
               [31.        ,  0.91474236],
               [38.        ,  0.95507364],
               [44.        ,  0.99984331],
               [50.        ,  0.96496603],
               [57.        ,  0.89986683],
               [63.        ,  0.98589658],
               [69.        ,  0.99339038],
               [75.        ,  0.92175127],
               [82.        ,  0.9496777 ],
               [88.        ,  0.99937328],
               [94.        ,  0.96945937]])
        >>> # to render as a figure
        >>> import matplotlib.pyplot as plt
        >>> more_pts = np.array(more_pts)
        >>> max_pts = np.array(get_locmaxs(more_pts))
        >>> plt.scatter(max_pts[:, 0], max_pts[:, 1]) # doctest: +ELLIPSIS
        <matplotlib.collections.PathCollection object at ...>
        >>> plt.plot(more_pts[:, 0], more_pts[:, 1]) # doctest: +ELLIPSIS
        [<matplotlib.lines.Line2D object at ...]
        >>> # plt.show() # uncomment to display

    .. seealso::
        :func:`.get_globmax`
    """
    locmaxs = []
    # ignore first point (as a local max)
    prev_y = xy_tuples[0][1] + 1
    # the last point is also ignored
    prev_x = -1
    ascending = False
    for x, y in xy_tuples:
        if y > prev_y:
            ascending = True
        elif ascending:
            locmaxs.append((prev_x, prev_y))
            ascending = False
        prev_x, prev_y = x, y
    return locmaxs


_glob_max_meths = ['greatest_local', 'max']


def get_globmax(xy_tuples, meth='greatest_local'):
    """
    Finds the global maximum in ``xy_tuples``.

    Args:

        xy_tuples: ``Sequence[tuple]``, numpy 2d array
            Sequence of pairs $(x, y)$ (the points).
            If a numpy array, it must have two columns $(x, y)$, one row
            per point.
            The max is searched on $y$ dimension along $x$ dimension.

        meth: ``str``

            - ``'greatest_local'``: (default) the global maximum is the
              greatest of local maximums (see :func:`.get_locmaxs`).
              Hence, if no local maximum is found, it is considered that no
              global maximum exists (the function returns None).

            - ``'max'``: the function simply returns the max of
            ``xy_tuples.``.

    Return:
        The global maximum or ``None`` if not found.

    Example:
        >>> x = np.arange(100)
        >>> pts = list(zip(x, np.cos(x)))
        >>> get_globmax(pts)
        (np.int64(44), np.float64(0.9998433086476912))
        >>> # this is the greatest local maximum
        >>> loc_maxs = np.array(get_locmaxs(pts))
        >>> loc_maxs[np.argmax(loc_maxs[:, 1])]
        array([44.        ,  0.99984331])
        >>> # situation with no local max (see get_locmaxs for a better
        >>> # understanding)
        >>> pts2 = list(zip(x.tolist(), np.linspace(1, 50, 100).tolist()))
        >>> get_globmax(pts2) is None
        True
        >>> # but a max point exists necessarily
        >>> get_globmax(pts2, meth='max')
        (99, 50.0)


    .. seealso::
        :func:`.get_locmaxs`

    """
    if meth not in _glob_max_meths:
        raise ValueError(str(meth)+' is not known. Valid meth values:' +
                         _glob_max_meths)
    # method 'greatest_local' (not optimal but for historical needs)
    loc_maxs = get_locmaxs(xy_tuples)
    loc_maxs.sort(key=lambda t: t[1], reverse=True)
    if len(loc_maxs) > 0:
        return loc_maxs[0]
    if meth == 'max':
        # return max(xy_tuples, key=lambda t: t[1])
        return xy_tuples[np.argmax(np.array(xy_tuples)[:, 1])]
        # tmp = list(xy_tuples)
        # tmp.sort(key=lambda t:t[1], reverse=True)
        # return tmp[0]
    return None


_interpoline_meths = ['slope', 'barycenter']


def interpoline(x1, y1, x2, y2, x, meth='slope'):
    """
    Interpolates linearly (``x1``, ``y1``), (``x2``, ``y2``) at value ``x``.

    Return:
        $f(x) = ax + b$ such that $f(x_1) = y_1$, $f(x_2) = y_2$.

    Example:
        >>> x1 = 10
        >>> x2 = 20
        >>> y1 = 18
        >>> y2 = 5
        >>> x = 15
        >>> y = interpoline(x1, y1, x2, y2, x, meth='slope')
        >>> y
        11.5
        >>> interpoline(x1, y1, x2, y2, x, meth='barycenter')
        11.5
        >>> # plot the line and point (x, f(x))
        >>> import matplotlib.pyplot as plt
        >>> plt.plot([x1, x2], [y1, y2], marker='+') # doctest: +ELLIPSIS
        [...
        >>> plt.scatter([x], [y]) # doctest: +ELLIPSIS
        <...
        >>> # plt.show() # uncomment to display

    """
    if meth == 'slope':
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        return a * x + b
    elif meth == 'barycenter':
        t = (x - x1) / abs(x2 - x1)
        return (1 - t) * y1 + t * y2
    else:
        raise ValueError(str(meth) + ' is not a valid method: ' +
                         _interpoline_meths)


_mv_avg_meths = ['basic', 'cumsum', 'convolve']


def calc_moving_average_list(xy_tuples, window_sz, meth='basic', x_start=None):
    """
    Computes the moving average of ``xy_tuples``.

    The average is computed for the y-dimension, 2nd column.

    Args:
        xy_tuples: ``Sequence[tuple]``, numpy 2d array
            Sequence of pairs ``(x, y)`` (the points).
            If a numpy array, it must have two columns (``x``, ``y``), one row
            per point.
        window_sz: ``int``
            The window size for average.
        meth: ``str``
            - 'basic': manual default method.
            - 'cumsum': use numpy.cumsum.
            - 'convolve': use the convolution trick.
        x_start: ``int``
            xy_tuples[x_start][0] is the first element of the x-dimension
            average/output.
            Default is ``None`` for ``x_start = int(window_sz) // 2``.
            In other words, the mean of ``xy_tuples[:window_sz]`` is the first
            element of the moving average and its x coordinate is
            ``xy_tuples[x_start][0]``. The next x-coordinates of the moving
            average are:
            ``xy_tuples[x_start+1][0], xy_tuples[x_start+2][0],`` ...

    Return:
         Moving average as a list of tuples (x, y).

    Examples:
        >>> import numpy as np
        >>> xy = list(zip(np.arange(8).tolist(), np.arange(10, 17).tolist()))
        >>> xy = np.round(xy, decimals=3).tolist()
        >>> xy
        [[0, 10], [1, 11], [2, 12], [3, 13], [4, 14], [5, 15], [6, 16]]
        >>> calc_moving_average_list(xy, 5)
        [(2, np.float64(12.0)), (3, np.float64(13.0)), (4, np.float64(14.0))]
        >>> calc_moving_average_list(xy, 5, meth='cumsum')
        [[2.0, 12.0], [3.0, 13.0], [4.0, 14.0]]
        >>> calc_moving_average_list(xy, 5, x_start=3)
        [(3, np.float64(12.0)), (4, np.float64(13.0)), (5, np.float64(14.0))]
        >>> calc_moving_average_list(xy, 5, meth='convolve')
        [[2.0, 12.0], [3.0, 13.0], [4.0, 14.0]]
    """
    if x_start is None:
        x_start = int(window_sz) // 2
    x_offset = x_start
    if meth == 'basic':
        i = 0
        window_amps = np.zeros((window_sz))
        mvavg = []
        avg_amp = 0
        for j, (t, amp) in enumerate(xy_tuples):
            window_amps[i] = amp
            i += 1
            if j >= window_sz - 1:
                avg_amp = np.mean(window_amps)
                mvavg.append((xy_tuples[x_offset][0], avg_amp))
                x_offset += 1
            i %= window_sz
        return mvavg
    # below are two variants of the code found here:
    # https://stackoverflow.com/questions/14313510/how-to-calculate-rolling-
    # moving-average-using-python-numpy-scipy#14314054
    elif meth == 'cumsum':
        sig = np.array([xy[1] for xy in xy_tuples])
        x = np.array([xy[0] for xy in xy_tuples])
        n = window_sz
        avg = np.cumsum(sig)
        avg[n:] = avg[n:] - avg[:-n]
        return np.hstack((
            x.reshape(-1, 1)[x_offset:len(avg) - n + x_offset + 1],
            (avg[n-1:] / n).reshape(-1, 1)
        )).tolist()
    elif meth == 'convolve':
        sig = np.array([xy[1] for xy in xy_tuples])
        x = np.array([xy[0] for xy in xy_tuples])
        avg = np.convolve(sig, np.ones(window_sz), 'valid') / window_sz
        return np.hstack((
            x.reshape(-1, 1)[x_offset:len(avg) + x_offset],
            avg.reshape(-1, 1)
        )).tolist()
    else:
        raise ValueError(str(meth) + ' is not a valid method: ' +
                         _mv_avg_meths)


def zeropad(ref_num, nums):
    """
    Pads/Prefixes nums with zeros to match the number of digits of ref_num.

    Args:
        ref_num: an integer.
        nums: integer or str list.

    Return:
        - if nums is a sequence returns a list of zero-padded int-s (as str).
        - if nums is a int returns a zero-padded int (as str).

    Example:
        >>> zeropad(96, 0)
        '00'
        >>> zeropad(96, [0, 1, 2, 3])
        ['00', '01', '02', '03']
        >>> zeropad(96, list(range(4)))
        ['00', '01', '02', '03']

    """
    zpadded_nums = []
    nums_is_seq = True
    if not hasattr(nums, '__len__'):
        nums = [nums]
        nums_is_seq = False
    for n in nums:
        sn = str(n)
        if not str_isint(sn):
            raise ValueError('nums must be int or sequence of int')
        dl = len(str(ref_num)) - len(sn)
        if dl < 0:
            raise ValueError('The reference number is smaller than the'
                             ' integers to pad with zeros')
        zpadded_nums += [('0'*dl)+sn]  # equiv. to sn.zfill(len(ref_num))
    if len(zpadded_nums) == 1 and not nums_is_seq:
        return zpadded_nums[0]
    return zpadded_nums
