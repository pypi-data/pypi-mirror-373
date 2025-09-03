import matplotlib.pyplot as plt
from MPSPlots.styles import mps as plot_style
from functools import wraps

import matplotlib.pyplot as plt
from MPSPlots.styles import mps as plot_style
from functools import wraps
import numpy as np

def pre_plot(nrows: int = 1, ncols: int = 1, subplot_kw: dict = {}):
    """
    Decorator factory that creates a matplotlib figure with subplots
    before calling the decorated plotting function.

    Parameters
    ----------
    nrows : int
        Number of subplot rows.
    ncols : int
        Number of subplot columns.
    """
    def decorator(function):
        @wraps(function)
        def wrapper(*args,
                    show: bool = True,
                    save_as: str = None,
                    figure_size: tuple = None,
                    tight_layout: bool = True,
                    axes: plt.Axes = None,
                    xscale: str = None,
                    yscale: str = None,
                    xlim: tuple = None,
                    ylim: tuple = None,
                    style: str = plot_style,
                    **kwargs):

            with plt.style.context(style):
                if axes is None:
                    figure, axes = plt.subplots(
                        nrows=nrows,
                        ncols=ncols,
                        figsize=figure_size,
                        squeeze=False,
                        subplot_kw=subplot_kw
                    )
                else:
                    figure = axes.get_figure()

                axes = np.array(axes).flatten()
                if nrows * ncols == 1:
                    axes = axes[0]

                # Call the decorated function
                if args and hasattr(args[0], "__class__"):
                    function(args[0], axes=axes, *args[1:], **kwargs)
                else:
                    function(*args, axes=axes, **kwargs)

                # Apply axis customizations
                all_axes = axes if isinstance(axes, np.ndarray) else [axes]
                for ax in all_axes:
                    if xscale:
                        ax.set_xscale(xscale)
                    if yscale:
                        ax.set_yscale(yscale)
                    if xlim:
                        ax.set_xlim(*xlim)
                    if ylim:
                        ax.set_ylim(*ylim)

                if tight_layout:
                    figure.tight_layout()

                if save_as is not None:
                    figure.savefig(save_as, dpi=300)

                if show:
                    plt.show()

                return figure

        return wrapper
    return decorator
