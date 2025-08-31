from varphi_devkit import VarphiCompiler, VarphiLine, VarphiTapeCharacter, VarphiHeadDirection

class VarphiToPythonCompiler(VarphiCompiler):
    _initial_state_found: bool
    _seen_state_names: set[str]
    _output: str

    def __init__(self):
        self._initial_state_found = False
        self._seen_state_names = set()
        self._output = """from varphi_python.lib import VarphiTapeCharacter, VarphiHeadDirection, Instruction, State, get_tape_from_stdin, execute_turing_machine
if __name__ == "__main__":
    initial_state = None
"""
        super().__init__()
    
    def handle_line(self, line: VarphiLine):
        if line.if_state not in self._seen_state_names:
            self._output += f"    {line.if_state} = State()\n"
            if not self._initial_state_found:
                self._output += f"    initial_state = {line.if_state}\n"
                self._initial_state_found = True
            self._seen_state_names.add(line.if_state)
        if line.then_state not in self._seen_state_names:
            self._output += f"    {line.then_state} = State()\n"
            self._seen_state_names.add(line.then_state)
        instruction = f"Instruction(next_state={line.then_state}, character_to_place={'VarphiTapeCharacter.TALLY' if line.then_character == VarphiTapeCharacter.TALLY else 'VarphiTapeCharacter.BLANK'}, direction_to_move={'VarphiHeadDirection.RIGHT' if line.then_direction == VarphiHeadDirection.RIGHT else 'VarphiHeadDirection.LEFT'})"
        if line.if_character == VarphiTapeCharacter.TALLY:
            self._output += f"    {line.if_state}.add_on_tally_instruction({instruction})\n"
        else:
            self._output += f"    {line.if_state}.add_on_blank_instruction({instruction})\n"
    
    def generate_compiled_program(self) -> str:
        self._output += f"    tape = get_tape_from_stdin()\n"
        self._output += f"    output_tape = execute_turing_machine(initial_state, tape)\n"
        self._output += f"    print(tape)\n"
        return self._output
