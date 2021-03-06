from torch import _C
from . import _lazy_init, _lazy_call, device_count, device


def get_rng_state(device_id=-1):
    r"""Returns the random number generator state of the current
    GPU as a ByteTensor.

    Args:
        device_id (int, optional): The device to return the RNG state of.
            Default: -1 (i.e., use the current device).

    .. warning::
        This function eagerly initializes CUDA.
    """
    _lazy_init()
    with device(device_id):
        return _C._cuda_getRNGState()


def get_rng_state_all():
    r"""Returns a tuple of ByteTensor representing the random number states of all devices."""

    results = []
    for i in range(device_count()):
        with device(i):
            results.append(get_rng_state())
    return results


def set_rng_state(new_state, device_id=-1):
    r"""Sets the random number generator state of the current GPU.

    Args:
        new_state (torch.ByteTensor): The desired state
    """
    new_state_copy = new_state.clone()

    # NB: What if device_id=-1?  You might be afraid that the "current"
    # device would change by the time we actually get around to invoking
    # the lazy callback.  But actually, this is not possible: changing
    # the current device involves a CUDA call, which would in turn
    # initialize the state.  So then _lazy_call would execute cb
    # immediately.
    def cb():
        with device(device_id):
            _C._cuda_setRNGState(new_state_copy)

    _lazy_call(cb)


def set_rng_state_all(new_states):
    r"""Sets the random number generator state of all devices.

    Args:
        new_state (tuple of torch.ByteTensor): The desired state for each device"""
    for i, state in enumerate(new_states):
        set_rng_state(state, i)


def manual_seed(seed):
    r"""Sets the seed for generating random numbers for the current GPU.
    It's safe to call this function if CUDA is not available; in that
    case, it is silently ignored.

    Args:
        seed (int or long): The desired seed.

    .. warning::
        If you are working with a multi-GPU model, this function is insufficient
        to get determinism.  To seed all GPUs, use :func:`manual_seed_all`.
    """
    _lazy_call(lambda: _C._cuda_manualSeed(seed))


def manual_seed_all(seed):
    r"""Sets the seed for generating random numbers on all GPUs.
    It's safe to call this function if CUDA is not available; in that
    case, it is silently ignored.

    Args:
        seed (int or long): The desired seed.
    """
    _lazy_call(lambda: _C._cuda_manualSeedAll(seed))


def seed():
    r"""Sets the seed for generating random numbers to a random number for the current GPU.
    It's safe to call this function if CUDA is not available; in that
    case, it is silently ignored.

    .. warning::
        If you are working with a multi-GPU model, this function will only initialize
        the seed on one GPU.  To initialize all GPUs, use :func:`seed_all`.
    """
    _lazy_call(lambda: _C._cuda_seed())


def seed_all():
    r"""Sets the seed for generating random numbers to a random number on all GPUs.
    It's safe to call this function if CUDA is not available; in that
    case, it is silently ignored.
    """
    _lazy_call(lambda: _C._cuda_seedAll())


def initial_seed():
    r"""Returns the current random seed of the current GPU.

    .. warning::
        This function eagerly initializes CUDA.
    """
    _lazy_init()
    return _C._cuda_initialSeed()
