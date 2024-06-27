#pylint:disable=W0120
#pylint:disable=W0102
import re
from word2number import w2n
import json as js

vrbs = js.loads(open("vrbs.json","r").read())
class wtags:
	def __init__(self,ptrn,tg="",ret_wrd=True,has_id=True,apnd=False):
		self.ret_wrd = ret_wrd
		self.has_id = has_id
		self.tg1 = tg
		if has_id: self.tg2 = tg.replace(">",":0>")
		else: self.tg2 = tg
		self.rep_ = {}
		self.apnd = apnd
		if ptrn == "Verb": self.ptrn = self.isvrb
		else: self.ptrn = ptrn
		self.ptyp = type(self.ptrn)
		if self.ptyp == list:
			for num,wrd in enumerate(ptrn):
				if " " in wrd:
					wrd = wrd.lower()
					wrd_ = wrd.replace(" ","_")
					self.rep_[wrd] = wrd_
					ptrn[num] = wrd_
			self.ptrn = ptrn
		elif self.ptyp == str: self.ptrn = ("^"+ptrn+"$").lower()
	
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
	def isvrb(slf,wrd):
		for y in vrbs:
			if wrd in y:
				wrd = y[0]
				tg = slf.tg2
				break
		else: tg = ""
		return tg,wrd
		
	

def get_dt(txt):
	for ptr,frm in {
	r"\b((\d{,2})[snrt][tdh] ([a-z]{3,9})( \d{4})?)\b": "d:{d1}_{d2}_{d3}",
	r"\b((\d{,2})[snrt][tdh] of ([a-z]{3,9})( \d{4})?)\b":"d:{d1}_{d2}_{d3}",
	r"\b(([a-z]{3,9}) (\d{,2})[snrt][tdh]( \d{4})?)\b":"d:{d3}_{d1}_{d3}",
	r"\b((\d{,2}):(\d{,2}) ([pa]\.?m))\b":"t:{d1}_{d2}_{d3}",
	r"\b((\d+)'o clock)":"t:{d1}_00_"
	}.items():
		all1 = re.findall(ptr,txt)
		if all:
			for al in all1:
				txt = re.sub(al[0],frm.format_map({f"d{ky}":vl.strip() for ky,vl in enumerate(al)}),txt)		
	return txt
	
	
unk = wtags(".+","<unk>",True,True,True)
pr1 = wtags(["haja","kamaldeen","kamaliya","rahim","rafeel","santhosh","vishal","naveen","rahul","nithish","nithin","stephen","tony","stark","robert","chris","peter","vijay","kumar","jai","subramani","priya","divya","sakthi","thilak","yogeash","suriya","jayam","ravi","bala"],"<pr1>",True,True,True)
pr2 = wtags(["mother","father","friend","brother","sister","wife","husband","founder","owner","son","daughter","grandma","grandfather","student","friend","creator","boss","assistant","teacher","baby","child"],"<pr2>",True,True,False)
pr3 = wtags(["i","me","my","you","your","his","her","hers","she","he","we","our","they","us"],"<pr3>",True,True,False)
pr4 = wtags(["who","whom"],"<pr4>",True,False,False)

pl1 = wtags(["bangalore","india","tamil nadu","karnataka","udangudi","thoothkudi","thirunelvelai","chennai","madras","mallaswaram","soldevanahalli","mejastic"],"<pl1>",True,True,False)
pl2 = wtags(["school","collage","home","factory","company","office","bustop","bustand","institute","state","district","country"],"<pl2>",True,True,False)
pl3 = wtags(["here","there"],"<pl3>",True,True,False)
pl4 = wtags(["where"],"<pl4>",True,False,False)

dt1 = wtags(r"[dt]:\w+_\w+_(\w+)?","<dt1>",True,True,True)
dt2 = wtags(["year","month","weak","day","hour","minute","second","birthday","deathday","anniversary"],"<dt2>",True,True,False)
dt3 = wtags([],"<dt3>",True,True,False)
dt4 = wtags(["when"],"<dt4>",True,False,False)

