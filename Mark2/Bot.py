import datetime as dt
from functools import reduce
import re
from utils import timer
t = timer()
import json as js
from Data_processer import processer
import random as rd
from control import ctl


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
		self.tgmem_dic = {"<pr2>":self.pr2,"<pr3>":self.pr3,"<pl2>":self.pl2,"<pl3>":self.pl3,"<dt2>":self.dt2,"<dt3>":self.dt3,"<tng2>":self.tng2,"<tng3>":self.tng3}
	
	@property
	def memorys(self): return [self.pr2,self.pr3,self.pl2,self.pl3,self.dt2,self.dt3,self.tng2,self.tng3]
	def  __combiner(self,ls,sym="&",srt=True):
		if srt: ls = sorted(ls)
		try: return reduce(lambda a,b: a+sym+b,ls)
		except TypeError: return ls[0]
		except: return ""
	def print(self):
		for x,y in zip(self.tgmem_dic.keys(),self.memorys): print(f"{x[1:-1]} : {y}")
	
	def replacer(self,ls,rt="sym"):
		rep,rep_tg,ret,num,mx = [],[],[],0,0
		for wrd,tg in ls:
			if rt=="sym" and tg=="<pre>": continue
			print(tg,wrd,rt)
			if tg[-2] == "3":
				try:
					wrd2 = self.tgmem_dic[tg][wrd]
				except: wrd2 = wrd
				rep.append(wrd2)
				rep_tg.append(tg)
				mx = num
			elif tg[-2] == "1" or tg[-2] == "2":
				rep.append(wrd)
				rep_tg.append(tg)
				mx = num
			else: ret.append(wrd)
			num += 1
		ret = self.replacer2(rep,rep_tg) +ret
		if rt=="sym": return self.__combiner(ret)
		elif rt == "txt": return self.__combiner(ret," ",False)
	
	def get_tg(self,ls):
		if "<tng2>" in ls: return self.tng2
		else: return self.pr2
	
	def replacer2(self,rep,tg):
		try:
			nw,rep2 = self.get_tg(tg[:2])[self.__combiner((rep[0],rep[1]))],rep.copy()
		except IndexError: return rep
		except KeyError: return rep
		rep2.pop(0)
		tg.pop(0)
		rep2.pop(0)
		tg.pop(0)
		for y in range(len(rep)):
			try:
				nw = self.get_tg(tg[:2])[self.__combiner((rep[y+2],nw))]
				rep2.pop(y)
			except:
				rep2.insert(0,nw)
				break
		else: rep2.insert(0,nw)
		return rep2
				
				
	def set_pr3(self,vr,it):
		if vr == "you":
			self.pr3["you"] = it
			self.pr3["your"] = it
		elif vr == "i":
			self.pr3["i"] = it
			self.pr3["my"] = it
		elif vr == "he":
			self.pr3["he"] = it
			self.pr3["his"] = it
		elif vr == "she":
			self.pr3["she"] = it
			self.pr3["hers"] = it
		elif vr == "both":
			self.pr3["he"] = it
			self.pr3["his"] = it
			self.pr3["she"] = it
			self.pr3["hers"] = it
		else: pass
		self.tng2[self.__combiner([it,"name"])] = it
				
	def set_pr2(self,vr,it,pr3=""):
		it = self.replacer(it,"txt")
		self.tng3["it"] = it
		self.replacer(vr)
		self.pr2[self.replacer(vr)] = it
		if pr3: self.set_pr3(pr3,it)
		else: self.tng2[self.__combiner([it,"name"])] = it
	
	def set_pl2(self,vr,it,pl3="",pre="in "):
		it = self.replacer(it,"txt")
		self.tng3["it"] = it
		if pl3: self.pl3[pl3] = it
		self.pl2[self.replacer(vr)] = pre+it
	
	def set_dt2(self,vr,it):
		if type(it) == str: it = self.replacer(it,"txt")
		else: it = it
		self.tng3["it"] = it
		self.dt2[self.replacer(vr)] = it
			
	def set_tng2(self,vr,it):
		it = self.replacer(it,"txt")
		self.tng3["it"] = it
		self.tng2[self.replacer(vr)] = it
		
	def get_pr(self,vr):
		return self.replacer(vr,"txt")
	
	def get_pl(self,vr):
		return self.replacer(vr,"txt")
	
	def get_dt(self,vr): pass
	
	def get_tng(self,vr):
		return self.replacer(vr,"txt")
	
