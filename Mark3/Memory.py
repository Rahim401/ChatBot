import json as js
from functools import reduce
from utils import timer
import datetime as dt
t = timer()

gnd_data = js.loads(open("/storage/emulated/0/Datasets/gnd.json","r").read())
now = dt.datetime.now()
base_dt = dt.datetime(year=now.year,month=1,day=1,hour=0,minute=0,second=0,microsecond=0)

def predict_gnd(name): # Used to predict the Gender By Name
	try: gnd = gnd_data[name[-3:].lower()]
	except KeyError: return ("unk",0)
	if gnd[0] > gnd[1]: return "male",(gnd[0]/sum(gnd))
	else: return "female",(gnd[1]/sum(gnd))
	
def Dt2Sdt(Dt):
	return Dt.strftime("d:%Y_%m_%d t:%I_%M_%p")
	
def Sdt2Dt(Dt,base_dt=base_dt):
	if " " in Dt:
		date,time = Dt.split(" ")
		date = Sdt2Dt(date)
		return Sdt2Dt(time,base_dt=date)
	else:
		if Dt[0]=="d":
			year,month,day = Dt[3:].split("_")
			try: month = int(month) if month.isnumeric() else dt.datetime.strptime(month,"%B").month if month else 1
			except ValueError: month = dt.datetime.strptime(month,"%b").month
			return dt.datetime(int(year) if year else base_dt.year,month,int(day) if day else 1,hour=0,minute=0,second=0,microsecond=0)
		else:
			hour,minute,apm = Dt[2:].split("_")
			hour = "00" if not hour else "0"+hour if len(minute)==1 else hour
			minute = "00" if not minute else "0"+minute if len(minute)==1 else minute
			apm = apm if apm else "pm"
			new_time = dt.datetime.strptime(f"t:{hour}_{minute}_{apm}","t:%I_%M_%p")
			return base_dt.replace(hour=new_time.hour,minute=new_time.minute,second=0,microsecond=0)
			
def Sdt_overrider(dtst,dtnd):
	dtst,dtnd = dtst.split("_"),dtnd.split("_")
	for y in range(3):
		if dtnd[y].replace("d:","") == "": continue
		else: dtst[y] = dtnd[y]
	return "_".join(dtst)

class Memory:
	# This memory class is used to store the informations
	def __init__(self):
		self.pr2 = {}
		self.pl2 = {}
		self.dt2 = {}
		self.tng2 = {}
		self.pr3 = {}
		self.pl3 = {}
		self.dt3 = {}
		self.tng3 = {}
		self.merger = "&"
		self.tg_ls = ["<pr2>","<pr3>","<pl2>","<pl3>","<dt2>","<dt3>","<tng2>","<tng3>"]
	
	@property
	def mem_ls(self): #returns all memorys as list
		return [self.pr2,self.pr3,self.pl2,self.pl3,self.dt2,self.dt3,self.tng2,self.tng3]
	
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
	
	def merge2(self,ls,upto=0,demerge=False): #Merges with replacing the variables it already has
		if type(ls)==str: ls = self.demerge(ls)
		if demerge and len(ls) == 1:
			try: return self.demerge2(ls)
			except KeyError: pass
		if ls[-1]=="name": ls.pop(-1) # is ls has name pops it out
		print(ls)
		try: ls[0] = self.allmem[ls[0]]
		except KeyError: pass
		upto = len(ls) + upto
		def Sub_merge(st,nd): # Def that checks and reduces
			mr = st+self.merger+nd
			if upto==ls.index(nd): return mr
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
		
		
	def set_pr3(self,vr,it):
		for ky,vl in {"you":"you&your","i":"my&i","female":"she&her&hers","male":"he&his&him","unk":"she&her&hers&he&his&him"}.items():
			if vr == ky:
				for x in vl.split("&"): self.pr3[x] = it
				break
		else: pass
	
	def set_pr2(self,vr,it):
		it = self.merge2(it)
		if len(vr) == 1 and vr[0] in ["i","you","she","he"]:
			self.set_pr3(vr[0],it)
		else:
			self.pr2[self.merge2(vr,-1)] = it
			self.set_pr3(predict_gnd(it)[0],it)
		self.tng3["it"] = it
		
	def set_pl2(self,vr,it,pl=""):
		it = self.merge2(it)
		if pl: self.pl3[pl] = it
		self.pl2[self.merge2(vr,-1)] = it
		self.tng3["it"] = it
	
	def set_tng2(self,vr,it):
		it = self.merge2(it)
		self.tng2[self.merge2(vr,-1)] = it
		self.tng3["it"] = it
	
	def set_dt2(self,vr,it):
		it = Sdt2Dt(self.merge2(it))
		mr = self.merge2(vr,-1)
		self.dt2[mr] = it
		if "&born" in mr:
			self.tng2[mr.replace("&born","&age")] = str(now.year - it.year)
			birthday = it.replace(year=now.year)
			self.dt2[mr.replace("&born","&birthday")] = birthday if now < birthday else birthday.replace(year=birthday.year+1)
		self.tng3["it"] = it
			
	def get_pr(self,vr):
		ret = self.merge2(vr,demerge=True)
		self.tng3["it"] = ret
		if "&" not in ret: return ret
			
	def get_pl(self,vr):
		ret = self.merge2(vr,demerge=True)
		self.tng3["it"] = ret
		if "&" not in ret: return ret
		
	def get_dt(self,vr):
		ret = self.merge2(vr)
		self.tng3["it"] = ret
		if "&" not in ret: return Sdt2Dt(ret,base_dt)
		
	def get_tng(self,vr):
		ret = self.merge2(vr,demerge=True)
		self.tng3["it"] = ret
		if "&" not in ret: return ret


# } End of the class

if __name__ == "__main__":
	mem = Memory()
	mem.set_pr3("you","Alpha")
	mem.set_pr3("i","Rahim")
	mem.set_pr2(["your","boss"],["Rahim"])
	mem.set_pr2(["my","mother"],["kamaliya"])
	mem.set_pr2(["your","boss","mother","mother"],["ansariya"])
	mem.set_tng2(["my","favoriet","number"],["67"])
	mem.set_dt2(["i","born"],["dt:2003_4_26"])
	mem.set_tng2(["my","age"],["18"])
	mem.set_pl2("i","bangalore")
	mem.set_pl2(["your","boss","mother","mother"],["tamilnadu"])
	mem.print()
	print(mem.get_pr("i"))
	t.stop()