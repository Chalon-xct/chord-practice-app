from midiutil import MIDIFile
import io
import base64
import math

INTERVALS = {
    'major': [0, 4, 7],
    'minor': [0, 3, 7],
    'dim': [0, 3, 6],
    'aug': [0, 4, 8],
    'maj7': [0, 4, 7, 11],
    'm7': [0, 3, 7, 10],
    '7': [0, 4, 7, 10],
    'sus4': [0, 5, 7],
    'sus2': [0, 2, 7]
}

SEMITONES = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

NOTE_FREQUENCIES = {
    'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
    'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
    'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
}


def note_to_midi_number(note_name, octave):
    semitone = SEMITONES.get(note_name, 0)
    return 12 * (octave + 1) + semitone


def parse_chord_name(chord_name):
    for suffix in ['maj7', 'm7', 'sus4', 'sus2', 'dim', 'aug', 'min', 'minor', '7']:
        if chord_name.endswith(suffix):
            if suffix == 'minor':
                suffix = 'min'
            root = chord_name[:-len(suffix)]
            return root, suffix
    if chord_name.endswith('m'):
        return chord_name[:-1], 'minor'
    return chord_name, 'major'


def get_chord_notes(chord_name, octave=4):
    root, chord_type = parse_chord_name(chord_name)
    intervals = INTERVALS.get(chord_type, INTERVALS['major'])
    
    root_semitone = SEMITONES.get(root, 0)
    notes = []
    
    for interval in intervals:
        note_semitone = (root_semitone + interval) % 12
        notes.append(NOTE_NAMES[note_semitone])
    
    return notes


def get_chord_midi_numbers(chord_name, octave=4):
    root, chord_type = parse_chord_name(chord_name)
    intervals = INTERVALS.get(chord_type, INTERVALS['major'])
    
    root_semitone = SEMITONES.get(root, 0)
    midi_numbers = []
    
    for interval in intervals:
        note_semitone = root_semitone + interval
        note_octave = octave + note_semitone // 12
        note_semitone = note_semitone % 12
        midi_num = note_to_midi_number(NOTE_NAMES[note_semitone], note_octave)
        midi_numbers.append(midi_num)
    
    return midi_numbers


def generate_chord_midi(chord_name, duration=2, octave=4):
    midi = MIDIFile(1)
    midi.addTempo(0, 0, 120)
    
    midi_numbers = get_chord_midi_numbers(chord_name, octave)
    
    for midi_num in midi_numbers:
        midi.addNote(0, 0, midi_num, 0, duration, 100)
    
    bio = io.BytesIO()
    midi.writeFile(bio)
    bio.seek(0)
    
    return base64.b64encode(bio.read()).decode('utf-8')


def generate_single_note_midi(note_name, duration=1.5, octave=4):
    midi = MIDIFile(1)
    midi.addTempo(0, 0, 120)
    
    midi_num = note_to_midi_number(note_name, octave)
    midi.addNote(0, 0, midi_num, 0, duration, 100)
    
    bio = io.BytesIO()
    midi.writeFile(bio)
    bio.seek(0)
    
    return base64.b64encode(bio.read()).decode('utf-8')


def generate_chord_progression_midi(chords, chord_duration=2):
    midi = MIDIFile(1)
    midi.addTempo(0, 0, 120)
    
    current_time = 0
    
    for chord in chords:
        midi_numbers = get_chord_midi_numbers(chord)
        
        for midi_num in midi_numbers:
            midi.addNote(0, 0, midi_num, current_time, chord_duration, 100)
        
        current_time += chord_duration
    
    bio = io.BytesIO()
    midi.writeFile(bio)
    bio.seek(0)
    
    return base64.b64encode(bio.read()).decode('utf-8')
