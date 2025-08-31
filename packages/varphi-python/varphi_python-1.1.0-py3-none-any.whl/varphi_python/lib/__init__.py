"""
Varphi-Python runtime library

This library includes types and functions used by compiled Varphi programs.
"""

from varphi_devkit import VarphiTapeCharacter, VarphiHeadDirection
from .types import Instruction, State
from .functions import get_tape_from_stdin, execute_turing_machine
