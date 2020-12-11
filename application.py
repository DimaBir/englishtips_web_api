from gevent import monkey
monkey.patch_all()

from app import app
from gevent.pywsgi import WSGIServer

if __name__ == "__main__":
    # http_server = WSGIServer(('0.0.0.0', 5000), app, keyfile='AVRL_cs_technion_ac_il.key',
    #                          certfile='avrl_cs_technion_ac_il.crt')
    # http_server.serve_forever()
    app.run(debug=True)
