import serial
import time


class GrundigPN200():
    """Driver for the Grundig PN200 power supply over a serial link.

    This class exposes a small, blocking, high-level API to control both
    channels (A and B) of the PN200. Methods are named in snake_case and
    channel-specific state is stored on the instance (channel_a_*/channel_b_*).

    Notes:
    - All serial communication is simple line-based ASCII. Commands sent
      to the instrument are returned as decoded, stripped text by
      `send_cmd` when applicable.
    - Call `connect_to` (or instantiate) before issuing commands.
    """

    serial = None
    channel_a_voltage = 0.0
    channel_a_current = 0.0
    channel_a_state = False

    channel_b_voltage = 0.0
    channel_b_current = 0.0
    channel_b_state = False

    def __init__(self, comport: str = "COM3", baudrate: int = 9600):
        """Create the driver and open a serial connection.

        This constructor attempts to open the requested serial port using
        `connect_to`. If the port is unavailable an exception from the
        underlying serial driver will propagate.

        Args:
            comport: Serial port name (e.g. "COM3").
            baudrate: Serial baud rate.
        """
        self.set_remote()
        self.set_independent_mode()
        self.connect_to(comport, baudrate)

    def connect_to(self, comport: str = "COM3", baudrate: int = 9600):
        """Open (or switch) the serial connection to the device.

        If an existing connection exists it will be closed cleanly before
        opening the new one. The opened Serial object is stored on
        `self.serial`.

        Args:
            comport: Serial device identifier (platform specific, e.g. "COM3").
            baudrate: Serial port baud rate.

        Raises:
            serial.SerialException: If the port cannot be opened.
        """
        if self.serial:
            try:
                self.serial.close()
            except Exception:
                pass
        ser = serial.Serial(comport, baudrate, timeout=1)
        print(ser)
        self.serial = ser

    def send_cmd(self, cmd: str) -> str:
        """Send a command line to the instrument and return its response.

        This helper writes the ASCII command followed by a newline, waits a
        short moment for the device to process the command, then reads one
        line from the serial input. The returned value is the decoded and
        stripped text line ('' if nothing was received).

        Args:
            cmd: Command string (without trailing newline). Examples: "SEL_A",
                 "VSET 5.0" or compound strings separated by ';'.

        Returns:
            Decoded response string from the device (stripped of whitespace).

        Raises:
            RuntimeError: If the serial port is not open.
        """
        if not self.serial:
            raise RuntimeError("Serial port is not open")
        self.serial.write((cmd + '\n').encode('ascii'))
        time.sleep(0.1)
        response = self.serial.readline().decode('ascii').strip()
        return response

    def set_remote(self):
        """Place the instrument in remote (serial-controlled) mode.

        This sends the device-specific control byte to switch the front-panel
        control to the serial interface. No response is expected; calling
        code should verify behavior via readback if required.

        Raises:
            RuntimeError: If the serial port is not open.
        """
        if not self.serial:
            raise RuntimeError("Serial port is not open")
        self.serial.write(b'\x09')

    def set_local(self):
        """Return the instrument to local (front-panel) control.

        Sends the control byte that tells the PN200 to accept front-panel
        input again. As with `set_remote`, no textual response is returned
        by this helper.

        Raises:
            RuntimeError: If the serial port is not open.
        """
        if not self.serial:
            raise RuntimeError("Serial port is not open")
        self.serial.write(b'\x01')

    def set_independent_mode(self):
        """Switch the instrument to independent channel mode.

        In independent mode channels A and B operate separately. This helper
        sends the appropriate command and returns the device response.
        """
        self.send_cmd('OPER_IND')


    def update_chnel_a(self):
        """Apply the stored settings for channel A to the instrument.

        Behavior:
        - If channel A is turned off (channel_a_state is False) the method
          selects channel A and forces VSET to 0.
        - Otherwise it builds a compact command sequence that selects A and
          sets any configured voltage/current values. Only values that are
          not None are sent.

        Returns:
            The device response string produced by `send_cmd`.
        """
        if not self.channel_a_state:
            return self.send_cmd('SEL_A; VSET 0;')

        parts = ['SEL_A']
        if self.channel_a_voltage is not None:
            parts.append(f'VSET {float(self.channel_a_voltage)}')
        if self.channel_a_current is not None:
            parts.append(f'ISET {float(self.channel_a_current)}')
        if len(parts) == 1:
            # Nothing to set, just select A
            cmd = 'SEL_A;'
        else:
            cmd = '; '.join(parts) + ';'
        return self.send_cmd(cmd)

    def update_chnel_b(self):
        """Apply the stored settings for channel B to the instrument.

        This mirrors `update_chnel_a` but operates on channel B state and
        values. If the channel is off it selects B and forces VSET 0.

        Returns:
            The device response string produced by `send_cmd`.
        """
        if not self.channel_b_state:
            return self.send_cmd('SEL_B; VSET 0;')
        parts = ['SEL_B']
        if self.channel_b_voltage is not None:
            parts.append(f'VSET {float(self.channel_b_voltage)}')
        if self.channel_b_current is not None:
            parts.append(f'ISET {float(self.channel_b_current)}')
        if len(parts) == 1:
            # Nothing to set, just select B
            cmd = 'SEL_B;'
        else:
            cmd = '; '.join(parts) + ';'
        return self.send_cmd(cmd)


    def set_channel_a(self, voltage: float = None, current: float = None):
        """Store voltage/current targets for channel A and apply them.

        Arguments that are None leave the current stored value unchanged
        (but this helper explicitly overwrites unconditionally to the
        provided value; callers should pass the current value to preserve
        it if desired).

        Returns:
            The device response from `update_chnel_a`.
        """
        self.channel_a_voltage = voltage
        self.channel_a_current = current
        return self.update_chnel_a()

    def set_channel_b(self, voltage: float = None, current: float = None):
        """Store voltage/current targets for channel B and apply them.

        See `set_channel_a` for behavior details. Returns the device response
        from `update_chnel_b`.
        """
        self.channel_b_voltage = voltage
        self.channel_b_current = current
        return self.update_chnel_b()

    def channel_a_on(self):
        """Enable (turn on) channel A and apply stored settings.

        Sets the internal channel flag and then pushes the relevant
        parameters to the instrument.
        """
        self.channel_a_state = True
        return self.update_chnel_a()

    def channel_a_off(self):
        """Disable (turn off) channel A and apply the change.

        When a channel is turned off the driver sets its output voltage to 0
        on the device to ensure a safe state.
        """
        self.channel_a_state = False
        return self.update_chnel_a()

    def channel_b_on(self):
        """Enable (turn on) channel B and apply stored settings."""
        self.channel_b_state = True
        return self.update_chnel_b()

    def channel_b_off(self):
        """Disable (turn off) channel B and apply the change."""
        self.channel_b_state = False
        return self.update_chnel_b()


if __name__ == "__main__":
    grundig = GrundigPN200()
    print(grundig.serial)



    

