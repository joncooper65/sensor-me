#Talking to the pressure sensor
#-----------------------------

#STEP 1
#------

#The pi needed some config first to use the I2C bus
#here is a good guide: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
#I followed this, here are my comands

# sudo apt-get install python-smbus
# sudo apt-get install i2c-tools

# sudo nano /etc/modules ... and add these two lines
# i2c-bcm2708 
# i2c-dev

# sudo nano /etc/modprobe.d/raspi-blacklist.conf...this file was empty so I didn't need to edit it to allow spi-bcm2708 and i2c-bcm2708

# sudo nano /boot/config.txt ... and add the text
# dtparam=i2c1=on
# dtparam=i2c_arm=on

# use the following to see if it worked, it will show which I2C addresses are being used:
# sudo i2cdetect -y 1

#STEP 2
#------

#Download and install dependencies (git only needs installing once ;)
#sudo apt-get update
#sudo apt-get install git build-essential python-dev python-smbus
#cd some_project_directory
#git clone https://github.com/adafruit/Adafruit_Python_BMP.git
#cd Adafruit_Python_BMP
#sudo python setup.py install

# Now that's done, lets write a program - there are a couple of examples in the example folder that came down with the code

#!/usr/bin/python
import Adafruit_BMP.BMP085 as BMP085
import smbus
import time
import os
import sys
import urllib
import urllib2
import RPi.GPIO as GPIO

def sendData(url,key,temp,pres):
  values = {'key' : key,'field1' : temp,'field2' : pres}
  postdata = urllib.urlencode(values)
  req = urllib2.Request(url, postdata)

  log = time.strftime("%d-%m-%Y,%H:%M:%S") + ","
  log = log + "{:.3f}C".format(temp) + ","
  log = log + "{:.3f}mBar".format(pres) + ","

  try:
    # Send data to Thingspeak
    response = urllib2.urlopen(req, None, 5)
    html_string = response.read()
    response.close()

  except urllib2.HTTPError, e:
    log = log + 'Server could not fulfill the request. Error code: ' + e.code
    print log
  except urllib2.URLError, e:
    log = log + 'Failed to reach server. Reason: ' + e.reason
    print log
  except:
    log = log + 'Unknown error'
    print log

def main():

  # Setup GPIO
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  ledGpio = 17
  GPIO.setup(ledGpio , GPIO.OUT)

  try:
    sensor = BMP085.BMP085()
    while True:
      temperature = sensor.read_temperature()
      pressure = sensor.read_pressure()
      sendData('https://api.thingspeak.com/update','84T4PU3OJKFDE6MC',temperature,pressure)
      sys.stdout.flush()

      print 'Temp = {0:0.2f} *C'.format(temperature)
      print 'Pressure = {0:0.2f} Pa'.format(pressure)
      print 'Altitude = {0:0.2f} m'.format(sensor.read_altitude())
      print 'Sealevel Pressure = {0:0.2f} Pa'.format(sensor.read_sealevel_pressure())

      # Toggle LED while we wait for next reading
      #Delay for a minute - Thingspeak doesn't accept more than one post per 15s per channel
      for i in range(0,60):
        GPIO.output(ledGpio, not GPIO.input(ledGpio))
        time.sleep(1)

  except Exception, e:
    GPIO.cleanup()
    print "Exception! " + time.strftime("%d-%m-%Y,%H:%M:%S")
    print str(e)

if __name__=="__main__":
   main()
