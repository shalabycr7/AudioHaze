from . import audio_processing


def echo(input_path, output_path):
    # Applies an echo effect to a given input audio file
    sound = audio_processing.AudioProcessing(input_path)
    sound.set_echo(0.09)
    sound.save_to_file(output_path)
