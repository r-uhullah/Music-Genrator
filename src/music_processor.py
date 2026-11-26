from copyreg import clear_extension_cache
from pathlib import Path

from statistics import median
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


def extract_melody_candidates(midi_data):
    candidate_data = []
    reject_count = 0

    for index, instrument in enumerate(midi_data.instruments):
        note_data = extract_instrument_notes(instrument)
        is_overlapping = has_overlapping_notes(note_data)

        if is_overlapping or instrument.is_drum or len(note_data) == 0:
            reject_count += 1
            continue

        new_candidate = {
            "instrument_index": index,
            "instrument_name": instrument.name,
            "program": instrument.program,
            "notes": note_data,
        }

        candidate_data.append(new_candidate)
    return candidate_data, reject_count


def process_midi_file(midi_path):
    file_path = Path(midi_path)
    candidate_list = []
    rejected = 0
    success = False

    try:
        midi_data = pretty_midi.PrettyMIDI(str(file_path))
        candidate_list, rejected = extract_melody_candidates(midi_data)
        success = True
    except Exception as error:
        print(f"Error in file - {file_path.name}: {error}")
    return candidate_list, file_path, rejected, success


def process_midi_dataset(folder_path):
    folder = Path(folder_path)
    training_data = []
    total_file_scanned = 0
    successful_scans = 0
    failed_scans = 0
    total_rejected = 0

    for item in folder.rglob("*.mid"):
        if not item.is_file():
            continue
        total_file_scanned += 1

        try:
            candidate_list, file_path, file_rejected, success = process_midi_file(item)
            if not success:
                failed_scans += 1
                continue

            total_rejected += file_rejected
            successful_scans += 1

            for candidate in candidate_list:
                new_candidate = {
                    "source_file": str(file_path),
                    "instrument_index": candidate["instrument_index"],
                    "instrument_name": candidate["instrument_name"],
                    "program": candidate["program"],
                    "notes": candidate["notes"],
                }

                training_data.append(new_candidate)

        except Exception as error:
            print(f"Error in file - {item}: {error}")
            failed_scans += 1

    statistics = {
        "total_file": total_file_scanned,
        "successful_scans": successful_scans,
        "failed_scans": failed_scans,
        "total_candidates": len(training_data),
        "total_rejected_instruments": total_rejected,
    }

    return training_data, statistics


def inspect(training_data):
    if not training_data:
        return {
            "total_candidates": 0,
            "min_notes": 0,
            "max_notes": 0,
            "average_notes": 0,
            "median_notes": 0,
            "lowest_pitch": None,
            "highest_pitch": None,
            "average_pitch_range": 0,
            "total_intervals": 0,
            "repeated_notes": 0,
            "small_intervals": 0,
            "large_intervals": 0,
            "largest_interval": 0,
            "instrument_counts": {},
        }

    note_counts = []
    pitch_ranges = []
    global_lowest_pitch = None
    global_highest_pitch = None
    total_intervals = 0
    repeated_notes = 0
    small_intervals = 0
    large_intervals = 0
    largest_interval = 0
    pitch_interval = []
    instrument_count = {}
    duration_list = []
    min_duration = 100
    max_duration = 0

    for candidate in training_data:
        notes = candidate["notes"]
        note_counts.append(len(notes))
        instrument_name = pretty_midi.program_to_instrument_name(candidate["program"])
        instrument_count[instrument_name] = instrument_count.get(instrument_name, 0) + 1

        for note in notes:
            duration = note["duration"]
            duration_list.append(duration)

            max_duration = max(max_duration, duration)
            min_duration = min(min_duration, duration)

        if notes:
            pitches = [n["pitch"] for n in notes]
            cand_low = min(pitches)
            cand_high = max(pitches)
            pitch_ranges.append(cand_high - cand_low)

            if global_lowest_pitch is None or cand_low < global_lowest_pitch:
                global_lowest_pitch = cand_low
            if global_highest_pitch is None or cand_high > global_highest_pitch:
                global_highest_pitch = cand_high

            for a, b in zip(pitches, pitches[1:]):
                interval = b - a
                pitch_interval.append(interval)
                total_intervals += 1

                if abs(interval) == 0:
                    repeated_notes += 1

                if abs(interval) in (1, 2):
                    small_intervals += 1
                if abs(interval) > 7:
                    large_intervals += 1

                largest_interval = max(largest_interval, abs(interval))

    stats = {
        "total_candidates": len(training_data),
        "min_notes": min(note_counts),
        "max_notes": max(note_counts),
        "average_notes": sum(note_counts) / len(note_counts),
        "median_notes": median(note_counts),
        "lowest_pitch": global_lowest_pitch,
        "highest_pitch": global_highest_pitch,
        "average_pitch_range": (
            sum(pitch_ranges) / len(pitch_ranges) if pitch_ranges else 0
        ),
        "total_intervals": total_intervals,
        "repeated_notes": repeated_notes,
        "small_intervals": small_intervals,
        "large_intervals": large_intervals,
        "largest_interval": largest_interval,
        "average_interval_size": sum(abs(i) for i in pitch_interval)
        / len(pitch_interval),
        "instrument_counts": instrument_count,
        "duration_list": duration_list,
        "max_duration": max_duration,
        "min_duration": min_duration,
    }

    return stats


def quantize_data(training_data):
    quantized_sequence = []

    for candidates in training_data:
        notes = candidates["notes"]
        melody = []

        for note in notes:
            duration = note["duration"]

            idx = round(duration / 0.125)
            idx = max(1, min(16, idx))
            clean_duration = round(idx * 0.125, 3)
            melody.append((note["pitch"], clean_duration))
        quantized_sequence.append(melody)

    return quantized_sequence


if __name__ == "__main__":
    training_data, statistics = process_midi_dataset(
        r"C:\Users\user\Desktop\Code\Python\Projects\Music Generator\data\raw\MIDI"
    )
    seqs = quantize_data(training_data)
    print("Candidates:", len(seqs))
    print("First candidate length:", len(seqs[0]))
    print("First 5 notes:", seqs[0][:5])
    print("Total notes:", sum(len(s) for s in seqs))
    print(seqs[0])

    # from collections import Counter

    # # training_data, _ = process_midi_dataset(r"...\data\raw\MIDI")
    # quantized = quantize_data(training_data)

    # counts = Counter(quantized)
    # total = sum(counts.values())

    # for dur, count in sorted(counts.items()):
    #     print(f"{dur:>5.2f}s  {count:>7}  {100*count/total:>5.1f}%")
    # print("Total:", total)
    # print(inspect(training_data))
    # from collections import Counter

    # stats = inspect(training_data)

    # # Count rounded durations
    # dur_counts = Counter(round(d, 3) for d in stats["duration_list"])

    # # Print top 15
    # for dur, count in dur_counts.most_common(15):
    #     pct = 100 * count / len(stats["duration_list"])
    #     print(f"{dur:>7.3f}s  {count:>7}  {pct:>5.1f}%")
    # print(statistics)
    # for candidate in training_data[:3]:
    #     print(candidate["source_file"])
    #     print(candidate["instrument_name"])
    #     print("Number of notes:", len(candidate["notes"]))
    #     print("First five notes:", candidate["notes"][:5])
