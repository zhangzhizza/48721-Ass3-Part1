"""
This script connects to the remote server to run the python code.
"""
import argparse, os, logging, traceback, socket

def main():
    parser = argparse.ArgumentParser(description='Send a Python script to the server to execute.')
    parser.add_argument('--ip', type=str, default='128.2.111.196', help='The remote server IP')
    parser.add_argument('--port', type=int, default=48721, help='The remote server port')
    parser.add_argument('--key', type=str, help='The connection key')
    parser.add_argument('--path', type=str, help='The local path the Python script (to be run)')
    args = parser.parse_args();
    run_client(args.ip, args.port, args.key, args.path);
        
def run_client(ip, port, key, path):
	# Create logger
	logger = logging.getLogger('xremote')
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s_%(name)s_%(levelname)s: %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)
	# Create the socket
	s = socket.socket();
	logger.info('xremote client has been initiated')
	try:
		s.connect((ip, port));
		logger.info('xremote client has been connected to the server %s'%(':'.join([ip, str(port)])));
		# Protocol: send key first
		s.sendall(bytearray(key, encoding = 'utf-8'));
		recv = s.recv(1024).decode(encoding = 'utf-8');
		recv = recv.split(':');
		if recv[0] == 'error':
			logger.error('Server says: %s, xremote exits'%(recv[1]));
			return 1;
		elif recv[0] == 'ready_to_recieve':
			# Protocol: send the script file
			if not os.path.isfile(path):
				logger.error('The script file %s does not exist, check your path input, ' 
							 'xremote exits'%path)
				return 1;
			else:
				logger.info('Starts to send the script file to the server')
				f = open(path, 'rb');
				f_line = f.readline(1024);
				while len(f_line)>0:
					s.sendall(f_line);
					f_line = f.readline(1024);
				s.sendall(b'$%^endtransfer^%$');
		recv = s.recv(1024).decode(encoding = 'utf-8');
		recv = recv.split(':');
		if recv[0] != 'received':
			logger.error('The server did not recieve the script file, xremote exits')
			return 1;
		else:
			# Protocol: receive the program running log
			logger.info('The server starts to run the script...')
			recv = s.recv(1024).decode(encoding = 'utf-8');
			recv = recv.split(':');
			while recv[0] == 'script_out':
				logger.info('%s: %s'%(recv[0], ':'.join(recv[1:])));
				recv = s.recv(1024).decode(encoding = 'utf-8');
				recv = recv.split(':');
			if recv[0] == 'log_finished':
				logger.info('Script running is finished in the server')

		logger.info('xremote is done, xremote exits')
		return 0;
		
	except Exception as e:
		logger.error('%s\nxremote exits'%(traceback.format_exc()))
		return 1;


if __name__ == '__main__':
    main()
