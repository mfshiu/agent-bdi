import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from GuideMain import GuideMain
# import Helper

if __name__ == '__main__':
    # Helper.init_logging()
    # logging.info('***** Main start *****')
    print('***** Main start *****')

    a = GuideMain()
    a.start()
