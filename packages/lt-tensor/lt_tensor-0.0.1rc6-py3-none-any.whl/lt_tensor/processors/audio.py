__all__ = [
    "AudioProcessor",
    "AudioProcessorConfig",
    "convert_to_float16",
    "MelLoss",
    "MultiMelScaleLoss",
]

import warnings
import librosa
import numpy as np
from lt_utils.common import *
from lt_tensor.common import *
from lt_utils.misc_utils import default
from lt_utils.type_utils import is_file

import torch.nn.functional as F
from lt_utils.file_ops import FileScan
from librosa.filters import mel as _mel_filter_bank
from lt_tensor.misc_utils import get_window, to_numpy, to_tensor

DEFAULT_DEVICE = torch.tensor([0]).device


def convert_to_float16(audio: Tensor):
    """Convert and audio from float32 to float16"""
    if audio.dtype in [torch.float16, torch.bfloat16]:
        return audio
    data = audio / audio.abs().max()
    data = data * 32767
    return data.half()


class AudioProcessorConfig(ModelConfig):
    sample_rate: int = 24000
    n_mels: int = 80
    n_fft: int = 1024
    win_length: int = 1024
    hop_length: int = 256
    f_min: float = 0
    f_max: Optional[float] = None
    center: bool = True
    std: int = 4
    mean: int = -4
    n_iter: int = 32
    normalized: bool = False
    onesided: Optional[bool] = None
    n_stft: int = None
    normalize_mel: bool = True
    window_type: Literal["hann", "hamming"] = "hann"

    def __init__(
        self,
        sample_rate: int = 24000,
        n_mels: int = 80,
        n_fft: int = 1024,
        win_length: Optional[int] = None,
        hop_length: Optional[int] = None,
        f_min: float = 0,
        f_max: Optional[float] = None,
        center: bool = True,
        std: int = 4,
        mean: int = -4,
        normalized: bool = False,
        onesided: Optional[bool] = None,
        normalize_mel: bool = False,
        window_type: Literal["hann", "hamming"] = "hann",
        *args,
        **kwargs,
    ):
        assert window_type in [
            "hann",
            "hamming",
        ], f"Invalid window type {window_type}. It must be either 'hann' or 'hamming'"
        settings = {
            "sample_rate": sample_rate,
            "n_mels": n_mels,
            "n_fft": n_fft,
            "win_length": win_length,
            "hop_length": hop_length,
            "f_min": f_min,
            "f_max": f_max,
            "center": center,
            "std": std,
            "mean": mean,
            "normalized": normalized,
            "onesided": onesided,
            "normalize_mel": normalize_mel,
            "window_type": window_type,
        }
        super().__init__(**settings)
        self.post_process()

    def post_process(self):
        self.n_stft = self.n_fft // 2 + 1
        # some functions needs this to be a non-zero or not None value.
        self.default_f_min = max(self.f_min, (self.sample_rate / (self.n_fft - 1)) * 2)
        self.default_f_max = min(
            default(self.f_max, self.sample_rate // 2), self.sample_rate // 2
        )
        self.hop_length = default(self.hop_length, self.n_fft // 4)
        self.win_length = default(self.win_length, self.n_fft)


class AudioProcessor(Model):
    def __init__(
        self,
        config: Union[AudioProcessorConfig, Dict[str, Any]] = AudioProcessorConfig(),
    ):
        super().__init__()
        assert isinstance(config, (AudioProcessorConfig, dict))
        self.cfg = (
            config
            if isinstance(config, AudioProcessorConfig)
            else AudioProcessorConfig(**config)
        )

        self._mel_padding = (self.cfg.n_fft - self.cfg.hop_length) // 2
        self.window = nn.Parameter(
            get_window(
                self.cfg.win_length,
                self.cfg.window_type,
                requires_grad=False,
            ),
            requires_grad=False,
        )
        self.mel_filter_bank = nn.Parameter(
            self.get_mel_filterbank(
                sample_rate=self.cfg.sample_rate,
                n_fft=self.cfg.n_fft,
                n_mels=self.cfg.n_mels,
                f_min=self.cfg.f_min,
                f_max=self.cfg.f_max,
            ),
            requires_grad=False,
        )

    @staticmethod
    def normal_minmax(x: Tensor, min_val: float = -1.0, max_val: float = 1.0) -> Tensor:
        """Scales tensor to [min_val, max_val] range."""
        x_min, x_max = x.min(), x.max()
        return (x - x_min) / (x_max - x_min + 1e-8) * (max_val - min_val) + min_val

    def get_mel_filterbank(
        self,
        sample_rate: Optional[int] = None,
        n_fft: Optional[int] = None,
        n_mels: Optional[int] = None,
        f_min: Optional[float] = None,
        f_max: Optional[float] = None,
    ):
        return torch.from_numpy(
            _mel_filter_bank(
                sr=default(sample_rate, self.cfg.sample_rate),
                n_fft=default(n_fft, self.cfg.n_fft),
                n_mels=default(n_mels, self.cfg.n_mels),
                fmin=default(f_min, self.cfg.f_min),
                fmax=default(f_max, self.cfg.f_max),
            )
        ).to(device=self.device)

    def get_window(self, win_length: Optional[int] = None):
        if win_length is None or win_length == self.cfg.win_length:
            return self.window
        return torch.hann_window(
            default(win_length, self.cfg.win_length),
            device=self.device,
            requires_grad=False,
        )

    def log_norm(
        self,
        entry: Tensor,
        eps: float = 1e-5,
        mean: Optional[Number] = None,
        std: Optional[Number] = None,
    ) -> Tensor:
        mean = default(mean, self.cfg.mean)
        std = default(std, self.cfg.std)
        return (torch.log(eps + entry.unsqueeze(0)) - mean) / std

    def range_norm(self, x, C=1, clip_val=1e-5):
        return torch.log(torch.clamp(x, min=clip_val) * C)

    def compute_mel(
        self,
        wave: Tensor,
        norm: Optional[bool] = None,
        norm_fn: Callable[[Tensor], Tensor] = lambda x: torch.log(
            torch.clamp(x, min=1e-5) * 1
        ),
        eps: float = 1e-5,
    ) -> Tensor:
        if wave.ndim == 1:
            wave = wave.unsqueeze(0)
        wave = torch.nn.functional.pad(
            wave.unsqueeze(1),
            (self._mel_padding, self._mel_padding),
            mode="reflect",
        ).squeeze(1)

        if wave.device != self.device:
            wave = wave.to(device=self.device)

        spec = torch.stft(
            wave,
            self.cfg.n_fft,
            hop_length=self.cfg.hop_length,
            win_length=self.cfg.win_length,
            window=self.window,
            center=False,
            pad_mode="reflect",
            normalized=False,
            onesided=True,
            return_complex=True,
        )
        spec = torch.sqrt(torch.view_as_real(spec).pow(2).sum(-1) + 1e-12)
        results = torch.matmul(self.mel_filter_bank, spec)
        if default(norm, self.cfg.normalize_mel):
            return norm_fn(results).squeeze()
        return results.squeeze()

    def convert_to_float16(self, audio: Tensor):
        audio = to_tensor(audio)
        return convert_to_float16(audio)

    def compute_pitch(
        self,
        audio: Tensor,
        *,
        sr: Optional[float] = None,
        fmin: int = 65,
        fmax: float = 2093,
        win_length: int = 30,
        frame_time: float = 10 ** (-2),
    ) -> Tensor:
        sr = default(sr, self.cfg.sample_rate)
        from torchaudio.functional import detect_pitch_frequency

        return detect_pitch_frequency(
            audio,
            sample_rate=sr,
            frame_time=frame_time,
            win_length=win_length,
            freq_low=fmin,
            freq_high=fmax,
        ).squeeze()

    def pitch_shift(
        self,
        audio: Tensor,
        sample_rate: Optional[int] = None,
        n_steps: float = 2.0,
        bins_per_octave: int = 12,
        res_type: Literal["soxr_vhq", "soxr_hq", "soxr_mq", "soxr_lq"] = "soxr_vhq",
        scale: bool = False,
    ) -> Tensor:
        """
        Shifts the pitch of an audio tensor by `n_steps` semitones.

        Args:
            audio (Tensor): Tensor of shape (B, T) or (T,)
            sample_rate (int, optional): Sample rate of the audio. Will use the class sample rate if unset.
            n_steps (float): Number of semitones to shift. Can be negative.
            res_type (Literal["soxr_vhq", "soxr_hq", "soxr_mq", "soxr_lq"]): Resample type. soxr Very high-, High-, Medium-, Low-quality FFT-based bandlimited interpolation. Defaults to 'soxr_vhq'
            scale (bool): Scale the resampled signal so that ``y`` and ``y_hat`` have approximately equal total energy.
        Returns:
            Tensor: Pitch-shifted audio.
        """
        librosa.decompose.stft
        src_device = audio.device
        src_dtype = audio.dtype
        audio = audio.squeeze()
        sample_rate = default(sample_rate, self.cfg.sample_rate)

        def _shift_one(wav: Tensor):
            wav_np = self.to_numpy_safe(wav)
            shifted_np = librosa.effects.pitch_shift(
                wav_np,
                sr=sample_rate,
                n_steps=n_steps,
                bins_per_octave=bins_per_octave,
                res_type=res_type,
                scale=scale,
            )
            return torch.from_numpy(shifted_np)

        if audio.ndim == 1:
            return _shift_one(audio).to(device=src_device, dtype=src_dtype)
        return torch.stack([_shift_one(a) for a in audio]).to(
            device=src_device, dtype=src_dtype
        )

    def from_numpy(
        self,
        array: np.ndarray,
        device: Optional[torch.device] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> Tensor:
        converted = torch.from_numpy(array)
        if device is None:
            device = self.device
        return converted.to(device=device, dtype=dtype)

    def from_numpy_batch(
        self,
        arrays: List[np.ndarray],
        device: Optional[torch.device] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> Tensor:
        stacked = torch.stack([torch.from_numpy(x) for x in arrays])
        if device is None:
            device = self.device
        return stacked.to(device=device, dtype=dtype)

    def to_numpy_safe(self, tensor: Union[Tensor, np.ndarray]) -> np.ndarray:
        if isinstance(tensor, np.ndarray):
            return tensor
        return tensor.detach().to(DEFAULT_DEVICE).numpy(force=True)

    def interpolate(
        self,
        wave: Tensor,
        target_len: int,
        mode: Literal[
            "nearest",
            "linear",
            "bilinear",
            "bicubic",
            "trilinear",
            "area",
            "nearest-exact",
        ] = "nearest",
        align_corners: Optional[bool] = None,
        scale_factor: Optional[list[float]] = None,
        recompute_scale_factor: Optional[bool] = None,
        antialias: bool = False,
    ) -> Tensor:
        """
        The modes available for upsampling are: `nearest`, `linear` (3D-only),
        `bilinear`, `bicubic` (4D-only), `trilinear` (5D-only)
        """
        T = wave.shape[-1]
        B = 1 if wave.ndim < 2 else wave.shape[0]
        return F.interpolate(
            wave.view(B, 1, T),
            size=target_len,
            mode=mode,
            align_corners=align_corners,
            scale_factor=scale_factor,
            recompute_scale_factor=recompute_scale_factor,
            antialias=antialias,
        )

    def sp_istft(
        self,
        spec: Tensor,
        phase: Tensor,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        length: Optional[int] = None,
        center: bool = True,
        normalized: Optional[bool] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = False,
    ) -> Tensor:
        """Util for models that needs to reconstruct the audio using istft (namely istft based models)"""
        window = (
            torch.hann_window(win_length, device=spec.device)
            if win_length is not None and win_length != self.cfg.win_length
            else self.window.to(spec.device)
        )
        if not phase.is_complex():
            phase = torch.exp(phase * 1j)
        inp = spec * phase
        return torch.istft(
            inp,
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=window,
            center=center,
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            length=length,
            return_complex=return_complex,
        )

    def istft(
        self,
        wave: Tensor,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        length: Optional[int] = None,
        center: bool = True,
        normalized: Optional[bool] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = False,
    ) -> Tensor:
        window = (
            torch.hann_window(win_length, device=wave.device)
            if win_length is not None and win_length != self.cfg.win_length
            else self.window.to(wave.device)
        )
        if not torch.is_complex(wave):
            wave = wave * 1j
        return torch.istft(
            wave,
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=window,
            center=center,
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            length=length,
            return_complex=return_complex,
        )

    def stft(
        self,
        wave: Tensor,
        center: bool = True,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        normalized: Optional[bool] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = True,
    ) -> Tensor:

        window = (
            torch.hann_window(win_length, device=wave.device)
            if win_length is not None and win_length != self.cfg.win_length
            else self.window.to(wave.device)
        )

        results = torch.stft(
            input=wave,
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=window,
            center=center,
            pad_mode="reflect",
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            return_complex=True,  # always, then if we need a not complex type we use view as real.
        )
        if not return_complex:
            return torch.view_as_real(results)
        return results

    def loss_fn(self, inputs: Tensor, target: Tensor, ld: float = 1.0):
        if target.device != inputs.device:
            target = target.to(inputs.device)
        return (
            F.l1_loss(
                self.compute_mel(inputs), self.compute_mel(target.view_as(inputs))
            )
            * ld
        )

    def noise_reduction(
        self,
        audio: Union[Tensor, np.ndarray],
        noise_decrease: float = 0.25,
        n_fft: Optional[int] = None,
        win_length: Optional[int] = None,
        hop_length: Optional[int] = None,
        sample_rate: Optional[float] = None,
    ):
        import noisereduce as nr

        device = audio.device if isinstance(audio, Tensor) else None
        clear_audio = nr.reduce_noise(
            y=self.to_numpy_safe(audio),
            sr=default(sample_rate, self.cfg.sample_rate),
            n_fft=default(n_fft, self.cfg.n_fft),
            win_length=default(win_length, self.cfg.win_length),
            hop_length=default(hop_length, self.cfg.hop_length),
            prop_decrease=min(1.0, (max(noise_decrease, 1e-3))),
        )
        return self.from_numpy(clear_audio, device=device)

    def normalize_stft(
        self,
        wave: Tensor,
        length: Optional[int] = None,
        center: bool = True,
        n_fft: Optional[int] = None,
        hop_length: Optional[int] = None,
        win_length: Optional[int] = None,
        normalized: Optional[bool] = None,
        onesided: Optional[bool] = None,
        return_complex: bool = False,
    ) -> Tensor:
        window = (
            torch.hann_window(win_length, device=wave.device)
            if win_length is not None and win_length != self.cfg.win_length
            else self.window.to(wave.device)
        )
        spectrogram = torch.stft(
            input=wave,
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=window,
            center=center,
            pad_mode="reflect",
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            return_complex=True,
        )
        return torch.istft(
            spectrogram
            * torch.full(
                spectrogram.size(),
                fill_value=1,
                device=spectrogram.device,
            ),
            n_fft=default(n_fft, self.cfg.n_fft),
            hop_length=default(hop_length, self.cfg.hop_length),
            win_length=default(win_length, self.cfg.win_length),
            window=self.window,
            length=length,
            center=center,
            normalized=default(normalized, self.cfg.normalized),
            onesided=default(onesided, self.cfg.onesided),
            return_complex=return_complex,
        )

    def normalize_audio(
        self,
        wave: Tensor,
        top_db: Optional[float] = None,
        norm: Optional[float] = np.inf,
        norm_axis: int = 0,
        norm_threshold: Optional[float] = None,
        norm_fill: Optional[bool] = None,
        ref: float | Callable[[np.ndarray], Any] = np.max,
    ):
        if isinstance(wave, Tensor):
            wave = self.to_numpy_safe(wave)
        if top_db is not None:
            wave, _ = librosa.effects.trim(wave, top_db=top_db, ref=ref)
        wave = librosa.util.normalize(
            wave,
            norm=norm,
            axis=norm_axis,
            threshold=norm_threshold,
            fill=norm_fill,
        )
        results = torch.from_numpy(wave).float().unsqueeze(0).to(self.device)
        return self.normalize_stft(results)

    def load_audio(
        self,
        path: PathLike,
        librosa_normalizer: bool = False,
        other_normalizer: Optional[Callable[[Tensor], Tensor]] = None,
        min_max_norm: bool = False,
        min_norm: float = -1.0,
        max_norm: float = 1.0,
        output_dtype: Literal["float32", "float16"] = "float32",
        apply_noise_reduction: bool = False,
        noise_reduction_strength: float = 0.2,
        *,
        top_db: Optional[float] = None,
        mono: bool = True,
        sample_rate: Optional[float] = None,
        duration: Optional[float] = None,
        offset: float = 0.0,
        dtype: Any = np.float32,
        res_type: Literal["soxr_vhq", "soxr_hq", "soxr_mq", "soxr_lq"] = "soxr_vhq",
        fix: bool = True,
        scale: bool = False,
        axis: int = -1,
        norm: Optional[float] = np.inf,
        norm_axis: int = 0,
        norm_threshold: Optional[float] = None,
        norm_fill: Optional[bool] = None,
        ref: float | Callable[[np.ndarray], Any] = np.max,
    ) -> Tensor:
        assert output_dtype in ["float32", "float16"]
        is_file(path, True)
        sample_rate = default(sample_rate, self.cfg.sample_rate)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)
            wave, sr = librosa.load(
                str(path),
                sr=sample_rate,
                mono=mono,
                offset=offset,
                duration=duration,
                dtype=dtype,
                res_type=res_type,
            )
        if sr != sample_rate:
            wave = librosa.resample(
                wave,
                orig_sr=sr,
                target_sr=sample_rate,
                res_type=res_type,
                fix=fix,
                scale=scale,
                axis=axis,
            )
        if top_db is not None:
            wave, _ = librosa.effects.trim(wave, top_db=top_db, ref=ref)
        if librosa_normalizer:
            wave = librosa.util.normalize(
                wave,
                norm=norm,
                axis=norm_axis,
                threshold=norm_threshold,
                fill=norm_fill,
            )
        if apply_noise_reduction:
            wave = self.noise_reduction(wave, noise_reduction_strength)
        results = torch.from_numpy(wave)
        results = self.normalize_stft(
            results.view(1, results.shape[-1]).to(
                device=self.device, dtype=torch.float32
            )
        )

        if other_normalizer is not None:
            results = other_normalizer(results)

        if output_dtype == "float16":
            results = convert_to_float16(results)
        if min_max_norm:
            results = self.normal_minmax(results, min_norm, max_norm)

        return results.view(1, results.shape[-1])

    def find_audios(
        self,
        path: PathLike,
        additional_extensions: List[str] = [],
        maximum: int | None = None,
    ):
        extensions = ["*.wav", "*.aac", "*.m4a", "*.mp3"]
        extensions.extend(
            [
                x if "*" in x else f"*{x}"
                for x in additional_extensions
                if isinstance(x, str)
            ]
        )
        return FileScan.files(
            path,
            extensions,
            maximum,
        )

    def collate_mel(self, mels: List[Tensor], same_size: bool = False):
        n_mels = mels[0].shape[-1]
        B = len(mels)
        if same_size:
            return torch.stack(mels, dim=0).view(B, n_mels, mels[0].shape[-1])
        largest = max([a.shape[-1] for a in mels])
        return torch.stack(
            [F.pad(x, (0, largest - x.shape[-1]), value=0.0) for x in mels], dim=0
        ).view(B, n_mels, mels[0].shape[-1])

    def collate_wave(self, waves: List[Tensor], same_size: bool = False):
        B = len(waves)
        if same_size:
            largest = waves[0].shape[-1]
            return torch.stack(waves, dim=0).view(B, waves[0].shape[-1])

        largest = max([a.shape[-1] for a in waves])
        return torch.stack(
            [F.pad(x, (0, largest - x.shape[-1]), value=0.0) for x in waves], dim=0
        ).view(B, largest)


class MelLoss(Model):
    def __init__(
        self,
        sample_rate: int = 24000,
        n_mels: int = 80,
        window_length: int = 1024,
        n_fft: int = 1024,
        hop_length: int = 256,
        f_min: float = 0,
        f_max: Optional[float] = None,
        loss_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
        center: bool = False,
        power: float = 1.0,
        normalized: bool = False,
        pad_mode: str = "reflect",
        onesided: Optional[bool] = None,
        weight: float = 1.0,
    ):
        super().__init__()
        import torchaudio

        self.mel_fn = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            center=center,
            onesided=onesided,
            normalized=normalized,
            power=power,
            pad_mode=pad_mode,
            n_fft=n_fft,
            hop_length=hop_length,
            win_length=window_length,
            n_mels=n_mels,
            f_min=f_min,
            f_max=f_max,
        )
        self.loss_fn = loss_fn
        self.weight = weight

    def forward(self, wave: Tensor, target: Tensor):
        x_mels = self.mel_fn.forward(wave)
        y_mels = self.mel_fn.forward(target)
        return self.loss_fn(x_mels, y_mels) * self.weight

    def _forward(
        self,
        inp: Tensor,
        out: Tensor,
        previous_loss: Optional[Tensor] = None,
    ):
        if previous_loss is None:
            return self.forward(inp, out)
        previous_loss += self.forward(inp, out)
        return previous_loss


def mms_loss_config(option: int = 0):
    match option:
        case 0:
            return dict(
                n_mels=[20, 40, 80, 160],
                window_lengths=[256, 512, 1024, 2048],
                n_ffts=[256, 512, 1024, 2048],
                hops=[64, 128, 256, 512],
                f_min=[0, 0, 0, 0],
                f_max=[None, None, None, None],
            )
        case 1:
            return dict(
                n_mels=[96, 128, 256],
                window_lengths=[512, 1024, 2048],
                n_ffts=[512, 1024, 2048],
                hops=[128, 256, 512],
                f_min=[0, 0, 0],
                f_max=[None, None, None],
            )
        case _:
            return dict(
                n_mels=[5, 10, 20, 40, 80, 160, 320],
                window_lengths=[32, 64, 128, 256, 512, 1024, 2048],
                n_ffts=[32, 64, 128, 256, 512, 1024, 2048],
                hops=[8, 16, 32, 64, 128, 256, 512],
                f_min=[0, 0, 0, 0, 0, 0, 0],
                f_max=[None, None, None, None, None, None, None],
            )


class MultiMelScaleLoss(Model):
    def __init__(
        self,
        sample_rate: int = 24000,
        n_mels: List[int] = [20, 40, 80, 160],
        window_lengths: List[int] = [256, 512, 1024, 2048],
        n_ffts: List[int] = [256, 512, 1024, 2048],
        hops: List[int] = [64, 128, 256, 512],
        f_min: List[float] = [0, 0, 0, 0],
        f_max: List[Optional[float]] = [None, None, None, None],
        loss_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
        center: bool = False,
        power: float = 1.0,
        normalized: bool = False,
        pad_mode: str = "reflect",
        onesided: Optional[bool] = None,
        weight: float = 1.0,
    ):
        super().__init__()
        assert (
            len(n_mels)
            == len(window_lengths)
            == len(n_ffts)
            == len(hops)
            == len(f_min)
            == len(f_max)
        )
        self._setup_mels(
            sample_rate,
            n_mels,
            window_lengths,
            n_ffts,
            hops,
            f_min,
            f_max,
            center,
            power,
            normalized,
            pad_mode,
            onesided,
            loss_fn,
            weight,
        )

    @classmethod
    def from_preset_cfg(
        cls,
        sample_rate: int = 24000,
        center: bool = False,
        power: float = 1.0,
        normalized: bool = False,
        pad_mode: str = "reflect",
        onesided: Optional[bool] = None,
        weight: float = 1.0,
        option: int = 0,
    ):
        """Initialize MultiMelScaleLoss, with a predefined config.

        Args:
            option (int, optional): Choose between 0 to 3, more information in 'options'. Defaults to 0.

        Options:
            0:
                ```
                    n_mels=[20, 40, 80, 160],
                    window_lengths=[256, 512, 1024, 2048],
                    n_ffts=[256, 512, 1024, 2048],
                    hops=[64, 128, 256, 512],
                    f_min=[0, 0, 0, 0],
                    f_max=[None, None, None, None],
                ```
            1:
                ```
                    n_mels=[96, 128, 256],
                    window_lengths=[512, 1024, 2048],
                    n_ffts=[512, 1024, 2048],
                    hops=[128, 256, 512],
                    f_min=[0, 0, 0],
                    f_max=[None, None, None],
                ```
            2:
                ```
                    n_mels=[5, 10, 20, 40, 80, 160, 320],
                    window_lengths=[32, 64, 128, 256, 512, 1024, 2048],
                    n_ffts=[32, 64, 128, 256, 512, 1024, 2048],
                    hops=[8, 16, 32, 64, 128, 256, 512],
                    f_min=[0, 0, 0, 0, 0, 0, 0],
                    f_max=[None, None, None, None, None, None, None],
                ```
            3:
                TODO: Implement a randomized function to create the sequence that does not results in empty bands.

        Returns:
            _type_: _description_
        """
        match option:
            case 0:
                kwargs = dict(
                    n_mels=[20, 40, 80, 160],
                    window_lengths=[256, 512, 1024, 2048],
                    n_ffts=[256, 512, 1024, 2048],
                    hops=[64, 128, 256, 512],
                    f_min=[0, 0, 0, 0],
                    f_max=[None, None, None, None],
                )
            case 1:
                kwargs = dict(
                    n_mels=[96, 128, 256],
                    window_lengths=[512, 1024, 2048],
                    n_ffts=[512, 1024, 2048],
                    hops=[128, 256, 512],
                    f_min=[0, 0, 0],
                    f_max=[None, None, None],
                )
            case _:  # 2:
                kwargs = dict(
                    n_mels=[5, 10, 20, 40, 80, 160, 320],
                    window_lengths=[32, 64, 128, 256, 512, 1024, 2048],
                    n_ffts=[32, 64, 128, 256, 512, 1024, 2048],
                    hops=[8, 16, 32, 64, 128, 256, 512],
                    f_min=[0, 0, 0, 0, 0, 0, 0],
                    f_max=[None, None, None, None, None, None, None],
                )
            # case _:
            #     pass
        return cls(
            sample_rate=sample_rate,
            center=center,
            power=power,
            normalized=normalized,
            pad_mode=pad_mode,
            onesided=onesided,
            weight=weight,
            **kwargs,
        )

    def _setup_mels(
        self,
        sample_rate: int,
        n_mels: List[int],
        window_lengths: List[int],
        n_ffts: List[int],
        hops: List[int],
        f_min: List[float],
        f_max: List[Optional[float]],
        center: bool,
        power: float,
        normalized: bool,
        pad_mode: str,
        onesided: Optional[bool],
        loss_fn: Callable,
        weight: float,
    ):
        assert (
            len(n_mels)
            == len(window_lengths)
            == len(n_ffts)
            == len(hops)
            == len(f_min)
            == len(f_max)
        )
        _mel_kwargs = dict(
            sample_rate=sample_rate,
            center=center,
            onesided=onesided,
            normalized=normalized,
            power=power,
            pad_mode=pad_mode,
            loss_fn=loss_fn,
            weight=weight,
        )

        self.mel_losses: List[MelLoss] = nn.ModuleList(
            [
                MelLoss(
                    **_mel_kwargs,
                    n_fft=n_fft,
                    hop_length=hop,
                    window_length=win,
                    n_mels=mel,
                    f_min=fmin,
                    f_max=fmax,
                )
                for mel, win, n_fft, hop, fmin, fmax in zip(
                    n_mels, window_lengths, n_ffts, hops, f_min, f_max
                )
            ]
        )

    def forward(self, input_wave: Tensor, target_wave: Tensor) -> Tensor:
        loss = None
        for i, loss_fn in enumerate(self.mel_losses):
            if i == 0:
                loss = loss_fn.forward(input_wave, target_wave)
            else:
                loss += loss_fn.forward(input_wave, target_wave)
        return loss
