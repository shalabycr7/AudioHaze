import numpy as np
from scipy.io.wavfile import read, write


class AudioProcessing:
    __slots__ = ('audio_data', 'sample_freq')

    def __init__(self, input_audio_path):
        self.sample_freq, audio_data = read(input_audio_path)
        self.audio_data = AudioProcessing.convert_to_mono_audio(audio_data)

    def save_to_file(self, output_path):
        # Writes a WAV file representation of the processed audio data
        write(output_path, self.sample_freq, self.audio_data.astype(np.int16))

    def set_echo(self, delay):
        # Applies an echo that is 0...<input audio duration in seconds> seconds from the beginning
        output_delay = int(delay * self.sample_freq)
        output_audio = np.zeros_like(self.audio_data, dtype=np.float32)

        for i in range(output_audio.shape[0]):
            if i - output_delay < 0:
                output_audio[i] = self.audio_data[i]
            else:
                output_audio[i] = self.audio_data[i] + 0.6 * output_audio[i - output_delay]

        self.audio_data = (output_audio / np.max(np.abs(output_audio)) * 32767).astype(np.int16)

    @staticmethod
    def convert_to_mono_audio(input_audio):
        # Returns a numpy array that represents the mono version of a stereo input
        return ((np.array(input_audio[:, 0], dtype=np.float32) / 2) +
                (np.array(input_audio[:, 1], dtype=np.float32) / 2))
