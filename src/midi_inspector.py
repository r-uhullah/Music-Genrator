from pathlib import Path

import pretty_midi


def inspect_database(folder_path):
    folder = Path(folder_path)

    midi_files = list(folder.rglob("*.mid"))

    total_instruments = 0
    total_notes = 0
    empty_instruments = 0
    successful_files = 0
    failed_files = 0

    for item in midi_files:
        if not item.is_file():
            continue

        try:
            midi_data = pretty_midi.PrettyMIDI(str(item))

            successful_files += 1

            for instrument in midi_data.instruments:
                total_instruments += 1

                if not instrument.notes:
                    empty_instruments += 1

                total_notes += len(instrument.notes)

        except Exception as error:
            failed_files += 1
            print(f"Failed: {item.name} | {error}")

    print("===========================")
    print("      Dataset Report")
    print("===========================")

    print(f"Total MIDI files: {len(midi_files)}")
    print(f"Successfully read: {successful_files}")
    print(f"Failed files: {failed_files}")

    print(f"Total instruments: {total_instruments}")
    print(f"Total notes: {total_notes}")
    print(f"Empty instruments: {empty_instruments}")


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    midi_folder = PROJECT_ROOT / "data" / "raw" / "MIDI"
    inspect_database(midi_folder)
