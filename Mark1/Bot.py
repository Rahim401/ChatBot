import json
from functools import reduce
from utils import timer as tm
t = tm()
import Data_processer as dp
import random as rd
from control import ctl


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
	add = lambda a,b: a+"&"+b
	return (reduce(add,ky_tx),reduce(add,vl_tx))

def expand(txt,dic):
	txt = txt.lower().split(" ")
	txt2 = ""
	for y in txt:
		for ky,vl in dic.items():
			if y == ky:
				y=vl
				break
		txt2 = txt2 + " " + y
	return txt2.strip()

class Bot:
	def __init__(self,name,do=False):
		self.ltm = {"pr":{"you":name,name:"you"},"pl":{},"tg":{"name&your":name}}
		if do: self.do = ctl.chk
		else: self.do = False
		self.pre = dp.preprocesser()
		
	def predict(self,txt):
		typ = type(txt)
		if typ == str:
			txt2,sm = self.pre.do(txt)
			txt3 = txt2.replace(":0","").replace(":1","").replace(":2","")
			pre = ""
			if "<mt>" in txt3 and "<nm>" in txt3:
				pre = "Mt-unk"
				mt = sm["<mt>"]
				if mt in ("add","+","sum") and "<nm:1>" in txt2:
					pre = "Mt-add"
				elif mt in ("subtract","-","difference") and "<nm:1>" in txt2:
					if "subtract" in txt or "from" in txt: pre = "Mt-!sub"
					else: pre = "Mt-sub"
				elif mt in ("multiply","*","x","product","times") and "<nm:1>" in txt2: pre = "Mt-mul"
				elif mt in ("divide","/","ati") and "<nm:1>" in txt2:
					if "are there in" in txt or "from" in txt: pre = "Mt-!div"
					else: pre = "Mt-div"
				elif mt in ("power","raises","^") and "<nm:1>" in txt2: pre = "Mt-pow"
				elif mt in ("square"): pre = "Mt-sqr"
				elif mt in ("cube"): pre = "Mt-cub"
				elif mt in ("squrt"): pre = "Mt-sqrt"
				elif mt in ("cubrt"): pre = "Mt-cubrt"
			elif "<st>" in txt3 and "<trn>" in txt3: pre = "Do-trn"
			elif txt3.startswith("<vrb>"):
				pre = "Do-unk"
				vr = sm['<vrb:0>']
				if vr in ("open","launch") and any([y in txt3 for y in ("<tg>","<unk>")]): pre = "Do-opn"
				elif vr in ("say","meet") and any([y in txt3 for y in ("<pr>","<unk>")]): pre = "Do-say"
				elif vr == "search" and any([y in txt3 for y in ("<pr>","<pl>","<tg>","<unk>")]): pre = "Do-src"
				elif vr in ("call","make") and any([y in txt3 for y in ("<pr>","<unk>","<pr2>","<nm>")]): pre = "Do-call"
				elif vr == "dial" and any([y in txt3 for y in ("<pr>","<nm>")]): pre = "Do-dial"
			elif txt.startswith("wh"):
				pre = "G-unk"
				if any(map(txt.startswith,["who","whom"])): pre = "G-pr"
				elif txt.startswith("where"): pre = "G-pl"
				elif txt.startswith("what"):
					if "<dt2>" in txt3: pre = "G-dt"
					else: pre = "G-tg"
			else:
				pre = "S-unk"
				if "<pre>" in txt3 and ("<pl>" in txt3 or "<pl2>" in txt3): pre = "S-pl"
				elif "<vrb>" in txt3 and "<vrb2>" not in txt3: pre = "S-vrb"
				elif "<vrb2>" in txt3:
					if "<tg2>" in txt3: pre = "S-tg"
					else: pre = "S-pr"
			return pre,sm,[txt,txt2,txt3]
		else: return [self.predict(x) for x in txt]
		
	def protocals(self,pre,sm,txts=None):
		main,sub = pre.split("-")
		if txts: txt,txt1,txt2 = txts
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
					elif trn == "arpln": sw = "arpln"
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
			for y in sorted(sm.values()):
				if y not in ("who","whom","where","what","which"): ky= ky+"&"+y
			try:
				rm = {"i":"you","you":"me","my":"your","your":"my"}
				if sub == "pr": return expand(self.ltm["pr"][ky[1:]],rm).capitalize()
				elif sub == "pl": return expand(self.ltm["pl"][ky[1:]],rm).capitalize()
				elif sub == "tg": return expand(self.ltm["tg"][ky[1:]],rm).capitalize()
				elif sub == "dt": pass
				else: return rd.choice(["Sorry boss i can't able to understand that"])
			except KeyError: return rd.choice(["Don't know","I don't know sir"])
		elif main == "S":
			if sub == "pl":
				ky,vl = get_kv(txt1,"<pre>",sm)
				self.ltm["pl"][ky] = vl
				try: sm.pop("<vrb:0>")
				except: pass
				try: sm.pop("<tg:0>")
				except: pass
				ky,vl = get_kv(txt1,"<pre>",sm)
				self.ltm["pl"][ky] = vl
			elif sub == "vrb":
				ky,vl = get_kv(txt1,"<vrb:0>",sm)
				self.ltm[self.pre.wrd_enc(vl.replace("&",""))[0][1:3]][ky] = vl
			elif sub == "pr":
				ky,vl = get_kv(txt1,"<vrb2>",sm)
				self.ltm["pr"][ky] = vl
				ky,vl = get_kv(txt1,"<vrb2>",sm,False)
				self.ltm["pr"][vl] = ky.replace("&"," ")
			elif sub == "tg":
				ky,vl = get_kv(txt1,"<vrb2>",sm)
				self.ltm["tg"][ky] = vl
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
			elif inp == "ltm": print(self.ltm)
			t.start()
			pre,sm,txts = self.predict(inp)
			out = self.protocals(pre,sm,txts)
			t.stop()
			print("Bot : "+out)
			if spk: ctl.spk(out)
			


bt = Bot("alpha",True)
bt.assist(True,True)