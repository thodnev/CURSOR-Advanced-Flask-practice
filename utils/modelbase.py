from flask_sqlalchemy import model
import sqlalchemy as sa       # original package for inspect()

"""Provides useful Model base class for Flask-SQLAlchemy."""

__all__ = 'ModelBase',


class ModelBase(model.Model):
    """Implement our own model class, with a decent repr default.

    see https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/customizing/#model-class
    on customizing Flask-SQLALchemy base
    """
    def __repr__(self) -> str:
        return self._repr()


    def _repr(self, *columns):
        """__repr__ helper
        
        Used like  _repr('id', 'user', 'blah')
        inside __repr__  of models
        """

        # if fields not excplicitly provided, use all
        # we can get from instance
        if not columns:
            columns = [c.name for c in self.__table__.columns]

        # get DB<->object mapping state
        # https://docs.sqlalchemy.org/en/20/orm/session_state_management.html
        # https://github.com/pallets-eco/flask-sqlalchemy/blob/main/src/flask_sqlalchemy/model.py#L56
        state = sa.inspect(self)
        assert state is not None

        if state.transient:
            kind = 'T~'
        elif state.pending:
            kind = 'P~'
        else:
            kind = ''
        cls = f'{kind}{type(self).__name__}'

        # Build fancy attribute list
        fields = []
        for name in columns:
            try:
                val = getattr(self, name)
                fields.append(f'{name}={val!r}')
            except sa.orm.exc.DetachedInstanceError:
                fields.append(f'{name}=...')
        
        if fields:
            return f'<{cls}({", ".join(fields)})>'
        return f'<{cls} {id(self)}>'