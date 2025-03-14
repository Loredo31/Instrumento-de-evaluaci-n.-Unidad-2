from machine import Pin
import time
import network
from umqtt.simple import MQTTClient
import ujson  # Para enviar datos en formato JSON

# Configuración WiFi y MQTT
SSID = "LOREDO LAP"
PASSWORD = "u55/5B85"
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/temdigital"

# Conectar a WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    print("Conectando a WiFi...")
    time.sleep(1)

print("Conectado a WiFi!")

# Conectar a MQTT con manejo de errores
def conectar_mqtt():
    global client
    for _ in range(3):  # Máximo 3 intentos de reconexión
        try:
            client = MQTTClient("ESP32", MQTT_BROKER)
            client.connect()
            print("Conectado a MQTT!")
            return True  # Conexión exitosa
        except Exception as e:
            print(f"Error conectando a MQTT: {e}")
            time.sleep(3)
    print("No se pudo conectar a MQTT después de varios intentos.")
    return False  # Fallo definitivo

if not conectar_mqtt():
    raise SystemExit  # Detiene el programa si no hay conexión MQTT

# Pines del KY-028
DOUT_PIN = 4   # Salida digital del sensor

# Configuración de pines
dout = Pin(DOUT_PIN, Pin.IN)   # Salida digital como entrada

contador = 0  # Contador para enviar ping MQTT

while True:
    try:
        temperatura_digital = dout.value()  # 0 o 1 (umbral configurado con el potenciómetro)

        print(f"Digital: {temperatura_digital}")

        # Verificar conexión MQTT antes de publicar
        if client:
            # Enviar datos en formato JSON
            payload = ujson.dumps({"Digital": temperatura_digital})
            client.publish(MQTT_TOPIC, payload)

        # Enviar ping cada 10 lecturas para mantener la conexión activa
        if contador >= 10:
            try:
                client.ping()
            except:
                print("MQTT desconectado, reconectando...")
                conectar_mqtt()
            contador = 0
        else:
            contador += 1

    except OSError as e:
        print(f"Error en MQTT: {e}, reconectando...")
        conectar_mqtt()  # Reintentar conexión en caso de error

    time.sleep(2)  # Reducir la frecuencia de envío
