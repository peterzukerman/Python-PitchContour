# Pitch Contour

## Parselmouth - Praat in Python

**Parselmouth** is a Python library for the [Praat](http://www.praat.org) software. Here I use it for generating 4 types of modifications:
1. Volume (dB +-)
2. Pitch (sets entire audio pitch to x Hz)
3. Noise (overlays noise based on SNR)
4. Pitch Contour (changes tone)


## Installation

```
pip install praat-parselmouth
```

## Libraries used
```Python
import json
import os
import sys
import shutil
import numpy as np
import wave
import parselmouth
import glob
from parselmouth.praat import call
from pydub import AudioSegment
```

## Documentation

```Python
openFile(jsonPath, filePath)
```
Loads in json files (with start and end times of speech) and the path to the audio files. Returns a 2d array in the format [jsonFiles, samples], where jsonFiles is an array of json objects, and samples is an array of pydub AudioSegments.

```Python
openModifiers(path)
```
Loads in noise that will be overlayed on the samples. Returns an array of AudioSegments.

```Python
adjustVolume(sample, decibels)
```
Adjusts sample volume by decibels. Positive or negative.

```Python
adjustPitch(wavPath, pitch)
```
Creates a pitchTier with a pitchPoint at the given pitch, and resynthesis the wav (from wavPath) based on the pitchTier. Saves the new sound in the format 
```Python
("pitch{}.wav".format(" " + str(pitch) + "Hz"), 'WAV')
```








