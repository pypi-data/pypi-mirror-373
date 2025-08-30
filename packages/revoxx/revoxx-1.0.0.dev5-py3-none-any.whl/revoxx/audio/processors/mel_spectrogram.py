"""Mel spectrogram processor and configuration."""

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import librosa

from .processor_base import AudioProcessor
from ...constants import AudioConstants
from ...utils.audio_utils import normalize_audio


@dataclass(frozen=True)
class MelConfig:
    """Configuration for mel spectrogram parameters.

    This class manages mel spectrogram parameters based on sample rate
    and provides methods to calculate adaptive parameters.
    """

    # Base parameters (for 48kHz reference)
    BASE_SAMPLE_RATE: int = 48000
    BASE_FMIN: int = 50
    BASE_FMAX: int = 24000
    BASE_N_MELS: int = 96

    # Computed base range
    BASE_FREQ_RANGE: int = BASE_FMAX - BASE_FMIN  # 23950

    # Limits
    MIN_N_MELS: int = 80
    MAX_N_MELS: int = 110

    @classmethod
    def calculate_params(cls, sample_rate: int, fmin: float) -> dict:
        """Calculate mel parameters for a given sample rate.

        Args:
            sample_rate: Target sample rate in Hz
            fmin: Minimum frequency in Hz

        Returns:
            Dictionary with calculated parameters:
                - nyquist: Nyquist frequency
                - fmax: Maximum frequency (limited by Nyquist)
                - freq_range: Frequency range (fmax - fmin)
                - scale_factor: Scaling factor relative to base
                - n_mels: Number of mel bins (adaptive)
        """
        nyquist = sample_rate / 2

        # Adaptive fmax calculation to prevent empty mel filters
        if sample_rate <= 48000:
            # For standard rates, use BASE_FMAX or Nyquist
            fmax = min(nyquist, cls.BASE_FMAX)
        else:
            # For high sample rates, use 48% of sample rate to ensure valid mel filters
            # This prevents empty filter banks at frequencies like 192kHz
            fmax = sample_rate * 0.48

        # Ensure fmax doesn't exceed Nyquist (with small margin for numerical stability)
        fmax = min(fmax, nyquist - 1)

        freq_range = fmax - fmin

        # Calculate scale factor and adjust n_mels more conservatively for high rates
        if sample_rate <= 48000:
            scale_factor = freq_range / cls.BASE_FREQ_RANGE
            n_mels = max(
                cls.MIN_N_MELS, min(cls.MAX_N_MELS, int(cls.BASE_N_MELS * scale_factor))
            )
        else:
            # For high sample rates, use logarithmic scaling to prevent too many mel bins
            # This ensures mel filters have enough frequency coverage
            scale_factor = np.log2(sample_rate / cls.BASE_SAMPLE_RATE)
            # Keep n_mels moderate to ensure each filter has enough frequency range
            n_mels = min(
                int(cls.BASE_N_MELS * (1 + scale_factor * 0.25)), cls.MAX_N_MELS
            )

        return {
            "nyquist": nyquist,
            "fmax": fmax,
            "freq_range": freq_range,
            "scale_factor": scale_factor,
            "n_mels": n_mels,
        }


