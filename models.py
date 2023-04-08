from utils import ModelBase
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(model_class=ModelBase)       # model_class to use customized base


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    md5hash = db.Column(db.String(32))
    name = db.Column(db.String(32 + len('.webm')))
    uploaded_at = db.Column(db.DateTime(timezone=True))



if __name__ == '__main__':
    from flask import Flask
    dummyapp = Flask(__name__)
    dummyapp.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///database.sqlite')
    db.init_app(dummyapp)

    # Trick Flask into thinking we're into app context
    # to experement in interactive session
    ctx = dummyapp.app_context()

    # normally used as:
    # with app.app_context():
    #     db.create_all()
    #     ...
    ctx.__enter__()


    # your demo code below
    import datetime

    db.create_all()

    cat = File(md5hash='bdb7895cd9c8a947aa35b6f73bf2fbc7',
               name='cat-g8624951f0_1280.jpg',
               uploaded_at=datetime.datetime.now())
    dog = File(md5hash='thereissomehash',
               name='dog.jpg',
               uploaded_at=datetime.datetime.now())

    db.session.add(cat)
    db.session.add(dog)     # cat and dog will be added simultaneously
    db.session.commit()     # now it's on our database

    # Get all files from db 
    res = db.session.execute(db.select(File))
    files = res.scalars().all()
    files = list(files)

    # Get files whose names is 'dog.jpg'
    res = db.session.execute(db.select(File).filter(File.name == 'dog.jpg'))
    dogfiles = res.scalars().all()
    dogfiles = list(dogfiles)

