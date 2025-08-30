# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md


def updater(method_to_call):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Call the specified method
            method_to_call(*args, **kwargs)
            # Call the original method
            return func(*args, **kwargs)

        return wrapper

    return decorator
