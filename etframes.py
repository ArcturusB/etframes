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

def adjust_ticks_to_bounds(ticks, bounds, pad=1e-5,
                           show_data_min=True, show_data_max=True):
    ticks_selection = (bounds[0] - pad <= ticks) & \
                      (bounds[1] + pad >= ticks)
    inbound_ticks = ticks[ticks_selection]
    outbound_ticks = []
    if show_data_min and bounds[0] + pad < inbound_ticks.min():
        outbound_ticks.append(bounds[0])
    if show_data_max and bounds[1] - pad > inbound_ticks.max():
        outbound_ticks.append(bounds[1])
    return inbound_ticks, outbound_ticks

def add_range_ticks(axes, xbounds, ybounds,
                    show_x_min=True, show_x_max=True,
                    show_y_min=True, show_y_max=True):

    axes.tick_params(direction='out')
    # Set minor ticks to the same size as major ones to align min and max
    # labels, and make them transparent to hide them.
    axes.tick_params(
        which='minor',
        direction='out',
        size=mpl.rcParams['xtick.major.size'],
        width=mpl.rcParams['xtick.major.width'],
        pad=mpl.rcParams['xtick.major.pad'],
        color=(0,0,0,0))
    for axis in (axes.xaxis, axes.yaxis):
        formatter = axis.get_major_formatter()
        # formatter = FormatStrFormatter('%.1f')
        axis.set_minor_formatter(formatter)

    xticks, xboundticks = adjust_ticks_to_bounds(
        axes.get_xticks(),
        xbounds,
        show_data_min=show_x_min, show_data_max=show_x_max)
    yticks, yboundticks = adjust_ticks_to_bounds(
        axes.get_yticks(),
        ybounds,
        show_data_min=show_y_min, show_data_max=show_y_max)
    axes.set_xticks(xticks)
    axes.set_yticks(yticks)
    axes.set_xticks(xboundticks, minor=True)
    axes.set_yticks(yboundticks, minor=True)


def interval_frac(interval, datapoint):
    """Given an interval and a point in the same range, return
    the fractional distance of that point along the interval
    Clipped to [0,1]
    """
    pos = (datapoint - interval[0])/interval.ptp()
    # don't allow past border of axis
    return max(0.0, min(1.0, pos))


def data_bounds_on_axis(view_interval, data_bounds):
    "Map min/max from data space to viewport space."
    
    if data_bounds is None:
        return (0.0, 1.0)
    
    lower = interval_frac(view_interval, data_bounds[0])
    upper = interval_frac(view_interval, data_bounds[1])
    return lower, upper


class RangeFrameArtist(Artist):
    "Draws range frames on a graph"
    
    def __init__(self, color, linewidth, xbounds, ybounds):
        """
        color: str indicating color of line
        linewidth: width of line to draw
        xbounds, ybounds: tuple (min,max) of data on x and y axis
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

        xminf, xmaxf = data_bounds_on_axis(self.axes.viewLim.intervalx,
                                           self.xbounds)

        yminf, ymaxf = data_bounds_on_axis(self.axes.viewLim.intervaly,
                                           self.ybounds)


        xline = [(xminf,0), (xmaxf,0)]
        yline = [(0,yminf), (0,ymaxf)]

        range_lines = LineCollection(segments=[xline, yline],
                                     linewidths=[self.linewidth],
                                     colors=[self.color])

        range_lines.set_transform(self.axes.transAxes)
        range_lines.set_zorder(10)

        return range_lines




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

    show_x_min, show_x_max, show_y_min, show_y_max : bool (default: True)
        If true, add the value of the minimum or maximum data value on the
        corresponding axis.
    """

    if axes is None:
        axes = matplotlib.pylab.gca()

    if xbounds is None:
        xbounds = axes.dataLim.intervalx
    if ybounds is None:
        ybounds = axes.dataLim.intervaly

    axes.add_artist(RangeFrameArtist(color=color,
                                     linewidth=linewidth,
                                     xbounds=xbounds,
                                     ybounds=ybounds))

    cleanframe_and_ticks(axes)
    add_range_ticks(axes, xbounds, ybounds,
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

