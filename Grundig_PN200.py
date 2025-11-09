import serial
import time


class GrundigPN200():
    
    serial = {}
    
    def __self__( comport: str = "COM3", baudrate: int = 9600):
        self.connectTo(comport, baudrate)
    
    
    def connectTo(self, comport: str = "COM3", baudrate: int = 9600):
        if self.serial:
            self.serial.close()
        else:
            ser = serial.Serial(comport, baudrate, timeout=1)
            print(ser)
            self.serial = ser
    
    def sendCMD(self, cmd):
        self.serial.write((cmd+'\n').encode('ascii'))
        time.sleep(0.1)
        response = self.serial.readline().decode('ascii').strip()
        return response

    def setRemote(self):
        self.serial.write(b'\x09')

    def setLocal(self):
        self.serial.write(b'\x01')

    def setIndependentMode(self):
        self.sendCMD('OPER_IND')

    def FanON(self):
        self.sendCMD('SEL_B; VSET 12;')

    def FanOFF(self):
        self.sendCMD('SEL_B; VSET 0;')

    def LaserON(self):
        self.sendCMD('SEL_A; VSET 5; ISET 0.010')

    def LaserOFF(self):
        self.sendCMD('SEL_A; VSET 0; ISET 0.010')
        
        
if __name__ == "main":
    grundig = GrundigPN200()
    print(grundig.serial)

    
    
    
    