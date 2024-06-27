#pylint:disable=W0102
from utils import timer
t = timer()
import re
from Control import ctl
from functools import reduce
from Bot_utils import Memory
import datetime as dt
import random as rd

now = dt.datetime.now()
now_func = dt.datetime.now
Math_op_dilouge = {
		"Sum": [	lambda nums : reduce(lambda a,b:a+b,nums),
						["Your sum is {}","It is {}","Gotcha , {}","Got it,{}","I think {}","The sum is {}"]],
		
		"Sub" : [	lambda nums : reduce(lambda a,b:a-b,nums),
						["{} is the difference","It is {}","Gotcha , {}","Got it,{}","I think {}","The difference is {}"]],
		
		"Mul" : [	lambda nums : reduce(lambda a,b:a*b,nums),
						["{} is the product","It is {}","Gotcha , {}","Got it,{}","I think {}","The Product is {}"]],
		
		"Div" : [	lambda nums : reduce(lambda a,b:a/b,nums),
						["There are {0} {2}s in {1}","It is {0}","Gotcha , {0}","Got it,{0}","I think it is {0}"]],
		
		"Pow" : [	lambda nums : nums[0]**nums[1],
						["{1} to the power of {2} is {0}","It is {}","{}","Got it,{}","I think {}","{1}^{2} is {0}"]],
		
		"Sqr" : [	lambda nums : nums[0]**2,
						["{} is the square of {}","It is {}","Square of {1} is {0}","Got it,{}","I think it's {}","{}"]],
		
		"Cub" : [	lambda nums : nums[0]**3,
						["{} is the cube of {}","It is {}","Cube of {1} is {0}","Got it,{}","I think it's {}","{}"]],
		
		"Sqrt" : [	lambda nums : nums[0]**(1/2),
						["{} is the square root of {}","It's {}","Square root of {1} is {0}","Got it,{}","I think it's {}","{}"]],
		
		"Cubrt" : [	lambda nums : nums[0]**(1/3),
						["{} is the cube root of {}","It's {}","Cube root of {1} is {0}","Got it,{}","I think it's {}","{}"]],
		}

