import ast

from src.holon import logger
from src.holon.HolonicAgent import HolonicAgent
from brain import brain_helper


class Controller(HolonicAgent):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.active_subject = None
        self.registered_subjects = []


    def _on_connect(self, client, userdata, flags, rc):
        client.subscribe("dialog.knowledge")
        client.subscribe("brain.register_subject")
        client.subscribe("brain.unregister_subject")
        client.subscribe("brain.subject_done")
        super()._on_connect(client, userdata, flags, rc)


    def _on_topic(self, topic, data):
        if "dialog.knowledge" == topic:
            if self.active_subject:
                self._publish(f'{self.active_subject}.knowledge', data)
            else:
                knowledge = ast.literal_eval(data)
                if (subject := knowledge[0][0]) in self.registered_subjects:
                    self.active_subject = subject
                    logger.info(f"Active subject: {self.active_subject}")
                    self._publish(f'{self.active_subject}.knowledge', data)
                else:
                    logger.warning(f"Uknown subject: {subject}")
        elif "brain.register_subject" == topic:
            if not data in self.registered_subjects:
                self.registered_subjects.append(data)
                logger.info(f"Register subject: {data}")
        elif "brain.unregister_subject" == topic:
            if data in self.registered_subjects:
                self.registered_subjects.remove(data)
                logger.info(f"Unregister subject: {data}")
        elif "brain.subject_done" == topic:
            logger.info(f"subject: {self.active_subject} is done.")
            self.active_subject = None
            
        super()._on_topic(topic, data)
