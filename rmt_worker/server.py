"""
The server to run code submitted remotely
"""
import socket, os, time, threading
from util.logger import Logger

FD = os.path.dirname(os.path.realpath(__file__));
LOG_LEVEL = 'INFO';
LOG_FMT = "[%(asctime)s] %(name)s %(levelname)s:%(message)s";
KEYS = ['abcd']

class WorkerServer(object):

	def __init__(self, ip, port = 14786):
		self._log_file_path = '%s/log/%s_%s_server.log'%(FD, socket.gethostname(), time.time());
		self._logger_main = Logger().getLogger('48721_worker_server', LOG_LEVEL, LOG_FMT, 
			log_file_path = self._log_file_path);
		self._client_threads = [];
		self._port = port;
		self._ip = ip;

	def run_server(self):
		s = socket.socket();
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((self._ip, self._port))        
		s.listen(5)
		self._logger_main.info('Socket starts at ' + (':'.join(str(e) for e in s.getsockname())));
		while True:
			self._logger_main.info("Listening...")
			c, addr = s.accept()
			client_thread = threading.Thread(target = self._client_handler
													, args = (c, addr));
			client_thread.start();
		s.close();

	def _client_handler(self, c, addr):
		local_logger = Logger().getLogger('Client_%s'
                                    %(threading.current_thread().getName()),
                                              LOG_LEVEL, LOG_FMT, self._log_file_path);
		addr = (':'.join(str(e) for e in addr));   
		local_logger.info('Got connection from ' + addr);
		recv = c.recv(1024).decode(encoding = 'utf-8')
		if recv.lower() in KEYS:
			c.sendall(b'ok');
		else:
			local_logger.warning('Recieved untrusted connecton from ' + addr);

		time.sleep(20);
		local_logger.info('Finished task for ' + addr);
