import SaniTrendCloud
import time
from pycomm3 import LogixDriver
from pycomm3.exceptions import CommError


import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import PWMLED


def scale(Input, Input_Min, Input_Max, Scaled_Min, Scaled_Max):
    slope = (Scaled_Max - Scaled_Min) / (Input_Max - Input_Min)
    offset = Scaled_Min - (Input_Min * slope)
    output = (slope * Input) + offset
    return output


# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
ads.gain = 1
# you can specify an I2C adress instead of the default 0x48
# ads = ADS.ADS1115(i2c, address=0x49)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P1)

led = PWMLED(18)
led.off()

def main():

    # Set up SaniTrend parameters, tags, cloud configurations, etc...
    SaniTrend = SaniTrendCloud.Config(ConfigFile="../SaniTrendConfig.json")

    # Setup PLC Communication Driver
    PLC = LogixDriver(SaniTrend.PLCIPAddress)

    PLCErrorCount = 0
    runCode = True

    while runCode:
        try:
            # Get Connection Status For EMS
            SaniTrend.ConnectionStatus()
            value = scale(chan.value, 4799.853515625 , 23999.267578125, 30, 230)
            value = round(value, 2)
            led.off()
            if PLC.connected:
                # Read PLC tags
                SaniTrend.TagData = PLC.read(*SaniTrend.Tags)
                # Log Data to InfluxDB and send to Thingworx
                SaniTrend.LogData()
                PLCErrorCount = 0
                
                
                PLC.write(
                    (
                        'Test_Analog_Out', SaniTrend.Sim_Value
                    ),
                    (
                        'RPI_Value', value
                    )
                )

            else:
                PLC.open()

            time.sleep(SaniTrend.PLCScanRate * 0.001)
            led.pulse(fade_in_time=0.1, fade_out_time=0.1)
        except CommError:
            PLCErrorCount += 1
            print(f'Communication Error! Fail Count: {PLCErrorCount}')
            SaniTrend.LogErrorToFile('PLC Comms Failed', CommError)
            led.on()
            if PLCErrorCount < 6:
                time.sleep(10)
            else:
                time.sleep(30)
            PLC = LogixDriver(SaniTrend.PLCIPAddress)

        except KeyboardInterrupt:
            print("\n\nExiting Python and closing PLC connection...\n\n\n")
            PLC.close()
            runCode = False

        except Exception as error:
            print(error)
            print('Shutting Down...')
            PLC.close()
            SaniTrend.LogErrorToFile('Final Exception', error)
            runCode = False

if __name__ == "__main__":
    main()