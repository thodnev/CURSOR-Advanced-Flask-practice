import catday
import models   # Flask-SQLAlchemy
from models import db
from controllers import Storage, StorageError
from flask import Flask, Response, request, abort, send_file, render_template
import logging

app = Flask(__name__)

# We use SQLite for testing
# (!) But it is embeddable db not suitable to serve online users
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testdb.sqlite'
# Attach Flask-SQLAlchemy to app
db.init_app(app)

# Limit maximum incoming length to 16 MiB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# This is our own controller
storage = Storage(directory='uploads', db=db, model=models.File)
storage.init_app(app)

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

# (!) IMPORTANT (!):
# Below is minimal example. Uploads (as well as any other user input)
# should be handled with caution and never trusted
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    msg = ''

    if request.method == 'POST':
        file = request.files['images']
        try:
            dbfile = app.storage.store(
                iobuf=file.stream, name=file.filename,
                unify_name=True, fastcheck=False)
        except StorageError as err:
            msg = str(err)
        else:
            msg = f'Saved as {dbfile.name} with id {dbfile.id}'

    return render_template('upload.html', status=msg)

        



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