import serial
import time


class GrundigPN200():
    """Driver for the Grundig PN200 power supply over serial.

    Methods use snake_case and channel naming (channel_a/channel_b).
    """

    serial = None

    def __init__(self, comport: str = "COM3", baudrate: int = 9600):
        """Initialize and (optionally) connect to the device.

        Args:
            comport: Serial port name (e.g. "COM3").
            baudrate: Serial baud rate.
        """
        self.connect_to(comport, baudrate)

    def connect_to(self, comport: str = "COM3", baudrate: int = 9600):
        """Open the serial connection to the device.

        If an existing connection is open it will be closed first.
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
        """Send a textual command to the device and return the response.

        Args:
            cmd: Command string (without trailing newline).

        Returns:
            The decoded, stripped response line from the device.
        """
        if not self.serial:
            raise RuntimeError("Serial port is not open")
        self.serial.write((cmd + '\n').encode('ascii'))
        time.sleep(0.1)
        response = self.serial.readline().decode('ascii').strip()
        return response

    def set_remote(self):
        """Set the instrument to remote mode (send control from serial)."""
        if not self.serial:
            raise RuntimeError("Serial port is not open")
        self.serial.write(b'\x09')

    def set_local(self):
        """Set the instrument to local mode (front-panel control)."""
        if not self.serial:
            raise RuntimeError("Serial port is not open")
        self.serial.write(b'\x01')

    def set_independent_mode(self):
        """Switch the instrument to independent operation mode."""
        self.send_cmd('OPER_IND')

    # Channel methods: A corresponds to SEL_A (previously Laser),
    # B corresponds to SEL_B (previously Fan).
    def channel_a(self, voltage: float = None, current: float = None, enable: bool = True):
        """Set channel A (SEL_A) voltage and/or current, or disable it.

        Args:
            voltage: Voltage in volts to set (e.g. 5 or 5.0). If None, voltage is not changed.
            current: Current in amperes to set (e.g. 0.01). If None, current is not changed.
            enable: If False, the channel will be disabled (VSET 0). If True, sets provided values.

        Returns:
            The device response (decoded string) if available, otherwise an empty string.
        """
        if not enable:
            return self.send_cmd('SEL_A; VSET 0;')

        parts = ['SEL_A']
        if voltage is not None:
            parts.append(f'VSET {float(voltage)}')
        if current is not None:
            parts.append(f'ISET {float(current)}')
        if len(parts) == 1:
            # Nothing to set, just select A
            cmd = 'SEL_A;'
        else:
            cmd = '; '.join(parts) + ';'
        return self.send_cmd(cmd)

    def channel_b(self, voltage: float = None, current: float = None, enable: bool = True):
        """Set channel B (SEL_B) voltage and/or current, or disable it.

        Args:
            voltage: Voltage in volts to set (e.g. 12 or 12.0). If None, voltage is not changed.
            current: Current in amperes to set. If None, current is not changed.
            enable: If False, the channel will be disabled (VSET 0). If True, sets provided values.

        Returns:
            The device response (decoded string) if available, otherwise an empty string.
        """
        if not enable:
            return self.send_cmd('SEL_B; VSET 0;')

        parts = ['SEL_B']
        if voltage is not None:
            parts.append(f'VSET {float(voltage)}')
        if current is not None:
            parts.append(f'ISET {float(current)}')
        if len(parts) == 1:
            cmd = 'SEL_B;'
        else:
            cmd = '; '.join(parts) + ';'
        return self.send_cmd(cmd)
        
if __name__ == "__main__":
    grundig = GrundigPN200()
    print(grundig.serial)

    
    
    
    