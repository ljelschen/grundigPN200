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