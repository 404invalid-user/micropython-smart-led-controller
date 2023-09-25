import json
import time
from machine import Pin, PWM

RED_PIN = Pin(0)
GREEN_PIN = Pin(1)
BLUE_PIN = Pin(2)

red_pwm = PWM(RED_PIN)
green_pwm = PWM(GREEN_PIN)
blue_pwm = PWM(BLUE_PIN)

current_color = [0, 0, 0,0]

#  function to set the color of the LED strip
def set_color(red, green, blue, brightness):
    global current_color
    current_color = [red, green, blue,brightness]
    
    brightness = min(brightness, 100)
    # Scale the duty cycle based on the provided brightness percentage
    duty = int(brightness * 65535 / 100)

    # Calculate the duty cycle for each color channel
    red_duty = int(red * duty / 255)
    green_duty = int(green * duty / 255)
    blue_duty = int(blue * duty / 255)

    # Set the duty cycle of each PWM channel
    red_pwm.duty_u16(red_duty)
    green_pwm.duty_u16(green_duty)
    blue_pwm.duty_u16(blue_duty)

# Function to change the color of the LED strip gradually
def change_color(red, green, blue, brightness):
    # Calculate the delay based on the brightness of the color
    brightness = max(red, green, blue)
    delay = 1 / brightness

    # Change the color gradually by increasing or decreasing the brightness of each color component
    for i in range(256):
        r = int((i / 255) * red)
        g = int((i / 255) * green)
        b = int((i / 255) * blue)
        set_color(r, g, b, brightness)
        time.sleep(delay)

# Function to turn the LED strip on or off
def toggle_led_strip(on):
    if on:
        set_color(*current_color)
    else:
        set_color(0, 0, 0)

# Set the initial color to red
set_color(255, 0, 0, 50)

# get config
def LoadConfig(file):
    f = open(file)
    text = f.read()
    f.close()
    return json.loads(text)

config = LoadConfig('config.json')

from phew import server, connect_to_wifi
from phew.template import render_template


connect_to_wifi(config['WIFI_SSID'], config['WIFI_PASSWORD'])

@server.route("/", methods=["GET"])
def index(request):
    return await render_template("index.html")


@server.route("/setrgb", methods=["POST"])
def setrgb(request):
    red = int(request.data.get("red", 0))
    green = int(request.data.get("green", 0))
    blue = int(request.data.get("blue", 0))
    brightness = int(request.data.get('brightness',100))
    set_color(red, green, blue,brightness)
    return "Gosh, a request", 200, "text/html"

@server.route("/fadergb", methods=["POST"])
def fadergb(request):
    red = int(request.data.get("red", 0))
    green = int(request.data.get("green", 0))
    blue = int(request.data.get("blue", 0))
    brightness = int(request.data.get('brightness',100))
    change_color(red, green, blue,brightness)
    return "Gosh, a request", 200, "text/html"


@server.route("/value", methods=["GET"])
def value(request):
    r, g, b, brightness = current_color
    response = {
        "r": r,
        "g": g,
        "b": b,
        "brightness": brightness
    }
    return json.dumps(response)

@server.route("/status-code", methods=["GET", "POST"])
def status_code(request):
  return "Here, have a status code", 200, "text/html"


@server.catchall()
def catchall(request):
  return "Not found", 404

server.run()
