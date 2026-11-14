from machine import Pin
from machine import Timer
from machine import WDT
from debounced_input import DebouncedInput
from operation import Operation

import time
import machine

import display_service
import time_service

RELAY_TIMER_DELAY = 6*1000              # затримка таймера реле в мілісекундах
RETRY_TIMER_DELAY = 90*1000             # затримка таймера повторної спроби в мілісекундах
BLINK_DELAY = 500                       # затримка між блиманням світлодіодів
INPUT_POLL_INTERVAL_MS = 10             # інтервал опитування входів
DISPLAY_REFRESH_INTERVAL_MS = 1000      # інтервал оновлення дисплея
RESTART_DELAY = 5*60*1000               # затримка між перезапусками ESP32
WATCHDOG_TIMEOUT = 5*1000               # таймаут watchdog в мілісекундах


# # Кнопка на GPIO4 з внутрішнім pull-up
# triggerBatteryStateButton = Pin(4, Pin.IN, Pin.PULL_UP)

# Кнопка на GPIO5 з внутрішнім pull-up
batteryStatePin = Pin(5, Pin.IN, Pin.PULL_UP)
batteryStateInput = DebouncedInput(batteryStatePin)

# Кнопка на GPIO4 з внутрішнім pull-up
chargingStateInput = DebouncedInput(Pin(4, Pin.IN, Pin.PULL_UP))

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
    print("Restarting by schedule...")
    machine.reset()

def led_blink(timer, led):
    led.value(0 if led.value() else 1)

def relay_release():
    relayKillSwitchOut.value(1)     # вимкнути реле Kill Switch
    relayIgnitionOut.value(1)       # вимкнути реле Ignition

def relay_release_event(timer):
    relay_release()

def retry_operation_event(timer):
    global operationInProgress
    
    if batteryStatePin.value() == 0 and operationInProgress:
        relay_release()
        operationInProgress = False

print("NTP: start")
time_service.init_time()
print("NTP: OK")

print("OLED: start")
oled = display_service.init_display()
print("OLED: OK")

relayTimer = Timer(0)
retryTimer = Timer(1)
ledTimer = Timer(2)
restartTimer = machine.Timer(3)

displayMessage = "Starting..."
operation = Operation.discharging
lastDisplayTime = time.ticks_ms()
displayDue = True

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
        restartTimer.deinit()  # зупинити таймер перезапуску ESP32, якщо він був активний
        
        if chargingStateInput.value() == 1:
            operation = Operation.start_charging
            ledGreen.value(1)           
            ledRed.value(0)  
            ledYellow.value(1)                
            relayIgnitionOut.value(0)   # увімкнути реле Ignition
        elif chargingStateInput.value() == 0:
            operation = Operation.stop_charging
            ledGreen.value(0)     
            ledRed.value(1)      
            ledYellow.value(1)          
            relayKillSwitchOut.value(0) # увімкнути реле Kill Switch

        operationInProgress = True

        relayTimer.init(period=RELAY_TIMER_DELAY, mode=Timer.ONE_SHOT, callback=relay_release_event) 
        retryTimer.init(period=RETRY_TIMER_DELAY, mode=Timer.ONE_SHOT, callback=retry_operation_event)  # запустити таймер повторної спроби, якщо операція не завершиться успішно
        # Перезапуск ESP32 через таймер після завершення операції зарядки батареї 
        restartTimer.init(period=RESTART_DELAY, mode=machine.Timer.ONE_SHOT, callback=restart)

        if operation == Operation.start_charging:
            ledTimer.init(period=BLINK_DELAY, mode=Timer.PERIODIC, callback=lambda t: led_blink(t, ledGreen))
        elif operation == Operation.stop_charging:
            ledTimer.init(period=BLINK_DELAY, mode=Timer.PERIODIC, callback=lambda t: led_blink(t, ledRed))

    if batteryStateInput.value() == 1 and operationInProgress:
        retryTimer.deinit()  # зупинити таймер повторної спроби, якщо він був активний
        relay_release()      # вимкнути реле Kill Switch та Ignition
        ledTimer.deinit()
        operationInProgress = False
        
    now = time.ticks_ms()
    if displayDue or time.ticks_diff(now, lastDisplayTime) >= DISPLAY_REFRESH_INTERVAL_MS:
        displayMessage = time_service.local_time() + "     " + operation.value
        display_service.display_message(oled, displayMessage)
        lastDisplayTime = now
        displayDue = False

    wdt.feed()                # скидання таймера watchdog  
    time.sleep_ms(INPUT_POLL_INTERVAL_MS)