def get_kv(txt,wrd,sm):
	txt_ls = txt.split(" ")
	pre_idx = txt_ls.index(wrd)
	ky_tx,vl_tx = [],[]
	for tx in txt_ls:
		try:
			if tx[-3] == ":": tx1 = tx.replace(tx[-3:],">")
			else: tx1 = tx
			if txt_ls.index(tx) <= pre_idx: ky_tx.append([sm[tx],tx1])
			else: vl_tx.append([sm[tx],tx1])
		except: pass
	if len(ky_tx) < len(vl_tx): ky_tx,vl_tx = vl_tx,ky_tx
	return [ky_tx,vl_tx]
	
class Bot:
	def __init__(self,name="alpha",user="rahim",do=False):
		self.ltm = memory()
		self.ltm.set_pr3("you",name)
		self.ltm.set_pr3("i",user)
		self.pre = processer()
		if do: self.do = ctl.chk
		else: self.do = False
			
	def predict(self,txt):
		if type(txt) == str:
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
			elif "<st>" in txt3 and "<trn>" in txt3: pre = ["Do","trn"]
			elif txt3.startswith("<vrb>"):
				pre[0] = "Do"
				vr = sm['<vrb:0>']
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
				if "<pre>" in txt3 and ("<pl1>" in txt3 or "<pl2>" in txt3): pre[1] = "pl"
				elif "<vrb>" in txt3 and "<vrb3>" not in txt3: pre[1] = "vrb"
				elif "<vrb3>" in txt3:
					if "<tng2>" in txt3: pre[1] = "tg"
					else: pre[1] = "pr"
			return pre,sm,[txt,txt2,txt3]
		else: return [self.predict(x) for x in txt]
			
	
	def protocals(self,pre,sm,txts=None):
		main,sub = pre
		if txts: txt,txt1,txt2 = txts
		print(sm)
		do = self.do
		#Maths
		if main == "Mt":
			nums = [int(vl) for vl in sm.values() if vl.isdigit()]
			if "!" in sub:
				nums.reverse()
				sub = sub.replace("!","")
			if sub == "add":
				sum = reduce(lambda a,b:a+b,nums)
				return rd.choice(["Your sum is {}","It is {}","Gotcha , {}","Got it,{}","I think {}","The sum is {}"]).format(sum)
			elif sub == "sub":
				diff = reduce(lambda a,b:a-b,nums)
				return rd.choice(["{} is the difference","It is {}","Gotcha , {}","Got it,{}","I think {}","The difference is {}"]).format(diff)
			elif sub == "mul":
				pro = reduce(lambda a,b:a*b,nums)
				return rd.choice(["{} is the product","It is {}","Gotcha , {}","Got it,{}","I think {}","The Product is {}"]).format(pro)
			elif sub == "div":
				quo = int(reduce(lambda a,b:a/b,nums))
				return rd.choice(["There are {quo} {b}s in {a}","It is {quo}","Gotcha , {quo}","Got it,{quo}","I think it is {quo}"]).format_map({"a":nums[0],"b":nums[1],"quo":quo})
			elif sub == "pow":
				pow = nums[0]**nums[1]
				return rd.choice(["{1} to the power of {2} is {0}","It is {}","{}","Got it,{}","I think {}","{1}^{2} is {}"]).format(pow,nums[0],nums[1])
			elif sub == "sqr":
				sqr = nums[0]**2
				return rd.choice(["{} is the square of {}","It is {}","Square of {1} is {0}","Got it,{}","I think it's {}","{}"]).format(sqr,nums[0])
			elif sub == "cub":
				cub = nums[0]**3
				return rd.choice(["{} is the cube of {}","It is {}","Cube of {1} is {0}","Got it,{}","I think it's {}","{}"]).format(cub,nums[0])
			elif sub == "sqrt":
				sqrt = nums[0]**(1/2)
				return rd.choice(["{} is the square root of {}","It's {}","Square root of {1} is {0}","Got it,{}","I think it's {}","{}"]).format(sqrt,nums[0])
			elif sub == "cubrt":
				cubrt = nums[0]**(1/3)
				return rd.choice(["{} is the cube root of {}","It's {}","Cube root of {1} is {0}","Got it,{}","I think it's {}","{}"]).format(cubrt,nums[0])
			else: return rd.choice(["Sorry , i did'nt got that","Sorry, I couldn't able to recognize that","I think i got that wrong"])
		#That Oning
		elif main=="Do":
			if sub=="trn":
				trn,st = sm["<trn>"],sm["<st>"]
				if do:
					if trn == "hotspot": sw = "htspt"
					elif trn == "wifi": sw = "wifi"
					elif trn in ("torch","flash"): sw = "fls"
					elif trn in ("net","internet"): sw = "net"
					elif trn == "bluetooth": sw = "bt"
					elif trn == "aeroplane_mode": sw = "arpln"
					ctl.turn(sw,st)
				return rd.choice(["Done sir","Your {} is {} now","Done boss"]).format(trn,st)
			elif sub == "opn":
				app = [sm[y] for y in ["<unk:0>","<tg:0>"] if y in sm.keys()][0]
				if do: ctl.app_open(app)
				return rd.choice(["Done sir","Opening {}","It's here"]).format(app)
			elif sub == "say":
				pr = [sm[y] for y in ["<unk:0>","<pr:0>"] if y in sm.keys()][0]
				return rd.choice(["Hello {}","Nice to meet you {}"]).format(pr)
			elif sub == "src":
				if do:
					if "chrome" in txt: on="chrome"
					else: on = "win"
					ctl.search(txt=txt.replace("search for","").replace("search","").replace("in chrome","").strip(),on=on)
				return rd.choice(["Done sir","Yes boss"])
			elif sub == "call":
				pr = [sm[y] for y in ["<unk:0>","<pr:0>","<pr2:0>","<nm:0>"] if y in sm.keys()][0]
				if do: ctl.call(pr)
				return rd.choice(["calling {}","Done Boss"]).format(pr)
			elif sub == "dial":
				nm = sm["<nm:0>"]
				if do: ctl.dial(nm)
				return rd.choice(["dialing {}","Done Sir"]).format(nm)
		elif main == "G":
			ky = ""
			it = [[vl,ky.replace(ky[-3:],">")] for ky,vl in sm.items() if vl not in ("who","whom","where","what","which")]
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
				if len(ky) == 1 and "<pr2>" not in txt2: self.ltm.set_pr3(ky[0][0],vl[0][0])
				else: self.ltm.set_pr2(ky,vl,"both")
			elif sub == "tg":
				ky,vl = get_kv(txt1,"<vrb3>",sm)
				self.ltm.set_tng2(ky,vl)
			return "Ok sir"
		else: return ""
		
	def assist(self,listen=False,spk=False):
		while True:
			if listen:
				inp,_ = ctl.spc_rec2(th=0.80)
				if inp: print("\nYou : "+inp)
				else: continue
			else: inp = input("\nYou : ")
			if inp in ("end","quit"): break
			elif inp == "ltm": self.ltm.print()
			pre,sm,txts = self.predict(inp)
			out = self.protocals(pre,sm,txts)
			print("Bot : "+out)
			if spk: ctl.spk(out)

		
		
	
	
if __name__ == "__main__":
	bt = Bot()
	bt.assist(True,True)
	t.stop()