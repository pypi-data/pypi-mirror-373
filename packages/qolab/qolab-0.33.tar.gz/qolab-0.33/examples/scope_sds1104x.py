import pyvisa
from qolab.hardware.scope import SDS1104X

if __name__ == "__main__":
    print("Testing SDS1104X")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("TCPIP::192.168.0.61::INSTR")
    scope = SDS1104X(instr)
    print(f"ID: {scope.idn}")
    print(f"Ch1 mean: {scope.mean(1)}")
    print(f"Ch1 available points: {scope.getAvailableNumberOfPoints(1)}")
    print(f"Sample Rate: {scope.getSampleRate()}")
    print(f"Time per Div: {scope.getTimePerDiv()}")
    print(f"Ch1 Volts per Div: {scope.getChanVoltsPerDiv(1)}")
    print(f"Ch1 Voltage Offset: {scope.getChanOffset(1)}")
    ch1 = scope.getTrace(1)
    ch1.plot()
