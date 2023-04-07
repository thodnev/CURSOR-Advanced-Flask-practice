from functools import lru_cache
from flask import Flask, abort, request, Response

from statapi import methods

app = Flask(__name__)


@app.route('/stats/')
@lru_cache(maxsize=1)  # can use cuz no flask proxies refered
def stats_root():
    """List all methods."""
    ret = {'methods': list(methods)}
    return ret  # auto-converted to json by flask


@app.route('/stats/<string:method>', methods=['GET'])
def stats(method):
    format = request.args.get('format')

    try:
        func = methods[method]
    except KeyError:
        abort(404, f'Method {method} not found')

    try:
        # format is set on a statapi module level defaults
        res, mime = func() if format is None else func(format=format)
    except Exception as exc:
        abort(400)

    # TODO: add error reporting verbosity
    #       e.g. when format is not supported

    return Response(res, mimetype=mime)


if __name__ == '__main__':
    # We need to set logging to be able to see everything
    import logging
    app.logger.setLevel(logging.DEBUG)

    # (!) Never run your app on '0.0.0.0 unless you're deploying
    #     to production, in which case a proper WSGI application
    #     server and a reverse-proxy is needed
    #     0.0.0.0 means "run on all interfaces" -- insecure
    app.run(host='127.0.0.1', port=5000, debug=True)