class MelSpectrogramProcessor(AudioProcessor[Tuple[np.ndarray, Optional[float]]]):
    """Processes audio to generate mel spectrograms.

    This processor converts audio signals to mel-scale spectrograms,
    which provide a perceptually-motivated frequency representation
    of audio. Mel spectrograms are commonly used for speech visualization
    and analysis.

    The mel scale approximates human auditory perception, with higher
    resolution at lower frequencies where speech information is concentrated.

    Attributes:
        n_fft: FFT window size
        hop_length: Number of samples between successive frames
        n_mels: Number of mel frequency bins
        fmin: Minimum frequency (Hz)
        fmax: Maximum frequency (Hz)
        mel_filter: Pre-computed mel filterbank matrix
    """

    def __init__(
        self,
        sample_rate: int = AudioConstants.DEFAULT_SAMPLE_RATE,
        n_fft: int = AudioConstants.N_FFT,
        hop_length: int = AudioConstants.HOP_LENGTH,
        n_mels: int = AudioConstants.N_MELS,
        fmin: float = AudioConstants.FMIN,
        fmax: float = AudioConstants.FMAX,
    ):
        """Initialize the mel spectrogram processor.

        Args:
            sample_rate: Audio sample rate in Hz
            n_fft: FFT window size (default: 2048)
            hop_length: Hop between frames (default: 512)
            n_mels: Number of mel bands (default: 80)
            fmin: Minimum frequency in Hz (default: 0)
            fmax: Maximum frequency in Hz (default: 8000)
        """
        super().__init__(sample_rate)
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        self.fmin = fmin
        self.fmax = fmax

        # Pre-compute mel filterbank for efficiency
        # Clamp fmax to Nyquist frequency if needed
        actual_fmax = min(fmax, sample_rate / 2)
        self.mel_filter = librosa.filters.mel(
            sr=sample_rate, n_fft=n_fft, n_mels=n_mels, fmin=fmin, fmax=actual_fmax
        )
        self.actual_fmax = actual_fmax

        # Pre-compute mel frequencies for efficiency
        self.mel_frequencies = librosa.mel_frequencies(
            n_mels=n_mels + 2, fmin=fmin, fmax=actual_fmax
        )[
            1:-1
        ]  # Remove edge bins

    @classmethod
    def create_for(
        cls, sample_rate: int, fmin: float = None
    ) -> Tuple["MelSpectrogramProcessor", int]:
        """Create processor with adaptive parameters for sample rate.

        Args:
            sample_rate: Target sample rate in Hz
            fmin: Minimum frequency (uses MelConfig.BASE_FMIN if None)

        Returns:
            Tuple of (processor, n_mels)
        """
        if fmin is None:
            fmin = MEL_CONFIG.BASE_FMIN

        params = MEL_CONFIG.calculate_params(sample_rate, fmin)
        processor = cls(
            sample_rate=sample_rate,
            n_mels=params["n_mels"],
            fmin=fmin,
            fmax=params["fmax"],
        )
        return processor, params["n_mels"]

    def process(self, audio_data: np.ndarray) -> Tuple[np.ndarray, Optional[float]]:
        """Convert audio frame to mel-scale dB values and detect the highest frequency.

        Processes a single frame of audio data to produce mel-scale
        magnitude values in decibels.

        Args:
            audio_data: Audio frame (n_fft samples)

        Returns:
            Tuple of:
                - np.ndarray: Mel-scale magnitudes in dB (n_mels values)
                - float: Highest frequency with significant energy (Hz) or None

        Note:
            Automatically detects if input is already normalized (max <= 1.0)
            to handle both live recording and loaded audio files correctly.
        """
        # Use centralized normalization function
        audio_norm = normalize_audio(audio_data)

        # Apply window
        windowed = audio_norm * np.hanning(len(audio_norm))

        # Compute FFT
        fft = np.fft.rfft(windowed, n=self.n_fft)
        power = np.abs(fft) ** 2

        # Apply mel filterbank
        mel_power = np.dot(self.mel_filter, power[: self.n_fft // 2 + 1])

        # Convert to dB
        mel_db = AudioConstants.POWER_TO_DB_FACTOR * np.log10(
            mel_power + AudioConstants.DB_REFERENCE
        )

        # Clamp to display range (we cannot visually represent values above 0 dB)
        mel_db = np.clip(mel_db, AudioConstants.DB_MIN, 0)

        # Detect the highest frequency with significant energy
        # Use the raw FFT power spectrum for precise frequency detection
        power_db = AudioConstants.POWER_TO_DB_FACTOR * np.log10(
            power[: self.n_fft // 2 + 1] + AudioConstants.DB_REFERENCE
        )

        # Find the highest frequency above noise floor
        significant_bins = np.where(power_db > AudioConstants.FREQUENCY_NOISE_FLOOR_DB)[
            0
        ]

        if len(significant_bins) > 0:
            highest_bin = significant_bins[-1]
            # Convert bin to frequency
            freq_per_bin = self.sample_rate / self.n_fft
            highest_freq = highest_bin * freq_per_bin
            # Clamp to Nyquist frequency (sample_rate / 2)
            highest_freq = min(float(highest_freq), self.sample_rate / 2)
        else:
            highest_freq = None
        return mel_db, highest_freq


# Global configuration instance
MEL_CONFIG = MelConfig()
