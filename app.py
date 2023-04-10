import catday
from models import db   # Flask-SQLAlchemy
from flask import Flask, Response, abort, send_file
import logging

app = Flask(__name__)

# We use SQLite for testing
# (!) But it is embeddable db not suitable to serve online users
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testdb.sqlite'
# Attach Flask-SQLAlchemy to app
db.init_app(app)

# Add all catday routes
app.register_blueprint(catday.cats_bp, url_prefix='/cats')
# a hack to make app logger accessible
catday.cats_bp.logger = app.logger


@app.route('/')
def hello_world():
    # TODO: use proper template instead of the following
    ret = r'Try <a href="/cats/catoftheday.jpg">Cat of the Day</a>'
    ret += r'<br><img src="/cats/catoftheday.jpg" alt="catoftheday"'
    ret += r' style="max-height: 90vh; margin: auto; display: flex"></img>'
    return Response(ret, mimetype='text/html')

    


if __name__ == '__main__':
    # We need to set logging to be able to see everything
    import logging
    app.logger.setLevel(logging.DEBUG)

    with app.app_context():
        db.create_all()         # create tables if do not exist


    # (!) Never run your app on '0.0.0.0 unless you're deploying
    #     to production, in which case a proper WSGI application
    #     server and a reverse-proxy is needed
    #     0.0.0.0 means "run on all interfaces" -- insecure
    app.run(host='127.0.0.1', port=5000, debug=True)