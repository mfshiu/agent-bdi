import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import signal

from dialog.nlu import chatgpt
import guide_config


if __name__ == '__main__':
    # Helper.init_logging()
    # logging.info('***** Main start *****')
    print('***** RunTrans start *****')

    chatgpt.set_openai_api_key(guide_config.openai_api_key)

    def signal_handler(signal, frame):
        print("signal_handler")
    signal.signal(signal.SIGINT, signal_handler)

    prompt = "我要去公園"
    knowledge = chatgpt.understand(prompt)
    print(knowledge)
