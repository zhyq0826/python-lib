import logging
import sys
"""
logging.warning('test carefull') # will print a message to the console
logging.info('sweet') # will not pring anythin

"""

def main1(loglevel='debug'):
    numeric_level = getattr(logging,loglevel.upper(),None)
    if not isinstance(numeric_level,int):
        raise ValueError('invalid log level:%s'%loglevel)

    logging.basicConfig(filename='exmple.log',filemode='w',level=numeric_level)
    logging.debug('this message should go to the log file')
    logging.info('so should this')
    logging.warning('and this,too')

def main2(loglevel='debug'):
    numeric_level = getattr(logging,loglevel.upper(),None)
    if not isinstance(numeric_level,int):
        raise ValueError('invalid log level:%s'%loglevel)

    logging.basicConfig(format='%(levelname)s:%(asctime)s  %(message)s',filemode='w',level=numeric_level)
    logging.debug('this message should appear on the console')
    logging.info('so should this')
    logging.warning('and this,too')

def main3():
    # create logger
    logger = logging.getLogger('simple_example')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    # 'application' code
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')

if __name__=='__main__':
    try:
        loglevel = sys.argv[-1]
    except:
        loglevel = 'debug'
    main3()
