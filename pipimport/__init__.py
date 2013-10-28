# encoding: utf-8
# Author: Carles F. Julià <carles AT fjulia.name>

import sys
import os.path
import subprocess
import site
import json
import atexit

pip_bin = os.path.join(sys.prefix,'bin','pip')
python_bin = os.path.join(sys.prefix,'bin','python')
ignore_list_f = [os.path.join(s,".pipimport-ignore.json")
					for s in [sys.prefix,'.']]

def openone(flist, *args):
	for p in flist:
		try:
			f = open(p, *args)
			return (p,f)
		except IOError:
			pass
	return None,None

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
		self.ignoref, f = openone(ignore_list_f)
		if f:
			self.ignore = set(json.load(f))
			f.close()
		else:
			self.ignore = set()

	def __call__(self, name, *args, **kwargs):
		try:
			return self.realimport(name, *args, **kwargs)
		except ImportError:
			pass
		if name in self.ignore:
			raise ImportError
		print "Will install module {}".format(name)
		try:
			pip_install(name)
		except PipInstallError:
			self.ignore.add(name)
			raise ImportError
		rescan_path()
		return self.realimport(name, *args, **kwargs)

	def saveignore(self):
		fl = [i for i in [self.ignoref]+ignore_list_f if i]
		p, f = openone(fl, 'w')
		if f:
			json.dump(list(self.ignore),f)
			f.close()
		


def install():
	import __builtin__
	if isinstance(__builtin__.__import__, ImportReplacement):
		return
	importreplacement = ImportReplacement()
	__builtin__.__import__ = importreplacement


@atexit.register
def uninstall():
	import __builtin__
	if isinstance(__builtin__.__import__, ImportReplacement):
		__import__.saveignore()
		__builtin__.__import__ = __import__.realimport