"""Entry point to mds-toolbox API"""

from functools import update_wrapper

import click

import mds


def init_app(f):
    """Initialize the application functions before the execution"""

    @click.pass_context
    def setup(ctx, **kwargs):
        """
        Extract app settings and configure application setup, then start mds functions.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the function.
        """
        user_settings = dict()
        # Assume that upper settings are app settings related
        upper_keys = [k for k in kwargs.keys() if k.isupper()]

        # Remove upper settings from plot arguments to avoid crash in PlotSettings class
        for k in upper_keys:
            user_settings[k] = kwargs.pop(k)

        # Perform general app initialization
        mds.setup(**user_settings)

        # Start application
        return ctx.invoke(f, **kwargs)

    # Return the setup function which wraps the original function
    return update_wrapper(setup, f)


# Return the decorator function
