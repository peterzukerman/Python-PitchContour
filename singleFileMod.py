import json
import glob
import fnmatch
import os
import sys
import shutil
import numpy as np
import wave
import parselmouth
from parselmouth.praat import call
from scipy.io.wavfile import read
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


from pydub import AudioSegment
from pydub.playback import play
import ffmpy

def openFile(jsonPath, path):
    return [json.load(open(jsonPath)), AudioSegment.from_file(path, format="wav")]

def trimAudio(audio, myJson):
    startMod = myJson['manual']['start']
    endMod = myJson['manual']['stop']
    audio = audio[startMod*1000:]
    audio = audio[:endMod*1000]
    return audio

def playAudio(overlayedAudio):
    for sound in overlayedAudio:
        play(sound)
    
def openModifiers(path):
    directory = os.fsencode(path)
    os.chdir(path)
    modifiers = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".wav"):
            #print(filename)
            mod = AudioSegment.from_file(str(filename), format="wav")
            modifiers.append(mod)
    return modifiers

def addOverlay(noise, audio, constants, snr):
    overlayedAudio = []

    for soundEffect, constant in zip(noise, constants):
        overlayedAudio.append(audio.overlay(soundEffect + (soundEffect - (snr/constant))))
    return overlayedAudio

def findModifier(sample, backgroundNoise):
    averagesSample = []
    averagesBackgroundNoise = []
    modifiers = []
    for value in sample:
        averagesSample.append(value.rms)

    for audio in backgroundNoise:
        averagesBackgroundNoise.append(audio.rms)

    for average in averagesSample:
        for noiseAverage in averagesBackgroundNoise:
            modifiers.append(average / noiseAverage)
    return modifiers

def adjustVolume(sample, decibels):
    return sample + decibels

def adjustPitch(wavepath, pitch):
    sound = parselmouth.Sound(wavepath)

    manipulation = call(sound, "To Manipulation", 0.001, 200, 600)
    pitch_tier = call("Create PitchTier", "name", 0, 1)

    call(pitch_tier, "Add point", 0, pitch)
    #call(pitch_tier, "Add point", 0.4, 225)
    #call(pitch_tier, "Add point", endMod, 100)
    #instead of extract, create pitch tier, and add 2 points to it (keep in mind voiceless/voiced)

    call([pitch_tier, manipulation], "Replace pitch tier")
    soundPitch = call(manipulation, "Get resynthesis (overlap-add)")

    #sound.pre_emphasize()
    soundPitch.save("pitch{}.wav".format(" " + str(pitch) + "Hz"), 'WAV')

def contour2PitchPoints(wavePath, jsonPath, pitchPoints):
    jsonFile = json.load(open(jsonPath))

    startMod = jsonFile['manual']['start']
    endMod = jsonFile['manual']['stop']

    sound = parselmouth.Sound(wavePath)

    manipulation = call(sound, "To Manipulation", 0.001, min(pitchPoints[0], pitchPoints[1]), max(pitchPoints[0], pitchPoints[1]))
    pitch_tier = call("Create PitchTier", "name", startMod, endMod)

    call(pitch_tier, "Add point", startMod, pitchPoints[0])
    call(pitch_tier, "Add point", endMod, pitchPoints[1])

    call([pitch_tier, manipulation], "Replace pitch tier")
    contourSound = call(manipulation, "Get resynthesis (overlap-add)")

    contourSound.save("contour {}-{}.wav".format(pitchPoints[0], pitchPoints[1]), 'WAV')

