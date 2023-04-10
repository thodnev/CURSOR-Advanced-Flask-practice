import logging
# Setup logging ASAP, as we want all
# messages to appear in log when this file is
# used as the project root (i.e. without Flask)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)


import utils
from flask import Blueprint, abort, send_file
import PIL.Image
import pathlib as pth
import random

from time import perf_counter

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


def get_cat(numext, try_random=False):
    try:
        ret = find_cat_file(numext=numext,
                            try_random=try_random)
    except ValueError:      # integer unconvertable or wrong range
        abort(404, 'Wrong image number')
    else:
        cats_bp.logger.debug('Retrieve image "%s" for '
                        'base %s with ext "%s"',
                        *ret)
        return ret




# The blueprint where all related routes reside
cats_bp = Blueprint('cats', __name__, static_folder=None)

# Note:
#   If a rule ends with a slash and is requested without a slash by the user,
#   the user is automatically redirected to the same page with a trailing 
#   slash attached.
#   If a rule does not end with a trailing slash and the user requests
#   the page with a trailing slash, a 404 not found is raised.
# So we try to always define rules with trailing slashes '/'

@cats_bp.route('/')
def list_cats():
    msg = 'There are {num} cats in our collection'
    return msg.format(num=len(CATS))


@cats_bp.route('/cat<int:num>.<string:ext>')
def cat_original(num, ext):
    t_start = perf_counter()    # measure request time

    file, base, ext = get_cat(f'{num}.{ext}', try_random=False)

    name = f'cat{base}{ext}'   # the filename passed to browser
    
    cats_bp.logger.debug('Original extension is %s', file.suffix)
    
    # if the extension is different, perform conversion with PIL
    if ext.lower() != file.suffix.lower():
        
        try:
            img = PIL.Image.open(file)
            # Save to buffer in memory and serve with Flask
            buf = utils.ImageIO(img, ext=ext)
        except utils.ImageIOError as err:
            abort(400, str(err))
        else:
            # now our file gets mocked by conversion result
            file = buf
    
    # if the file has the same extension,
    # don't convert at all and return directly

    took = perf_counter() - t_start

    if cats_bp.logger.isEnabledFor(logging.DEBUG):
        msg = f'Request took {took * 1000:.2f} ms'
        cats_bp.logger.debug(msg)

    return send_file(file, as_attachment=False, download_name=name)


@cats_bp.route('/catoftheday<name>')
def cat_modified(name):
    file, base, ext = get_cat(name, try_random=True)

    date = utils.DateTriple()       # try UADateTriple() here
    date_suffix = date.tostr(fmt='{day}_{month:.3}').lower()

    text = date.tostr(fmt='{weekday:.3},\n{day}\n{month:.3}')

    try:
        img = PIL.Image.open(file)
        bgcolor = (255, 255, 255, int(255 * 0.4))
        cut = utils.cutter.text_cutout(img, text, bgcolor=bgcolor)
        if ext in ['.jpg', '.jpeg', '.jfif']:
            # eliminate alpha-channel as JPEG has no alpha
            cut = cut.convert('RGB')
        file = utils.ImageIO(cut, ext=ext)
    except utils.ImageIOError as err:
        abort(400, str(err))

    # passed to browser
    name = f'catoftheday{base}-{date_suffix}{ext}'
    return send_file(file, as_attachment=False, download_name=name)
