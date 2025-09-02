import librosa
import numpy as np

def extract_mfcc(audio_path: str, sr: int = 22050, n_mfcc: int = 13) -> np.ndarray:
    """
    Extract MFCC features from an audio file.

    Args:
        audio_path (str): path to audio file
        sr (int): sampling rate
        n_mfcc (int): number of MFCC coefficients

    Returns:
        np.ndarray: MFCC features (shape: [n_mfcc, frames])
    """
    y, sr = librosa.load(audio_path, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc

def extract_mel_spectrogram(audio_path: str, sr: int = 22050, n_mels: int = 128) -> np.ndarray:
    """
    Extract Mel spectrogram from an audio file.

    Args:
        audio_path (str): path to audio file
        sr (int): sampling rate
        n_mels (int): number of Mel bands

    Returns:
        np.ndarray: Mel spectrogram (shape: [n_mels, frames])
    """
    y, sr = librosa.load(audio_path, sr=sr)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    return mel_spec_db
