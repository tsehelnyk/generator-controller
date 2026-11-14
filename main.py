from machine import Pin
from machine import Timer
from machine import WDT

import uasyncio as asyncio
import machine

from debounced_input import DebouncedInput
from operation import OperationSteps
import display_service
import time_service


RELAY_TIMER_DELAY = 6*1000                  # затримка таймера реле в мілісекундах
RETRY_TIMER_DELAY = 120*1000                # затримка таймера повторної спроби в мілісекундах
INPUT_POLL_INTERVAL_MS = 200                # інтервал опитування входів
OUTPUT_CONTROL_INTERVAL_MS = 1000           # інтервал опитування виходів
DISPLAY_REFRESH_INTERVAL_MS = 1000          # інтервал оновлення дисплея
RESTART_DELAY = 5*60*1000                   # затримка між перезапусками ESP32
WATCHDOG_TIMEOUT = 5*1000                   # таймаут watchdog в мілісекундах

BATTERY_STATE_PIN = 5                       # GPIO5 - вхід стану батареї
CHARGING_STATE_PIN = 4                      # GPIO4 - вхід стану зарядки
IGNITION_RELAY_PIN = 18                     # GPIO18 - реле запалювання
KILL_SWITCH_RELAY_PIN = 19                  # GPIO19 - реле Kill Switch
GREEN_LED_PIN = 16                          # GPIO16 - green LED
RED_LED_PIN = 17                            # GPIO17 - red LED
YELLOW_LED_PIN = 23                         # GPIO23 - yellow LED

RELAY_ON = 0
RELAY_OFF = 1
LED_ON = 1
LED_OFF = 0

def restart(timer):
    print("Restarting by schedule...")
    machine.reset()

def relay_on(relay, relay_timer, retry_timer):
    retry_timer.deinit()
    relay.value(RELAY_ON)
    relay_timer.init(period=RELAY_TIMER_DELAY, mode=Timer.ONE_SHOT, callback = lambda t: relay_release(t, relay)) 
    retry_timer.init(period=RETRY_TIMER_DELAY, mode=Timer.ONE_SHOT, callback = lambda t: relay_on(relay, relay_timer, retry_timer))

def relay_release(timer, relay):
    relay.value(RELAY_OFF)

def get_operation_from_inputs(batteryStateInput, chargingStateInput):
    if batteryStateInput.value() == 1 and chargingStateInput.value() == 1:
        return OperationSteps.discharging

    elif batteryStateInput.value() == 1 and chargingStateInput.value() == 0:
        return OperationSteps.charging   

    elif batteryStateInput.value() == 0 and chargingStateInput.value() == 1:
        return OperationSteps.startCharging

    elif chargingStateInput.value() == 0 and batteryStateInput.value() == 0:
        return OperationSteps.stopCharging

print("NTP: start")
time_service.init_time()
print("NTP: OK")

print("OLED: start")
oled = display_service.init_display()
print("OLED: OK")

ignition_relay_timer = Timer(0)
kill_switch_relay_timer = Timer(1)
retryTimer = Timer(2)
restartTimer = Timer(3)

displayMessage = "Starting..."
operation = OperationSteps.discharging

input_alive = False
output_alive = False
display_alive = False

async def poll_inputs_task():
    # Кнопка з внутрішнім pull-up
    batteryStatePin = Pin(BATTERY_STATE_PIN, Pin.IN, Pin.PULL_UP)
    batteryStateInput = DebouncedInput(batteryStatePin)

    # Кнопка з внутрішнім pull-up
    chargingStatePin = Pin(CHARGING_STATE_PIN, Pin.IN, Pin.PULL_UP)
    chargingStateInput = DebouncedInput(chargingStatePin)

    global input_alive
    global operation

    operation = get_operation_from_inputs(batteryStateInput, chargingStateInput)
    input_operation = operation

    while True:
        input_alive = True

        input_operation = get_operation_from_inputs(batteryStateInput, chargingStateInput)

        if input_operation.operation == operation.nextOperation:
            restartTimer.deinit()  
            operation = input_operation
            restartTimer.init(period=RESTART_DELAY, mode=machine.Timer.ONE_SHOT, callback=restart)

        await asyncio.sleep_ms(INPUT_POLL_INTERVAL_MS)

async def control_outputs_task():
    # Зовнішні світлодіоди
    ledGreen = Pin(GREEN_LED_PIN, Pin.OUT)              # charging, ignition
    ledGreen.value(LED_OFF)                             # вимкнути зелений LED
    ledRed = Pin(RED_LED_PIN, Pin.OUT)                  # charged, kill switch
    ledRed.value(LED_OFF)                               # вимкнути червоний LED
    ledYellow = Pin(YELLOW_LED_PIN, Pin.OUT)            # discharging
    ledYellow.value(LED_ON)                             # увімкнути жовтий LED

    # Ініціалізація реле
    relayIgnitionOut = Pin(IGNITION_RELAY_PIN, Pin.OUT)
    relayIgnitionOut.value(RELAY_OFF)                   # вимкнути реле Ignition
    relayKillSwitchOut = Pin(KILL_SWITCH_RELAY_PIN, Pin.OUT)
    relayKillSwitchOut.value(RELAY_OFF)                 # вимкнути реле Kill Switch

    last_operation = operation.previousOperation

    global output_alive

    while True:
        output_alive = True

        if operation != last_operation:
            retryTimer.deinit()

            print(operation.operation.value)

            if operation == OperationSteps.charging:
                ledGreen.value(LED_ON)
                ledRed.value(LED_OFF)
                ledYellow.value(LED_OFF)

            elif operation == OperationSteps.discharging:
                ledGreen.value(LED_OFF)
                ledYellow.value(LED_ON)
                ledRed.value(LED_OFF)

            elif operation == OperationSteps.startCharging:
                ledGreen.value(LED_ON)
                ledRed.value(LED_OFF)
                ledYellow.value(LED_ON)
                relayKillSwitchOut.value(RELAY_OFF)
                relay_on(relayIgnitionOut, ignition_relay_timer, retryTimer)

            elif operation == OperationSteps.stopCharging:
                ledGreen.value(LED_OFF)
                ledRed.value(LED_ON)
                ledYellow.value(LED_ON)
                relayIgnitionOut.value(RELAY_OFF)
                relay_on(relayKillSwitchOut, kill_switch_relay_timer, retryTimer)
                    
            last_operation = operation

        await asyncio.sleep_ms(OUTPUT_CONTROL_INTERVAL_MS)

async def display_task():
    global display_alive
    while True:
        display_alive = True
        displayMessage = time_service.local_time() + "     " + operation.operation.value
        display_service.display_message(oled, displayMessage)
        
        await asyncio.sleep_ms(DISPLAY_REFRESH_INTERVAL_MS)

async def watchdog_task():
    wdt = WDT(timeout=WATCHDOG_TIMEOUT)
    global input_alive, output_alive, display_alive
    while True:
        await asyncio.sleep(1)

        if input_alive and output_alive and display_alive:
            wdt.feed()
            input_alive = False
            output_alive = False
            display_alive = False

async def main():
    asyncio.create_task(poll_inputs_task())
    asyncio.create_task(control_outputs_task())
    asyncio.create_task(display_task())
    asyncio.create_task(watchdog_task())

    while True:
        await asyncio.sleep(1)

asyncio.run(main())
