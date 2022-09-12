import os
import numpy
import pickle
from keras.utils import np_utils
from keras.models import Sequential
from music21 import instrument, note, chord, stream
from keras.layers import BatchNormalization as BatchNorm
from keras.layers import Dense, Dropout, LSTM, Activation


def get_model_location(model_name):
    result = "model//class_engine//ml_models//"

    if model_name == "anime":
        result += "Anime"
    elif model_name == "beethoven":
        result += "Beethoven"
    elif model_name == "lofi":
        result += "Lofi"
    elif model_name == "maestro":
        result += "Maestro_2017"
    elif model_name == "maestro_2017":
        result += "Maestro_2017"
    elif model_name == "maestro_2018":
        result += "Maestro_2018"
    elif model_name == "mozart":
        result += "Mozart"
    return result


def get_instrument(instrument_name):
    # https://web.mit.edu/music21/doc/moduleReference/moduleInstrument.html
    instrument_name = instrument_name.lower()

    if instrument_name == "piano":
        return instrument.Piano()
    elif instrument_name == "guitar":
        return instrument.Guitar()
    elif instrument_name == "trumpet":
        return instrument.Trumpet()


class AlphaGenerate():
    def __init__(self, number_of_notes = 128, model_name="anime", instrument_name="piano", file_name="Model") -> None:
        self.notes = None
        self.sequence_length = 32
        self.base_number_of_notes = 128
        self.input_notes_file_name = "notes"
        self.output_directory_name = "model//class_engine//output"
        self.number_of_notes = number_of_notes
        self.model_pickle_file_name = "model.pkl"
        self.instrument = get_instrument(instrument_name)
        self.data_directory_name = get_model_location(model_name)

        self.notes = self.get_notes()
        self.model = self.load_model()

        self.file_name = file_name

    def create(self, songs_amount = 1, number_of_notes = 128, instrument_name="piano", file_name="Model"):
        self.file_name = file_name
        self.number_of_notes = number_of_notes
        self.instrument = get_instrument(instrument_name)

        songs_created = list()
        pitch_names = sorted(set(item for item in self.notes))
        network_input, normalized_input = self.prepare_sequences(pitch_names)

        for index in range(songs_amount):
            file_name = f'{self.file_name}-No-{index}'
            songs_created.append((self.get_files_location(file_name), file_name))
            prediction_output = self.generate_notes(network_input, pitch_names, len(set(self.notes)), self.number_of_notes)
            self.create_midi(prediction_output, file_name)

        return songs_created
    
    def get_files_location(self, file_name):
        music_model, instrument, background_music, _, _ = file_name.split("-")

        return f"/files/{music_model}/{instrument}/{background_music}/{file_name}"

    def get_notes(self):
        with open(f'{self.data_directory_name}//{self.input_notes_file_name}', 'rb') as filepath:
            return pickle.load(filepath)

    def prepare_sequences(self, pitch_names):
        network_input, output = list(), list()
        note_to_int = dict((note, number) for number, note in enumerate(pitch_names))

        for index in range(len(self.notes) - self.sequence_length):
            sequence_in = self.notes[index: index + self.sequence_length]
            sequence_out = self.notes[index + self.sequence_length]
            output.append([note_to_int[sequence_out]])
            network_input.append([note_to_int[note_character] for note_character in sequence_in])
        
        normalized_input = numpy.reshape(network_input, (len(network_input), self.sequence_length, 1))
        normalized_input = normalized_input / float(len(set(self.notes)))

        return (network_input, normalized_input)

    def load_model(self):
        return pickle.load(open(f"{self.data_directory_name}//{self.model_pickle_file_name}", 'rb'))

    def generate_notes(self, network_input, pitch_names, vocals_number, notes_number):
        prediction_output = list()
        int_to_note = dict((number, note) for number, note in enumerate(pitch_names))
        
        seeds = numpy.random.randint(0, len(network_input) - 1)
        pattern = network_input[seeds]

        for _ in range(notes_number):
            prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
            prediction_input = prediction_input / float(vocals_number)
            prediction = self.model.predict(prediction_input, verbose=0)

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
                    new_note.storedInstrument = self.instrument
                    notes.append(new_note)
                
                new_chord = chord.Chord(notes)
                new_chord.offset = offset
                output_notes.append(new_chord)

            else:
                new_note = note.Note(pattern)
                new_note.offset = offset
                new_note.storedInstrument = self.instrument
                output_notes.append(new_note)
            
            offset += 0.5
        
        midi_stream = stream.Stream(output_notes)
        midi_stream.write('midi', fp=f'{self.output_directory_name}//{file_name}.mid')
