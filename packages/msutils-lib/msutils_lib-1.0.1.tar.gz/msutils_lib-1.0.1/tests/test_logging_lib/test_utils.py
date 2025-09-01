import time

from ms_utils.logging_lib import time_it_decorator


def test_time_it_decorator():
    """Smoke test for time it decorator."""

    @time_it_decorator
    def example_function():
        """example function"""
        time.sleep(1)

    example_function()
