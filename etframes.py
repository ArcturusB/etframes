"""
This module implements two graph types described in Edward Tufte's
"Visual Display of Quantitative Information".

Author: Adam Hupp <adam@hupp.org>
License: Distributed under the PSF license, http://www.python.org/psf/license/

"""
import matplotlib.pylab

import matplotlib as mpl
from matplotlib.collections import LineCollection
from matplotlib.artist import Artist
from matplotlib.ticker import FixedLocator, FormatStrFormatter

__all__ = ["add_range_frame", "add_dot_dash_plot"]


def cleanframe_and_ticks(axes):

    # Turn off the default frame
    axes.set_frame_on(False)

    # Only show ticks on bottom and left frame
    axes.get_xaxis().tick_bottom()
    axes.get_yaxis().tick_left()

def adjust_ticks_to_bounds(ticks, minor_ticks, bounds, pad=1e-5,
                           show_data_min=True, show_data_max=True):
    # inbound major ticks
    ticks_selection = (bounds[0] - pad <= ticks) & \
                      (bounds[1] + pad >= ticks)
    inbound_ticks = ticks[ticks_selection]
    # inbound minor ticks
    try:
        minor_ticks_selection = (bounds[0] - pad <= minor_ticks) & \
                                (bounds[1] + pad >= minor_ticks)
        inbound_minor_ticks = minor_ticks[minor_ticks_selection]
    except TypeError:
        inbound_minor_ticks = []
    # outbound major ticks
    outbound_ticks = []
    if show_data_min and bounds[0] + pad < inbound_ticks.min():
        outbound_ticks.append(bounds[0])
    if show_data_max and bounds[1] - pad > inbound_ticks.max():
        outbound_ticks.append(bounds[1])
    return inbound_ticks, outbound_ticks, inbound_minor_ticks

def set_tick_for_data_bounds(axes, axis_name):
    ''' Set minor ticks to the same size as major ones to align min and max
    labels, and make them transparent to hide them. '''
    axes.tick_params(
        axis=axis_name,
        which='minor',
        direction='out',
        size=mpl.rcParams['xtick.major.size'],
        width=mpl.rcParams['xtick.major.width'],
        pad=mpl.rcParams['xtick.major.pad'],
        color=(0,0,0,0))
    for axis in (axes.xaxis, axes.yaxis):
        formatter = axis.get_major_formatter()
        axis.set_minor_formatter(formatter)

def add_range_ticks(axes, xbounds, ybounds,
                    show_x_min=True, show_x_max=True,
                    show_y_min=True, show_y_max=True):

    axes.tick_params(direction='out', which='both')

    xticks, xboundticks, xminorticks = adjust_ticks_to_bounds(
        axes.get_xticks(),
        axes.get_xticks(minor=True),
        xbounds,
        show_data_min=show_x_min, show_data_max=show_x_max)
    yticks, yboundticks, yminorticks = adjust_ticks_to_bounds(
        axes.get_yticks(),
        axes.get_yticks(minor=True),
        ybounds,
        show_data_min=show_y_min, show_data_max=show_y_max)
    axes.set_xticks(xticks)
    axes.set_yticks(yticks)
    if show_x_min or show_x_max:
        set_tick_for_data_bounds(axes, 'x')
        axes.set_xticks(xboundticks, minor=True)
    else:
        axes.set_xticks(xminorticks, minor=True)
    if show_y_min or show_y_max:
        set_tick_for_data_bounds(axes, 'y')
        axes.set_yticks(yboundticks, minor=True)
    else:
        axes.set_yticks(yminorticks, minor=True)


class RangeFrameArtist(Artist):
    "Draws range frames on a graph"
    
    def __init__(self, color, linewidth, xbounds, ybounds):
        """
        color: str indicating color of line
        linewidth: width of line to draw
        xbounds, ybounds: tuple (min,max) of data on x and y axis, as a
            fraction of the axes size.
        """
        Artist.__init__(self)
        self.color = color
        self.linewidth = linewidth
        self.xbounds = xbounds
        self.ybounds = ybounds
        
    def draw(self, renderer, *args, **kwargs):
        if not self.get_visible(): return

        rf = self.make_range_frame()
        rf.draw(renderer)


    def make_range_frame(self):

        xline = [(self.xbounds[0], 0), (self.xbounds[1], 0)]
        yline = [(0, self.ybounds[0]), (0, self.ybounds[1])]

        range_lines = LineCollection(segments=[xline, yline],
                                     linewidths=[self.linewidth],
                                     colors=[self.color])

        range_lines.set_transform(self.axes.transAxes)
        range_lines.set_zorder(10)

        return range_lines


