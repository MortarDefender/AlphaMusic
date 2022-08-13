import numpy
import pickle
from datetime import datetime
from music21 import instrument, note, stream, chord


class AlphaGenerate():
    def __init__(self, number_of_notes = 128, input_notes_file_name = "notes") -> None:
        self.notes = None
        self.sequence_length = 32
        self.data_directory_name = "data"
        self.number_of_notes = number_of_notes
        self.output_directory = "midi_generated"
        self.model_pickle_file_name = "main.pkl"
        self.input_notes_file_name = f"{input_notes_file_name}"

    def create(self, songs_amount = 1):
        songs_created = list()
        self.notes = self.get_notes()
        pitch_names = sorted(set(item for item in self.notes))  # is the for needed
        network_input, normalized_input = self.prepare_sequences(pitch_names)
        model = self.load_model(normalized_input)  # var needed ??? 

        for index in range(songs_amount):
            # current_time = datetime.now()
            # file_name = f'{current_time.strftime("%Y-%m-%d %H:%M:%S")}||{index}'
            file_name = f'Model{index}'
            songs_created.append(file_name)
            prediction_output = self.generate_notes(model, network_input, pitch_names, len(set(self.notes)), self.number_of_notes)
            self.create_midi(prediction_output, file_name)
        
        return songs_created
    
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
    
    def load_model(self):
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
                    new_note.storedInstrument = instrument.Piano()  # change to class variable
                    notes.append(new_note)
                
                new_chord = chord.Chord(notes)
                new_chord.offset = offset
                output_notes.append(new_chord)

            else:
                new_note = note.Note(pattern)
                new_note.offset = offset
                new_note.storedInstrument = instrument.Piano()  # change to class variable
                output_notes.append(new_note)
            
            offset += 0.5
        
        midi_stream = stream.Stream(output_notes)
        midi_stream.write('midi', fp=f'{self.data_directory_name}/{file_name}.mid')
