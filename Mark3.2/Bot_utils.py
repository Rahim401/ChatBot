#pylint:disable=W0120
#pylint:disable=W0102
import re
from utils import timer
t = timer()
from functools import reduce
from word2number import w2n
import datetime as dt
import json as js

vrbs = js.loads(open("vrbs.json","r").read())
gnd_data = js.loads(open("gnd.json","r").read())
now = dt.datetime.now()
wtgs = []

# Wanted Defs {
def predict_gnd(name): # Used to predict the Gender By Name
	try: gnd = gnd_data[name[-3:].lower()]
	except KeyError: return ("unk",0)
	if gnd[0] > gnd[1]: return "male",(gnd[0]/sum(gnd))
	else: return "female",(gnd[1]/sum(gnd))

def Tg2Tg(tg):
	if ":" not in tg: return tg
	else: return tg.replace(tg[-3:-1],"")
# } Wanted Defs


# Wanted Class {
class wtags:
	# Word tag : used to identify the differebt types of word and Gorup them into Tags
	def __init__(self,ptrn,tg="",ret_wrd=True,has_id=True,apnd=False):
		self.ret_wrd = ret_wrd
		self.has_id = has_id
		self.tg1 = tg
		self.tg2 = tg.replace(">",":0>") if has_id else tg
		self.rep_ = {}
		self.apnd = [self.tg1] if apnd==True else [] if apnd==False else apnd
		self.ptrn = self.isvrb if ptrn=="Verb" else ptrn
		self.ptyp = type(self.ptrn)
		if self.ptyp == list:
			for wnum,wrd in enumerate(ptrn):
				if " " in wrd:
					wrd = wrd.lower()
					wrd_ = wrd.replace(" ","_")
					self.rep_[wrd] = wrd_
					ptrn[wnum] = wrd_
			self.ptrn = ptrn
		elif self.ptyp == str: self.ptrn = ("^"+ptrn+"$").lower()
		wtgs.append(self)
	
	def __str__(self): return self.tg1
	
	def __repr__(self): return self.tg1
	
	def iswtag(self,wrd):
		tg = ""
		if self.ptyp == list:
			if wrd in self.ptrn: tg = self.tg2
		elif self.ptyp == str:
			if re.findall(self.ptrn,wrd): tg = self.tg2
		elif self.ptyp == type(lambda a:a):
			tg,wrd = self.ptrn(self,wrd)
		return tg,wrd
	
	def fl_sm(self,wrd,sm={}):
		tg,wrd = self.iswtag(wrd)
		if tg:
			if self.has_id:
				num = 0
				while tg.replace("-c","") in [y.replace("-c","") for y in sm.keys()]:
					renum = num+1
					tg = re.sub(f":{num}>",f":{renum}>",tg)
					num = num+1
			if self.ret_wrd: sm[tg] = wrd
		return tg,wrd,sm
		
	@staticmethod
	def isvrb(slf,wrd): # Used to identify the Verbs using  a large dictionary(Json)
		for y in vrbs:
			if wrd in y:
				wrd = y[0]
				tg = slf.tg2
				break
		else: tg = ""
		return tg,wrd
		

# Word Tags Group or Dictionary {
pr1 = wtags(["haja","kamaldeen","kamaliya","ansariya","rahim","rafeel","santhosh","vishal","naveen","rahul","nithish","nithin","stephen","tony","stark","robert","chris","peter","vijay","kumar","jai","subramani","priya","divya","sakthi","thilak","yogeash","suriya","jayam","ravi","bala","parvis"],"<pr1>",True,True,True)
pr2 = wtags(["mother","father","friend","brother","sister","wife","husband","founder","owner","son","daughter","grandma","grandfather","student","friend","creator","boss","assistant","teacher","baby","child","boy","girl","male","female"],"<pr2>",True,True,["<pr2>","<pr1>","<pr3>","<adj>"])
pr3 = wtags(["i","you","she","he","we","our","they","us"],"<pr3>",True,True,False)
pr4 = wtags(["who","whom"],"<pr4>",False,False,False)