# The Protocals Parent class {
class protocals():
	
	def __init__(self,ltm=Memory(),do=False):
		self.isctl = ctl.chk
		if do: self.do = self.isctl
		else: self.do = False
		self.ltm = ltm
		self.txt1,self.txt2,self.txt3,self.sm = "","","",{}
		self.ProtosIn = [self.Math,self.Talks,self.Info,self.Switch,self.DoIt,self.GetInfo,self.SetInfo]
	
	def say(self,output,*args,**kwargs): # returns a random formated dilogue
		out = rd.choice(output)
		if args: return out.format(*args)
		elif kwargs: return out.format_map(**kwargs)
		else: return out
	
	def Math(self):
		if "<mt>" not in self.txt3: return None
		mt = self.sm["<mt>"]
		self.sm.pop("<mt>")
		nums = []
		for vl in self.sm.values():
			if vl.isdigit(): nums.append(int(vl)); continue
			else:
				vl1 = self.ltm.merge2(vl)
				if vl1.isdigit(): nums.append(int(vl1))
		if "are there in" in self.txt1 or "from" in self.txt1: nums.reverse()
		if mt in ("add","+","sum"): ToDo = Math_op_dilouge["Sum"]
		elif mt in ("subtract","-","difference"): ToDo = Math_op_dilouge["Sub"]
		elif mt in ("multiply","*","x","product","times"): ToDo = Math_op_dilouge["Mul"]
		elif mt in ("divide","/","are_there_in"): ToDo = Math_op_dilouge["Div"]
		elif mt in ("power","raises","^"): ToDo = Math_op_dilouge["Pow"]
		elif mt in ("square"): ToDo = Math_op_dilouge["Sqr"]
		elif mt in ("cube"): ToDo = Math_op_dilouge["Cub"]
		elif mt in ("square_root"): ToDo = Math_op_dilouge["Sqrt"]
		elif mt in ("cube_root"): ToDo = Math_op_dilouge["Cubrt"]
		else: return None
		solution = round(ToDo[0](nums),2)
		self.ltm.__tng3__["it"] = str(solution)
		return self.say(ToDo[1],solution,*nums)
	
	def Talks(self):
		if self.txt1 in ("how are you","how are you doing"): return self.say(["I'm fine","Thanks for asking, I'm great","I'm totally fine ,u_gnd","I'm great","Fine u_gnd"])
		
		
		
	def Info(self):
		if not any([y in self.txt1 for y in ("what","how")]): return None
		if any([y in self.txt1 for y in (" day","weekday")]):
			if any([y in self.txt1 for y in ("today","this","it")]): date = now
			elif "yesterday" in self.txt1: date = now-dt.timedelta(days=1)
			elif "tomorrow" in self.txt1: date = now+dt.timedelta(days=1)
			else: return None
			return self.say(["It's {}","This is {}","{}","I think {}","hmm , {}"],date.strftime("%A"))
		elif "date" in self.txt1:
			if any([y in self.txt1 for y in ("today","this","it")]): date = now
			elif "yesterday" in self.txt1: date = now-dt.timedelta(days=1)
			elif "tomorrow" in self.txt1: date = now+dt.timedelta(days=1)
			else: return None
			return self.say(["It's {}","This is {}","{}","I think {}"],date.strftime(r"%d/%m/%G"))
		elif "time" in self.txt1 and any([y in self.txt1 for y in ("now","this","it","")]):
			return self.say(["It's {}","{}","The time now is {}"],now_func().strftime("%I:%M %p"))
		elif "internet" in self.txt1 and any([y in self.txt1 for y in ("left","balance")]):
			if self.do:
				Net_balance = ctl.ussd("*111*2*1#")
				if Net_balance:
					if ":" in Net_balance:
						return self.say(["Your internet balance is {}","{} is left","It is {}"],Net_balance[Net_balance.index(":")+1:-1])
					else: return self.say(["0MB","I think there is nothing","It's 0MB, i think so"])
			return self.say(["Sorry, i can't get that","I don't know"])
		
	
	def Switch(self):
		if not ("<st>" in self.txt3 and "<sw>" in self.txt3): return None
		trn,st = self.sm["<sw>"],self.sm["<st>"]
		if self.do:
			if trn == "hotspot": sw = "htspt"
			elif trn == "wifi": sw = "wifi"
			elif trn in ("torch","flash"): sw = "fls"
			elif trn in ("net","internet"): sw = "net"
			elif trn == "bluetooth": sw = "bt"
			elif trn == "aeroplane_mode": sw = "arpln"
			ctl.turn(sw,st)
		self.ltm.__tng3__["it"] = trn
		return rd.choice(["Done Sir!","Your {} is {} now","Done!","Done Boss!"]).format(trn,st)
	
	def DoIt(self):
		if not self.txt3.startswith("<vrb1>"): return None
		vr = self.sm['<vrb1:0>']
		if vr in ("open","launch") and any([y in self.txt3 for y in ("<tng1>","<unk>")]):
		 	app = [self.sm[y] for y in ["<unk:0>","<tg1:0>"] if y in self.sm.keys()][0]
		 	todo = ctl.app_open,app
		 	ret = ["Done sir","Opening {}","It's here"],app
		elif vr == "search" and any([y in self.txt3 for y in ("<pr1>","<pl1>","<tng1>","<unk>")]):
			if "chrome" in self.txt1: on="chrome"
			else: on = "win"
			todo = ctl.search,self.txt1.replace("search for","").replace("search","").replace("in chrome","").strip(),on
			ret = ["Done sir","Yes boss"]
		elif vr in ("call","make") and any([y in self.txt3 for y in ("<pr1>","<unk>","<pr2>","<num>")]):
			pr = "".join([self.sm[y] for y in self.sm.keys() if (y in ["<unk:0>","<pr1:0>","<pr2:0>"] or y.startswith("<num:"))])
			todo = ctl.call,pr
			ret = ["calling {}","Done Boss"],pr
		elif vr == "dial" and any([y in self.txt3 for y in ("<pr1>","<num>")]):
			nm = self.sm["<num:0>"]
			todo = ctl.dial,nm
			ret = ["dialing {}","Done Sir"],nm
		else: return None
		if self.do: todo[0](*todo[1:])
		return self.say(*ret)
	
	def GetInfo(self):
		if "4>" not in self.txt3: return None
		ret = self.ltm.Get_it(self.txt3,self.sm)
		return self.say(["I don't know","Sorry, i don't know","Don't know u_gnd"]) if ret=="Unk" else ret 
		
	def SetInfo(self):
		ret = self.ltm.Set_it(self.txt3,self.sm)
		return self.say(["Ok u_gnd","Got it","Ok","I Got it"]) if ret=="Done" else None
	
	def FindCallProto(self,txts,sm): #Finds and executes the protocal if wanted
		self.txt1,self.txt2,self.txt3,self.sm = *txts,sm
		for Proto in self.ProtosIn:
			ret = Proto()
			if ret: return ret
		else: return None
		
# } Main class ends


if __name__ == "__main__":
	t.stop()
