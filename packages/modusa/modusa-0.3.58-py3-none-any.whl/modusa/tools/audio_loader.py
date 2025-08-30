#!/usr/bin/env python3


import soundfile as sf
from scipy.signal import resample
from pathlib import Path
import tempfile
from scipy.signal import resample
from .youtube_downloader import download
from .audio_converter import convert


def load(path, sr=None):
	"""
	Loads audio file from various sources.

	.. code-block:: python
		
		import modusa as ms
		audio_fp = ms.load(
			"https://www.youtube.com/watch?v=lIpw9-Y_N0g",
			sr = None)

	Parameters
	----------
	path: str
		- Path to the audio
		- Youtube URL
	sr: int
		- Sampling rate to load the audio in.

	Return
	------
	np.ndarray
		- Audio signal.
	int
		- Sampling rate of the loaded audio signal.
	title
		- Title of the loaded audio.
		- Filename without extension or YouTube title.
	"""
	
	# Check if the path is YouTube
	if ".youtube." in str(path):
		# Download the audio in temp directory using tempfile module
		with tempfile.TemporaryDirectory() as tmpdir:
			# Download
			audio_fp: Path = download(url=path, content_type="audio", output_dir=Path(tmpdir))
			
			# Convert the audio to ".wav" form for loading
			wav_audio_fp: Path = convert(inp_audio_fp=audio_fp, output_audio_fp=audio_fp.with_suffix(".wav"))
			
			# Load the audio in memory
			audio_data, audio_sr = sf.read(wav_audio_fp)
			title = audio_fp.stem
			
			# Convert to mono if it's multi-channel
			if audio_data.ndim > 1:
				audio_data = audio_data.mean(axis=1)
				
			# Resample if needed
			if sr is not None:
				if audio_sr != sr:
					n_samples = int(len(audio_data) * sr / audio_sr)
					audio_data = resample(audio_data, n_samples)
					audio_sr = sr
		
	else:
		# Check if the file exists
		fp = Path(path)
		
		if not fp.exists():
			raise FileNotFoundError(f"{path} does not exist.")
		
		# Load the audio in memory
		audio_data, audio_sr = sf.read(fp)
		title = fp.stem
		
		# Convert to mono if it's multi-channel
		if audio_data.ndim > 1:
			audio_data = audio_data.mean(axis=1)
			
		# Resample if needed
		if sr is not None:
			if audio_sr != sr:
				n_samples = int(len(audio_data) * sr / audio_sr)
				audio_data = resample(audio_data, n_samples)
				audio_sr = sr
	
	return audio_data, audio_sr, title