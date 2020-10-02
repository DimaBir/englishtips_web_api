from app import app

from gevent import monkey
from gevent.pywsgi import WSGIServer

if __name__ == '__main__':
    monkey.patch_all()
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('avrl_cs_technion_ac_il.crt', 'AVRL_cs_technion_ac_il.key')
    # app.run(host="0.0.0.0", port=80, ssl_context=context, threaded=True, debug=False)
    # app.run(debug=True)

    http_server = WSGIServer(('0.0.0.0', 80), app, keyfile='AVRL_cs_technion_ac_il.key',
                             certfile='avrl_cs_technion_ac_il.crt')
    http_server.serve_forever()
