# encoding: utf-8
# Author: Carles F. Julià <carles AT fjulia.name>

"""
Pipimport automatically installs missing modules using pip at import time.
It is best used with virtualenv.

Just import pipimport and call install():

>>> import pipimport
>>> pipimport.install()

Now you can import missing modules and they will be downloaded and installed by pip.

Author: Carles F. Julià <carles AT fjulia.name>
"""

import sys
import os.path
import subprocess
import site
import atexit
import os.path

try:
    import __builtin__
except ImportError:
    import builtins as __builtin__

_pip_bin = os.path.join(sys.prefix, 'bin', 'pip')
_ignore_list_f = [os.path.join(s, ".pipimport-ignore")
                  for s in [sys.prefix, '.']]


def _openone(flist, *args):
    for p in flist:
        try:
            f = open(p, *args)
            return (p, f)
        except IOError:
            pass
    return None, None


class PipInstallError(Exception):
    pass


def _pip_install(name):
    try:
        subprocess.check_call([_pip_bin, "install", name])
    except subprocess.CalledProcessError:
        raise PipInstallError()


def _rescan_path():
    absprefix = os.path.abspath(sys.prefix)
    abspaths = [os.path.abspath(s) for s in sys.path]
    paths = [s for s in abspaths if s.startswith(absprefix)
             and (s.endswith('site-packages') or s.endswith('site-python'))]
    site.addsitedir(paths[0])


class ImportPipInstaller(object):

    def __init__(self):
        self.realimport = __import__
        self.ignoref, f = _openone(_ignore_list_f)
        if f:
            self.ignore = set([l.strip() for l in f])
            f.close()
        else:
            self.ignore = set()

    def __call__(self, name, *args, **kwargs):
        try:
            return self.realimport(name, *args, **kwargs)
        except ImportError:
            pass
        if name in self.ignore:
            raise ImportError()
        print("Will install module {}".format(name))
        try:
            _pip_install(name)
        except PipInstallError:
            self.ignore.add(name)
            raise ImportError()
        _rescan_path()
        return self.realimport(name, *args, **kwargs)

    def saveignore(self):
        fl = [i for i in [self.ignoref] + _ignore_list_f if i]
        p, f = _openone(fl, 'w')
        if f:
            f.writelines([i + '\n' for i in self.ignore])
            f.close()


def install():
    if isinstance(builtins.__import__, ImportPipInstaller):
        return
    importreplacement = ImportPipInstaller()
    builtins.__import__ = importreplacement


@atexit.register
def uninstall():
    if isinstance(builtins.__import__, ImportPipInstaller):
        __import__.saveignore()
        builtins.__import__ = __import__.realimport
