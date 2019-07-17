import os
from pydub import AudioSegment
from pydub.playback import play
import json
import sys
import librosa

cwd = os.getcwd()

wavepath = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/1499777912068.wav'
jsonPath = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/1499777912068.json'


raw = AudioSegment.from_file(wavepath, format="wav")
jsonFile = json.load(open(jsonPath))

startMod = jsonFile['manual']['start']
endMod = jsonFile['manual']['stop']

raw = raw[startMod*1000:]
raw = raw[:endMod*1000]
sound = raw

#play(sound)
#print(sound.frame_rate)

# shift the pitch down by half an octave (speed will decrease proportionally)
def shiftPitchDown(pitch, sound):
    octaves = float(pitch)

    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))

    lowpitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    play(lowpitch_sound)
    playbackConst = float(pitch)

    newSound = lowpitch_sound.speedup(playback_speed=playbackConst, chunk_size=150, crossfade=25)
    return newSound

def shiftSpeed(speed, sound):
    newSound = sound.speedup(playback_speed=speed, chunk_size=150, crossfade=25)
    return newSound


def split():
    length = sound.duration_seconds
    interval = 1000 * length / 3 
    arr = []
    tempSound = sound
    for x in range(0, 2):
        #print(tempSound[:interval].duration_seconds)
        arr.append(tempSound[:interval])
        #print(length*1000-interval)
        tempSound = tempSound[interval:]
        print(tempSound.duration_seconds)

    return arr

  
def main():
    #if pitch != 1:
        #play(shiftPitchDown(pitch))
    #if speed != 1:
        #play(shiftSpeed(speed))
    soundArr = split() 
    soundArr[0] = shiftPitchDown(-0.5, soundArr[0])
    #soundArr[2] = shiftPitchDown(-0.5, soundArr[2])

    
    complete = soundArr[0]
    soundArr.remove(soundArr[0])
    for sound in soundArr:
        complete = complete + sound
    play(complete)

if __name__== "__main__":
    main()