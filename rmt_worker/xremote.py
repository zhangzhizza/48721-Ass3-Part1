"""
This script connects to the remote server to run the python code.
"""
import argparse, os, logging, traceback, socket, colorlog

def main():
    parser = argparse.ArgumentParser(description='Send a Python script to the server to execute.')
    parser.add_argument('--ip', type=str, default='128.2.111.196', help='The remote server IP')
    parser.add_argument('--port', type=int, default=48721, help='The remote server port')
    parser.add_argument('--key', type=str, help='The connection key')
    parser.add_argument('--path', type=str, help='The local path the Python script (to be run)')
    args = parser.parse_args();
    run_client(args.ip, args.port, args.key, args.path);
        
def run_client(ip, port, key, path):
	# Create main logger
	logger = logging.getLogger('xremote')
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s_%(name)s_%(levelname)s: %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)
	# Create scripting output logger
	logger_scpout = logging.getLogger('script_out')
	logger_scpout.setLevel(logging.DEBUG)
	ch_scpout = colorlog.StreamHandler()
	ch_scpout.setLevel(logging.INFO)
	formatter = colorlog.ColoredFormatter('%(log_color)s%(message)s', 
											log_colors={
											'DEBUG':    'cyan',
											'INFO':     'green',
											'WARNING':  'yellow',
											'ERROR':    'red',
											'CRITICAL': 'red,bg_white',
											},)
	ch_scpout.setFormatter(formatter)
	logger_scpout.addHandler(ch_scpout)
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
			logger.info('Server says: it starts to run the script, '+
						'the following is the script running output from the server...')
			recv = s.recv(1024).decode(encoding = 'utf-8');
			recv = recv.split(':');
			while recv[0] == 'script_out':
				logger_scpout.info('%s%s'%('', ':'.join(recv[1:])));
				recv = s.recv(1024).decode(encoding = 'utf-8');
				recv = recv.split(':');
			if recv[0] == 'scripting_finish':
				logger.info('Server says: the scripting is finished in the server, '+
							'the results are being collected...');
				s.sendall(b'ready_to_recieve');
			# Protocol: receive the results
			recv = s.recv(1024).decode(encoding = 'utf-8');
			recv = recv.split(':');
			if recv[0] == 'res_collect_fail':
				logger.error('Server says: the results collection failed in the server, xremote exits');
			elif recv[0] == 'res_send':
				recv = s.recv(1024).decode(encoding = 'utf-8');
				recv = recv.split(':');
				res_size = int(recv[1])/1024.0; # kb
				logger.info('Server says: the results have been collected, '+
							'the client starts to download the results (%.2f kb)...'%(res_size));
				s.sendall(b'break') # Break
				# Receive the results
				# Create this result dir
				res_dir = '.' + os.sep + get_res_name('xremote_res.zip');
				with open(res_dir, 'wb+') as io_f:
					recv = s.recv(1024);
					io_f.write(recv)
					written_byte = len(recv);
					recv_byte = len(recv);
					while recv_byte < res_size * 1024.0:
						recv = s.recv(1024);	
						recv_byte += len(recv);
						io_f.write(recv);
						written_byte += len(recv);
						written_prop = (written_byte/1024.0)/res_size;
						if written_byte%10240 == 0:
							logger.info('Downloading in progress %s%'%(written_prop * 100));
			
				logger.info('The results has been downloaded at %s'%(os.path.abspath(res_dir)));
		logger.info('xremote is done, xremote exits')
		return 0;
		
	except Exception as e:
		logger.error('%s\nxremote exits'%(traceback.format_exc()))
		return 1;

def get_res_name(org_name, bk_name = None, in_para_int = None):
	if bk_name == None:
		bk_name = org_name;
	org_name_fnt, org_name_ext = _get_name_fnt_ext(org_name);
	open_para_idx = org_name_fnt.rfind('(');
	if in_para_int == None:
		in_para_int = 1;
		next_add_name = '(1)';
	else:
		in_para_int += 1;
		next_add_name = '(%s)'%(in_para_int);
	if os.path.isfile('.' + os.sep + org_name):
		bk_name_fnt, bk_name_ext = _get_name_fnt_ext(bk_name);
		if len(org_name_ext) > 0:
			new_name = bk_name_fnt + next_add_name + '.' + bk_name_ext;
		else:
			new_name = bk_name_fnt + next_add_name;
		return get_res_name(new_name, bk_name, in_para_int);
	else:
		return org_name;

def _get_name_fnt_ext(org_name):
	org_name_list = org_name.split('.');
	org_name_list_lg = len(org_name_list);
	if org_name_list_lg > 1:
		org_name_fnt = '.'.join(org_name_list[0: org_name_list_lg - 1]);
		org_name_ext = org_name_list[-1];
	else:
		org_name_fnt = org_name;
		org_name_ext = '';
	return (org_name_fnt, org_name_ext);




if __name__ == '__main__':
    main()
