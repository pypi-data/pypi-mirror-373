import os
import numpy as np
import scipy.signal
from .base import array


def resample(y: np.ndarray, fs_old: int, fs_new: int, axis: int = -1, *args, **kwargs):
    if fs_old == fs_new:
        return y
    n = round(y.shape[axis] * fs_new / fs_old)
    return scipy.signal.resample(y, n, axis=axis, *args, **kwargs)


def audio_read(files: (str, list), fs_new: int = None, always_3d: bool = False, **kwargs):
    """
    Audio Reader

    Parameters
    ----------
    files       :   File names, specified either as a list or a string (in case of 1 signal).
    fs_new      :   Desired sample rate (if different from the original)
    always_3d   :   Always return signals array as a 3D array with dimensions (m, n, ch), where:
                        m - number of signals
                        n - number of frames
                        ch - number of channels (can be either 1 or 2)
    kwargs      :   Passed to <soundfile.read>

    Returns
    -------

    """
    import soundfile as sf

    files = np.atleast_1d(array(files))
    assert files.ndim == 1
    (channels, samplerate, frames) = [], [], []
    for i, f in enumerate(files):
        info = sf.info(f)
        channels.append(info.channels), samplerate.append(info.samplerate), frames.append(info.frames)
    (channels, samplerate, frames) = np.unique(channels), np.unique(samplerate), np.unique(frames)
    assert channels.size == 1, 'Inconsistent number of channels.'
    assert samplerate.size == 1, 'Inconsistent sample rates.'
    assert frames.size == 1, 'Inconsistent signal lengths.'

    if 'start' not in kwargs.keys():
        kwargs['start'] = 0
    if 'stop' not in kwargs.keys():
        kwargs['stop'] = frames[0]
    frames = kwargs['stop'] - kwargs['start']

    info = sf.info(files[0])
    M = np.zeros((len(files), frames, info.channels))

    # Read
    for i, f in enumerate(files):
        (M[i, :, :], _) = sf.read(f, always_2d=True, **kwargs)

    # Resample
    if fs_new is not None:
        M = resample(M, info.samplerate, fs_new, axis=1)

    if not always_3d:
        M = M.squeeze()
    return M, samplerate[0]


def audio_write(files, M, fs, fs_save=None, mode='w', **kwargs):
    """
    Audio Writer

    Parameters
    ----------
    files       :   str or list
        File names, specified either as a list or a string (in case of 1 file).
    M           :   array_like
        Signals 3D array, with dimensions (m, n, ch), where:
            m - number of signals
            n - number of frames
            ch - number of channels (can be either 1 or 2)
        If M is given as 1D, M is interpreted as a single channel.
        If M is given as 2D, then:
            If it has dimensions (n, 2), it is interpreted as single stereo signal.
            If it has dimensions (m, n), it is interpreted as m different signals.
    fs          :   int
        Original sample rate [Hz]
    fs_save     :   int, optional
        Desired sample rate to save signals (if different from the original) [Hz]
    mode        :   str {'w', 'a'}
        Save mode (write / append)
    kwargs      :   dict
        Passed to <soundfile.write>

    Returns
    -------

    """
    import soundfile as sf

    files = np.atleast_1d(array(files))
    M = array(M)
    if M.ndim == 1:
        M = M[np.newaxis, :, np.newaxis]
    elif M.ndim == 2:
        if M.shape[1] == 2:
            M = M[np.newaxis, :, :]
        else:
            M = M[:, :, np.newaxis]
    assert files.ndim == 1 and M.ndim == 3
    assert files.size == M.shape[0]

    # Resample
    if fs_save is None:
        fs_save = fs
    else:
        M = resample(M, fs, fs_save, axis=1)

    # Write
    for i, f in enumerate(files):
        if mode.lower() == 'a':
            if not os.path.isfile(f):
                with sf.SoundFile(f, 'w', samplerate=fs_save, **kwargs):
                    pass

            with sf.SoundFile(f, 'r+') as h:
                h._update_frames(h.seek(0, sf.SEEK_END))
                h.buffer_write(M, dtype='float64')

        elif mode.lower() == 'w+':
            sf.write(f, M[i, :, :].squeeze(), fs_save, **kwargs)

        else:
            raise ValueError('Invalid declaration of variable `mode`.')


def time_array(n: int, fs: int) -> np.ndarray:
    """
    Create time array range from 0 to (n-1)/fs with n samples.

    Parameters
    ----------
    n :     Length
    fs :    Sample rate

    Returns
    -------

    """
    t = np.linspace(0, (n - 1) / fs, n)
    return t


def time2samples(fs: int, *args):
    args = list(args)
    for i in range(len(args)):
        if args[i] is not None:
            args[i] = round(fs * args[i])
    if len(args) == 1:
        return args[0]
    return args
