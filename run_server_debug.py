import os

from src.server.bvm_server import server, config

if __name__ == '__main__':
    # Disables OAuthlib's HTTPs verification (Required for running locally).
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['FLASK_ENV']='development'
    ip = config['ip']
    port = config['port']
    server.run(ip, port, debug=True)