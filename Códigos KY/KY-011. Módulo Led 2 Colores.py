import network
import machine
import time
from umqtt.simple import MQTTClient

# 🔹 Configuración WiFi
SSID = "LOREDO LAP"
PASSWORD = "u55/5B85"

# 🔹 Configuración MQTT
MQTT_BROKER = "192.168.137.202"  # IP del servidor MQTT
MQTT_TOPIC = "prgs/ledrgb2"

# 🔹 Configuración de pines para KY-029
PIN_ROJO = 25  # GPIO para el color rojo
PIN_VERDE = 26  # GPIO para el color verde

# Configurar los pines en modo salida
led_rojo = machine.Pin(PIN_ROJO, machine.Pin.OUT)
led_verde = machine.Pin(PIN_VERDE, machine.Pin.OUT)

# 🔹 Función para conectar WiFi
def conectar_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print("🔄 Conectando a WiFi...")
        wifi.connect(SSID, PASSWORD)
        tiempo_inicio = time.time()
        while not wifi.isconnected():
            if time.time() - tiempo_inicio > 10:
                print("❌ No se pudo conectar a WiFi")
                return False
            time.sleep(1)
    print("✅ Conectado a WiFi:", wifi.ifconfig())
    return True

# 🔹 Conectar WiFi
if not conectar_wifi():
    raise Exception("⚠ Error al conectar WiFi")

# 🔹 Configuración de MQTT
try:
    client = MQTTClient("ESP32_BICOLOR", MQTT_BROKER)
    client.connect()
    print("✅ Conectado a MQTT")
except Exception as e:
    print("❌ Error conectando a MQTT:", e)
    raise

# 🔹 Función para cambiar color del LED bicolor
def cambiar_color(rojo, verde, codigo):
    led_rojo.value(rojo)
    led_verde.value(verde)
    client.publish(MQTT_TOPIC, str(codigo))  # Enviar estado a MQTT
    print(f"📤 Enviado - Estado LED: {codigo}")

# 🔹 Secuencia de colores
colores = [
    (1, 0, 1),  # Rojo
    (0, 1, 2),  # Verde
    (1, 1, 3),  # Amarillo (Rojo + Verde)
    (0, 0, 0)   # Apagado
]

# 🔹 Bucle principal
while True:
    try:
        for r, g, codigo in colores:
            cambiar_color(r, g, codigo)
            time.sleep(2)  # Espera 2 segundos entre cambios
    except Exception as e:
        print("❌ Error en el bucle:", e)