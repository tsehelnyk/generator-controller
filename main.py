from machine import Pin
from machine import Timer

import display_service
import time_service

import time


RELAY_TIMER_DELAY = 5000                # затримка таймера в мілісекундах
BATTERY_STATUS_CHECK_DELAY = 100000     # затримка між перевірками стану батареї

# Кнопка на GPIO4 з внутрішнім pull-up
triggerBatteryStateButton = Pin(4, Pin.IN, Pin.PULL_UP)

# Кнопка на GPIO5 з внутрішнім pull-up
batteryStateInput = Pin(5, Pin.IN, Pin.PULL_UP)

# Кнопка на GPIOx з внутрішнім pull-up
# switchAuto = Pin(x, Pin.IN, Pin.PULL_UP)

batteryCharged = True  # стан зарядки

# Зовнішні світлодіоди
ledGreen = Pin(16, Pin.OUT)         # charging
ledGreen.value(0)                   # вимкнути зелений LED
ledRed = Pin(17, Pin.OUT)           # discharged, ignition
ledRed.value(0)                     # вимкнути червоний LED
ledYellow = Pin(23, Pin.OUT)        # discharging
ledYellow.value(1)                  # увімкнути жовтий LED

# buzzer = Pin(23, Pin.OUT)

# Реле
relayIgnitionOut = Pin(18, Pin.OUT)
relayIgnitionOut.value(1)           # вимкнути реле Ignition
relayKillSwitchOut = Pin(19, Pin.OUT)
relayKillSwitchOut.value(1)         # вимкнути реле Kill Switch

operation_in_progress = False       # стан виконання операції

def battery_state_isr(pin):
   global batteryCharged
   batteryCharged =  not batteryCharged
   print("Button pressed!" + (" Battery is now CHARGING" if batteryCharged else " Battery is now DISCHARGING") + ". Battery state input: " + str(batteryStateInput.value()))

# Функція, яку викликає таймер
def relay_release(timer):
    # print("Таймер 0 спрацював!")
    relayKillSwitchOut.value(1)     # вимкнути реле Kill Switch
    relayIgnitionOut.value(1)       # вимкнути реле Ignition

def battery_status_check(timer):
    # print("Таймер 1 спрацював!")
    if batteryStateInput.value() == 1:
        global batteryCharged
        batteryCharged = not batteryCharged
        global operation_in_progress
        operation_in_progress = False

triggerBatteryStateButton.irq(trigger=Pin.IRQ_RISING, handler=battery_state_isr)
# batteryStateInput.irq(trigger=Pin.IRQ_FALLING, handler=battery_state_isr)

time_service.init_time()
oled = display_service.init_display()

# Створюємо таймер з ID=0
relayTimer = Timer(0)
batteryStatusCheckTimer = Timer(1)

# time_start = time.ticks_ms()        # час запуску програми
displayMessage = "Starting..."

while True:
    sleep = 0.5

    if batteryStateInput.value() == 1:
        if batteryCharged:
            displayMessage = time_service.local_time() + "     " + "DISCHARGING"
            ledGreen.value(0)           
            ledYellow.value(1)          
            ledRed.value(0)  
        else:
            displayMessage = time_service.local_time() + "     " + "CHARGING"
            ledGreen.value(1)           
            ledRed.value(0)  
            ledYellow.value(0)      

    if batteryStateInput.value() == 0 and not operation_in_progress:
        if batteryCharged:
            displayMessage = time_service.local_time() + "     " + "START        CHARGING"
            ledGreen.value(1)           
            ledRed.value(0)  
            ledYellow.value(1)          
            # buzzer.value(1)              
            relayIgnitionOut.value(0)   # увімкнути реле Ignition
        else:
            displayMessage = time_service.local_time() + "     " + "STOP         CHARGING"
            ledGreen.value(0)     
            ledRed.value(1)      
            ledYellow.value(1)          
            # buzzer.value(1)                
            relayKillSwitchOut.value(0) # увімкнути реле Kill Switch

        operation_in_progress = True

        relayTimer.init(period=RELAY_TIMER_DELAY, mode=Timer.ONE_SHOT, callback=relay_release) 
        batteryStatusCheckTimer.init(period=BATTERY_STATUS_CHECK_DELAY, mode=Timer.ONE_SHOT, callback=battery_status_check)
        # time_start = time.ticks_ms()

    display_service.display_message(oled, displayMessage)    
    time.sleep(sleep)
