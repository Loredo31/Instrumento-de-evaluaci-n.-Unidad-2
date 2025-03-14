import time
import network
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configuración de pines y conexión
LED_R_PIN = 15  # Pin del canal rojo (R) del LED RGB
LED_G_PIN = 2   # Pin del canal verde (G) del LED RGB
LED_B_PIN = 4   # Pin del canal azul (B) del LED RGB
MQTT_BROKER = "192.168.137.202"
MQTT_TOPIC = "prgs/ledrgb"
MQTT_CLIENT_ID = "rgb_led_{}".format(int(time.time()))
WIFI_SSID = "LOREDO LAP"
WIFI_PASSWORD = "u55/5B85"

# Configuración de los pines de los LEDs con PWM para control de intensidad
led_r = PWM(Pin(LED_R_PIN), freq=1000, duty=0)  # Rojo
led_g = PWM(Pin(LED_G_PIN), freq=1000, duty=0)  # Verde
led_b = PWM(Pin(LED_B_PIN), freq=1000, duty=0)  # Azul

# Variable para almacenar el último color
last_color = None

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

def set_led_color(color_value):
    """ Función para establecer el color del LED RGB basado en un valor entero """
    global last_color
    try:
        # Publicar número solo si el color ha cambiado
        if color_value != last_color:
            print(f"📊 Color LED cambiado a: {color_value}")
            # Publicar el número correspondiente al color en MQTT
            client.publish("prgs/color_number", str(color_value))  # Solo enviamos el valor numérico
            last_color = color_value  # Actualizar el último color

        # Configurar el color del LED
        if color_value == 1:  # Rojo
            led_r.duty(1023)
            led_g.duty(0)
            led_b.duty(0)
        elif color_value == 2:  # Verde
            led_r.duty(0)
            led_g.duty(1023)
            led_b.duty(0)
        elif color_value == 3:  # Azul
            led_r.duty(0)
            led_g.duty(0)
            led_b.duty(1023)
        elif color_value == 4:  # Blanco (todos los LEDs encendidos)
            led_r.duty(1023)
            led_g.duty(1023)
            led_b.duty(1023)
        else:  # Apagar el LED si el valor no es válido
            led_r.duty(0)
            led_g.duty(0)
            led_b.duty(0)
    except Exception as e:
        print(f"❌ Error al establecer color: {e}")

def on_message(topic, msg):
    """ Callback para recibir el mensaje MQTT y cambiar el color del LED """
    print(f"📬 Mensaje recibido en {topic}: {msg}")
    try:
        color_value = int(msg.decode())  # Convertir el mensaje a un valor entero
        set_led_color(color_value)  # Establecer el color basado en el valor entero
    except ValueError:
        print("❌ El mensaje no es un valor válido.")

if connect_wifi():
    client = connect_mqtt()
    if client:
        client.set_callback(on_message)  # Establecer la función de callback para mensajes entrantes
        client.subscribe(MQTT_TOPIC)  # Suscribirse al tema MQTT

        # Ciclo para cambiar los colores
        color_cycle = [1, 2, 3, 4]  # Ciclo de colores (1: Rojo, 2: Verde, 3: Azul, 4: Blanco)
        color_index = 0
        
        while True:
            try:
                # Cambiar el color según el ciclo
                set_led_color(color_cycle[color_index])
                
                # Publicar el color cada vez que cambia
                color_index = (color_index + 1) % len(color_cycle)  # Ciclo de colores
                time.sleep(3)  # Cambiar color cada 3 segundos
            except Exception as e:
                print("❌ Error en loop MQTT:", e)
                break
else:
    print("❌ No se pudo conectar a Wi-Fi.")
