from utils import timer
t = timer()
from functools import reduce
import re
import json as js
from Data_processer import *
import random as rd
from control import ctl

gnd_data = js.loads(open("/storage/emulated/0/Datasets/gnd.json","r").read())

def predict_gnd(name):
	try: gnd = gnd_data[name[-3:].lower()]
	except KeyError: return ("unk",0)
	if gnd[0] > gnd[1]: return "male",(gnd[0]/sum(gnd))
	else: return "female",(gnd[1]/sum(gnd))
	
pro = pr3.ptrn+pl3.ptrn+dt3.ptrn+tng3.ptrn
class memory:
	def __init__(self):
		self.pr2 = {}
		self.pl2 = {}
		self.dt2 = {}
		self.tng2 = {}
		self.pr3 = {}
		self.pl3 = {}
		self.dt3 = {}
		self.tng3 = {}
		self.tg_ls = ["<pr2>","<pr3>","<pl2>","<pl3>","<dt2>","<dt3>","<tng2>","<tng3>"]
	
	@property
	def mem_ls(self): #returns all memorys as list
		return [self.pr2,self.pr3,self.pl2,self.pl3,self.dt2,self.dt3,self.tng2,self.tng3]
	
	@property
	def allmem(self): #returns all memory combined together
		mem = {}
		for y in self.mem_ls: mem.update(y)
		return mem
		
	def merge(self,ls,sym="&",sort=True): #merges the the words of the tag
		if sort: ls = sorted(ls)
		try: return reduce(lambda a,b: a+sym+b,ls)
		except: return ""
		
	def print(self): #prints the value of curen memorys
		for x,y in zip(self.tg_ls,self.mem_ls): print(f"{x[1:-1]} : {y}")
	
	def merge2(self,ls,rt="ky"):
		rep,ret = [],[]
		for wrd in ls:
			if wrd in pro:
				try: wrd2 = self.allmem[wrd]
				except: wrd2 = wrd
				rep.append(wrd2)
			else:
				rep.append(wrd)
		if len(rep) > 1:
			try:
				nw = self.allmem[self.merge(rep[:2])]
				rep = rep[2:]
				if len(rep):
					for y in rep.copy():
						try:
							nw = self.allmem[self.merge([nw,y])]
							rep.remove(y)
						except KeyError:
							rep.insert(0,nw)
							break
					else: rep.insert(0,nw)
				else: rep.insert(0,nw)
			except KeyError: pass
		ret = ret+rep
		if rt=="vl": return self.merge(ret," ",False)
		else: return self.merge(ret)
		
	def set_pr3(self,vr,it):
		for ky,vl in {"you":"you&your","i":"my&i","female":"she&her&hers","male":"he&his&him","unk":"she&her&hers&he&his&him"}.items():
			if vr == ky:
				for x in vl.split("&"): self.pr3[x] = it
				break
		else: pass
		self.tng2[self.merge([it,"name"])] = it
	
	def set_pr2(self,vr,it):
		mr = self.merge2(it,"vl")
		try: it = self.pr2[mr]
		except KeyError: it = mr
		if len(vr) == 1 and vr[0] in ["i","you","she","he"]: self.set_pr3(vr[0],it)
		else:
			self.pr2[self.merge2(vr)] = it
			self.set_pr3(predict_gnd(it)[0],it)
			self.tng2[self.merge([it,"name"])] = it
		self.tng3["it"] = it
		
	def set_pl2(self,vr,it,pl=""):
		mr = self.merge2(it,"vl")
		try: it = self.pl2[mr]
		except KeyError: it = mr
		if pl3: self.pl3[pl] = it
		self.pl2[self.merge2(vr,"vl")] = it
		self.tng3["it"] = it
	
	def set_tng2(self,vr,it):
		mr = self.merge2(it,"vl")
		try: it = self.tng2[mr]
		except KeyError: it = mr
		self.tng2[self.merge2(vr)] = it
		self.tng3["it"] = it
	
	def get_pr(self,vr):
		mr = self.merge2(vr)
		if "&" in mr: ret = self.pr2[mr]
		else: ret = mr
		self.tng3["it"] = ret
		return ret
			
	def get_pl(self,vr):
		if len(vr) == 1 and vr[0] in ["i","you","she","he"]:
			ret = self.pl2[self.merge2(vr)]
		else: ret = self.pl2[self.merge2(vr)]
		self.tng3["it"] = ret
		return "in "+ret
		
	def get_dt(self,vr): pass
	
	def get_tng(self,vr):
		mr = self.merge2(vr)
		try: ret = self.tng2[mr]
		except: ret = mr
		self.tng3["it"] = ret
		return ret


