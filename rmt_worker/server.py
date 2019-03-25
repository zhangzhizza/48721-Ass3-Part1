"""
The server to run code submitted remotely
"""
import socket, os, time, threading, traceback, subprocess, _thread, signal
from util.logger import Logger

FD = os.path.dirname(os.path.realpath(__file__));
LOG_LEVEL = 'INFO';
LOG_FMT = "[%(asctime)s] %(name)s %(levelname)s:%(message)s";
KEYS = ['Pd3QWzATcQ', 'UDOvBEIPiH', 'nw7UJeBc3K', 'j0YSw56PpW']
GROUP_NAMES = ['admin', 'iw_right_time', 'csl_load_razor', 'csl_short_cycle']
MAX_CLIENTS = 10;

class WorkerServer(object):

	def __init__(self, ip, port = 48721):
		self._log_file_path = '%s/log/%s_%s_server.log'%(FD, socket.gethostname(), time.time());
		self._logger_main = Logger().getLogger('48721_worker_server', LOG_LEVEL, LOG_FMT, 
			log_file_path = self._log_file_path);
		self._client_threads = [];
		self._clients_count = 0;
		self._lock = threading.Lock();
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
			try:
				c, addr = s.accept()
				client_thread = threading.Thread(target = self._client_handler
													, args = (c, addr));
				client_thread.start();
				self._lock.acquire();
				self._clients_count += 1;
				self._lock.release();
			except Exception as e:
					self._logger_main.error('Error is encountered when accepting the connection from %s, %s'
											%((':'.join(str(e) for e in addr)), traceback.format_exc()));
		s.close();

	def _client_handler(self, c, addr):
		local_logger = Logger().getLogger('Client_%s'
                                    %(threading.current_thread().getName()),
                                              LOG_LEVEL, LOG_FMT, self._log_file_path);
		addr = (':'.join(str(e) for e in addr));   
		local_logger.info('Got connection from ' + addr);
		recv = c.recv(1024).decode(encoding = 'utf-8')
		if self._clients_count > MAX_CLIENTS:
			c.sendall(b'error:The server is too busy, try again later');
			local_logger.warning('Current client number %s is higher the the max allowed %s'
									%(self._clients_count, MAX_CLIENTS));
		elif recv not in KEYS:
			c.sendall(b'error:The KEY is invalid')
			local_logger.warning('Recieved untrusted connecton from ' + addr);
		else:
			# Determine the sender group name
			this_exp_gp_name = GROUP_NAMES[KEYS.index(recv)]
			local_logger.info('The connection\'s group name is %s'%this_exp_gp_name);
			c.sendall(b'ready_to_recieve');
			# Start to recieve the file
			local_logger.info('Recieving the Python script file...');
			recv_byte = b'';
			while True:
				recv = c.recv(1024);
				recv_byte += recv;
				recv_decode_this = recv.decode(encoding = 'utf-8');
				if '$%^endtransfer^%$' in recv_decode_this:
					break;
			recv_decode = recv_byte.decode(encoding = 'utf-8');
			recv_decode_list = recv_decode.split('$%^next^%$');
			# Remove the ending strings
			recv_decode_list[-1] = recv_decode_list[-1].split('$%^endtransfer^%$')[0]
			# Create the group dir if not exist
			this_gp_dir = FD + '/log/' + this_exp_gp_name;
			if not os.path.isdir(this_gp_dir):
				os.makedirs(this_gp_dir);
			# Create this exp dir
			run_dir = self._get_working_folder(this_gp_dir);
			os.makedirs(self._get_working_folder(this_gp_dir))
			# Write the python script to drive
			file_names_to_write = ['run.py'];
			file_counter = 0;
			for file_name in file_names_to_write:
				with open(run_dir + '/' + file_name, 'wb+') as io_f:
					local_logger.info('Writing the Python script file to %s...'%run_dir);
					io_f.write(bytearray(recv_decode_list[file_counter], encoding = 'utf-8'));
					local_logger.info('Writing is finished');
					file_counter += 1;
			c.sendall(b'received'); 
			# Start to run the script
			local_logger.info('Starting to run the script');
			python_process = subprocess.Popen('python run.py',
                        shell = True,
                        cwd = run_dir,
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        preexec_fn=os.setsid);
			log_t = threading.Thread(target = self._log_subprocess_info,
                                args = (python_process.stderr, c, local_logger));
			prs_t = threading.Thread(target = self._python_process_handler,
								args = (python_process, c, run_dir, this_gp_dir, local_logger));
			log_t.start()
			prs_t.start()
			log_t.join()
			prs_t.join()
			
		local_logger.info('Finished task for ' + addr);
		self._lock.acquire();
		self._clients_count -= 1;
		self._lock.release();

	def _log_subprocess_info(self, out_err, c, logger):
		for line in iter(out_err.readline, b''):
			logger.info(line.decode())
			line = 'script_out:' + line.decode();
			c.sendall(bytearray(line, encoding = 'utf-8'));
			c.recv(1024);
		c.sendall(b'scripting_finish')

	def _python_process_handler(self, process, c, run_dir, this_gp_dir, logger):
		while True:
			if process.poll() is None:
				# The process is still running
				continue;
			else:
		    	# The process terminates
				#os.killpg(process.pid, signal.SIGTERM);
				time.sleep(2);
				try:
					# Zip the results
					# Delete the zipped file first
					if os.path.isfile(this_gp_dir + '/results.zip'):
						os.remove(this_gp_dir + '/results.zip')
					run_dir_rl = run_dir.split(os.sep)[-1]
					logger.info('Zipping the results at %s...'%(run_dir))
					subprocess.call('zip -r results.zip %s'%(run_dir_rl),
					        shell = True,
					        cwd = this_gp_dir,
					        stdout = subprocess.PIPE,
					        stderr = subprocess.PIPE,
					        preexec_fn=os.setsid);
					logger.info('Zipping is successful')
					trial_count = 10;
					while trial_count > 0:
						recv = c.recv(1024).decode(encoding = 'utf-8')
						if recv == 'ready_to_recieve':
							c.sendall(b'res_send')
							break;
						else:
							trial_count -= 1;
					if trial_count > 0:
						# Send the results
						res_size = os.path.getsize(this_gp_dir + '/results.zip');
						logger.info('Results file to send is %s bytes'%(res_size))
						# Send the file size first
						c.sendall(bytearray('res_size:%s'%(res_size), encoding = 'utf-8'));
						c.recv(1024); # Break
						f = open(this_gp_dir + '/results.zip', 'rb');
						f_line = f.readline(1024);
						send_size = 0;
						while len(f_line)>0:	
							# Send 1024 bytes a time
							c.sendall(f_line);
							send_size += len(f_line)
							f_line = f.readline(1024);
					else:
						logger.error('Server fails to recieve ready_to_recieve signal from the client');
				except Exception as e:
					logger.error('Error is encountered when zipping the results, %s'
											%(traceback.format_exc()));
					recv = c.recv(1024).decode(encoding = 'utf-8')
					if recv == 'ready_to_recieve':
						c.sendall(b'res_collect_fail')
				break;
			#time.sleep(2);
		return 0;


	def _get_working_folder(self, parent_dir, dir_sig = '-run'):
		"""
		Assumes folders in the parent_dir have suffix -exp{run
		number}. Finds the highest run number and sets the output folder
		to that number + 1. 

		Parameters
		----------
		parent_dir: str
		Parent dir of the Eplus output directory.

		Returns
		-------
		parent_dir/run_dir
		Path to Eplus save directory.
		"""
		os.makedirs(parent_dir, exist_ok=True)
		experiment_id = 0
		for folder_name in os.listdir(parent_dir):
		    if not os.path.isdir(os.path.join(parent_dir, folder_name)):
		        continue
		    try:
		        folder_name = int(folder_name.split(dir_sig)[-1])
		        if folder_name > experiment_id:
		            experiment_id = folder_name
		    except:
		        pass
		experiment_id += 1

		ret_dir = os.path.join(parent_dir, 'Eplus-env') + '%s%d'%(dir_sig, experiment_id);
		return ret_dir