from __future__ import annotations

import librosa
import librosa.filters
import numba
import numpy as np
from scipy import signal
from scipy.io import wavfile

from .hparams import hparams as hp


def get_mel_chunks(
    audio_np: np.ndarray, fps: int, mel_step_size: int = 16
) -> list[np.ndarray]:
    """
    Get mel chunks from audio.

    Args:
        audio_np: The audio data in numpy array, `np.float32` in 16kHz with 1 channel.
        fps: The frame per second of the video.
        mel_step_size: The step size for mel spectrogram chunks

    Returns:
        The mel chunks.
    """
    # Convert the audio waveform to a mel spectrogram

    mel_chunks = []
    if audio_np is None or len(audio_np) == 0:
        return mel_chunks

    mel = melspectrogram(audio_np)

    # Check for NaN values in the mel spectrogram, which could indicate issues with audio processing
    if np.isnan(mel.reshape(-1)).sum() > 0:
        raise ValueError(
            "Mel contains nan! Using a TTS voice? Add a small epsilon noise to the wav file and try again"
        )

    # Split the mel spectrogram into smaller chunks suitable for processing
    mel_idx_multiplier = 80.0 / fps  # Calculate index multiplier based on frame rate
    i = 0
    while True:
        start_idx = int(i * mel_idx_multiplier)
        if start_idx + mel_step_size > len(mel[0]):  # Handle last chunk
            mel_chunks.append(mel[:, len(mel[0]) - mel_step_size :])
            break
        mel_chunks.append(mel[:, start_idx : start_idx + mel_step_size])
        i += 1

    return mel_chunks


def save_wav(wav, path, sr):
    """
    Save a wav file.

    Args:
        wav (np.ndarray): The wav file to save, as a numpy array.
        path (str): The path to save the wav file to.
        sr (int): The sample rate to use when saving the wav file.
    """
    wav *= 32767 / max(0.01, np.max(np.abs(wav)))
    wavfile.write(path, sr, wav.astype(np.int16))


def preemphasis(wav, k, preemphasize=True):
    """
    Apply preemphasis to a wav file.

    Args:
        wav (np.ndarray): The wav file to apply preemphasis to, as a numpy array.
        k (float): The preemphasis coefficient.
        preemphasize (bool, optional): Whether to apply preemphasis. Defaults to True.

    Returns:
        np.ndarray: The wav file with preemphasis applied.
    """
    if preemphasize:
        return signal.lfilter([1, -k], [1], wav)
    return wav


def inv_preemphasis(wav, k, inv_preemphasize=True):
    """
    Apply inverse preemphasis to a wav file.

    Args:
        wav (np.ndarray): The wav file to apply inverse preemphasis to, as a numpy array.
        k (float): The preemphasis coefficient.
        inv_preemphasize (bool, optional): Whether to apply inverse preemphasis. Defaults to True.

    Returns:
        np.ndarray: The wav file with inverse preemphasis applied.
    """
    if inv_preemphasize:
        return signal.lfilter([1], [1, -k], wav)
    return wav


def get_hop_size():
    """
    Get the hop size.

    Returns:
        int: The hop size.
    """
    hop_size = hp.hop_size
    if hop_size is None:
        assert hp.frame_shift_ms is not None
        hop_size = int(hp.frame_shift_ms / 1000 * hp.sample_rate)
    return hop_size


def linearspectrogram(wav):
    """
    Compute the linear spectrogram of a wav file.

    Args:
        wav (np.ndarray): The wav file to compute the spectrogram of, as a numpy array.

    Returns:
        np.ndarray: The linear spectrogram of the wav file.
    """
    D = _stft(preemphasis(wav, hp.preemphasis, hp.preemphasize))
    S = _amp_to_db(np.abs(D)) - hp.ref_level_db

    if hp.signal_normalization:
        return _normalize(S)
    return S


def melspectrogram(wav):
    """
    Compute the mel spectrogram of a wav file.

    Args:
        wav (np.ndarray): The wav file to compute the spectrogram of, as a numpy array.

    Returns:
        np.ndarray: The mel spectrogram of the wav file.
    """
    D = _stft(preemphasis(wav, hp.preemphasis, hp.preemphasize))
    S = _amp_to_db(_linear_to_mel(np.abs(D))) - hp.ref_level_db

    if hp.signal_normalization:
        return _normalize(S)
    return S


def _lws_processor():
    # Third-Party Libraries
    import lws

    return lws.lws(hp.n_fft, get_hop_size(), fftsize=hp.win_size, mode="speech")


def _stft(y):
    """
    Compute the short-time Fourier transform of a signal.

    Args:
        y (np.ndarray): The signal to compute the transform of, as a numpy array.

    Returns:
        np.ndarray: The short-time Fourier transform of the signal.
    """
    if hp.use_lws:
        return _lws_processor(hp).stft(y).T
    else:
        return librosa.stft(
            y=y,
            n_fft=hp.n_fft,
            hop_length=get_hop_size(),
            win_length=hp.win_size,
        )


##########################################################
# Those are only correct when using lws!!! (This was messing with Wavenet quality for a long time!)
def num_frames(length, fsize, fshift):
    """
    Compute number of time frames of spectrogram.

    Args:
        length: length of signal
        fsize: frame size
        fshift: frame shift

    """
    pad = fsize - fshift
    if length % fshift == 0:
        M = (length + pad * 2 - fsize) // fshift + 1
    else:
        M = (length + pad * 2 - fsize) // fshift + 2
    return M


def pad_lr(x, fsize, fshift):
    """
    Compute left and right padding.

    Args:
        x: input signal
        fsize: frame size
        fshift: frame shift
    """
    M = num_frames(len(x), fsize, fshift)
    pad = fsize - fshift
    T = len(x) + 2 * pad
    r = (M - 1) * fshift + fsize - T
    return pad, pad + r