#some wanted defs
def get_kv(txt,wrd,sm,sort=True):
	txt_ls = txt.split(" ")
	pre_idx = txt_ls.index(wrd)
	ky_tx,vl_tx = [],[]
	for tx in txt_ls:
		try:
			if txt_ls.index(tx) <= pre_idx: ky_tx.append(sm[tx])
			else: vl_tx.append(sm[tx])
		except: pass
	if len(ky_tx) < len(vl_tx): ky_tx,vl_tx = vl_tx,ky_tx
	if sort: ky_tx,vl_tx = sorted(ky_tx),sorted(vl_tx)
	return ky_tx,vl_tx
		
#The bot class
class Bot:
	def __init__(self,name="alpha",user="rahim",do=False):
		self.ltm = memory()
		self.ltm.set_pr3("you",name)
		self.ltm.set_pr3("i",user)
		self.pre = processer()
		self.isctl = ctl.chk
		if do: self.do = self.isctl
		else: self.do = False
	
	@property
	def u_gnd(self):
		gnd = predict_gnd(self.ltm.pr3["i"])[0]
		if gnd == "male": return ["male","sir"]
		elif gnd == "female": return ["female","mam"]
		else: return ["unk",""]
		
	def predict(self,txt):
		if type(txt) == str:
			if " it" in txt: txt = re.sub(rf"\bit\b",self.ltm.tng3["it"],txt.lower())
			txt2,sm = self.pre.snt_enc(txt)
			txt3,pre = txt2,["unk","unk"]
			for y in range(3): txt3 = txt3.replace(f":{y}","")
			if "<mt>" in txt3 and "<num>" in txt3:
				pre[0] = "Mt"
				mt = sm["<mt>"]
				if mt in ("add","+","sum") and "<num:1>" in txt2: pre[1] = "add"
				elif mt in ("subtract","-","difference") and "<num:1>" in txt2:
					if "subtract" in txt or "from" in txt: pre[1] = "!sub"
					else: pre[1] = "sub"
				elif mt in ("multiply","*","x","product","times") and "<num:1>" in txt2: pre[1] = "mul"
				elif mt in ("divide","/","are_there_in") and "<num:1>" in txt2:
					if "are there in" in txt or "from" in txt: pre[1] = "!div"
					else: pre[1] = "div"
				elif mt in ("power","raises","^") and "<num:1>" in txt2: pre[1] = "pow"
				elif mt in ("square"): pre[1] = "sqr"
				elif mt in ("cube"): pre[1] = "cub"
				elif mt in ("square_root"): pre[1] = "sqrt"
				elif mt in ("cube_root"): pre[1] = "cubrt"
			elif "<st>" in txt3 and "<sw>" in txt3: pre = ["Do","trn"]
			elif txt3.startswith("<vrb1>"):
				pre[0] = "Do"
				vr = sm['<vrb1:0>']
				if vr in ("open","launch") and any([y in txt3 for y in ("<tng1>","<unk>")]): pre[1] = "opn"
				elif vr in ("say","meet") and any([y in txt3 for y in ("<pr1>","<unk>")]): pre[1] = "say"
				elif vr == "search" and any([y in txt3 for y in ("<pr1>","<pl1>","<tng1>","<unk>")]): pre[1] = "src"
				elif vr in ("call","make") and any([y in txt3 for y in ("<pr1>","<unk>","<pr2>","<num>")]): pre[1] = "call"
				elif vr == "dial" and any([y in txt3 for y in ("<pr1>","<num>")]): pre[1] = "dial"
			elif txt.startswith("wh"):
				pre[0] = "G"
				if any(map(txt.startswith,["who","whom"])): pre[1] = "pr"
				elif txt.startswith("where"): pre[1] = "pl"
				elif txt.startswith("what"):
					if "<dt2>" in txt3: pre[1] = "dt"
					else: pre[1] = "tg"
			else:
				pre[0] = "S"
				if "<pre>" in txt3 and ("<pl1>" in txt3 or "<pl2>" in txt3 or "<unk>" in txt3): pre[1] = "pl"
				elif "<vrb>" in txt3 and "<vrb3>" not in txt3: pre[1] = "vrb"
				elif "<vrb3>" in txt3:
					if "<tng2>" in txt3: pre[1] = "tg"
					else: pre[1] = "pr"
			return pre,sm,[txt,txt2,txt3]
		else: return [self.predict(x) for x in txt]
			
	
	def protocals(self,pre,sm,txts=None):
		main,sub = pre
		if txts: txt,txt1,txt2 = [y.lower() for y in txts]
		do = self.do
		#Maths
		if main == "Mt":
			nums = [int(vl) for vl in sm.values() if vl.isdigit()]
			if "!" in sub:
				nums.reverse()
				sub = sub.replace("!","")
			if sub == "add":
				solution = reduce(lambda a,b:a+b,nums)
				ret = rd.choice(["Your sum is {}","It is {}","Gotcha , {}","Got it,{}","I think {}","The sum is {}"]).format(solution)
			elif sub == "sub":
				diff = reduce(lambda a,b:a-b,nums)
				ret = rd.choice(["{} is the difference","It is {}","Gotcha , {}","Got it,{}","I think {}","The difference is {}"]).format(diff)
			elif sub == "mul":
				solution = reduce(lambda a,b:a*b,nums)
				ret = rd.choice(["{} is the product","It is {}","Gotcha , {}","Got it,{}","I think {}","The Product is {}"]).format(solution)
			elif sub == "div":
				solution = int(reduce(lambda a,b:a/b,nums))
				ret = rd.choice(["There are {quo} {b}s in {a}","It is {quo}","Gotcha , {quo}","Got it,{quo}","I think it is {quo}"]).format_map({"a":nums[0],"b":nums[1],"quo":solution})
			elif sub == "pow":
				solution = nums[0]**nums[1]
				ret = rd.choice(["{1} to the power of {2} is {0}","It is {}","{}","Got it,{}","I think {}","{1}^{2} is {0}"]).format(solution,nums[0],nums[1])
			elif sub == "sqr":
				solution = nums[0]**2
				ret = rd.choice(["{} is the square of {}","It is {}","Square of {1} is {0}","Got it,{}","I think it's {}","{}"]).format(solution,nums[0])
			elif sub == "cub":
				solution = nums[0]**3
				ret = rd.choice(["{} is the cube of {}","It is {}","Cube of {1} is {0}","Got it,{}","I think it's {}","{}"]).format(solution,nums[0])
			elif sub == "sqrt":
				solution = nums[0]**(1/2)
				ret = rd.choice(["{} is the square root of {}","It's {}","Square root of {1} is {0}","Got it,{}","I think it's {}","{}"]).format(solution,nums[0])
			elif sub == "cubrt":
				solution = nums[0]**(1/3)
				ret = rd.choice(["{} is the cube root of {}","It's {}","Cube root of {1} is {0}","Got it,{}","I think it's {}","{}"]).format(solution,nums[0])
			else:
				solution = None
				ret = rd.choice(["Sorry , i did'nt got that","Sorry, I couldn't able to recognize that","I think i got that wrong"])
			if solution != None: self.ltm.set_tng2(["answer"],[str(solution)])
			return ret
		#That Oning
		elif main=="Do":
			if sub=="trn":
				trn,st = sm["<sw>"],sm["<st>"]
				if do:
					if trn == "hotspot": sw = "htspt"
					elif trn == "wifi": sw = "wifi"
					elif trn in ("torch","flash"): sw = "fls"
					elif trn in ("net","internet"): sw = "net"
					elif trn == "bluetooth": sw = "bt"
					elif trn == "aeroplane_mode": sw = "arpln"
					ctl.turn(sw,st)
					self.ltm.tng3["it"] = trn
				return rd.choice(["Done sir","Your {} is {} now","Done boss"]).format(trn,st)
			elif sub == "opn":
				app = [sm[y] for y in ["<unk:0>","<tg:0>"] if y in sm.keys()][0]
				if do: ctl.app_open(app)
				return rd.choice(["Done sir","Opening {}","It's here"]).format(app)
			elif sub == "say":
				try: pr = sm["<pr1:0>"]
				except KeyError: pr = sm["<unk:0>"]
				return rd.choice(["Hello {}","Nice to meet you {}"]).format(pr)
			elif sub == "src":
				if do:
					if "chrome" in txt: on="chrome"
					else: on = "win"
					ctl.search(txt=txt.replace("search for","").replace("search","").replace("in chrome","").strip(),on=on)
				return rd.choice(["Done sir","Yes boss"])
			elif sub == "call":
				pr = "".join([sm[y] for y in sm.keys() if (y in ["<unk:0>","<pr1:0>","<pr2:0>"] or y.startswith("<num:"))])
				if do: ctl.call(pr)
				return rd.choice(["calling {}","Done Boss"]).format(pr)
			elif sub == "dial":
				nm = sm["<num:0>"]
				if do: ctl.dial(nm)
				return rd.choice(["dialing {}","Done Sir"]).format(nm)
		elif main == "G":
			ky = ""
			it = [vl for ky,vl in sm.items() if vl not in ("who","whom","where","what","which")]
			try:
				if sub == "pr": return self.ltm.get_pr(it)
				elif sub == "pl": return self.ltm.get_pl(it)
				elif sub == "tg": return self.ltm.get_tng(it)
				elif sub == "dt": pass
				else: return rd.choice(["Sorry boss i can't able to understand that"])
			except KeyError: return rd.choice(["Don't know","I don't know sir"])
		elif main == "S":
			if sub == "pl":
				ky,vl = get_kv(txt1,"<pre>",sm)
				self.ltm.set_pl2(ky,vl)
			elif sub == "vrb":
				ky,vl = get_kv(txt1,"<vrb:0>",sm)
				#self.ltm[self.pre.wrd_enc(vl.replace("&",""))[0][1:3]][ky] = vl
			elif sub == "pr":
				ky,vl = get_kv(txt1,"<vrb3>",sm)
				self.ltm.set_pr2(ky,vl)
			elif sub == "tg":
				ky,vl = get_kv(txt1,"<vrb3>",sm)
				self.ltm.set_tng2(ky,vl)
			return f"Ok {self.u_gnd[1]}"
		return rd.choice(["Sorry boss i can't able to understand that","I didn't got that","Can you repet"])
		
	def assist(self,listen=False,spk=False):
		while True:
			if listen and self.isctl:
				inp,_ = ctl.spc_rec2(th=0.80);
				if inp: print("\nYou : "+inp)
				else: continue
			else: inp = input("\nYou : ")
			if inp in ("end","quit"): break
			elif inp == "ltm": self.ltm.print()
			t.start()
			pre,sm,txts = self.predict(inp)
			#print(pre,sm,txts)
			out = self.protocals(pre,sm,txts)
			t.stop()
			print("Bot : "+out)
			if spk and self.isctl: ctl.spk(out)
		
			
				
if __name__ == "__main__":
	bot = Bot("alpha",do=True)
	bot.ltm.set_pr2(["your","boss"],["rahim"])
	bot.assist(1,1)
	t.stop()