import paho.mqtt.client as mqtt
from aiohttp import web
import json

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
        cobu_handler.obu_status(msg.topic, msg.payload)
        cobu_handler.check_risk_level()
        match msg.topic:
            case "vc2324/weather-current MQTT":
                data = json.loads(msg.payload)
                if data["current_kind"] == "rainy":
                    cobu_handler._risk_level +=1
                elif data["current_kind"] == "misty":
                    cobu_handler._risk_level +=1
                elif data["current_kind"] == "icy":
                    cobu_handler._risk_level +=2
            
            case "vc2324/dms MQTT":
                if msg.payload == "drunk":
                    cobu_handler._risk_level += 3
                elif msg.payload == "normal":
                    pass
                else:
                    cobu_handler._risk_level += 1
                

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
    def __init__(self, cobu_handler):
        self.app = web.Application()
        self.routes = web.RouteTableDef()
        self.cobu_handler = cobu_handler

        @self.routes.get('/vehicle-status')
        async def get_handler(request):
            status = self.cobu_handler.display_status()
            return web.Response(text = status)
        

        self.app.add_routes(self.routes)
    
    def start(self):
        web.run_app(self.app)
    
    def stop(self):
        web.run_app(self.app)

class CobuHandler:
    def __init__(self, mqtt_client, risk_level, log):
        self._mqtt_client = mqtt_client
        self._risk_level = risk_level
        self._log = log

    def check_risk_level(self):
        if self._risk_level >= 3:
            self._mqtt_client.publish("vc2324/alert/brake", "Alert")

    def obu_status(self, topic, payload):
        self._log.append(topic + payload)
        print(topic, payload)
    
    def display_status(self):
        return self._log


mqtt_client = MqttClient('127.0.0.1', 1883)
cobu_handler = CobuHandler(mqtt_client)
http_server = HttpServer(cobu_handler)
mqtt_client.subscribe("vc2324/radio MQTT")
mqtt_client.subscribe("vc2324/weather-forecast MQTT")
mqtt_client.subscribe("vc2324/weather-current MQTT")
mqtt_client.subscribe("vc2324/dms MQTT")
mqtt_client.subscribe("vc2324/key-not-recognized MQTT")
mqtt_client.subscribe("vc2324/key-is-ok MQTT")
mqtt_client.subscribe("vc2324/alert/brake MQTT")

mqtt_client.start()

mqtt_client.stop()
http_server.start()