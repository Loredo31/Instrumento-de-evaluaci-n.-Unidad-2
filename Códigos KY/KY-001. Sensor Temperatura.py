from machine import Pin
import dht
import network
import time
import ubinascii
from umqtt.simple import MQTTClient

# Configuración WiFi
SSID = "LOREDO LAP"
PASSWORD = "u55/5B85"

# Configuración MQTT
MQTT_BROKER = "192.168.137.202"
MQTT_CLIENT_ID = ubinascii.hexlify(network.WLAN().config('mac')).decode()
MQTT_TOPIC_TEMP = "sensor/temperatura"
MQTT_TOPIC_HUM = "sensor/humedad"

# Conectar al WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(1)
print("Conectado a WiFi")

# Configurar MQTT
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
client.connect()
print("Conectado al broker MQTT")

# Configurar sensor DHT11/DHT22 en el pin GPIO4
sensor = dht.DHT11(Pin(4))  # Usa DHT22 si es el caso: dht.DHT22(Pin(4))

while True:
    try:
        sensor.measure()  # Tomar lectura del sensor
        temperatura = sensor.temperature()
        humedad = sensor.humidity()

        # Enviar datos por MQTT
        client.publish(MQTT_TOPIC_TEMP, str(temperatura))
        client.publish(MQTT_TOPIC_HUM, str(humedad))

        print(f"Temperatura: {temperatura}°C, Humedad: {humedad}%")

    except Exception as e:
        print("Error al leer el sensor:", e)

    time.sleep(2)  # Esperar 2 segundos antes de la siguiente lectura
