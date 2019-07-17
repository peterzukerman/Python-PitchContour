import os
from pydub import AudioSegment
from pydub.playback import play


cwd = os.getcwd()

wavepath = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/1499777912068.wav'

sound = AudioSegment.from_file(wavepath, format="wav")

play(sound)
print(sound.frame_rate)

# shift the pitch down by half an octave (speed will decrease proportionally)
octaves = -0.5

new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))

lowpitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

newSound = lowpitch_sound.speedup(playback_speed=1.5, chunk_size=150, crossfade=25)

#Play pitch changed sound
play(newSound)