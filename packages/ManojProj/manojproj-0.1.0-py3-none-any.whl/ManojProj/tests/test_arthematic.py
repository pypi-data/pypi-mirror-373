#import pytest
from calc.math import arthematic

class setupcl:
	def __init__(self,msg):
		self.msg=msg

@pytest.fixture
def setupstart():
	setup=setupcl('Setup complete')
	return setup

@pytest.fixture
def loguser(setupstart):
	print('staring the log process')
	print('log process takes time')
	yield
	print('ending log process')
	print(setupstart.msg)

def test_add(setupstart):
	print(setupstart.msg) #no printing happened
	assert setupstart.msg=='Setup complete'
	assert arthematic.add(5,4)==9

def test_add1(loguser):
	assert arthematic.add(3,3)==6


