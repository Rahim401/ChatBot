import json as js
from functools import reduce
from utils import timer
import datetime as dt
t = timer()

gnd_data = js.loads(open("/storage/emulated/0/Datasets/gnd.json","r").read())
def predict_gnd(name): # Used to predict the Gender By Name
	try: gnd = gnd_data[name[-3:].lower()]
	except KeyError: return ("unk",0)
	if gnd[0] > gnd[1]: return "male",(gnd[0]/sum(gnd))
	else: return "female",(gnd[1]/sum(gnd))

class Memory():
	# This memory class is used to store the informations
	def __init__(self):
		self.__pr2__ = {}
		self.__pl2__ = {}
		self.__tng2__ = {}
		self.__pr3__ = {}
		self.__tng3__ = {}
		self.merger = "&"
		self.tg_ls = ["<pr2>","<pr3>","<pl2>","<tng2>","<tng3>"]
	
	@property
	def mem_ls(self): #returns all memorys as list
		return [self.__pr2__,self.__pr3__,self.__pl2__,self.__tng2__,self.__tng3__]
	
	@property
	def allmem(self): #returns all memory combined together
		mem = {}
		for y in self.mem_ls: mem.update(y)
		return mem
	
	@property
	def allremem(self): #returns all memory combined together
		mem = {}
		for y in self.mem_ls:
			for ky,vl in y.items():
				ky = "i" if ky=="you" else "my" if ky=="your" else "you" if ky=="i" else "your" if ky=="my" else ky
				if vl in mem: mem[vl].append(ky)
				else: mem[vl] = [ky,]
		return mem
		
	def merge(self,ls): #merges the the words of the tag
		return self.merger.join(ls)
	
	def demerge(self,ky): #convertes the merged keys to list
		return ky.split(self.merger)
		
	def print(self): #prints the value of current memorys
		for x,y in zip(self.tg_ls,self.mem_ls): print(f"{x[1:-1]} : {y}")
	
	def merge2(self,ls,upto=False,demerge=False): #Merges with replacing the variables it already has
		if type(ls)==str: ls = self.demerge(ls)
		if len(ls) == 1 and demerge:
			try: return self.demerge2(ls)
			except KeyError: pass
		try: ls[0] = self.allmem[ls[0]]
		except KeyError: pass
		def Sub_merge(st,nd): # Def that checks and reduces
			mr = st+self.merger+nd
			if upto and nd==ls[-1]: return mr
			try: return self.allmem[mr]
			except KeyError: return mr
		return reduce(Sub_merge,ls) # returns the reduced output
	
	def demerge2(self,ky):
		if type(ky)==str:
			vl1 = self.allremem[ky]
			if "my" in vl1: return "my"
			elif "your" in vl1: return "your"
			else: return self.demerge2(self.demerge(vl1[0]))
		else:
			vl = self.merge([self.demerge2(ky[0]),*ky[1:]])
			if vl=="your": return "you"
			elif vl=="my": return "me"
			else: return vl.replace("&"," ")
		
	def Set_it(self,sm):
		(ky_typ,ky),(vl_typ,vl) = tuple(sm.items()) # Gets the key,value and their type from the sm dict came from processer
		if ky.count("&") < vl.count("&"): ky_typ,ky,vl_typ,vl = vl_typ,vl,ky_typ,ky #swaps the ky and vl if vl has more words
		ky,vl = self.merge2(ky,True),self.merge2(vl) #Get the pureified ky and vl
		if "pr" in vl_typ: # Find and sets the pr dicts
			if ky in ("i","you","he","you"): gnd = ky
			else:
				self.__pr2__[ky] = vl
				gnd = predict_gnd(vl)[0] # gets the gender of the person
			for ky1,vl1 in {"you":"you&your","i":"my&i","female":"she&her&hers","male":"he&his&him","unk":"she&her&hers&he&his&him"}.items():
				if gnd == ky1:
					for x in vl1.split("&"): self.__pr3__[x] = vl
					break
		elif "pl" in vl_typ: self.__pl2__[ky] = vl # Find and sets pl
		elif "tng" in vl_typ: self.__tng2__[ky] = vl # Find and sets tng
		else: raise ValueError("Unknown type")
		
		
		
			
		
		
	

		

# } End of the class

if __name__ == "__main__":
	mem = Memory()
	mem.Set_it({"pr3:":"i","pr1:":"rahim"})
	mem.Set_it({"pr3:":"you","pr1:":"alpha"})
	mem.Set_it({"pr1:":"i","pr2:":"your&boss"})
	mem.Set_it({"pr1:":"kamaliya","pr2:":"my&mother"})
	mem.Set_it({"vrb1:":"my&mother&live","pl1:":"america"})
	mem.print()
	t.stop()