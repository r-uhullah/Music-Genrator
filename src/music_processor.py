from pathlib import Path

import pretty_midi


def custom_note_priority(note):
    return (note.start, note.pitch)


def extract_instrument_notes(midi_instrument):
    note_data = []
    sorted_notes = sorted(midi_instrument.notes, key=custom_note_priority)
    for note in sorted_notes:
        note_name = pretty_midi.note_number_to_name(note.pitch)
        note_data.append(
            {
                "pitch": note.pitch,
                "name": note_name,
                "velocity": note.velocity,
                "start": note.start,
                "end": note.end,
                "duration": note.end - note.start,
            }
        )
    return note_data


def has_overlapping_notes(note_data):
    # note_data = sorted(midi_instrument.notes, key=lambda note: note.start)

    for i in range(len(note_data) - 1):
        note_a = note_data[i]
        note_b = note_data[i + 1]

        if note_a["end"] > note_b["start"]:
            return True
    return False


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    midi_path = PROJECT_ROOT / "data" / "raw" / "MIDI" / "ashover20.mid"

    midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    first_instrument = midi_data.instruments[0]

    note_data = extract_instrument_notes(first_instrument)
    print("\n\n", has_overlapping_notes(note_data))

    # print(note_data)
    # print(f"Extracted {len(note_data)} notes from '{first_instrument.name}':\n")
    # for item in note_data[:5]:
    #     print(item)
