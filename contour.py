import glob
import os.path
import parselmouth
from pydub import AudioSegment
from pydub.playback import play
from parselmouth.praat import call

import json
import sys


wavepath = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/1499777912068.wav'
jsonPath = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/1499777912068.json'


jsonFile = json.load(open(jsonPath))

startMod = jsonFile['manual']['start']
endMod = jsonFile['manual']['stop']


sound = parselmouth.Sound(wavepath)

manipulation = call(sound, "To Manipulation", 0.001, 200, 600)
pitch_tier = call("Create PitchTier", "name", 0, 1)

call(pitch_tier, "Add point", startMod, 500)
#call(pitch_tier, "Add point", 0.4, 225)
#call(pitch_tier, "Add point", endMod, 100)
#instead of extract, create pitch tier, and add 2 points to it (keep in mind voiceless/voiced)

call([pitch_tier, manipulation], "Replace pitch tier")
sound_octave_up = call(manipulation, "Get resynthesis (overlap-add)")

#sound.pre_emphasize()
sound_octave_up.save("test.wav", 'WAV') # or parselmouth.

#start time, end time - take them from the existing file (in seconds)
#add point at time (0.1, 0,5, etc) with 100hz, add another point at (0.9)
#1 pitch tier with 2 pitch points

#manipulate - time step, minimum pitch, maximum pitch