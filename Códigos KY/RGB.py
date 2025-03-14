import time
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
RED_PIN = 15    # Pin del canal Rojo del LED RGB
GREEN_PIN = 12  # Pin del canal Verde del LED RGB
BLUE_PIN = 13   # Pin del canal Azul del LED RGB
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/rgb_led"
MQTT_CLIENT_ID = "rgb_led_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configuración de los pines PWM para el control de color
red_pwm = PWM(Pin(RED_PIN), freq=1000, duty=0)
green_pwm = PWM(Pin(GREEN_PIN), freq=1000, duty=0)
blue_pwm = PWM(Pin(BLUE_PIN), freq=1000, duty=0)

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
        client.set_callback(mqtt_callback)
        client.connect()
        client.subscribe(MQTT_TOPIC)
        print("✅ Conectado a MQTT y suscrito a:", MQTT_TOPIC)
        return client
    except Exception as e:
        print("❌ Error MQTT:", e)
        return None

def mqtt_callback(topic, msg):
    """ Función que se ejecuta cuando se recibe un mensaje MQTT """
    mensaje = msg.decode("utf-8").strip().lower()
    print(f"📩 Mensaje recibido en {topic}: {mensaje}")

    # Parsear el mensaje para establecer el color
    try:
        # Asumimos que el mensaje es de la forma "r,g,b" donde r, g, b son valores de 0 a 255
        r, g, b = map(int, mensaje.split(','))
        set_rgb_color(r, g, b)
    except ValueError:
        print("❌ Error al parsear el mensaje. Formato esperado: 'r,g,b'")

def set_rgb_color(r, g, b):
    """ Función para establecer el color del LED RGB """
    red_pwm.duty(1023 - r)   # PWM funciona al revés, 1023 es el máximo
    green_pwm.duty(1023 - g) # PWM funciona al revés, 1023 es el máximo
    blue_pwm.duty(1023 - b)  # PWM funciona al revés, 1023 es el máximo
    print(f"🎨 Color establecido - R: {r}, G: {g}, B: {b}")

if connect_wifi():
    client = connect_mqtt()
    if client:
        while True:
            try:
                client.check_msg()  # Escuchar mensajes MQTT
                time.sleep(0.1)  # Pequeño retraso para evitar sobrecarga
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
