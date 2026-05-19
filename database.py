import json
import os


def load_previous_state(state_file):

    # FILE DOES NOT EXIST
    if not os.path.exists(state_file):
        return {}

    # FILE EXISTS BUT EMPTY
    if os.path.getsize(state_file) == 0:
        return {}

    try:

        with open(state_file, "r") as file:
            return json.load(file)

    except json.JSONDecodeError:

        # INVALID JSON
        return {}


def save_current_state(state_file, data):

    with open(state_file, "w") as file:

        json.dump(
            data,
            file,
            indent=4
        )