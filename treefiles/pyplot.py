import inspect

try:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    pass
    # print("Could not import matplotlib or numpy")


def get_color_cycle():
    """Return the list of colors in the current matplotlib color cycle

    Parameters
    ----------
    None

    Returns
    -------
    colors : list
        List of matplotlib colors in the current cycle, or dark gray if
        the current color cycle is empty.
    """
    cycler = mpl.rcParams["axes.prop_cycle"]
    return cycler.by_key()["color"] if "color" in cycler.keys else [".15"]


def despine(
    fig=None,
    ax=None,
    top=True,
    right=True,
    left=False,
    bottom=False,
    offset=None,
    trim=False,
):
    """Remove the top and right spines from plot(s).

    fig : matplotlib figure, optional
        Figure to despine all axes of, defaults to the current figure.
    ax : matplotlib axes, optional
        Specific axes object to despine. Ignored if fig is provided.
    top, right, left, bottom : boolean, optional
        If True, remove that spine.
    offset : int or dict, optional
        Absolute distance, in points, spines should be moved away
        from the axes (negative values move spines inward). A single value
        applies to all spines; a dict can be used to set offset values per
        side.
    trim : bool, optional
        If True, limit spines to the smallest and largest major tick
        on each non-despined axis.

    Returns
    -------
    None

    """
    # Get references to the axes we want
    axes = None
    if fig is None and ax is None:
        axes = plt.gcf().axes
    elif fig is not None:
        axes = fig.axes
    elif ax is not None:
        axes = [ax]

    for ax_i in axes:
        for side in ["top", "right", "left", "bottom"]:
            # Toggle the spine objects
            is_visible = not locals()[side]
            ax_i.spines[side].set_visible(is_visible)
            if offset is not None and is_visible:
                try:
                    val = offset.get(side, 0)
                except AttributeError:
                    val = offset
                ax_i.spines[side].set_position(("outward", val))

        # Potentially move the ticks
        if left and not right:
            maj_on = any(t.tick1line.get_visible() for t in ax_i.yaxis.majorTicks)
            min_on = any(t.tick1line.get_visible() for t in ax_i.yaxis.minorTicks)
            ax_i.yaxis.set_ticks_position("right")
            for t in ax_i.yaxis.majorTicks:
                t.tick2line.set_visible(maj_on)
            for t in ax_i.yaxis.minorTicks:
                t.tick2line.set_visible(min_on)

        if bottom and not top:
            maj_on = any(t.tick1line.get_visible() for t in ax_i.xaxis.majorTicks)
            min_on = any(t.tick1line.get_visible() for t in ax_i.xaxis.minorTicks)
            ax_i.xaxis.set_ticks_position("top")
            for t in ax_i.xaxis.majorTicks:
                t.tick2line.set_visible(maj_on)
            for t in ax_i.xaxis.minorTicks:
                t.tick2line.set_visible(min_on)

        if trim:
            # clip off the parts of the spines that extend past major ticks
            xticks = np.asarray(ax_i.get_xticks())
            if xticks.size:
                firsttick = np.compress(xticks >= min(ax_i.get_xlim()), xticks)[0]
                lasttick = np.compress(xticks <= max(ax_i.get_xlim()), xticks)[-1]
                ax_i.spines["bottom"].set_bounds(firsttick, lasttick)
                ax_i.spines["top"].set_bounds(firsttick, lasttick)
                newticks = xticks.compress(xticks <= lasttick)
                newticks = newticks.compress(newticks >= firsttick)
                ax_i.set_xticks(newticks)

            yticks = np.asarray(ax_i.get_yticks())
            if yticks.size:
                firsttick = np.compress(yticks >= min(ax_i.get_ylim()), yticks)[0]
                lasttick = np.compress(yticks <= max(ax_i.get_ylim()), yticks)[-1]
                ax_i.spines["left"].set_bounds(firsttick, lasttick)
                ax_i.spines["right"].set_bounds(firsttick, lasttick)
                newticks = yticks.compress(yticks <= lasttick)
                newticks = newticks.compress(newticks >= firsttick)
                ax_i.set_yticks(newticks)


def move_legend(obj, loc, **kwargs):
    """
    Recreate a plot's legend at a new location.

    The name is a slight misnomer. Matplotlib legends do not expose public
    control over their position parameters. So this function creates a new legend,
    copying over the data from the original object, which is then removed.

    Parameters
    ----------
    obj : the object with the plot
        This argument can be either a seaborn or matplotlib object:

        - :class:`seaborn.FacetGrid` or :class:`seaborn.PairGrid`
        - :class:`matplotlib.axes.Axes` or :class:`matplotlib.figure.Figure`

    loc : str or int
        Location argument, as in :meth:`matplotlib.axes.Axes.legend`.

    kwargs
        Other keyword arguments are passed to :meth:`matplotlib.axes.Axes.legend`.

    Examples
    --------

    .. include:: ../docstrings/move_legend.rst

    """
    # This is a somewhat hackish solution that will hopefully be obviated by
    # upstream improvements to matplotlib legends that make them easier to
    # modify after creation.

    # Locate the legend object and a method to recreate the legend
    if isinstance(obj, mpl.axes.Axes):
        old_legend = obj.legend_
        legend_func = obj.legend
    elif isinstance(obj, mpl.figure.Figure):
        if obj.legends:
            old_legend = obj.legends[-1]
        else:
            old_legend = None
        legend_func = obj.legend
    else:
        err = "`obj` must be a seaborn Grid or matplotlib Axes or Figure instance."
        raise TypeError(err)

    if old_legend is None:
        err = f"{obj} has no legend attached."
        raise ValueError(err)

    # Extract the components of the legend we need to reuse
    handles = old_legend.legendHandles
    labels = [t.get_text() for t in old_legend.get_texts()]

    # Extract legend properties that can be passed to the recreation method
    # (Vexingly, these don't all round-trip)
    legend_kws = inspect.signature(mpl.legend.Legend).parameters
    props = {k: v for k, v in old_legend.properties().items() if k in legend_kws}

    # Delegate default bbox_to_anchor rules to matplotlib
    props.pop("bbox_to_anchor")

    # Try to propagate the existing title and font properties; respect new ones too
    title = props.pop("title")
    if "title" in kwargs:
        title.set_text(kwargs.pop("title"))
    title_kwargs = {k: v for k, v in kwargs.items() if k.startswith("title_")}
    for key, val in title_kwargs.items():
        title.set(**{key[6:]: val})
        kwargs.pop(key)

    # Try to respect the frame visibility
    kwargs.setdefault("frameon", old_legend.legendPatch.get_visible())

    # Remove the old legend and create the new one
    props.update(kwargs)
    old_legend.remove()
    new_legend = legend_func(handles, labels, loc=loc, **props)
    new_legend.set_title(title.get_text(), title.get_fontproperties())
