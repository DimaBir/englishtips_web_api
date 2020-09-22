from app import app


if __name__ == '__main__':
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('avrl_cs_technion_ac_il.crt', 'AVRL_cs_technion_ac_il.key')
    app.run(host="0.0.0.0", port=80, ssl_context=context, threaded=True, debug=False)
    # app.run(debug=True)
