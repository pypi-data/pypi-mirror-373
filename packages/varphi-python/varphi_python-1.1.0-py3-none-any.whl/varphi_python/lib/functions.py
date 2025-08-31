import sys
from .types import State, Tape, VarphiTapeCharacter, TuringMachine
from .exceptions import VarphiInvalidTapeCharacterException, VarphiDomainError, VarphiTuringMachineHaltedException

def get_tape_from_stdin() -> Tape:
    """Reads the input tape from standard input and returns it as a Tape object."""
    initial_characters = []
    while (input_character := sys.stdin.read(1)) not in {"\n", "\r"}:
        if input_character == '1':
            initial_characters.append(VarphiTapeCharacter.TALLY)
        elif input_character == '0':
            initial_characters.append(VarphiTapeCharacter.BLANK)
        else:
            raise VarphiInvalidTapeCharacterException(f"Invalid tape character {input_character} (ASCII #{ord(input_character)})")
    return Tape(initial_characters)

def execute_turing_machine(initial_state: State | None, tape: Tape) -> None: 
    """Construct the Turing machine given an initial state and run it.

    Reads the input tape from standard input and runs the Turing machine until it halts.
    """
    if initial_state is None:
        raise VarphiDomainError("Error: Input provided to an empty Turing machine.")
    turing_machine = TuringMachine(tape, initial_state)
    while True:
        try:
            turing_machine.step()
        except VarphiTuringMachineHaltedException:
            break
