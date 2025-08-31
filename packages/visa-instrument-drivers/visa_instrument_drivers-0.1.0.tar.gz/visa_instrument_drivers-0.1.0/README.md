# visa-instrument-drivers

Tiny, pragmatic VISA instrument drivers built on PyVISA.

```python
from visa_instrument_drivers import RigolDP800

psu = RigolDP800("DP832A")
psu.connect("TCPIP::192.168.0.107::INSTR")
psu.write_source_voltage(13.5)          # CH1
print(psu.read_source_voltage())        # 13.5 (setpoint)
psu.disconnect()