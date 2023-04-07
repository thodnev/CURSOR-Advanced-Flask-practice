import logging
import datetime as dt
from collections import namedtuple

__all__ = 'DateTriple', 'UADateTriple'

log = logging.getLogger(__name__)


class DateTriple(namedtuple('DateTriple', 'weekday day month')):
    WEEKDAYS = ('Monday', 'Tuesday', 'Wednesday', 
                'Thursday', 'Friday', 'Saturday', 'Sunday')
    MONTHS = ('January', 'February', 'March', 'April',
              'Mars', 'June', 'July', 'August',
              'September', 'October', 'November', 'December')

    def __new__(cls, date=None):
        """Create a namedtuple containing textual date representation.
        """
        date = dt.date.today() if date is None else date
        weekday = cls.WEEKDAYS[date.weekday()]
        day = date.day
        month = cls.MONTHS[date.month - 1]
        res = super().__new__(cls, weekday=weekday, day=day, month=month)
        return res
    
    def tostr(self, fmt='{weekday}\n{day} {month}'):
        """Returns string representation of the triple."""
        return fmt.format(**self._asdict())


class UADateTriple(DateTriple):
    WEEKDAYS = ('Понеділок', 'Вівторок', 'Середа', 
                'Четвер', 'П\'ятниця', 'Субота', 'Неділя')
    MONTHS = ('Січня', 'Лютого', 'Березня', 'Квітня', 
              'Травня', 'Червня', 'Липня', 'Серпня',
              'Вересня', 'Жовтня', 'Листопада', 'Грудня')


if log.isEnabledFor(logging.DEBUG):
    d = DateTriple().tostr()
    log.debug('Today is %s', d.replace('\n', ', '))