"""Audio processing functions."""

import numpy as np
import librosa
import scipy.signal
from scipy.ndimage import binary_dilation
from typing import List, Tuple


def load_audio(audio_path: str, sr: int = 22050) -> Tuple[np.ndarray, int]:
    """Load audio file and return audio array and sample rate."""
    audio, sample_rate = librosa.load(audio_path, sr=sr)
    return audio, sample_rate


def save_audio(file_path: str, audio: np.ndarray, sr: int) -> None:
    """Save audio array to file."""
    import soundfile as sf
    sf.write(file_path, audio, sr)


def bandpass_filter(audio: np.ndarray, sample_rate: int, 
                   freq_min: int = 2000, freq_max: int = 5000,
                   order: int = 6) -> np.ndarray:
    """Apply bandpass filter to isolate frequency range."""
    # Normalize frequencies to Nyquist frequency
    nyquist = sample_rate / 2
    low = freq_min / nyquist
    high = freq_max / nyquist
    
    # Design Butterworth bandpass filter
    b, a = scipy.signal.butter(order, [low, high], btype='band')
    
    # Apply filter
    filtered_audio = scipy.signal.filtfilt(b, a, audio)
    
    return filtered_audio


def detect_calls(audio: np.ndarray, sample_rate: int,
                frame_length: int = 2048, hop_length: int = 512,
                mad_multiplier: float = 2.0, min_duration: float = 0.4,
                max_gap: float = 0.08,) -> List[Tuple[float, float]]:
    """Detect calls using adaptive median + MAD threshold."""
    # Calculate frame-wise energy
    energy = librosa.feature.rms(y=audio, 
                                frame_length=frame_length, 
                                hop_length=hop_length)[0]
    
    # Normalize energy
    energy = energy / np.max(energy)
    
    # Calculate adaptive threshold using median + MAD
    median_energy = np.median(energy)
    mad = np.median(np.abs(energy - median_energy))
    energy_threshold = median_energy + mad_multiplier * mad
    
    # Ensure threshold is within reasonable bounds
    energy_threshold = np.clip(energy_threshold, 0.01, 0.9)
    
    # Create binary mask for energy above threshold
    energy_mask = energy > energy_threshold
    
    # Fill small gaps
    gap_frames = int(max_gap * sample_rate / hop_length)
    if gap_frames > 0:
        energy_mask = binary_dilation(energy_mask, iterations=gap_frames)
    
    # Convert frame indices to time
    times = librosa.frames_to_time(np.arange(len(energy)), 
                                  sr=sample_rate, 
                                  hop_length=hop_length)
    
    # Find continuous regions
    calls = []
    in_call = False
    start_time = None

    noise_floor = np.percentile(energy, 10)  # 10th percentile as noise estimate
    snr_threshold_db = 4

    for i, active in enumerate(energy_mask):
        if active and not in_call:
            start_time = times[i]
            start_idx = i
            in_call = True
        elif not active and in_call:
            end_time = times[i-1]
            end_idx = i-1
            duration = end_time - start_time

            if duration >= min_duration:
                region_energy = energy[start_idx:end_idx+1]
                peak = np.max(region_energy)
                snr_db = 10 * np.log10(peak / (noise_floor + 1e-8))
                if snr_db >= snr_threshold_db:
                    calls.append((start_time, end_time))

            in_call = False
    
    return calls


def crop_calls(audio: np.ndarray, sample_rate: int,
               call_times: List[Tuple[float, float]],
               padding: float = 0.1) -> List[np.ndarray]:
    """Crop audio segments containing detected calls."""
    cropped_calls = []
    audio_length = len(audio) / sample_rate
    
    for start_time, end_time in call_times:
        # Add padding
        padded_start = max(0, start_time - padding)
        padded_end = min(audio_length, end_time + padding)
        
        # Convert to sample indices
        start_sample = int(padded_start * sample_rate)
        end_sample = int(padded_end * sample_rate)
        
        # Extract segment
        segment = audio[start_sample:end_sample]
        
        # Only keep non-empty segments
        if len(segment) > 0:
            cropped_calls.append(segment)
    
    return cropped_calls


def spectral_subtraction(audio: np.ndarray, sr: int = 22050,
                        noise_duration: float = 0.1, noise_factor: float = 2.0,
                        n_fft: int = 1024, hop_length: int = 256) -> np.ndarray:
    """Remove background noise using spectral subtraction."""
    # Compute STFT
    stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(stft)
    phase = np.angle(stft)
    
    # Convert noise duration to frames
    noise_frames = int(noise_duration * sr / hop_length)
    
    # Clamp to available frames (in case audio is shorter than 2 * noise_duration)
    noise_frames = min(noise_frames, magnitude.shape[1] // 2)
    
    # Estimate noise from first/last noise_duration seconds
    noise_start = magnitude[:, :noise_frames]
    noise_end = magnitude[:, -noise_frames:]
    noise_spectrum = np.mean(np.concatenate([noise_start, noise_end], axis=1),
                           axis=1, keepdims=True)
    
    # Subtract noise spectrum
    clean_magnitude = magnitude - noise_factor * noise_spectrum
    
    # Apply spectral floor (prevent over-subtraction)
    floor = 0.1 * noise_spectrum
    clean_magnitude = np.maximum(clean_magnitude, floor)
    
    # Reconstruct audio
    clean_stft = clean_magnitude * np.exp(1j * phase)
    return librosa.istft(clean_stft) 