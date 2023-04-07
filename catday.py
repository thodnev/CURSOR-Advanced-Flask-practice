import logging
# Setup logging ASAP, as we want all
# messages to appear in log when this file is
# used as the project root (i.e. without Flask)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)


from utils import DateTriple, cutter
import pathlib as pth
import random

# Directory containing cat images,
# relative to project directory
CATDIR = './cats'

# The logger we use
log = logging.getLogger(__name__)

_PROJDIR = pth.Path(__file__).parent
log.debug('Project directory is "%s"', _PROJDIR.resolve())

def _get_cats(catdir=CATDIR):
    # Ensure all directories reside under project directory
    # and are resolved relative to it

    catdir = _PROJDIR.joinpath(pth.Path(catdir))
    assert catdir.is_relative_to(_PROJDIR)
    cats = tuple(catdir.iterdir())
    return cats

# collect all cat images under supplied directory
CATS = _get_cats(CATDIR)

# Put some info into log
log.info('Cats directory set to: %s', CATDIR)
if log.isEnabledFor(logging.INFO):
    log.info('Collected %s cat images:\n\t%s',
              len(CATS), '\n\t'.join(CATS))


def find_cat_file(numext, try_random=False):
    p = pth.Path(numext)
    base, ext = (p.stem, p.suffix) if p.suffix else ('', numext)

    # num specifies the cat image to use
    # if num is omitted, and try_random is True, random cat should appear
    if try_random is True and not base:
        num = random.randint(0, len(CATS) - 1)
    else:
        num = int(base)      # try integer conversion
    
    if num < 0 or num > len(CATS) - 1:
        raise ValueError
    
    return CATS[num], base, ext