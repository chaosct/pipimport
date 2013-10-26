# encoding: utf-8
# Author: Carles F. Julià <carles AT fjulia.name>

import sys
import os.path
import subprocess
import site


pip_bin = os.path.join(sys.prefix,'bin','pip')
python_bin = os.path.join(sys.prefix,'bin','python')

class PipInstallError(Exception):
	pass

def pip_install(name):
	try:
		subprocess.check_call([pip_bin, "install", name])
	except subprocess.CalledProcessError:
		raise PipInstallError

def rescan_path():
	paths = [s for s in sys.path if s.startswith(sys.prefix)
		and (s.endswith('site-packages') or s.endswith('site-python'))]
	site.addsitedir(paths[0])


class ImportReplacement(object):
	def __init__(self):
		self.realimport = __import__

	def __call__(self, name, *args, **kwargs):
		try:
			return self.realimport(name, *args, **kwargs)
		except ImportError:
			pass
		print "Will install module {}".format(name)
		try:
			pip_install(name)
		except PipInstallError:
			raise ImportError
		rescan_path()
		return self.realimport(name, *args, **kwargs)
		


def install():
	import __builtin__
	importreplacement = ImportReplacement()
	__builtin__.__import__ = importreplacement