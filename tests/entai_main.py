import multiprocessing
import signal

import helper
from holon.HolonicAgent import HolonicAgent
from document_import import DocumentImport
from km import KnowledgeManagement

from abdi_config import AbdiConfig

logger = helper.get_logger()


# class EntaiMain(HolonicAgent):
#     def __init__(self, cfg):
#         super().__init__(cfg)

#         self.head_agents.append(DocumentImport(cfg))
#         self.head_agents.append(KnowledgeManagement(cfg))

#         logger.debug(f"Init EntaiMain done.")


if __name__ == '__main__':
    logger.info(f'***** Enterprise AI start *****')

    def signal_handler(signal, frame):
        logger.warning("System was interrupted.")
    signal.signal(signal.SIGINT, signal_handler)

    multiprocessing.set_start_method('spawn')

    DocumentImport(AbdiConfig(helper.get_config())).start()
    KnowledgeManagement(AbdiConfig(helper.get_config())).start()
    