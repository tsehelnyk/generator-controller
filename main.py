from machine import Pin
from machine import Timer
from machine import WDT

import time
import machine

import display_service
import time_service

RELAY_TIMER_DELAY = 5*1000              # затримка таймера реле в мілісекундах
BLINK_DELAY = 500                       # затримка між блиманням світлодіодів
RESTART_DELAY = 30*60*1000              # затримка між перезапусками ESP32
WATCHDOG_TIMEOUT = 5*1000               # таймаут watchdog в мілісекундах

# # Кнопка на GPIO4 з внутрішнім pull-up
# triggerBatteryStateButton = Pin(4, Pin.IN, Pin.PULL_UP)

# Кнопка на GPIO5 з внутрішнім pull-up
batteryStateInput = Pin(5, Pin.IN, Pin.PULL_UP)

# Кнопка на GPIO4 з внутрішнім pull-up
chargingStateInput = Pin(4, Pin.IN, Pin.PULL_UP)

# Зовнішні світлодіоди
ledGreen = Pin(16, Pin.OUT)         # charging
ledGreen.value(0)                   # вимкнути зелений LED
ledRed = Pin(17, Pin.OUT)           # discharged, ignition
ledRed.value(0)                     # вимкнути червоний LED
ledYellow = Pin(23, Pin.OUT)        # discharging
ledYellow.value(1)                  # увімкнути жовтий LED

# buzzer = Pin(23, Pin.OUT)

# Ініціалізація реле
relayIgnitionOut = Pin(18, Pin.OUT)
relayIgnitionOut.value(1)           # вимкнути реле Ignition
relayKillSwitchOut = Pin(19, Pin.OUT)
relayKillSwitchOut.value(1)         # вимкнути реле Kill Switch

operationInProgress = False         # стан виконання операції

# Ініціалізація watchdog (5 секунд)
wdt = WDT(timeout=WATCHDOG_TIMEOUT)

def restart(timer):
    machine.reset()

def led_blink(timer, led):
    led.value(0)

def relay_release(timer):
    relayKillSwitchOut.value(1)     # вимкнути реле Kill Switch
    relayIgnitionOut.value(1)       # вимкнути реле Ignition

time_service.init_time()
oled = display_service.init_display()

relayTimer = Timer(0)
ledTimer = Timer(2)
restartTimer = machine.Timer(3)

displayMessage = "Starting..."
sleep = 1
operation = Operation.discharging

while True:
    if batteryStateInput.value() == 1 and not operationInProgress:
        if chargingStateInput.value() == 1:
            operation = Operation.discharging
            ledGreen.value(0)           
            ledYellow.value(1)          
            ledRed.value(0)  
        else:
            operation = Operation.charging
            ledGreen.value(1)           
            ledRed.value(0)  
            ledYellow.value(0)      

    if batteryStateInput.value() == 0 and not operationInProgress:
        if chargingStateInput.value() == 1:
            operation = Operation.start_charging
            ledGreen.value(1)           
            ledRed.value(0)  
            ledYellow.value(1)                
            relayIgnitionOut.value(0)   # увімкнути реле Ignition
        else:
            operation = Operation.stop_charging
            ledGreen.value(0)     
            ledRed.value(1)      
            ledYellow.value(1)          
            relayKillSwitchOut.value(0) # увімкнути реле Kill Switch

        operationInProgress = True

        relayTimer.init(period=RELAY_TIMER_DELAY, mode=Timer.ONE_SHOT, callback=relay_release) 
        restartTimer.deinit()  # зупинити таймер перезапуску ESP32, якщо він був активний

    if batteryStateInput.value() == 0 and operationInProgress:
        if operation == Operation.start_charging:
            ledGreen.value(1)
            ledTimer.init(period=BLINK_DELAY, mode=Timer.ONE_SHOT, callback=lambda t: led_blink(t, ledGreen))
        else if operation == Operation.stop_charging:
            ledRed.value(1)
            ledTimer.init(period=BLINK_DELAY, mode=Timer.ONE_SHOT, callback=lambda t: led_blink(t, ledRed))

    if batteryStateInput.value() == 1 and operationInProgress:
        operationInProgress = False

        # Перезапуск ESP32 через таймер після завершення операції зарядки батареї
        if chargingStateInput.value() == 1:
            restartTimer.init(period=RESTART_DELAY, mode=machine.Timer.ONE_SHOT, callback=restart)
        
    displayMessage = time_service.local_time() + "     " + operation.value
    display_service.display_message(oled, displayMessage)  
    wdt.feed()                            # скидання таймера watchdog  
    time.sleep(sleep) 
