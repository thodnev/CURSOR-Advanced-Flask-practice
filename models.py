from utils import ModelBase
from utils import upload
from flask_sqlalchemy import SQLAlchemy

import datetime
import hashlib

from typing import List, Optional
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


"""Contains application models."""

db = SQLAlchemy(model_class=ModelBase)
# model_class to use our customized base (not default one)

class File(db.Model):
    # (using older style):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(32),
                     db.CheckConstraint('LENGTH(hash) = 32'))
    name = db.Column(db.String(32 + len('.webm')), unique=True)
    uploaded_at = db.Column(db.DateTime(timezone=False))

    # OR (using newer type annotations style)
    # id: Mapped[int] = mapped_column(primary_key=True)
    # md5hash: Mapped[str] = mapped_column(String(32))
    # name: Mapped[str] = mapped_column(String(32 + len('.webm')))
    # uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True)))

    @staticmethod
    def compute_hash(iobuf, *, chunk_kb=1024):
        """Compute hash using algo table is relying on.
        
        (!) Since table fields depend on hash algo used,
        this method is defined on a table-level
        (all in one place)

        Returns:
            hash for a provided (binary) file-like object
        """
        hash = upload.get_hash(iobuf, 
                               hashmethod=hashlib.md5,
                               chunk_kb=chunk_kb)
        return hash.hex()
    
    @classmethod
    def find_by_hash(cls, hash):
        """Alias to query db for all files by provided hash"""
        found = db.session.scalars(
            db.select(cls).filter(cls.hash == hash))
        return found
    
    @classmethod
    def get_by_filename(cls, filename):
        found = db.session.execute(
            db.select(cls).filter(cls.name == filename))
        return found.scalar_one_or_none()
    
    @classmethod
    def get_by_id(cls, id):
        found = db.session.execute(
            db.select(cls).filter(cls.id == id))
        found = found.scalar_one_or_none()

        if found is None:
            raise LookupError
        return found



if __name__ == '__main__':
    import controllers as ctl
    from flask import Flask
    dummyapp = Flask(__name__)
    dummyapp.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///testdb.sqlite')
    #dummyapp.config['SQLALCHEMY_ECHO'] = True
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

    # cat = File(hash='bdb7895cd9c8a947aa35b6f73bf2fbc7',
    #            name='cat-g8624951f0_1280.jpg',
    #            uploaded_at=datetime.datetime.now())
    # dog = File(hash='hashmustbe32symcauseofconstraint',
    #            name='dog.jpg',
    #            uploaded_at=datetime.datetime.now())

    # db.session.add(cat)
    # db.session.add(dog)     # cat and dog will be added simultaneously
    # db.session.commit()     # now it's on our database

    # Get all files from db 
    res = db.session.execute(db.select(File))
    files = res.scalars().all()
    files = list(files)

    # Get files whose names is 'dog.jpg'
    res = db.session.execute(db.select(File).filter(File.name == 'dog.jpg'))
    dogfiles = res.scalars().all()
    dogfiles = list(dogfiles)

