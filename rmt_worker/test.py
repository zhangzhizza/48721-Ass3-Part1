import time, logging, os
# Create logger
logger = logging.getLogger('xremote')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
for i in range(5):
	time.sleep(0.5)
	logger.info('232322%d'%(i));

os.makedirs('%s'%(time.time()))