from gevent import monkey
monkey.patch_all()

from app import app
from gevent.pywsgi import WSGIServer

if __name__ == "__main__":
    # http_server = WSGIServer(('0.0.0.0', 80), app)
    # http_server.serve_forever()
    app.run(debug=True)
