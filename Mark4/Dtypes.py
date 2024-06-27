#pylint:disable=E0602

Main = globals()
Nouns = []

class Noun:
	meaning = "hi"
		
	def __init__(self):
		self._allEnt.append(self)
		
	def __init_subclass__(cls,names=()):
		cls._allEnt = []
		for y in names: Main[y] = cls
		Nouns.append(cls)
		
		
class person(Noun,names=("guy","human")):
	meaning = "hello everyone"
	def __init__(self,name=''):
		self.name = name
		super().__init__()
	
	def __str__(self):
		return self.name
		
		
		

x = guy("Rahim")
z = person()
q = person()

print(str(x))