pl1 = wtags(["bangalore","india","tamil nadu","karnataka","udangudi","thoothkudi","thirunelvelai","chennai","madras","mallaswaram","soldevanahalli","mejastic"],"<pl1>",True,True,False)
pl2 = wtags(["school","collage","home","factory","company","office","bustop","bustand","institute","state","district","country","place","city","village"],"<pl2>",True,True,["<pl2>","<pr1>","<pr2>","<pr3>","<adj>"])
pl3 = wtags(["here","there"],"<pl3>",True,True,False)
pl4 = wtags(["where"],"<pl4>",False,False,False)

tng2 = wtags(["book","mobile","watch","tv","computer","laptop","mouse","bulb","planet","number","phone","fan","charger","game","age","gender","height","weight","ram","name","dob","capital","date of birth","place","date","time","color","human","bot"],"<tng2>",True,True,["<pl1>","<pl2>","<pl3>","<pr1>","<pr2>","<pr3>","<adj>"])
tng3 = wtags(["it"],"<tng3>",True,True,False)
tng4 = wtags(["which","what","how many"],"<tng4>",False,False,False)

vrb3 = wtags(["is","are","was","were","am","will","did","do","be","been","have","had"],"<vrb3>",False,False,True)
art = wtags(["the","an","a"],"<art>",False,False,False)
num = wtags(r"\d+","<num>",True,True,False)
numc = wtags(list(w2n.american_number_system.keys()),"<num-c>",True,True,True)
cnj = wtags(["and","but","therefore","so"],"<cnj>",False,False,False)
adj = wtags(["favorite","favourite","good","bad","random","beautiful","lucky"],"<adj>",True,True,["<pl1>","<pl2>","<pl3>","<pr1>","<pr2>","<pr3>","<tng2>","<tng3>"])
lv = wtags(r"\d+(st|nd|rd|th)","<lv>",True,True,False)
st = wtags(["on","off"],"<st>",True,False,False)
sw = wtags(["flash","torch","internet","bluetooth","wifi","hotspot","net","gps","aeroplane mode"],"<sw>",True,False,False)
mt = wtags(["+","-","*","x","/","^","add","subtract","multiply","divide","square","cube","sum","square root","cube root","difference","product","times","are there in","power","raises","^"],"<mt>",True,False,False)
pre = wtags(["in","on","under","inside","outside","above","across","to","from"],"<pre>",False,False,False)
vrb1 = wtags("Verb","<vrb1>",True,True,["<pl1>","<pl2>","<pr1>","<pr2>","<pr3>","<tng2>","<tng3>"])
of = wtags("of","<of>",False,False,False)
unk = wtags(".+","<unk>",True,True,True)

wrd3s = pr3.ptrn+tng3.ptrn
# } End of the Word tag Dicts 

# List of all the Wtags
tgs = [y.tg1 for y in wtgs] # List of all the Wtags Names


# Words or Phases wanted to replace from the Input text
rep = {"my&me":"i","your":"you","his&him":"he","hers&her":"she","mom&momy":"mother","dad&daddy":"father","bro":"brother","this&that":"it","sis":"sister","there in":"are there in","wi-fi":"wifi","@please&can you&'s&was& name":"","date of birth":"born","@'m":" am"}
rep.update({f"@{y}":f" {y} " for y in "+-*/%^"}) # Adds the Maths symbols with their space to Replace Dict
for y in wtgs: rep.update(y.rep_) # Adds All the Replaceing words from the All Wtag classes to Replace Dict

