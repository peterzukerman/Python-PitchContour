import numpy
from scipy.io import wavfile
from IPython.display import Audio
import matplotlib.pyplot as plt
import warnings
import librosa
from IPython import get_ipython
from pydub import AudioSegment
from pydub.playback import play
warnings.filterwarnings('ignore')


path = r'/Users/peterzuker/Desktop/Audio Modification/10047/model_input/spells/1/exemplars/1499777912068.wav'

#reload the audio to use librosa's expected format
lr_speech_data, lr_speech_rate  = librosa.load(path)

stretched = librosa.effects.time_stretch(lr_speech_data, 1.47)

y, sr   = librosa.load(path)
D       = librosa.stft(y, n_fft=2048, hop_length=512)
D_slow  = librosa.phase_vocoder(D, 1./3, hop_length=512)
y_slow  = librosa.istft(D_slow, hop_length=512)

wavfile.write('test.wav', y_slow, D_slow)


rate, data = wavfile.read(path)
sound = AudioSegment.from_file(path, format="wav")

play(sound)

def remove_silence(audio, threshold ):
    #identify all samples with an absolute value greater than the threshold
    greater_index = numpy.greater(numpy.absolute(audio), threshold)
    #filter to only include the identified samples
    above_threshold_data = audio[greater_index]
    return above_threshold_data

#sotu_above_threshold = remove_silence(data, 200)
#write only the first 20 seconds for evaluation
#wavfile.write('test.wav', rate, sotu_above_threshold[rate])
