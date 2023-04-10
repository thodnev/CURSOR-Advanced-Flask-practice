"""Contains app controllers.

Controllers serve as a middleware between Model and View
"""

import models
from utils import upload
import datetime as dt
import pathlib as pth

import typing as t
import io


class StorageError(Exception):
    pass


class Storage:
    """Provides interface to files based on File model."""
    __slots__ = 'dir', 'db', '_Model'

    def __init__(self, directory, db, model):
        self.dir = pth.Path(directory)
        self.db = db
        self._Model = model

    def init_app(self, app):
        app.storage = self
    
    # @property
    # def db(self):
    #     return self.app.db
    
    def open(self, filename):
        ...
    
    def __contains__(self, val):
        if isinstance(val, io.BufferedIOBase):
            return self.has_file(val)
        return self.has_name(val)
    
    def has_name(self, val):
        ...
          
    def has_file(self, iobuf, *, fastcheck=False, _hash=None):
        ...

    def get_filenames(self, iobuf, *, fastcheck=False, hash=None):
        if hash is None:
            hash = self._Model.compute_hash(iobuf)

        # try finding existing files with the same hash
        samehash = [f.name for f in self._Model.find_by_hash(hash)]
 
        if samehash and fastcheck:
            return tuple(samehash)

        # if found same hash, compare with disk file byte-by-byte
        for samename in samehash:
            path = self.dir.joinpath(samename)
            with open(path, 'rb') as f:
                issame = upload.compare_buffers(f, iobuf)
            if issame:
                return (samename, )
        
        return tuple()


    def store(self,
              iobuf: io.BufferedIOBase,
              name: str,
              uploaded_at: t.Optional[dt.datetime]=None,
              *,
              unify_name: t.Optional[bool]=True,
              fastcheck: t.Optional[bool]=False,
              autocommit: t.Optional[bool]=True):
        """Store file-like object in database, as well as on disk.
        
        Args:
            iobuf: file-like object (binary mode) providing
                   file data
            name: original filename,
                  from where file extension is extracted
            uploaded_at: date when user uploaded the file
            unify_name: determines whether to store under original
                        name, or use unified (aka uuid) name instead
            fastlookup: whether check only by hash match and don't
                        compare files byte-by-byte
            autocommit: whether to automatically push File entry to db
                        or just return the ORM object - Transient
        """
        if uploaded_at is None:
            uploaded_at = dt.datetime.now()

        hash = self._Model.compute_hash(iobuf)

        # try finding existing files with the same hash
        existing = self.get_filenames(
            iobuf, fastcheck=fastcheck, _hash=hash)
        if existing:
            raise StorageError('file already exists', existing[0])

        # get only filename part
        name = pth.Path(pth.Path(name).name)

        # replace base with uuid, leaving .extension
        if unify_name:
            stem = upload.own_uuid(creation_date=uploaded_at)
            name = name.with_stem(stem)

        iobuf.seek(0)       # rewind buffer
        path = self.dir.joinpath(name)

        name = str(name)

        dbfile = self._Model(name=name,
                             hash=hash,
                             uploaded_at=uploaded_at)

        with open(path, 'xb') as diskfile:
            for chunk in upload.iter_chunked(iobuf):
                diskfile.write(chunk)

        if autocommit:
            self.db.session.add(dbfile)
            self.db.session.commit()

        return dbfile
    
    ...


# class Storage:
#     def __init__(self, app, directory, model):
#         self.app = app
#         self.dir = pth.Path(directory)
#         self.model = model

#         app.storage = self
    
#     def __get__(self, obj, objtype=None):
#         return FileStorage(app=self.app, dir=self.dir)