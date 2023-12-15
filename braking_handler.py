import paho.mqtt.client as mqtt

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
        if (msg.payload) == "Alert":
            if self.client.on_message("vc2324/key-is-ok") == "Driver confirmed":
                braking_handler.key_confirmed()
            else:
                braking_handler.key_unconfirmed()
        else:
            pass

    def subscribe(self, topic):
        self.client.subscribe(topic)
        print("Subscribed to " + topic)
    
    def publish(self,topic, message):
        self.client.publish(topic, message)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()


class BrakingHandler:
    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client
        self._status = "operative, no alert detected"

    def key_confirmed(self):
        print("Alert confirmed, start breaking")
        self._status = "operative, alert detected, braking"

    def key_unconfirmed(self):
        self._mqtt_client.publish("vc2324/alert/key-not-recognized", "Key not recognized, aborted the alert")
        self._status = "operative, alert detected, key not recognized"
            
    def display_status(self):
        return self._status

mqtt_client = MqttClient('127.0.0.1', 1883)
braking_handler = BrakingHandler(mqtt_client)

mqtt_client.subscribe("vc2324/alert/brake MQTT")
mqtt_client.subscribe("vc2324/key-is-ok MQTT")
mqtt_client.start()

mqtt_client.stop()
