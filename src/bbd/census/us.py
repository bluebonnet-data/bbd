from typing import Union

import us


def state_to_fips(state: Union[int, str]) -> str:
    # Convert state to fips
    if isinstance(state, int):
        state_lookup = f"{state:02d}"  # Pad with leading zero, e.g. 8 -> "08"
    else:
        state_lookup = state

    us_state = us.states.lookup(state_lookup)

    if us_state is None:
        raise RuntimeError(
            f"Could not find the requested state: {state}."
            f"Looked up: {state_lookup}."
        )

    if us_state.fips is None:
        raise RuntimeError(f"The state of {us_state} does not contain a fips code :(")

    return us_state.fips
