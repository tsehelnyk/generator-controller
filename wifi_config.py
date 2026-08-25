# wifi_config.py -- Wi-Fi configuration

SSID = "YourSSID"
PASSWORD = "YourPassword"
import network, time

def connect_wifi(ssid, password):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, password)
    while not sta.isconnected():
        time.sleep(1)
    print("Connected:", sta.ifconfig())
    return sta

def get_ip():
    sta = network.WLAN(network.STA_IF)
    if sta.isconnected():
        return sta.ifconfig()[0]
    else:
        return None
