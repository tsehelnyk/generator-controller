from machine import Pin
from machine import Timer

import display_service
import time_service

import time


# Створюємо таймер з ID=0
tim = Timer(0)

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

# Реле
relayIgnitionOut = Pin(18, Pin.OUT)
relayIgnitionOut.value(1)           # вимкнути реле Ignition
relayKillSwitchOut = Pin(19, Pin.OUT)
relayKillSwitchOut.value(1)         # вимкнути реле Kill Switch

def battery_state_isr(pin):
   global batteryCharged
   batteryCharged =  not batteryCharged
   print("Button pressed!" + (" Battery is now CHARGING" if batteryCharged else " Battery is now DISCHARGING") + ". Battery state input: " + str(batteryStateInput.value()))

triggerBatteryStateButton.irq(trigger=Pin.IRQ_RISING, handler=battery_state_isr)
# batteryStateInput.irq(trigger=Pin.IRQ_FALLING, handler=battery_state_isr)

time_service.init_time()
oled = display_service.init_display()

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

    if batteryStateInput.value() == 0:
        if batteryCharged:
            displayMessage = time_service.local_time() + "     " + "START        CHARGING"
            ledGreen.value(1)           
            ledRed.value(0)  
            ledYellow.value(1)          
            # buz.value(1)              
            relayIgnitionOut.value(0)   # увімкнути реле Ignition
            time.sleep(5)
            relayIgnitionOut.value(1)   # вимкнути реле Ignition
            # buz.value(1) 
            sleep = 100    
        else:
            displayMessage = time_service.local_time() + "     " + "STOP         CHARGING"
            ledGreen.value(0)     
            ledRed.value(1)      
            ledYellow.value(1)          
            # buz.value(1)                
            relayKillSwitchOut.value(0) # увімкнути реле Kill Switch
            time.sleep(5)
            relayKillSwitchOut.value(1) # вимкнути реле Kill Switch
            # buz.value(0)     
            sleep = 100

        display_service.display_message(oled, displayMessage)    
        time.sleep(sleep)

        if batteryStateInput.value() == 1:
            batteryCharged = not batteryCharged

    display_service.display_message(oled, displayMessage)    
    time.sleep(sleep) 
                 
# Функція, яку викликає таймер
# def timer_tick(timer):
#     print("Таймер спрацював!")

# Запускаємо таймер кожні 1000 мс (1 секунда)
# tim.init(period=1000, mode=Timer.PERIODIC, callback=tick)