##########################################################
# Librosa correct padding
def librosa_pad_lr(x, fsize, fshift):
    """
    Compute left and right padding for librosa.

    Args:
        x: input signal
        fsize: frame size
        fshift: frame shift.

    """
    return 0, (x.shape[0] // fshift + 1) * fshift - x.shape[0]


# Conversions
_mel_basis = None
_mel_basis_cache = None
_output_cache = None


@numba.jit(nopython=True, cache=True)
def _dot_mel(mel_basis, spectogram):
    return np.dot(mel_basis, spectogram)


def _linear_to_mel_numba(spectogram):
    """
    Convert a linear spectrogram to a mel spectrogram using optimized matrix multiplication.

    Args:
        spectogram (np.ndarray): The linear spectrogram to convert, shape around [401, 22]

    Returns:
        np.ndarray: The mel spectrogram, shape [80, 22]
    """
    global _mel_basis
    if _mel_basis is None:
        _mel_basis = _build_mel_basis()
        _mel_basis = np.ascontiguousarray(_mel_basis, dtype=np.float64)

    spectogram = np.ascontiguousarray(spectogram, dtype=np.float64)
    return _dot_mel(_mel_basis, spectogram)


@numba.jit(nopython=True, cache=True, parallel=False, fastmath=True)
def _dot_mel_hybrid(mel_basis, spectogram, out):
    """Hybrid approach using vectorized operations with controlled CPU usage."""
    # Process in smaller chunks to reduce CPU pressure
    chunk_size = 16  # Adjust this value to balance speed/CPU usage

    for j in range(0, spectogram.shape[1], chunk_size):
        end_j = min(j + chunk_size, spectogram.shape[1])
        # Use numpy's dot for each chunk
        out[:, j:end_j] = mel_basis.dot(np.ascontiguousarray(spectogram[:, j:end_j]))

    return out


def _linear_to_mel_hybrid(spectogram):
    """Hybrid implementation balancing speed and CPU usage."""
    global _mel_basis_cache, _output_cache

    if _mel_basis_cache is None:
        _mel_basis_cache = _build_mel_basis()
        _mel_basis_cache = np.ascontiguousarray(_mel_basis_cache, dtype=np.float64)

    spectogram = np.ascontiguousarray(spectogram, dtype=np.float64)

    # Reuse output array
    if _output_cache is None or _output_cache.shape != (
        _mel_basis_cache.shape[0],
        spectogram.shape[1],
    ):
        _output_cache = np.empty(
            (_mel_basis_cache.shape[0], spectogram.shape[1]), dtype=np.float64
        )

    return _dot_mel_hybrid(_mel_basis_cache, spectogram, _output_cache)


_linear_to_mel = _linear_to_mel_hybrid


def _build_mel_basis():
    """
    Build the mel basis for converting linear spectrograms to mel spectrograms.

    Returns:
        np.ndarray: The mel basis.
    """
    assert hp.fmax <= hp.sample_rate // 2
    return librosa.filters.mel(
        sr=hp.sample_rate,
        n_fft=hp.n_fft,
        n_mels=hp.num_mels,
        fmin=hp.fmin,
        fmax=hp.fmax,
    )


def _amp_to_db(x):
    """
    Convert amplitude to decibels.

    Args:
        x (np.ndarray): The amplitude to convert, as a numpy array.

    Returns:
        np.ndarray: The decibels.
    """
    min_level = np.exp(hp.min_level_db / 20 * np.log(10))
    return 20 * np.log10(np.maximum(min_level, x))


def _db_to_amp(x):
    return np.power(10.0, (x) * 0.05)


def _normalize(S):
    """
    Normalize a spectrogram.

    Args:
        S (np.ndarray): The spectrogram to normalize, as a numpy array.

    Returns:
        np.ndarray: The normalized spectrogram.
    """
    if hp.allow_clipping_in_normalization:
        if hp.symmetric_mels:
            return np.clip(
                (2 * hp.max_abs_value) * ((S - hp.min_level_db) / (-hp.min_level_db))
                - hp.max_abs_value,
                -hp.max_abs_value,
                hp.max_abs_value,
            )
        else:
            return np.clip(
                hp.max_abs_value * ((S - hp.min_level_db) / (-hp.min_level_db)),
                0,
                hp.max_abs_value,
            )

    assert S.max() <= 0 and S.min() - hp.min_level_db >= 0
    if hp.symmetric_mels:
        return (2 * hp.max_abs_value) * (
            (S - hp.min_level_db) / (-hp.min_level_db)
        ) - hp.max_abs_value
    else:
        return hp.max_abs_value * ((S - hp.min_level_db) / (-hp.min_level_db))


def _denormalize(D):
    """
    Denormalize a spectrogram.

    Args:
        D: spectrogram to denormalize

    Returns:
        denormalized spectrogram
    """
    if hp.allow_clipping_in_normalization:
        if hp.symmetric_mels:
            return (
                (np.clip(D, -hp.max_abs_value, hp.max_abs_value) + hp.max_abs_value)
                * -hp.min_level_db
                / (2 * hp.max_abs_value)
            ) + hp.min_level_db
        else:
            return (
                np.clip(D, 0, hp.max_abs_value) * -hp.min_level_db / hp.max_abs_value
            ) + hp.min_level_db

    if hp.symmetric_mels:
        return (
            (D + hp.max_abs_value) * -hp.min_level_db / (2 * hp.max_abs_value)
        ) + hp.min_level_db
    else:
        return (D * -hp.min_level_db / hp.max_abs_value) + hp.min_level_db
