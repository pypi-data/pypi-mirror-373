from enum import Enum
import pyvisa

class Channel(Enum):
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4

class DisplayState(Enum):
    OFF = 0
    ON = 1

class AttenuationRatio(Enum):
    AR100u = 0.0001
    AR200u = 0.0002
    AR500u = 0.0005
    AR1m = 0.001
    AR2m = 0.002
    AR5m = 0.005
    AR10m = 0.01
    AR20m = 0.02
    AR50m = 0.05
    AR100m = 0.1
    AR200m = 0.2
    AR500m = 0.5
    AR1 = 1
    AR2 = 2
    AR5 = 5
    AR10 = 10
    AR20 = 20
    AR50 = 50
    AR100 = 100
    AR200 = 200
    AR500 = 500
    AR1000 = 1000
    AR2000 = 2000
    AR5000 = 5000
    AR10000 = 10000
    AR20000 = 20000
    AR50000 = 50000

class Units(Enum):
    AMP = 'AMP'
    UNKN = 'UNKN'
    VOLT = 'VOLT'
    WATT = 'WATT'

class RigolMSO5000:

    def __init__(self, instr: pyvisa.Resource):
        self.instr = instr
        return

    def query_channel_offset(self, channel: Channel) -> float:
        msg = f":CHAN{channel.value}:OFFS?"
        resp = self.instr.query(msg)
        level = float(resp.strip())
        return level

    def write_channel_offset(self, channel: Channel, offset: float):
        msg = f":CHAN{channel.value}:OFFS {offset}"
        self.instr.write(msg)
        return

    def query_channel_scale(self, channel: Channel) -> float:
        msg = f":CHAN{channel.value}:SCAL?"
        resp = self.instr.query(msg)
        level = float(resp.strip())
        return level

    def write_channel_scale(self, channel: Channel, scale: float):
        msg = f":CHAN{channel.value}:SCAL {scale}"
        self.instr.write(msg)
        return

    def query_channel_probe(self, channel: Channel) -> AttenuationRatio:
        msg = f":CHAN{channel.value}:PROB?"
        resp = self.instr.query(msg)
        level = float(resp.strip())
        return AttenuationRatio(level)

    def write_channel_probe(self, channel: Channel, attenuation: AttenuationRatio):
        msg = f":CHAN{channel.value}:PROB {attenuation}"
        self.instr.write(msg)
        return

    def query_channel_display(self, channel: Channel) -> DisplayState:
        msg = f":CHAN{channel.value}:DISP?"
        resp = self.instr.query(msg)
        state = resp.strip()
        return DisplayState(state)

    def write_channel_display(self, channel: Channel, state: DisplayState):
        msg = f":CHAN{channel.value}:DISP {state.name}?"
        self.instr.write(msg)
        return

    def query_channel_units(self, channel: Channel) -> Units:
        msg = f":CHAN{channel.value}:UNIT?"
        resp = self.instr.query(msg)
        units = resp.strip()
        return Units(units)

    def write_channel_units(self, channel: Channel, units: Units):
        msg = f":CHAN{channel.value}:UNIT {units.value}?"
        self.instr.write(msg)
        return
