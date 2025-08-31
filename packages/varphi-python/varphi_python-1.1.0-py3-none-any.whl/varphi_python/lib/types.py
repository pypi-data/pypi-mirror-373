from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List
from collections import defaultdict
from varphi_devkit import VarphiTapeCharacter, VarphiHeadDirection
from .exceptions import VarphiTuringMachineHaltedException, VarphiNoTallyException


@dataclass(frozen=True)
class Instruction:
    """Represents an instruction for a Turing machine, detailing the next state,
    character to place, and the direction to move the head.
    """
    next_state: State
    character_to_place: VarphiTapeCharacter
    direction_to_move: VarphiHeadDirection

class State:
    """Represents a state in the Turing machine. This includes instructions for
    both when the tape head is on a blank or tally.

    Note that a state can have multiple instructions for the same character,
    in the case of a non-deterministic machine.
    """
    on_tally_instructions: List[Instruction]
    on_blank_instructions: List[Instruction]

    def __init__(self) -> None:
        """Initializes a State object."""
        self.on_tally_instructions = []
        self.on_blank_instructions = []

    def add_on_tally_instruction(self, instruction: Instruction) -> None:
        """Adds an instruction for when the tape head is on a tally."""
        if instruction in self.on_tally_instructions:
            return
        self.on_tally_instructions.append(instruction)

    def add_on_blank_instruction(self, instruction: Instruction) -> None:
        """Adds an instruction for when the tape head is on a blank."""
        if instruction in self.on_blank_instructions:
            return
        self.on_blank_instructions.append(instruction)


class Tape:
    """A class representing the tape of a Turing machine."""
    _tape: defaultdict[int, VarphiTapeCharacter]
    _maximum_accessed_index: int
    _minimum_accessed_index: int

    def __init__(self, initial_values: list[VarphiTapeCharacter]) -> None:
        self._tape = defaultdict(lambda: VarphiTapeCharacter.BLANK)  # Tape characters default to blank
        self._maximum_accessed_index = 0
        self._minimum_accessed_index = 0

        index_of_first_tally = None
        for i in range(len(initial_values)):
            if initial_values[i] == VarphiTapeCharacter.TALLY:
                index_of_first_tally = i
                break
        if index_of_first_tally is None:
            raise VarphiNoTallyException("Error: Input tape must contain at least one tally (1).")
        

        i = 0
        for j in range(index_of_first_tally, len(initial_values)):
            self[i] = initial_values[j]
            i += 1
    

    def _update_maximum_and_minimum_indices_accessed(self, index: int) -> None:
        self._maximum_accessed_index = max(self._maximum_accessed_index, index)
        self._minimum_accessed_index = min(self._minimum_accessed_index, index)

    def __getitem__(self, index: int) -> VarphiTapeCharacter:
        self._update_maximum_and_minimum_indices_accessed(index)
        return self._tape[index]

    def __setitem__(self, index: int, value: VarphiTapeCharacter) -> None:
        self._update_maximum_and_minimum_indices_accessed(index)
        self._tape[index] = value

    def __repr__(self) -> str:
        representation = ""
        for i in range(self._minimum_accessed_index, self._maximum_accessed_index + 1):
            representation += "1" if self._tape[i] == VarphiTapeCharacter.TALLY else "0"
        return representation
    
    def __str__(self) -> str:
        return self.__repr__()


class Head:
    """A class representing the head of a Turing machine."""
    _tape: Tape
    _current_tape_cell_index: int

    def __init__(self, tape: Tape) -> None:
        self._tape = tape
        self._current_tape_cell_index = 0

    def right(self) -> None:
        """Move the head one cell to the right."""
        self._current_tape_cell_index += 1

    def left(self) -> None:
        """Move the head one cell to the left."""
        self._current_tape_cell_index -= 1

    def read(self) -> VarphiTapeCharacter:
        """Read the value of the current cell."""
        return self._tape[self._current_tape_cell_index]

    def write(self, value: VarphiTapeCharacter) -> None:
        """Write a value to the current cell."""
        self._tape[self._current_tape_cell_index] = value

    def __repr__(self) -> str:
        return str(self._current_tape_cell_index)


class TuringMachine:
    """A class representing a Turing machine."""
    tape: Tape
    head: Head
    state: State

    def __init__(self, tape: Tape, initial_state: State) -> None:
        self.tape = tape
        self.head = Head(tape)
        self.state = initial_state

    def step(self):
        """Execute one step of the Turing machine

        Raises `VarphiTuringMachineHaltedException` if the machine halts.
        """
        tape_character = self.head.read()
        if tape_character == VarphiTapeCharacter.TALLY:
            possible_instructions_to_follow = self.state.on_tally_instructions
        else:
            possible_instructions_to_follow = self.state.on_blank_instructions
        if len(possible_instructions_to_follow) == 0:
            raise VarphiTuringMachineHaltedException()
        next_instruction = random.choice(possible_instructions_to_follow)
        self.state = next_instruction.next_state
        self.head.write(next_instruction.character_to_place)
        if next_instruction.direction_to_move == VarphiHeadDirection.LEFT:
            self.head.left()
        else:
            self.head.right()
