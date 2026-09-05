from machine import Pin
from machine import Timer

import display_service
import time_service

import time


RELAY_TIMER_DELAY = 3000                # затримка таймера реле в мілісекундах
BATTERY_STATUS_CHECK_DELAY = 300000     # затримка між перевірками стану батареї
BLINK_DELAY = 500                       # затримка між блиманням світлодіодів

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

# Базєр
# buz = Pin(23, Pin.OUT)

# Ініціалізація реле
relayIgnitionOut = Pin(18, Pin.OUT)
relayIgnitionOut.value(1)           # вимкнути реле Ignition
relayKillSwitchOut = Pin(19, Pin.OUT)
relayKillSwitchOut.value(1)         # вимкнути реле Kill Switch

operationInProgress = False       # стан виконання операції

def battery_state_isr(pin):
   global batteryCharged
   batteryCharged =  not batteryCharged

def relay_release(timer):
    relayKillSwitchOut.value(1)     # вимкнути реле Kill Switch
    relayIgnitionOut.value(1)       # вимкнути реле Ignition

def battery_status_check(timer):
    if batteryStateInput.value() == 1:
        global batteryCharged
        batteryCharged = not batteryCharged
        global operationInProgress
        operationInProgress = False

def led_blink(timer, led):
    led.value(0)

triggerBatteryStateButton.irq(trigger=Pin.IRQ_RISING, handler=battery_state_isr)

time_service.init_time()
oled = display_service.init_display()

# Створюємо таймер з ID=0
relayTimer = Timer(0)
batteryStatusCheckTimer = Timer(1)
ledTimer = Timer(2)

# time_start = time.ticks_ms()        # час запуску програми
displayMessage = "Starting..."
sleep = 0.5
operation = ""

while True:
    if batteryStateInput.value() == 1 and not operationInProgress and batteryStatusCheckTimer.active() == False:
        if batteryCharged:
            operation = "DISCHARGING"
            ledGreen.value(0)           
            ledYellow.value(1)          
            ledRed.value(0)  
        else:
            operation = "CHARGING"
            ledGreen.value(1)           
            ledRed.value(0)  
            ledYellow.value(0)      

    if batteryStateInput.value() == 0 and not operationInProgress and batteryStatusCheckTimer.active() == False:
        if batteryCharged:
            operation = "START CHARGING"
            ledGreen.value(1)           
            ledRed.value(0)  
            ledYellow.value(1)                
            relayIgnitionOut.value(0)   # увімкнути реле Ignition
        else:
            operation = "STOP CHARGING"
            ledGreen.value(0)     
            ledRed.value(1)      
            ledYellow.value(1)          
            relayKillSwitchOut.value(0) # увімкнути реле Kill Switch

        operationInProgress = True

        relayTimer.init(period=RELAY_TIMER_DELAY, mode=Timer.ONE_SHOT, callback=relay_release) 
        batteryStatusCheckTimer.init(period=BATTERY_STATUS_CHECK_DELAY, mode=Timer.ONE_SHOT, callback=battery_status_check)

    if batteryStateInput.value() == 0 and operationInProgress:
        operation = "OPERATION IN PROGRESS"
        if batteryCharged:
            ledGreen.value(1)
            ledTimer.init(period=BLINK_DELAY, mode=Timer.ONE_SHOT, callback=lambda t: led_blink(t, ledGreen))
        else:
            ledRed.value(1)
            ledTimer.init(period=BLINK_DELAY, mode=Timer.ONE_SHOT, callback=lambda t: led_blink(t, ledRed))

    if batteryStateInput.value() == 1 and operationInProgress:
        operation = "WAITING 4 BATTERY CHECK"
        if batteryCharged:
            ledGreen.value(1)
            ledTimer.init(period=BLINK_DELAY, mode=Timer.ONE_SHOT, callback=lambda t: led_blink(t, ledGreen))
        else:
            ledRed.value(1)
            ledTimer.init(period=BLINK_DELAY, mode=Timer.ONE_SHOT, callback=lambda t: led_blink(t, ledRed))
        
    displayMessage = time_service.local_time() + "     " + operation
    display_service.display_message(oled, displayMessage)    
    time.sleep(sleep) 
                 