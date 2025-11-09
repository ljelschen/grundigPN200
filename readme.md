# Grundig PN200 Python Driver

This small driver provides a thin wrapper around a Grundig PN200 power supply using a serial connection.

## Quick usage

```python
from grundig_PN200 import GrundigPN200

# Create driver — change COM port to match your system
psu = GrundigPN200(comport="COM3", baudrate=9600)

# Configure channel A: set stored targets (does not enable output)
psu.set_channel_a(voltage=5.0, current=0.010)

# Enable channel A output
psu.channel_a_on()

# Configure and enable channel B in one call
psu.set_channel_b(voltage=12.0, current=0.100)
psu.channel_b_on()

print('done')
```

## Example command layout

The driver builds compact command sequences such as:

```
SEL_A; VSET 5.0; ISET 0.010;
```

which the device accepts as a single write. `update_chnel_a`/`update_chnel_b` will only include VSET/ISET if the stored values are not None.

## Safety

- Always confirm the correct COM port and baud rate before enabling outputs.
- Make sure the expected loads are connected and rated for the voltages/currents you will enable.

## Next steps (optional)

- Add other modes (if you find a manual)

```
