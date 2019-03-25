from rmt_worker.server import *
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run xserver.')
    parser.add_argument('--ip', type=str, default='128.2.111.196', help='The X server IP')
    parser.add_argument('--port', type=int, default=48721, help='The X server port')
    args = parser.parse_args();
    xserver = WorkerServer(args.ip, args.port)
    xserver.run_server();

if __name__ == '__main__':
    main()