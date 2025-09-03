def is_in_notebook():
    try:
        from IPython import get_ipython

        if get_ipython().__class__.__name__ == "ZMQInteractiveShell":
            return True
        else:
            return False
    except (NameError, ModuleNotFoundError):
        return False
