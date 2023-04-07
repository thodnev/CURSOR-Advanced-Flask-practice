from functools import lru_cache
from flask import Flask, abort, request, Response
from flask import Blueprint, render_template

from statapi import methods

app = Flask(__name__)


# (!) Warning: normally static files *MUST* be served by
#     web server (e.g. Nginx), NOT Flask
#     But Flask provides a way to serve statics (if needed)
#     for simple projects, development and testing purposes
# (!) Flask adds default /static route to serve files from 'static' dir
# Custom folder for assets (also normally must be served by web server)
assets = Blueprint('assets', __name__, static_folder='assets')
app.register_blueprint(assets, url_prefix='/')


@app.route('/memory')
def memory():
    mem = methods['virtual_memory'](format=None)
    app.logger.debug('Got memory data:\n\t %r', mem)
    return render_template('memory.html.jinja',
                           pagetitle='Memory statistics',
                           statname='memory',
                           mem=mem
                           )

# TODO: add a template rendering route where progressbar gets filled
#       on client-side, with requests done using js fetch() method.
#       Some basics can be filled on server-side though, like page title
# TODO(extra): try to modify js:
#       - to make server return server-side rendered page
#       - with js dynamically updating its data
# TODO(extra): try extracting common template values into jinja block in separate file
#       and use template inheritance
@app.route('/memory-client')
def memory_client():
    ...
    # add logic here
    ...
    return render_template('memory-client.html')



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
