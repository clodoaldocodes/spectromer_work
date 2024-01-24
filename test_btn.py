import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

def button_callback(channel):
    print("Button was pushed!")

GPIO.setwarnings(False) # Ignore warning for now

GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.add_event_detect(14,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge

while True:
    a = GPIO.event_detected(14)
    if a:
        #if GPIO.input(14) == GPIO.RISING:
        message = input("Press enter to quit\n\n") # Run until someone presses enter

GPIO.cleanup() # Clean up