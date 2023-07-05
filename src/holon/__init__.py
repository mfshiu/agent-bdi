import logging

logger = logging.getLogger('ABDI')

class config:
    def __init__(self):
        self.mqtt_address = "localhost"
        self.mqtt_port = 1883
        self.mqtt_keepalive = 60
        self.mqtt_username = "eric"
        self.mqtt_password = "eric123"

        self.log_level = logging.DEBUG
        self.log_dir = "D:\\Work\\SDK\\agent-bdi\\tests\guide\\_log"
