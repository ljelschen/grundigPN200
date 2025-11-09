# Grundig PN200 Python Driver

This small driver provides a thin wrapper around a Grundig PN200 power supply using a serial connection.

Requirements
- Python 3.8+
- pyserial

Install

```powershell
```markdown
# Grundig PN200 — Python driver

A small, blocking, high-level driver for the Grundig PN200 dual-channel power supply using a serial connection.

This repository contains `Grundig_PN200.py`, a compact driver exposing a few convenience methods to control channels A and B.

## Requirements

- Python 3.8+
- pyserial

Install with PowerShell:

```powershell
pip install pyserial
```

## Quick usage

Example (save as `example.py` next to `Grundig_PN200.py`):

```python
from Grundig_PN200 import GrundigPN200

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

## What the driver provides

High-level class: `GrundigPN200`

Constructor
- GrundigPN200(comport: str = "COM3", baudrate: int = 9600)
	- Opens the serial port by calling `connect_to`. If the port cannot be opened the underlying `serial.Serial` exception will propagate.

Connection helpers
- connect_to(comport, baudrate): open (or switch) the serial port. Existing connection is closed first.

Low-level helpers
- send_cmd(cmd: str) -> str: write an ASCII command followed by newline, sleep briefly, and return one decoded response line ('' if none). Raises RuntimeError if serial port is not open.
- set_remote(): send the control byte b'\x09' to switch the instrument to remote (serial) control.
- set_local(): send the control byte b'\x01' to return the instrument to local/front-panel control.

Mode helpers
- set_independent_mode(): send the `OPER_IND` command to set independent channel mode.

Channel configuration and control
- set_channel_a(voltage: float = None, current: float = None): store values and apply them to channel A by calling `update_chnel_a()`.
- set_channel_b(voltage: float = None, current: float = None): store values and apply them to channel B.
- update_chnel_a(): push stored channel A settings to the instrument. If channel A is disabled the method selects A and forces VSET 0.
- update_chnel_b(): same as above for channel B.
- channel_a_on(), channel_a_off(), channel_b_on(), channel_b_off(): set the internal enabled flags and apply settings. When a channel is turned off the driver sets VSET to 0 on the device to ensure a safe state.

Instance attributes (public)
- `serial`: the opened pyserial Serial object (or None).
- `channel_a_voltage`, `channel_a_current`, `channel_a_state`
- `channel_b_voltage`, `channel_b_current`, `channel_b_state`

Notes on behavior and errors
- Commands are sent as simple ASCII lines and a single response line is read back by `send_cmd`.
- `send_cmd` and the `set_*` helpers will raise `RuntimeError` if the serial port isn't open.
- `connect_to` may raise `serial.SerialException` if the requested port cannot be opened.
- `set_remote` and `set_local` send control bytes and do not return textual responses; verify the instrument state with readback commands if needed.

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

- Add unit tests that mock `serial.Serial` to cover the command-building and error paths.
- Add a small CLI wrapper or example script to exercise common tasks.

If you'd like, I can also run a quick syntax check or add tests for this driver.
```
