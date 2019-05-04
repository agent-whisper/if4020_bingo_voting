import os

from src.server import bvm_server, config

if __name__ == '__main__':
    # Disables OAuthlib's HTTPs verification (Required for running locally).
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['FLASK_ENV']='development'
    ip = config['ip']
    port = config['port']
    bvm_server.run(ip, port, debug=True)