import time
import network
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración del relé y la conexión MQTT
RELAY_PIN = 14  # Pin GPIO al que está conectado el relé KY-019
MQTT_BROKER = "192.168.137.202"  # Dirección del broker MQTT
MQTT_TOPIC = "prgs/rele"  # Tópico de MQTT para controlar el relé
MQTT_CLIENT_ID = "rele_control_{}".format(int(time.time()))  # ID del cliente MQTT
WIFI_SSID = "LOREDO LAP"  # Tu SSID Wi-Fi
WIFI_PASSWORD = "u55/5B85"  # Tu contraseña Wi-Fi

# Configuración del pin para controlar el relé
relay = Pin(RELAY_PIN, Pin.OUT)  # Establece el pin como salida

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(10):
        if wlan.isconnected():
            print("✅ Wi-Fi conectado:", wlan.ifconfig())
            return True
        time.sleep(1)
    print("❌ No se pudo conectar a Wi-Fi")
    return False

def connect_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
        client.connect()
        print("✅ Conectado a MQTT")
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

def control_relay(command):
    """ Función para controlar el estado del relé con 1 o 0 """
    if command == 1:
        relay.on()  # Enciende el relé (conectar dispositivo)
        print("✅ Relé encendido")
    elif command == 0:
        relay.off()  # Apaga el relé (desconectar dispositivo)
        print("✅ Relé apagado")

def handle_mqtt_message(topic, msg):
    """ Función para manejar los mensajes recibidos de MQTT """
    print(f"📥 Mensaje recibido en {topic}: {msg.decode()}")
    try:
        command = int(msg.decode())  # Convertir el mensaje recibido a número entero
        if command == 1:
            control_relay(1)  # Enciende el relé
        elif command == 0:
            control_relay(0)  # Apaga el relé
        else:
            print("❌ Comando no válido. Solo se aceptan 1 o 0.")
    except ValueError:
        print("❌ Error: El mensaje recibido no es un número válido.")

if connect_wifi():
    client = connect_mqtt()
    if client:
        client.set_callback(handle_mqtt_message)  # Establecer la función de callback para manejar mensajes
        client.subscribe(MQTT_TOPIC)  # Suscribirse al tópico de MQTT
        while True:
            try:
                client.check_msg()  # Comprobar si hay nuevos mensajes en el tópico
                time.sleep(1)
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
