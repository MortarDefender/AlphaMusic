
## Train Section
import numpy
import pickle
from os.path import exists
from glob import glob as search
from keras.utils import np_utils
from keras.models import Sequential
from music21 import converter, instrument, note, chord
from keras.layers import BatchNormalization as BatchNorm
from keras.layers import Dense, Dropout, LSTM, Activation


class AlphaTrain():
    def __init__(self, epoch_amount = 75, batch_size = 64, sequence_length = 32, output_file_name = "model", input_notes_file_name = "notes", verbose = False) -> None:
        self.notes = None
        self.debug = verbose
        self.network_input = None
        self.batch_size = batch_size
        self.epoch_amount = epoch_amount
        self.data_directory_name = "data"
        self.sequence_length = sequence_length
        self.input_notes_file_name = f"{input_notes_file_name}"
        self.output_pickle_file_name = f"{output_file_name}.pkl"

    def run(self):
        self.notes = self.get_notes() 
        self.network_input, network_output = self.prepare_sequences()
        model = self.get_model()
        self.train(model, network_output)

    def train(self, model, network_output):
        model.fit(self.network_input, network_output, self.epoch_amount, self.batch_size)
        pickle.dump(model, open(self.output_pickle_file_name, 'wb'))
    
    def get_model(self):
        return self.__get_pickle_file_output(self.data_directory_name, self.output_pickle_file_name, self.create_network)

    def get_notes(self):
        return self.__get_pickle_file_output(self.data_directory_name, self.input_notes_file_name, self.create_notes)

    @staticmethod
    def __get_pickle_file_output(directory, file_name, create_object_function):
        if exists(f'{directory}/{file_name}'):
            with open(f'{directory}/{file_name}', 'rb') as filepath:
                return pickle.load(filepath)
        return create_object_function()

    def prepare_sequences(self):
        network_input, network_output = list(), list()
        pitch_names = sorted(set(item for item in notes))  # is the for needed
        note_to_int = dict((note, number) for number, note in enumerate(pitch_names))

        for index in range(len(self.notes) - self.sequence_length):
            sequence_in = self.notes[index: index + self.sequence_length]
            sequence_out = self.notes[index + self.sequence_length]
            network_output.append([note_to_int[sequence_out]])
            network_input.append([note_to_int[note_character] for note_character in sequence_in])

        network_input = numpy.reshape(network_input, (len(network_input), self.sequence_length, 1))
        network_input /= float(len(set(self.notes)))
        network_output = np_utils.to_categorical(network_output)

        return (network_input, network_output)

    def create_notes(self):
        notes = list()

        for file_name in search(f"{self.data_directory_name}/*.mid"):
            midi_file = converter.parse(file_name)

            if self.debug:
                print(f"Parsing {file_name}")
            
            current_notes = None

            try:
                s2 = instrument.partitionByInstrument(midi_file)  # change s2 to a different name
                current_notes = s2.parts[0].recurse()
            except Exception:  # what exception is this 
                current_notes = midi_file.flat.notes

            for element in current_notes:  # element 
                if isinstance(element, note.Note):
                    notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes.append('.'.join(str(n) for n in element.normalOrder))

        with open(f"{self.data_directory_name}/{self.input_notes_file_name}", 'wb') as filepath:
            pickle.dump(notes, filepath)

        return notes

    def create_network(self):
        model = Sequential()
        model.add(LSTM(
            512,
            input_shape=(self.network_input.shape[1], self.network_input.shape[2]),
            recurrent_dropout=0.3,
            return_sequences=True
        ))
        model.add(LSTM(512, return_sequences=True, recurrent_dropout=0.3,))
        model.add(LSTM(512))
        model.add(BatchNorm())
        model.add(Dropout(0.3))
        model.add(Dense(256))
        model.add(Activation('relu'))
        model.add(BatchNorm())
        model.add(Dropout(0.3))
        model.add(Dense(len(set(self.notes))))
        model.add(Activation('softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam')

        return model


## Generate Section
import numpy
import pickle
import os.path
from datetime import datetime
from music21 import instrument, note, stream, chord
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Activation
from keras.layers import BatchNormalization as BatchNorm



class AlphaGenerate():
    def __init__(self, sequence_length = 32, number_of_notes = 128, input_notes_file_name = "notes") -> None:
        self.notes = None
        self.data_directory_name = "data"
        self.sequence_length = sequence_length
        self.number_of_notes = number_of_notes
        self.output_directory = "midi_generated"
        self.model_pickle_file_name = "main.pkl"
        self.input_notes_file_name = f"{input_notes_file_name}"

    def create(self, songs_amount = 1):
        self.notes = self.get_notes()
        pitch_names = sorted(set(item for item in self.notes))  # is the for needed
        network_input, normalized_input = self.prepare_sequences(pitch_names)
        model = self.create_network(normalized_input)  # var needed ??? 

        for index in range(songs_amount):
            current_time = datetime.now()
            file_name = f'{current_time.strftime("%Y-%m-%d %H:%M:%S")}||{index}'
            prediction_output = self.generate_notes(model, network_input, pitch_names, len(set(self.notes)), self.number_of_notes)
            self.create_midi(prediction_output, file_name)
    
    def get_notes(self):
        with open(f'{self.data_directory_name}/{self.input_notes_file_name}', 'rb') as filepath:
            return pickle.load(filepath)
    
    def prepare_sequences(self, pitch_names):
        network_input, output = list(), list()
        note_to_int = dict((note, number) for number, note in enumerate(pitch_names))

        for index in range(len(self.notes) - self.sequence_length):
            sequence_in = self.notes[index: index + self.sequence_length]
            sequence_out = self.notes[index + self.sequence_length]
            output.append([note_to_int[sequence_out]])  # is output is needed
            network_input.append([note_to_int[note_character] for note_character in sequence_in])
        
        normalized_input = numpy.reshape(network_input, (len(network_input), self.sequence_length, 1))
        normalized_input /= float(len(set(self.notes)))

        return (network_input, normalized_input)
    
    def create_network(self):
        return pickle.load(open(self.model_pickle_file_name, 'rb'))
    
    def generate_notes(self, model, network_input, pitch_names, vocals_number, notes_number):
        prediction_output = list()
        int_to_note = dict((number, note) for number, note in enumerate(pitch_names))
        
        seeds = numpy.random.randint(0, len(network_input) - 1)
        pattern = network_input[seeds]

        for _ in range(notes_number):
            prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
            prediction_input /= float(vocals_number)
            prediction = model.predict(prediction_input, verbose=0)

            index = numpy.argmax(prediction)
            result = int_to_note[index]
            prediction_output.append(result)
            pattern.append(index)
            pattern = pattern[1:]

        return prediction_output
    
    def create_midi(self, prediction_output, file_name):
        offset = 0
        output_notes = list()

        for pattern in prediction_output:
            if '.' in pattern or pattern.isdigit():
                notes = list()
                notes_in_chord = pattern.split('.')

                for current_note in notes_in_chord:
                    new_note = note.Note(int(current_note))
                    new_note.storedInstrument = instrument.Piano()
                    notes.append(new_note)
                
                new_chord = chord.Chord(notes)
                new_chord.offset = offset
                output_notes.append(new_chord)

            else:
                new_note = note.Note(pattern)
                new_note.offset = offset
                new_note.storedInstrument = instrument.Piano()
                output_notes.append(new_note)
            
            offset += 0.5
        
        midi_stream = stream.Stream(output_notes)
        midi_stream.write('midi', fp=f'{self.data_directory_name}/{file_name}.mid')


## Utilities
# midi instruments converter and merger -> did not work ??
import glob
import pickle
import numpy
from keras.utils import np_utils
from keras.models import Sequential
from keras.callbacks import ModelCheckpoint
from mido import MidiFile, MetaMessage, MidiTrack
from music21 import converter, instrument, note, chord
from keras.layers import Dense, Dropout, LSTM, Activation
from keras.layers import BatchNormalization as BatchNorm


def convert_instruments():
    """ Get all the notes and chords from the midi files in the ./midi_songs directory """
    counter = 0
    for file in glob.glob("tempo_generated/*.mid"):
        midi = converter.parse(file)
        for part in midi.parts:
           part.insert(0, instrument.Ocarina())   #change instrument from list
        midi.write('midi', fp='ocarina_generated/{fname}.mid'.format(fname = counter))
        counter += 1

# https://web.mit.edu/music21/doc/moduleReference/moduleInstrument.html#music21.instrument.Instrument ------  instrument list


def change_tempo():
  count = 0
  for file in glob.glob("midi_generated/*.mid"):
    midi = MidiFile(file)
    for track in midi.tracks:
      track.append(MetaMessage('set_tempo', tempo=int((60.0 / 80) * 1000000), time=0))
    midi.save('tempo_generated/80bpm-{trackName}.mid'.format(trackName = count))
    count += 1
  
### change_tempo()
### convert_instruments()


# midi to wav
import os
import glob
import subprocess

env = os.environ.copy()
for midi in glob.glob("midi_generated_generated/*.mid"):
  file_name = midi[:-4].split('/')[1]
  print(file_name)
  subprocess.run(f"echo {file_name}", shell=True, env=env)
  subprocess.run(f'timidity "{midi}" -Ow -o "wav_generated/{file_name}.wav"', shell=True, env=env)


# merge background music
from pydub import AudioSegment

songs = []
for melody in glob.glob("wav_generated/*"):
  piano = AudioSegment.from_file(melody, format="wav")
  songs.append(piano + 10)   #increase volume by 6DB

# drum = AudioSegment.from_file("SFX/drum.wav", format="wav")
rain = AudioSegment.from_file("SFX/rain.wav", format="wav")

count = 0
for song in songs:
  # overlayDrum = song.overlay(drum, position=0)
  overlayRain = song.overlay(rain, position=0)
  overlayRain.export("Lo-Fi{id}.mp3".format(id = count), format="mp3")
  count += 1



# pickle midi songs data -> create notes only
import glob
import pickle
import numpy
from music21 import converter, instrument, note, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.layers import BatchNormalization as BatchNorm
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint

""" Get all the notes and chords from the midi files in the ./midi_songs directory """
notes = []

for file in glob.glob("data/*"):  #midi_songs
    midi = converter.parse(file)

    print("Parsing %s" % file)

    notes_to_parse = None

    try: # file has instrument parts
        s2 = instrument.partitionByInstrument(midi)
        notes_to_parse = s2.parts[0].recurse() 
    except: # file has notes in a flat structure
        notes_to_parse = midi.flat.notes

    for element in notes_to_parse:
        if isinstance(element, note.Note):
            notes.append(str(element.pitch))
        elif isinstance(element, chord.Chord):
            notes.append('.'.join(str(n) for n in element.normalOrder))

with open('notes', 'wb') as filepath:
    pickle.dump(notes, filepath)


if __name__ == '__main__':
    pass
