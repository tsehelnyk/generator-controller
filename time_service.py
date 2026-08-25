# import network
import ntptime
import time

# Підключення до Wi-Fi
# sta = network.WLAN(network.STA_IF)
# sta.active(True)
# sta.connect("SSID", "PASSWORD")

# while not sta.isconnected():
#     pass

# print("Wi-Fi підключено:", sta.ifconfig())

def init_time():
    # Синхронізація часу з NTP-сервера
    ntptime.settime()

    # Перевірка часу
    print("UTC час:", time.localtime())

def local_time(offset=3):
    t = time.localtime(time.time() + offset*3600)
    return "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