class Processer:
	#This class is used to Preprocess the texts link Grouping the texts and Replacing the words
	def __init__(self): pass
	
	def wrd_enc(self,wrd,sm): # Encodes  the single word by checking
		for x in wtgs:
			tg,wrd,sm = x.fl_sm(wrd,sm)
			if tg: break
		if x==unk: # If the word is unknown then it try it again with its prural form removes if it has
			for y1 in ("ies","ves","es","s"):
				if wrd.endswith(y1):
					sm.pop(tg)
					wrd = wrd[:-len(y1)]
					tg,x,wrd,sm = self.wrd_enc(wrd,sm)
					break
		if tg=="<art>": tg,wrd = "",""
		return tg,x,wrd,sm
	
	def snt_enc(self,snt): # Replaces , Groups and Creates Sm and returns
		sm = {}
		txt = ""
		#replacing needed {
		snt = snt.lower()
		for ky,vl in rep.items():
			if ky.startswith("@"):
				ky = ky[1:]
				for y in ky.split("&"): snt = snt.replace(y,vl)
			else:
				for x in ky.split("&"):
					if x in snt: snt = re.sub(rf"\b{x}\b",vl,snt)
		# }
		
		# proceessing {
		txt = []
		for wrd in snt.split(" "):
			if wrd.strip() == "": continue
			tg,tgt,wrd2,sm = self.wrd_enc(wrd,sm)
			if not tg: continue
			if len(txt) >= 1:
				if "<vrb1:" in tg and txt[-1] == "<vrb3>": txt.pop(-1)
				ptg1 = Tg2Tg(txt[-1]) 
				if ptg1 in tgt.apnd: # if the current tag is appendable to previous tag
					ptg = txt[-1]
					if ptg1 == tgt.tg1 and "2>" not in ptg1: #Appends if both the tags are same
						if tgt.ret_wrd:
							sm.pop(tg)
							sm[ptg] = sm[ptg]+" "+wrd2
					else: # appends if the tag is in list
						sm[tg],txt[-1] = sm[ptg]+"&"+wrd2,tg
						sm.pop(ptg)
				else: txt.append(tg)
			else: txt.append(tg)
			
			if len(txt) > 3:
				if txt[-3] == "<of>" and txt[-4] != "<mt>":
					pre_of,nxt_of = txt[-4],txt[-2]
					sm[pre_of] = sm[nxt_of]+"&"+sm[pre_of]
					sm.pop(nxt_of)
					for _ in range(2): txt.pop(-2)
			
		if len(txt) > 2:
			if txt[-2] == "<of>" and txt[-3] != "<mt>":
				pre_of,nxt_of = txt[-3],txt[-1]
				sm[pre_of] = sm[nxt_of]+"&"+sm[pre_of]
				sm.pop(nxt_of)
				for _ in range(2): txt.pop(-1)
		
		for ky in txt: # To Aling the Word Numbers from sentence
			if ky.startswith("<num-c:"):
				sm["<num:"+ky[-2:]] = str(w2n.word_to_num(sm[ky]))
				sm.pop(ky)
				
		txt = " ".join(txt)
		if ("on" in snt) and ("<sw>" not in sm) and ("<st>" in sm):
			sm.pop("<st>")
			txt = txt.replace("<st>","<pre>")
		txt = txt.replace("-c","").strip()
		
		return [txt," ".join([Tg2Tg(y) for y in txt.split(" ")])],sm
		# }

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
	
	def merge2(self,ls,upto=False): #Merges with replacing the variables it already has
		if type(ls)==str: ls = self.demerge(ls)
		if ls[0] in wrd3s:
			try: ls[0] = self.allmem[ls[0]]
			except KeyError: pass
		upto = upto and len(ls)>1
		if upto:
			last_wrd = ls[-1]
			ls.pop(-1)
		def Sub_merge(st,nd): # Def that checks and reduces
			mr = st+self.merger+nd
			try: return self.allmem[mr]
			except KeyError: return mr
		ret = reduce(Sub_merge,ls) # returns the reduced output
		return self.merge([ret,last_wrd]) if upto else ret
	
	def demerge2(self,ky):
		if type(ky) == str: ky = self.demerge(ky)
		allremem = self.allremem
		ret = ky.copy()
		while True: #It runs while any of the first not in allremem or in pr3s
			try: first = allremem[ret[0]]
			except KeyError: break
			for y in ["i","you","he","she"]:
				if y in first:
					ret.pop(0)
					ret.insert(0,y)
					break
			else:
				ret.pop(0)
				ret = self.demerge(first[0]) + ret
		if len(ret) != 1:
			for x,y in enumerate(ret[:-1]):
				if y == "i": ret[x] = "my"
				elif y == "you": ret[x] = "your"
				elif y == "he": ret[x] = "his"
				elif y == "she": ret[x] = "hers"
				else: ret[x] = ret[x]+"'s"
		else:
			if ret[0] == "i": return "me"
		if ky == ret: return "Unk"
		ret = " ".join(ret)
		return ret
			
				
		
	def Set_it(self,txts,sm):
		txt = txts[-1] if type(txts)==list else txts # gets the taged txt and taged without ids txt
		try: (ky_typ,ky),(vl_typ,vl) = tuple(sm.items()) # Gets the key,value and their type from the sm dict came from processer
		except ValueError: return None
		if ky.count("&") < vl.count("&"): ky_typ,ky,vl_typ,vl = vl_typ,vl,ky_typ,ky #swaps the ky and vl if vl has more words
		ky1 = self.merge2(ky,upto=True)
		vl = self.merge2(vl) #Get the pureified ky and vl
		if "<pre>" in txt: self.__pl2__[ky1] = vl # Find and sets pl
		elif "<vrb" in txt:
			if "<pr" in txt: # Find and sets the pr dicts
				if "<pr3:" in ky_typ: gnd = ky
				else:
					self.__pr2__[ky1] = vl
					gnd = predict_gnd(vl)[0] # gets the gender of the person
				self.__pr3__[gnd] = vl
			else: self.__tng2__[ky1] = vl # Find and sets tng
		else: return None
		self.__tng3__["it"] = vl
		return "Done"
	
	def Get_it(self,txts,sm):
		txt = txts[-1] if type(txts)==list else txts # gets the taged txt and taged without ids txt
		ky_typ,ky = tuple(sm.items())[-1] # Gets the key,value and their type from the sm dict came from processer
		ret = self.merge2(ky,upto=True)
		try:
			if "<pr4>" in txt:
				if "<pr3:" in ky_typ: pass
				elif ret in self.__pr2__: ret = self.__pr2__[ret]
				elif "&" in ret: pass
				else: return self.demerge2(ret)
			elif "<pl4>" in txt:
				ret = self.__pl2__[ret]
			elif "<tng4>" in txt:
				if ret.endswith("&name"): return ret.replace("&name","")
				if ret in self.__tng2__: ret = self.__tng2__[ret]
				elif "&" in ret: pass
				else: return self.demerge2(ret)
			else: return "Unk"
		except: return "Unk"
		self.__tng3__["it"] = ret
		if "&" in ret: return "Unk"
		else: return ret
		


