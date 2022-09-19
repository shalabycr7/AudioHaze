import numpy as np
from numpy import array, int16
from scipy.io.wavfile import read, write


class AudioProcessing(object):
    __slots__ = ('audio_data', 'sample_freq')

    def __init__(self, input_audio_path):
        self.sample_freq, self.audio_data = read(input_audio_path)
        self.audio_data = AudioProcessing.convert_to_mono_audio(self.audio_data)

    def save_to_file(self, output_path):
        # Writes a WAV file representation of the processed audio data
        write(output_path, self.sample_freq, array(self.audio_data, dtype=int16))

    def set_echo(self, delay):
        # Applies an echo that is 0...<input audio duration in seconds> seconds from the beginning
        output_audio = np.zeros(len(self.audio_data))
        output_delay = delay * self.sample_freq

        for count, e in enumerate(self.audio_data):
            output_audio[count] = e + self.audio_data[count - int(output_delay)]

        self.audio_data = output_audio

    @staticmethod
    def convert_to_mono_audio(input_audio):
        # Returns a numpy array that represents the mono version of a stereo input
        output_audio = []
        temp_audio = input_audio.astype(float)

        for e in temp_audio:
            output_audio.append((e[0] / 2) + (e[1] / 2))

        return np.array(output_audio, dtype='int16')
