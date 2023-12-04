import paho.mqtt.client as mqtt
from aiohttp import web
from random import randint
import time
import threading 

class MqttClient:
    def __init__(self, host, port):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.host = host
        self.port = port

        self.mqtt_connection()

    def mqtt_connection(self):
        self.client.connect(self.host, self.port, 60)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
    
    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def subscribe(self, topic):
        self.client.subscribe(topic)
        print("Subscribed to " + topic)
    
    def publish(self,topic, message):
        self.client.publish(topic, message)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

class HttpServer:
    def __init__(self, dms_handler):
        self.app = web.Application()
        self.routes = web.RouteTableDef()

        self.dms_handler = dms_handler

        @self.routes.get('/dms')
        async def get_handler(request):
            status = self.dms_handler.display_status()
            return web.Response(text = status)

        self.app.add_routes(self.routes)
    
    def start(self):
        web.run_app(self.app)
    
    def stop(self):
        web.run_app(self.app)

class DmsHandler:
    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client
        self._current_status = 'normal'

    def change_status(self):
        status = ['angry', 'tired', 'drunk',
              'discracted', 'normal']
        n = randint(0, 4)
        new_status = status[n]
        self._current_status = new_status
        self._mqtt_client.publish("vc2324/dms MQTT", "The driver status is " + new_status)
    
    def display_status(self):
        return self._current_status

mqtt_client = MqttClient('127.0.0.1', 1883)
dms_handler = DmsHandler(mqtt_client)
http_server = HttpServer(dms_handler)

mqtt_client.subscribe("vc2324/dms MQTT")
mqtt_client.start()

http_server.start()

# Start the thread for changing the status
def change_status_thread():
    while True:
        dms_handler.change_status()
        time.sleep(10)

change_status_thread = threading.Thread(target=change_status_thread)
change_status_thread.start()

mqtt_client.stop()