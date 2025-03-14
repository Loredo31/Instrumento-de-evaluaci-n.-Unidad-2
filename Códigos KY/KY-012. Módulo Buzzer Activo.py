import network
import machine
import time
from umqtt.simple import MQTTClient

# 🔹 Configuración WiFi
SSID = "LOREDO LAP"
PASSWORD = "u55/5B85"

# 🔹 Configuración MQTT
MQTT_BROKER = "prgs/buzzerpas"  # IP del servidor MQTT
MQTT_TOPIC = "sensor/buzzer"

# 🔹 Configuración del buzzer activo
PIN_BUZZER = 32  # Conectar el buzzer a este GPIO
buzzer = machine.Pin(PIN_BUZZER, machine.Pin.OUT)

# 🔹 Función para conectar WiFi
def conectar_wifi():
    wifi = network.WLA1N(network.STA_IF)
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
    client = MQTTClient("ESP32_Buzzer", MQTT_BROKER)
    client.connect()
    print("✅ Conectado a MQTT")
except Exception as e:
    print("❌ Error conectando a MQTT:", e)
    raise

# 🔹 Función para controlar el buzzer
def controlar_buzzer(estado):
    if estado == 1:
        buzzer.value(1)  # Activa el buzzer
        print("🔊 Buzzer encendido")
    else:
        buzzer.value(0)  # Apaga el buzzer
        print("🔇 Buzzer apagado")

# 🔹 Función para enviar datos por MQTT
def enviar_datos(estado):
    client.publish(MQTT_TOPIC, str(estado))
    print(f"📤 Enviado - Buzzer Estado: {estado}")

# 🔹 Bucle principal
while True:
    try:
        # Cambia entre 1 (encender) y 0 (apagar) según lo que necesites
        estado = 1  # 1 = Buzzer encendido, 0 = Buzzer apagado
        controlar_buzzer(estado)
        enviar_datos(estado)
        
        time.sleep(5)  # Ajusta el tiempo de muestreo
        
    except Exception as e:
        print("❌ Error en el bucle:", e)