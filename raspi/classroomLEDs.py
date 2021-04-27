import time
import datetime
import requests
import threading
from requests.exceptions import HTTPError
import adafruit_dotstar as dotstar
import board

num_pixels = 180
led_modes = {"solid": 0, "pulse": 1}
led_color = (0, 0, 0)
led_brightness = 0
led_mode = 0 # 0: solid; 1: pulse

def update_LEDs():
    # Use SPI on the Raspberry Pi which is faster than bit banging.
    # Explicitly slow the baud rate to 16 MHz using the undocumented parameter which
    #   appears to improve reliability.
    # The pixel order of the DotStar strips that we have appear to be BGR, but there are
    #   still unresolved issues regarding colors.   
    pixels= dotstar.DotStar(board.SCK, board.MOSI, num_pixels, brightness=0.2, pixel_order=dotstar.BGR, auto_write=False, baudrate=16000000)
    
    temp_led_brightness = 0;
    dimming = True;
    
    while True:
        if dimming:
            temp_led_brightness -= 0.005
        else:
            temp_led_brightness += 0.005
        
        if temp_led_brightness < 0:
            temp_led_brightness = 0 
            dimming = False
        elif temp_led_brightness > led_brightness:
            temp_led_brightness = led_brightness
            dimming = True
        
        if led_mode == 0:
            color_with_brightness = led_color + (led_brightness,)
        else:
            color_with_brightness = led_color + (temp_led_brightness,)
        
        #print(color_with_brightness)
        pixels.fill(color_with_brightness)
        pixels.show()
        time.sleep(0.01)


led_thread = threading.Thread(target = update_LEDs, daemon=True)
led_thread.start()

#Schedule
# 7:35-9:00, 9:05-10:30, 10:35-12:00, 12:05-1:30
# currently need hardcode schedule, make a way to adjust normal schedule
# be able to add in priority date (possibly use priority queue) to override normal schedule
# Input for color and brightness preset in schedule?
def check_schedule():
    #per 1: red, per 2: blue, per 3: green, per 4: yellow
    test_schedule = [["10:05:00", "10:06:00"]]
    norm_schedule = [["7:35:00", "9:00:00"], ["9:05:00", "10:30:00"], ["10:35:00", "12:00:00"], ["12:05:00", "1:30:00"]]
    now = datetime.now()
    period = 1
    while True:
        crnt_time = now.strftime("%H:%M:%S")
        if crnt_time >= norm_scedule[1][1] and crnt_time <= norm_scedule[1][2]:
            led_color = RED
            pixels.fill(color_with_brightness)
        pixels.show()
        time.sleep(0.5)
        else if crnt_time >= norm_scedule[2][1] and crnt_time <= norm_scedule[2][2]:
            led_color = BLUE
            pixels.fill(color_with_brightness)
        pixels.show()
        time.sleep(0.5)
        else if crnt_time >= norm_scedule[3][1] and crnt_time <= norm_scedule[3][2]:
            led_color = green
            pixels.fill(color_with_brightness)
        pixels.show()
        time.sleep(0.5)
        else if crnt_time >= norm_scedule[4][1] and crnt_time <= norm_scedule[4][2]:
            led_color = yellow
            pixels.fill(color_with_brightness)
        pixels.show()
        time.sleep(0.5)
        else:
            False

#Override Schedule
# possibly use priority queue
# can either create override in checl_schedule(), or
#     add override check when implementing in main
        
        
        



while True:
    
    try:
        # eventually, update the URL to that for the server running on EC2
        url = "http://localhost:3000/leds/1"
        response = requests.get(url = url)
        response.raise_for_status()
        
        jsonResponse = response.json()
        print(jsonResponse)
        
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    
    scenes = jsonResponse["scenes"]
    print(scenes)
    
    # don't assume that the scenes are sorted by time; it is important that they are
    #   since the LEDs will be set to the most recent scence whose time has passed
    scenes.sort(key=lambda k: k['time'])
    
    for scene in scenes:
        print(scene)
        print(scene["time"])
        print(scene["color"])
        print(scene["brightness"])
        print(scene["mode"])
        
        sch_date = datetime.datetime.strptime(scene["time"], '%Y-%m-%dT%H:%M:%S.%f')
        date_now = datetime.datetime.now()
        sch_time = datetime.time(sch_date.hour, sch_date.minute, sch_date.second)
        now = datetime.time(date_now.hour, date_now.minute, date_now.second)
        print(sch_time)
        print(now)
        
        if sch_date < date_now and sch_time < now:
            # the color can be specified as a tuple with 4 elements: (R, G, B, brightness)
            led_color = tuple(int(scene["color"][i:i+2], 16) for i in (2, 4, 6))
            print(led_color)
            led_brightness = scene["brightness"]
            print(led_brightness)
            led_mode = led_modes[scene["mode"]]
            print(led_mode)
    
    # a more sophisticated approach is needed where the server is checked only 
    #   occasionally but the LEDs are updated based on the last-read schedule more
    #   frequently
    time.sleep(60)
