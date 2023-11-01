import logging

import rospy
from std_msgs.msg import String, Int32, UInt8MultiArray

from broker.message_broker import MessageBroker
from broker.notifier import BrokerNotifier


logger = logging.getLogger("ABDI")


class RosNoeticBroker(MessageBroker):
    def __init__(self, notifier:BrokerNotifier):
        
        self.pub = rospy.Publisher('chatter', String, queue_size=10)
        self.publishers = {}
        
        super().__init__(notifier=notifier)


    def _on_data(self, data):
        self._notifier._on_message(message)

        data = message.payload.decode('utf-8', 'ignore')
        self._notifier._on_topic(message.topic, data)


    def _on_message(self, message):
        self._notifier._on_message(message)

        data = message.payload.decode('utf-8', 'ignore')
        self._notifier._on_topic(message.topic, data)



    ###################################
    # Implementation of MessageBroker #
    ###################################
    
    
    def start(self, options:dict):
        rospy.init_node(self._notifier.name, anonymous=True)
       

    def stop(self):
        logger.info(f"Ros broker is stopping...")
        
        
    def _get_publisher(self, topic, data):
        type_name = type(data).__name__
        topic_key = f"{topic}_{type_name}"
        publisher = self.publishers.get(topic_key)
        if not publisher:
            if "str" == type_name:
                publisher = rospy.Publisher(topic, String, queue_size=10)
            elif "int" == type_name:
                publisher = rospy.Publisher(topic, Int32, queue_size=10)
            elif "bytes" == type_name:
                publisher = rospy.Publisher(topic, UInt8MultiArray, queue_size=10)
            else:
                raise TypeError(f"Unsupported data type: {type_name}")
            
            self.publishers[topic_key] = publisher
            
        return publisher


    def publish(self, topic:str, payload):
        logger.info(f"topic: {topic}, payload: {payload}")
        
        publisher = self._get_publisher(topic, payload)
        rospy.loginfo(payload)
        publisher.publish(payload)
        
    
    def _callback_with_topic(self, topic_name):
        def callback(data):
            rospy.loginfo(f"Received on topic {topic_name}, data.data: {data.data}")
        return callback


    def subscribe(self, topic:str, data_type):
        logger.info(f"topic: {topic}, , data_type: {data_type}")
        
        if "str" == data_type:
            rospy.Subscriber(topic, String, self._callback_with_topic(topic))
        elif "int" == data_type:
            rospy.Subscriber(topic, Int32, self._callback_with_topic(topic))
        elif "bytes" == data_type:
            rospy.Subscriber(topic, UInt8MultiArray, self._callback_with_topic(topic))
        else:
            raise TypeError(f"Unsupported data type: {data_type}")
