#!/usr/bin/env python3


#--------Meta Information----------
_class_name = "AudioConverter"
_author_name = "Ankit Anand"
_author_email = "ankit0.anand0@gmail.com"
_created_at = "2025-07-11"
#----------------------------------


from modusa import excp
from modusa.tools.audio_converter import AudioConverter
import pytest
from pathlib import Path
import shutil

TEST_DP = Path(__file__).parents[1].resolve()
TMP_DP = TEST_DP / "tmp" # To store exported files

@pytest.fixture(scope="module", autouse=True)
def cleanup_dne_dir():
	"""
	This makes sure that the directory after the test
	is automatically deleted.
	"""
	yield
	dne_dir = TEST_DP / "tmp"
	if dne_dir.exists():
		shutil.rmtree(dne_dir)

def test_convert_non_exixiting_file():
	with pytest.raises(excp.FileNotFoundError):
		AudioConverter.convert("../dne.wav", "./dne.mp3")

def test_convert_non_existing_output_dir():
	AudioConverter.convert(TEST_DP / "data" / "song1.mp3", TEST_DP / "tmp" / "song1.wav")

def test_convert_to_same_format():
	AudioConverter.convert(TEST_DP / "data" / "song1.mp3", TEST_DP / "tmp" / "song1.mp3")
	
def test_when_input_fp_same_output_fp():
	with pytest.raises(excp.InputValueError):
		AudioConverter.convert(TEST_DP / "data" / "song1.mp3", TEST_DP / "data" / "song1.mp3")
		
def test_with_none():
	with pytest.raises(excp.InputTypeError):
		AudioConverter.convert(None, None)