def axis_data_bounds(user_bounds, axis_data_bounds, axis_display_limits):
    ''' Determine the data bound for a matplotlib Axis.

    Parameters
    ==========
    user_bounds : 2-tuple of float or None
        The data bounds requested by the user.
    axis_data_bounds : 2-tuple of float
        The axis data bounds, eg. `axes.dataLim.intervalx`
    axis_display_limits : 2-tuple of float
        The axis display limits, eg. `axes.get_xlim()`
    '''
    # use user_bounds if they are set, completing missing values with
    # axis_data_bounds
    if user_bounds is None:
        vmin, vmax = axis_data_bounds
    else:
        vmin, vmax = user_bounds

        if vmin is None:
            vmin = axis_data_bounds[0]
        if vmax is None:
            vmax = axis_data_bounds[1]

    # ensure that the returned values are within the axis_display limits
    axis_vmin, axis_vmax = axis_display_limits
    if axis_vmin is not None:
        vmin = max(vmin, axis_vmin)
    if axis_vmax is not None:
        vmax = min(vmax, axis_vmax)

    return vmin, vmax

def axes_data_bound(ax, xbounds, ybounds):
    ''' Determine the data bound for matplotlib Axes.

    Parameters
    ==========
    xbounds, ybounds : 2-tuples of float or None
        The x and y data limits requested by the user.
    axis_display_limits : 2-tuple of float
        The axis display limits, eg. `ax.get_xlim()`
    '''
    xmin, xmax = axis_data_bounds(xbounds, ax.dataLim.intervalx, ax.get_xlim())
    ymin, ymax = axis_data_bounds(ybounds, ax.dataLim.intervaly, ax.get_ylim())
    return xmin, xmax, ymin, ymax


def add_range_frame(axes=None, color="k", linewidth=1.0,
                    xbounds=None, ybounds=None,
                    show_x_min=True, show_x_max=True,
                    show_y_min=True, show_y_max=True):
    """
    Adds a range frame to a matplotlib graph.  The range frame is
    described in Tufte's "The Visual Display of Quantitative
    Information" p. 130.

    The range frame is an unobtrusive way of marking the minimum and
    maxiumum values on a scatterplot or other graph.
    
    axes: the matplotlib axes to apply a range frame to.  If None or
    unspecified, use the current axes

    color: string specification of the color. default is 'k', (black)

    linewidth: width of lines in range frame

    xbounds, ybounds: tuple (min,max) on x and y axes
        If None, use values from axes.dataLim.

    show_x_min, show_x_max, show_y_min, show_y_max : bool (default: True)
        If true, add the value of the minimum or maximum data value on the
        corresponding axis.
    """

    if axes is None:
        axes = matplotlib.pylab.gca()

    xmin, xmax, ymin, ymax = axes_data_bound(axes, xbounds, ybounds)

    # transform x and y bounds from data to axes coordinates in [0, 1]
    trans = axes.transData + axes.transAxes.inverted()
    frame_xmin, frame_ymin = trans.transform_point((xmin, ymin))
    frame_xmax, frame_ymax = trans.transform_point((xmax, ymax))

    axes.add_artist(RangeFrameArtist(color=color,
                                     linewidth=linewidth,
                                     xbounds=(frame_xmin, frame_xmax),
                                     ybounds=(frame_ymin, frame_ymax)))

    cleanframe_and_ticks(axes)
    add_range_ticks(axes, (xmin, xmax), (ymin, ymax),
                    show_x_min=show_x_min, show_x_max=show_x_max,
                    show_y_min=show_y_min, show_y_max=show_y_max)


def add_dot_dash_plot(axes=None, xs=None, ys=None):
    """
    Add a dot-dash-plot to a matplotlib graph, as described on p. 133
    of Tufte's "The Visual Display of Quantitative Information".

    axes: axes to apply the dash-dot-plot to.  If None or unspecified,
    use the current axes.

    xs: a list of values along the x-axis to plot
    yx: a list of values along the y-axis to plot

    """
    
    if axes is None:
        axes = matplotlib.pylab.gca()

    if xs is not None:
        axes.xaxis.set_minor_locator(FixedLocator(xs))

    if ys is not None:
        axes.yaxis.set_minor_locator(FixedLocator(ys))

    cleanframe_and_ticks(axes)

