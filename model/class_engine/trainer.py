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
