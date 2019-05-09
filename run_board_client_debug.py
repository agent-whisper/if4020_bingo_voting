import os

from src.client.bvm_board_client import board_client, config

if __name__ == '__main__':
    os.environ['FLASK_ENV']='development'
    ip = config['client_ip']
    port = config['client_port']
    board_client.run(ip, port, debug=True)