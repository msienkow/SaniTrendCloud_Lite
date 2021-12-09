import SaniTrendCloud
import time
from pycomm3 import LogixDriver
from pycomm3.exceptions import CommError


import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from gpiozero import PWMLED
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


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

disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
# font = ImageFont.load_default()
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
text = [
    {
        'title' : 'Temperature',
        'text' : ''
    },
    {
        'title' : 'Conductivity',
        'text' : ''
    },
    {
        'title' : 'SaniTrend',
        'text' : ''
    }
]
text_items = len(text)

def main():
    
    # Set up SaniTrend parameters, tags, cloud configurations, etc...
    SaniTrend = SaniTrendCloud.Config(ConfigFile="../SaniTrendConfig.json")

    # Setup PLC Communication Driver
    PLC = LogixDriver(SaniTrend.PLCIPAddress)

    PLCErrorCount = 0
    text_item = 0
    
    runCode = True

    while runCode:
        try:
            led.value = 0.5
            
            min = 4799.853515625
            max = 23999.267578125
            value = scale(chan.value, min, max, 30, 230)
            value = round(value, 2)
           
            # Get Connection Status For EMS
            SaniTrend.ConnectionStatus()

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

            led.value = 0
            
            text[0]['text'] = f'Temp: {value}°F'
            temp_voltage = round(chan.voltage, 2)
            text[1]['text'] = f'Cond: {temp_voltage}mS/cm'
            connection_text = 'Connected' if SaniTrend.isConnected else 'Disconnected'
            text[2]['text'] = connection_text
            draw.rectangle((0, 0, width, height), outline=0, fill=0)
            
            draw.text((x, top + 0), text[text_item]['title'], font=font, fill=255)
            draw.text((x, top + 16), text[text_item['text']], font=font, fill=255)
            # draw.text((x, top + 8), voltage_text, font=font, fill=255)
            # draw.text((x, top + 16), value_text, font=font, fill=255)
            # draw.text((x, top + 25), connection_text, font=font, fill=255)

            # Display image.
            disp.image(image)
            disp.show()

            text_item += 1

            time.sleep(SaniTrend.PLCScanRate * 0.001)
            
                   
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
            disp.fill(0)
            disp.show()
            led.value = 0

        except Exception as error:
            print(error)
            print('Shutting Down...')
            PLC.close()
            SaniTrend.LogErrorToFile('Final Exception', error)
            runCode = False
            disp.fill(0)
            disp.show()
            led.value = 0
            

if __name__ == "__main__":
    main()