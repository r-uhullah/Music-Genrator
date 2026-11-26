import random
from collections import Counter, defaultdict

from music_processor import process_midi_dataset, quantize_data


def tuple_to_str(data):
    converted = []
    for melody in data:
        string_melody = []

        for pitch, duration in melody:
            string_melody.append(f"{pitch}_{duration}")
        converted.append(string_melody)
    return converted


def build_transition_table(str_data):
    transitions = defaultdict(Counter)

    for melody in str_data:
        augumented = ["START"] + melody + ["END"]
        for state, next_state in zip(augumented, augumented[1:]):
            transitions[state][next_state] += 1

    return transitions


def generate_melody(transitions, max_length=50):
    current = "START"
    melody = []

    while len(melody) < max_length:
        options = transitions.get(current, {})

        if not options:
            break

        next_state = random.choices(
            list(options.keys()), weights=list(options.values()), k=1
        )[0]

        if next_state == "END":
            break

        melody.append(next_state)
        current = next_state

    return melody


if __name__ == "__main__":
    training_data, statistics = process_midi_dataset(
        r"C:\Users\user\Desktop\Code\Python\Projects\Music Generator\data\raw\MIDI"
    )
    seqs = quantize_data(training_data)
    str_seqs = tuple_to_str(seqs)
    table = build_transition_table(str_seqs)

    melody = generate_melody(table)
    print("Length:", len(melody))
    print("Full Melody:", melody)

    # print("Candidates:", len(str_seqs))  # should be 1997
    # print("First melody length:", len(str_seqs[0]))  # 68
    # print("First 5:", str_seqs[0][:5])  # ['76_0.5', '74_1.0', ...]

    # table = build_transition_table(str_seqs)

    # print("States:", len(table))  # expect ~200-500
    # print("START transitions:", len(table.get("START", {})))  # should be many, not 1
    # print(
    #     "END sources:", sum(1 for v in table.values() if "END" in v)
    # )  # should be many
    # total_obs = sum(sum(inner.values()) for inner in table.values())
    # print("Total observations:", total_obs)  # should be 377954 + 1997 = 379951
