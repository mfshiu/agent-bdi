from src.holon import logger


def speak(agent, sentence):
    logger.info(f"Say: '{sentence}'")
    agent.publish('voice.text', sentence)
