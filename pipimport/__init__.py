# encoding: utf-8
# Author: Carles F. Julià <carles AT fjulia.name>

import sys
import os.path
import subprocess
import importlib

pip_bin = os.path.join(sys.prefix,'bin','pip')

class PipInstallError(Exception):
	pass

def pip_install(name):
	try:
		subprocess.check_call([pip_bin, "install", name])
	except subprocess.CalledProcessError:
		raise PipInstallError

class PipLoader(object):
	def __init__(self):
		self.module = None

	def find_module(self, name, path):
		print "Will install module {}".format(name)
		self.module = None
		sys.meta_path.remove(self)
		try:
			pip_install(name)
			self.module = importlib.import_module(name)
		finally:
			sys.meta_path.append(self)
		return self

	def load_module(self, name):
		if not self.module:
			raise ImportError("Unable to load module")
		module = self.module
		sys.modules[name] = module
		return module

def install():
	sys.meta_path.append(PipLoader())