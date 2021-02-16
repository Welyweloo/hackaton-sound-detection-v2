from IPython.display import Audio
from scipy.io import wavfile

import audioop
import configparser
import csv
import matplotlib.pyplot as plt
import math
import numpy as np
import os
import pyaudio
import requests
import scipy.signal
import struct

# Turn off Tensorflow Warnings
# Source : https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf

import tensorflow_hub as hub
import threading
import time
import wave

# Retrieve config data
config = configparser.ConfigParser()
config.read('conf.ini')


### Defining constant ###
SOUND_THRESHOLD = 250               ### TO FIND YOUR SOUND_THRESHOLD PRINT THE RMS VALUE
SHORT_NORMALIZE = (1.0/32768.0)
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SWIDTH = 2
TIMEOUT_LENGTH = 5
RECORDED_SOUND_DIRECTORY = r'recorded_sounds'
SERVER = config['RASPBERRY']['Address']

# Load the MODEL.
MODEL = hub.load('https://tfhub.dev/google/yamnet/1')

class Classify:
    """Sound recognition and classification"""

    # Find the name of the class with the top score when mean-aggregated across frames.
    def class_names_from_csv(self, class_map_csv_text):
        """Returns list of class names corresponding to score vector."""

        class_names = []
        with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                class_names.append(row['display_name'])

        return class_names


    def stereo_to_mono(self, wavsamplefile):
        """Convert sound from wav poly to wav mono."""

        stereo = wave.open(wavsamplefile, 'rb')
        mono_filename = "{0}-mono.wav".format(wavsamplefile.replace('.wav',''))
        mono = wave.open(mono_filename, 'wb')
        mono.setparams(stereo.getparams())
        mono.setnchannels(1)
        mono.writeframes(audioop.tomono(stereo.readframes(float('inf')), stereo.getsampwidth(), 1, 1))
        mono.close()

        return mono_filename


    def ensure_sample_rate(self, original_sample_rate, waveform,
                        desired_sample_rate=16000):
        """Resample waveform if required."""

        if original_sample_rate != desired_sample_rate:
            desired_length = int(round(float(len(waveform)) /
                                    original_sample_rate * desired_sample_rate))
            waveform = scipy.signal.resample(waveform, desired_length)
        return desired_sample_rate, waveform

    def get_sound_class(self, output_sound_filename):
        """Detects the infered class and send it via 
        post request to an API
        """
    
        wav_file_name = self.stereo_to_mono(output_sound_filename)

        sample_rate, wav_data = wavfile.read(wav_file_name, 'rb')
        sample_rate, wav_data = self.ensure_sample_rate(sample_rate, wav_data)

        # Show some basic information about the audio.
        duration = len(wav_data)/sample_rate
        print(f'Sample rate: {sample_rate} Hz')
        print(f'Total duration: {duration:.2f}s')
        print(f'Size of the input: {len(wav_data)}')

        # Listening to the wav file.
        #Audio(wav_data, rate=sample_rate)
        waveform = wav_data / tf.int16.max
        scores, embeddings, spectrogram = MODEL(waveform)
        scores_np = scores.numpy()
        spectrogram_np = spectrogram.numpy()
        infered_class = class_names[scores_np.mean(axis=0).argmax()]

        print(f'The main sound is: {infered_class}')

        #Sending POST request to API
        if infered_class not in ['Speech', 'Silence']:
            url = SERVER + '/set_sound_detected/'
            data = {
                'sound_nature' : infered_class,
                'serial_number': config['RASPBERRY']['SerialNumber']
            }
            request = requests.post(url, data)



class Recorder:
    """Detecting and recording sound"""

    @staticmethod
    def rms(frame):
        """Determines the rms value of a sound"""

        count = len(frame) / SWIDTH
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.filename = ''
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=CHUNK)

    def record(self):
        """Records the sound"""

        print('Noise detected, recording beginning')
        recording = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(CHUNK)
            
            #if self.rms(data) >= SOUND_THRESHOLD: 
            #    end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            recording.append(data)
        self.write(b''.join(recording))

        return self.filename

    def write(self, recording):
        """Register the sound"""

        n_files = len(os.listdir(RECORDED_SOUND_DIRECTORY))

        self.filename = os.path.join(RECORDED_SOUND_DIRECTORY, '{}.wav'.format(n_files))

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        print('Written to file: {}'.format(self.filename))
        


    def listen(self):
        """Listens around while the program is running"""

        print('Listening beginning')
        while True:

            # Sending post request to turn on listenning status
            url = SERVER + '/set_listenning_status/'+config['RASPBERRY']['SerialNumber']
            response = requests.get(url)

            input = self.stream.read(CHUNK)
            rms_val = self.rms(input)
            print(rms_val)
            if rms_val > SOUND_THRESHOLD:
                
                print(f' {rms_val} - Sound DETECTED')
                output_sound_filename = self.record()
                classifier.get_sound_class(output_sound_filename)
                print('Returning to listening')


if __name__ == '__main__':

    print('Start sound detection and classication')
    while True:

        # Retrieving permission to start the program
        url = SERVER + '/get_assistant_status/'+config['RASPBERRY']['SerialNumber']
        response = requests.get(url)

        if response.text == 'True':
            classifier = Classify()

            class_map_path = MODEL.class_map_path().numpy()
            class_names = classifier.class_names_from_csv(class_map_path)

            recorder = Recorder()

            try:
                recorder.listen()
            except KeyboardInterrupt:

                # Removing all registered sound before exiting the program 
                folder = '/home/aurelie/Documents/Hackaton/recorded_sounds'

                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)

                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)   #https://docs.python.org/3/library/os.html#os.remove

                print('You pressed Ctrl + c : Program exit.')
                exit(0)