tng2 = wtags(["book","mobile","watch","tv","computer","laptop","mouse","bulb","planet","number","phone","fan","charger","game","age","gender","height","weight","ram","name","dob","capital","date of birth","place","date","time"],"<tng2>",True,True,False)
tng3 = wtags(["it"],"<tng3>",True,True,False)
tng4 = wtags(["which","what","how many"],"<tng4>",True,False,False)

vrb1 = wtags("Verb","<vrb1>",True,True,False)
vrb3 = wtags(["is","are","was","were","am"],"<vrb3>",False,False,False)

pre = wtags(["in","on","under","inside","outside","above","across","to","from"],"<pre>",False,False,False)
cnj = wtags(["and","but","therefore","so"],"<cnj>",False,False,False)
art = wtags(["the","an","a"],"<art>",False,False,False)
num = wtags(r"\d+","<num>",True,True,False)
numc = wtags(list(w2n.american_number_system.keys()),"<num-c>",True,True,True)
lv = wtags(r"\d+(st|nd|rd|th)","<lv>",True,True,False)
st = wtags(["on","off"],"<st>",True,False,False)
sw = wtags(["flash","torch","internet","bluetooth","wifi","hotspot","net","gps","aeroplane mode"],"<sw>",True,False,False)
mt = wtags(["+","-","*","x","/","^","add","subtract","multiply","divide","square","cube","sum","square root","cube root","difference","product","times","are there in","power","raises","^"],"<mt>",True,False,False)


wts = [pr1,pr2,pr3,pr4,pl1,pl2,pl3,pl4,dt1,dt2,dt4,tng2,tng3,tng4,vrb3,art,num,numc,cnj,lv,st,sw,mt,pre,vrb1,unk]
tgs = [y.tg1 for y in wts]

rep = {"mom&momy":"mother","dad&daddy":"father","bro":"brother","sis":"sister","there in":"are there in","wi-fi":"wifi","@please&can you&'s":"","date of birth":"born","@'m":" am"}
rep.update({f"@{y}":f" {y} " for y in "+-*/%^"})
for y in wts: rep.update(y.rep_)

class processer:
	def __init__(self): pass
	
	def wrd_enc(self,wrd,sm):
		for x in wts:
			tg,wrd,sm = x.fl_sm(wrd,sm)
			if tg: break
		if x==unk:
			for y1 in ("ies","ves","es","s"):
				if wrd.endswith(y1):
					sm.pop(tg)
					wrd = wrd[:-len(y1)]
					tg,x,wrd,sm = self.wrd_enc(wrd,sm)
					break
		return tg,x,wrd,sm
			
	
	def snt_enc(self,snt):
		sm = {}
		txt = ""
		#replacing neededs {
		snt = snt.lower()
		snt = get_dt(snt)
		for ky,vl in rep.items():
			if ky.startswith("@"):
				ky = ky[1:]
				for y in ky.split("&"): snt = snt.replace(y,vl)
			else:
				for x in ky.split("&"):
					if x in snt: snt = re.sub(rf"\b{x}\b",vl,snt)
		# }
		
		# proceessing {
		ptgt,ptg = cnj,""
		for wrd in snt.split(" "):
			if wrd.strip() == "": continue
			tg,tgt,wrd2,sm = self.wrd_enc(wrd,sm)
			if not tg: continue
			if ptgt.apnd and ptgt.tg1 == tgt.tg1:
				sm.pop(tg)
				sm[ptg] = sm[ptg] + " " + wrd2
			else:
				txt = txt + " " + tg
				ptgt,ptg = tgt,tg
		for ky in txt.split(" "):
			if ky.startswith("<num-c:"):
				sm["<num:"+ky[-2:]] = str(w2n.word_to_num(sm[ky]))
				sm.pop(ky)
		return txt.replace("-c","").strip(),sm
		# }
