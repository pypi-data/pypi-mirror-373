from enum import Enum
import pyvisa

class Channel(Enum):
    CH1 = 1
    CH2 = 2
    CH3 = 3

class OutputState(Enum):
    OFF = 0
    ON = 1

class RigolDP800:

    def __init__(self, instr: pyvisa.Resource):
        self.instr = instr
        return

    def query_source_current_level_immediate_amplitude(self, channel: Channel) -> float:
        msg = f":SOUR{channel.value}:CURR?"
        resp = self.instr.query(msg)
        level = float(resp.strip())
        return level

    def write_source_current_level_immediate_amplitude(self, channel: Channel, level: float):
        msg = f":SOUR{channel.value}:CURR {level}"
        self.instr.write(msg)
        return

    def query_source_voltage_level_immediate_amplitude(self, channel: Channel) -> float:
        msg = f":SOUR{channel.value}:VOLT?"
        resp = self.instr.query(msg)
        level = float(resp.strip())
        return level

    def write_source_voltage_level_immediate_amplitude(self, channel: Channel, level: float):
        msg = f":SOUR{channel.value}:VOLT {level}"
        self.instr.write(msg)
        return

    def query_output_state(self, channel: Channel) -> OutputState:
        msg = f":OUTP:STAT? {channel.name}"
        resp = self.instr.query(msg)
        output_state = resp.strip()
        return OutputState(output_state)

    def write_output_state(self, channel: Channel, state: OutputState):
        msg = f":OUTP:STAT {channel.name},{state.name}"
        self.instr.write(msg)
        return