def contour3PitchPoints(wavePath, jsonPath, pitchPoints):
    jsonFile = json.load(open(jsonPath))

    startMod = jsonFile['manual']['start']
    endMod = jsonFile['manual']['stop']

    sound = parselmouth.Sound(wavePath)

    manipulation = call(sound, "To Manipulation", 0.001, min(pitchPoints[0], pitchPoints[1], pitchPoints[2]), max(pitchPoints[0], pitchPoints[1], pitchPoints[2]))
    pitch_tier = call("Create PitchTier", "name", startMod, endMod)

    call(pitch_tier, "Add point", startMod, pitchPoints[0])
    call(pitch_tier, "Add point", (startMod + endMod) / 2, pitchPoints[1])
    call(pitch_tier, "Add point", endMod, pitchPoints[2])

    call([pitch_tier, manipulation], "Replace pitch tier")
    contourSound = call(manipulation, "Get resynthesis (overlap-add)")

    contourSound.save("contour {}-{}-{}.wav".format(pitchPoints[0], pitchPoints[1], pitchPoints[2]), 'WAV')

def export(audio, name):
    audio.export("{}.wav".format(name), format="wav")

def draw_spectrogram(spectrogram, dynamic_range=70):
    X, Y = spectrogram.x_grid(), spectrogram.y_grid()
    sg_db = 10 * np.log10(spectrogram.values)
    plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
    plt.ylim([spectrogram.ymin, spectrogram.ymax])
    plt.xlabel("time [s]")
    plt.ylabel("frequency [Hz]")

def draw_intensity(intensity):
    plt.plot(intensity.xs(), intensity.values.T, linewidth=3, color='w')
    plt.plot(intensity.xs(), intensity.values.T, linewidth=1)
    plt.grid(False)
    plt.ylim(0)
    plt.ylabel("intensity [dB]")

def intensity(filename, snd):
    intensity = snd.to_intensity()
    spectrogram = snd.to_spectrogram()
    plt.figure()
    draw_spectrogram(spectrogram)
    plt.twinx()
    draw_intensity(intensity)
    plt.xlim([snd.xmin, snd.xmax])
    filePlain, file_extension = os.path.splitext(filename)
    plt.savefig("{} int.png".format(filePlain))

def amplitute(filename, snd):
    plt.figure()
    plt.plot(snd.xs(), snd.values.T)
    plt.xlim([snd.xmin, snd.xmax])
    plt.xlabel("time [s]")
    plt.ylabel("amplitude")
    filePlain, file_extension = os.path.splitext(filename)
    plt.savefig("{} amp.png".format(filePlain))

def main(path, noisePath, jsonPath, snr):
    if os.path.isdir("output"):
        shutil.rmtree("output")
    os.mkdir("output")
    
    # ------ Loading --------
    file = openFile(jsonPath, path)
    backgroundNoise = openModifiers(noisePath)
    trimmed = trimAudio(file[1], file[0])
    os.chdir("..")
    os.chdir("output")

    # ------ Volume --------
    volume10Louder = adjustVolume(trimmed, 10)
    volume10Quieter = adjustVolume(trimmed, -10)
    export(volume10Louder, "volume +10db")
    export(volume10Quieter, "volume -10db")
    # ------ Pitch --------
    adjustPitch(path, 500)
    adjustPitch(path, 200)

    # ------ Noise --------
    constants = findModifier(trimmed, backgroundNoise)
    overlayedAudio = addOverlay(backgroundNoise, trimmed, constants, snr)
    x = 0
    for audio in overlayedAudio:
        export(audio, "noise {}".format(x))
        x = x + 1

    # ------ Contour --------
    pitchPoints2 = [[200, 500], [500, 200], [300, 400], [400, 300]]
    pitchPoints3 = [[200, 500, 200], [300, 500, 100]]
    for contour in pitchPoints2:
        contour2PitchPoints(path, jsonPath, contour)
    for contour in pitchPoints3:
        contour3PitchPoints(path, jsonPath, contour)


    sns.set() # Use seaborn's default style to make attractive graphs
    directory = os.fsencode(r'/Users/peterzuker/Desktop/Audio Modification/output')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        snd = parselmouth.Sound(filename)
        intensity(filename, snd)
        amplitute(filename, snd)
        
    

if __name__== "__main__":
    path = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/1499777912068.wav'
    overlayPath = r'/Users/peterzuker/Desktop/Audio Modification/Sounds'  
    jsonPath = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/1499777912068.json'
    snr = 0
    main(path, overlayPath, jsonPath, snr)