# } End of the class

if __name__ == "__main__":
	pre = Processer()
	mem = Memory()
	t.start()
	mem.Set_it(*pre.snt_enc("I am rahim"))
	mem.Set_it(*pre.snt_enc("you are alpha"))
	mem.Set_it(*pre.snt_enc("i am your boss"))
	mem.Set_it(*pre.snt_enc("my mother is kamaliya"))
	mem.Set_it(*pre.snt_enc("kamaliya mother is ansariya"))
	mem.Set_it(*pre.snt_enc("hers age is 78"))
	mem.Set_it(*pre.snt_enc("I am in udangudi"))
	mem.Set_it(*pre.snt_enc("Udangudi is my village"))
	mem.Set_it(*pre.snt_enc("I will be going to my village"))
	mem.Set_it(*pre.snt_enc("udangudi is a beautiful village"))
	mem.Set_it(*pre.snt_enc("it is in tamilnadu"))
	mem.Set_it(*pre.snt_enc("bangalore is the capital of karnataka"))
	mem.Set_it(*pre.snt_enc("karnataka is my state"))
	mem.Set_it(*pre.snt_enc("17 is my age"))
	mem.Set_it(*pre.snt_enc("i am ajay"))
	print(mem.Get_it(*pre.snt_enc("who are you")))
	mem.print()
	t.stop("To end")