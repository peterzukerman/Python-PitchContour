import json
import glob
import fnmatch
import os
import sys
import shutil
import numpy as np
import wave
from scipy.io.wavfile import read


from pydub import AudioSegment
from pydub.playback import play
import ffmpy

def openFiles(path):
    audio = []
    jsonFiles = []
    directory = os.fsencode(path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        os.chdir(path)

        if filename.endswith(".json"): 
            jsonFiles.append(json.load(open(file)))
        elif filename.endswith(".wav"):
            sound = AudioSegment.from_file(str(filename), format="wav")
            audio.append(sound)
    
    return [audio, jsonFiles]

def trimAudio(audio, jsonFiles):
    curr = 0
    trimmed = []

    for sound in audio:
        thisJson = jsonFiles[curr]
        startMod = thisJson['manual']['start']
        endMod = thisJson['manual']['stop']
        sound = sound[startMod*1000:]
        sound = sound[:endMod*1000]
        trimmed.append(sound)
        curr = curr + 1
    
    return trimmed

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

def addOverlay(noise, spells, constants, snr):
    overlayedAudio = []

    for speech in spells:
        for soundEffect, constant in zip(noise, constants):
            overlayedAudio.append(speech.overlay(soundEffect + (soundEffect - (snr/constant))))

    for sound in overlayedAudio:
        if sound.duration_seconds < 1.0:
            overlayedAudio.remove(sound)
    return overlayedAudio

def findModifier(samples, backgroundNoise):
    averagesSample = []
    averagesBackgroundNoise = []
    modifiers = []
    for audio in samples:
        for value in audio:
            averagesSample.append(value.rms)

    for audio in backgroundNoise:
        averagesBackgroundNoise.append(audio.rms)

    for average in averagesSample:
        for noiseAverage in averagesBackgroundNoise:
            modifiers.append(average / noiseAverage)
    return modifiers

def adjustVolume(sample, decibels):
    sample = sample + decibels

def adjustPitch(sample, octaves):
    newRate = int(sample.frame_rate * (2.0 ** octaves))
    adjustedSound = sample._spawn(sample.raw_data, overrides={'frame_rate': newRate})
    return adjustedSound


def export(overlayedAudio, path):
    os.chdir("..")
    if os.path.isdir("output"):
        shutil.rmtree("output")
    os.mkdir("output")
    os.chdir("output")
    num = 0
    for sound in overlayedAudio:
        sound.export("{}.wav".format(num), format="wav")
        num = num + 1

def main(path, overlayPath, snr):
    folder = openFiles(path)
    backgroundNoise = openModifiers(overlayPath)
    trimmed = trimAudio(folder[0], folder[1])
    export(trimmed, path)
    constants = findModifier(trimmed, backgroundNoise)
    overlayedAudio = addOverlay(backgroundNoise, trimmed, constants, snr)
    #print(overlayedAudio[0].raw_data)
    #playAudio(overlayedAudio)
    export(overlayedAudio, path)

if __name__== "__main__":
    print("Program for generating multiple augmentations of existing audio files.")

    print("\nExample: \n/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/ /Users/peterzuker/Desktop/Audio Modification/Sounds 5 False")

    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print('Usage:\t{}'.format(os.path.basename(__file__)), '[pathToAudio] [pathToOverlayAudio] snr useDefaultPath')
        exit()
    elif len(sys.argv) == 3 and sys.argv[2] == False:
        print('Usage:\t{}'.format(os.path.basename(__file__)), '[pathToAudio] [pathToOverlayAudio] snr useDefaultPath')
        exit()
    path = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/'
    overlayPath = r'/Users/peterzuker/Desktop/Audio Modification/Sounds'
    snr = 0
    if len(sys.argv) == 3:
        snr = float(sys.argv[1])      
    elif len(sys.argv) == 5:
        if sys.argv[4] == True:
            path = sys.argv[1]
            overlayPath = sys.argv[2] 
            snr = float(sys.argv[3])    


    main(path, overlayPath, snr)

