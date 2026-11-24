import warnings
from pathlib import Path

import pretty_midi

# Silence only this specific pretty_midi warning
warnings.filterwarnings(
    "ignore",
    message="Tempo, Key or Time signature change events found on non-zero tracks.*",
    category=RuntimeWarning,
)

# Finds the project root automatically based on where test_midi.py lives
PROJECT_ROOT = Path(__file__).resolve().parent.parent
midi_path = PROJECT_ROOT / "data" / "raw" / "MIDI" / "hpps36.mid"

# pretty_midi expects a string path, so convert the Path object with str()
midi_data = pretty_midi.PrettyMIDI(str(midi_path))
print("Number of instruments:", len(midi_data.instruments))

for instrument in midi_data.instruments:
    print("\nInstrument:", instrument.name)
    print("Number of notes:", len(instrument.notes))
    # print(instrument.notes)

    # Fixed: changed 'instrument.note' to 'instrument.notes'
    for note in instrument.notes[:10]:
        note_name = pretty_midi.note_number_to_name(note.pitch)
        # print(note)

        print(
            f"Note: {note_name}  | "
            f"Pitch: {note.pitch}  | "
            f"Start: {note.start:.2f}s  | "
            f"Duration: {note.end - note.start:.2f}s"
        )
