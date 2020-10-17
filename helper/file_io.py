import dill


def save_pickle(obj, path):
    """
    Save obj to path as a pickle file

    Parameters
    ----------
    obj: object
        Object to be dumped as pickle. Should be pickeable
    path: str
        Path to dump pickle to
    """
    pickle_out = open(path, "wb")
    dill.dump(obj, pickle_out)
    pickle_out.close()


def load_pickle(path):
    """
    Load obj from pickle file

    Parameters
    ----------
    path: str
        Path to load pickle from

    Returns
    -------
    obj: object
        Object loaded from pickle
    """
    pickle_in = open(path, "rb")
    obj = dill.load(pickle_in)
    pickle_in.close()
    return obj
