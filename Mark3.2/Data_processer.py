#pylint:disable=W0120
#pylint:disable=W0102
import re
from utils import timer
t = timer()
from word2number import w2n
import datetime as dt
import json as js


vrbs = js.loads(open("vrbs.json","r").read())
gnd_data = js.loads(open("gnd.json","r").read())
now = dt.datetime.now()
weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
months = ["january","febraury","march","april","may","june","july","august","september","november","december"]
SBmonths = '|'.join(months+[y[:3] for y in months])
DtPatterns = {
	r"\b((\d{,2})(st|nd|rd|th)?( of | )("+SBmonths+")( \d{4})?)\\b": "d:{5}_{4}_{1}",
	r"\b(("+SBmonths+") (\d{,2})(st|nd|rd|th)?( \d{4})?)\\b":"d:{4}_{1}_{2}",
	r"\b(([0-9][012]?):([0-6][0-9]?) ?(pm|am))\b":"t:{1}_{2}_{3}",
	r"\b(([0-9][012]?) ?(pm|am))\b":"t:{1}__{2}",
	r"\b(([0-9][012]?) ?o'clock)\b":"t:{1}__"
}

# Wanted Defs {
def predict_gnd(name): # Used to predict the Gender By Name
	try: gnd = gnd_data[name[-3:].lower()]
	except KeyError: return ("unk",0)
	if gnd[0] > gnd[1]: return "male",(gnd[0]/sum(gnd))
	else: return "female",(gnd[1]/sum(gnd))

def FindWeekDate(day,to):
	rng = (7,) if to==0 else (-7,0) if to==-1 else (7,14)
	for num in range(*rng):
		date = (now+dt.timedelta(days=num))
		if weekdays[date.weekday()] == day: return date
	else: return None

def RepDeltas(txt):
	txt = txt.replace("comeing","this")
	match = re.findall(r"\b((last|this|next) (\w+))\b",txt) + re.findall(r"\b((day|month|year) is (this|next))\b",txt)+re.findall(r"\b(on ()({"+'|'.join(weekdays)+"}))\\b",txt)
	for ful,to,delta in match:
		if delta in ["this","next","last"]: to,delta = delta,to
		to = -1 if to=="last" else 0 if to in ("this","") else 1
		if delta == "month": txt = txt.replace(ful,now.replace(month=(now.month+to) if now.month != 12 else 1).strftime("%B"))
		elif delta == "year": txt = txt.replace(ful,now.replace(year=now.year+to).strftime("%Y"))
		elif delta == "day": txt = txt.replace(ful,(now+dt.timedelta(days=to)).strftime("%A"))
		else: txt = txt.replace(ful,FindWeekDate(delta,to).strftime("d:%Y_%B_%d"))
	txt = txt.lower()
	for ptr,frm in DtPatterns.items():
		all1 = re.findall(ptr,txt)
		for al in all1: txt = txt.replace(al[0],frm.format(*[y.strip() for y in al]))
	return txt
	
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
		self.apnd = apnd
		self.ptrn = self.isvrb if ptrn=="Verb" else ptrn
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
	def isvrb(slf,wrd): # Used to identify the Verbs using  a large dictionary(Json)
		for y in vrbs:
			if wrd in y:
				wrd = y[0]
				tg = slf.tg2
				break
		else: tg = ""
		return tg,wrd
		


# Word Tags Group or Dictionary {
unk = wtags(".+","<unk>",True,True,True)
pr1 = wtags(["haja","kamaldeen","kamaliya","rahim","rafeel","santhosh","vishal","naveen","rahul","nithish","nithin","stephen","tony","stark","robert","chris","peter","vijay","kumar","jai","subramani","priya","divya","sakthi","thilak","yogeash","suriya","jayam","ravi","bala"],"<pr1>",True,True,True)
pr2 = wtags(["mother","father","friend","brother","sister","wife","husband","founder","owner","son","daughter","grandma","grandfather","student","friend","creator","boss","assistant","teacher","baby","child"],"<pr2>",True,True,False)
pr3 = wtags(["i","me","my","you","your","his","her","hers","she","he","we","our","they","us"],"<pr3>",True,True,False)
pr4 = wtags(["who","whom"],"<pr4>",True,False,False)

pl1 = wtags(["bangalore","india","tamil nadu","karnataka","udangudi","thoothkudi","thirunelvelai","chennai","madras","mallaswaram","soldevanahalli","mejastic"],"<pl1>",True,True,False)
pl2 = wtags(["school","collage","home","factory","company","office","bustop","bustand","institute","state","district","country"],"<pl2>",True,True,False)
pl3 = wtags(["here","there"],"<pl3>",True,True,False)
pl4 = wtags(["where"],"<pl4>",True,False,False)

dt1 = wtags(r"\b[dt]:\w{3,20}\b","<dt1>",True,True,True)
dt2 = wtags(["birthday","deathday","wedding day"],"<dt2>",True,True,False)
dt3 = wtags(["year","month","weak","day","hour","minute","second"],"<dt3>",True,True,False)
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

# } End of the Word tag Dicts 

# List of all the Wtags
wts = [pr1,pr2,pr3,pr4,pl1,pl2,pl3,pl4,dt1,dt2,dt4,tng2,tng3,tng4,vrb3,art,num,numc,cnj,lv,st,sw,mt,pre,vrb1,unk]
tgs = [y.tg1 for y in wts] # List of all the Wtags Names

# Words or Phases wanted to replace from the Input text
rep = {"mom&momy":"mother","dad&daddy":"father","bro":"brother","sis":"sister","there in":"are there in","wi-fi":"wifi","@please&can you&'s":"","date of birth":"born","@'m":" am"}
rep.update({f"@{y}":f" {y} " for y in "+-*/%^"}) # Adds the Maths symbols with their space to Replace Dict
for y in wts: rep.update(y.rep_) # Adds All the Replaceing words from the All Wtag classes to Replace Dict


class Processer:
	#This class is used to Preprocess the texts link Grouping the texts and Replacing the words
	def __init__(self): pass
	
	def wrd_enc(self,wrd,sm): # Encodes  the single word by checking
		for x in wts:
			tg,wrd,sm = x.fl_sm(wrd,sm)
			if tg: break
		if x==unk: # If the word is unknown then it try it again with its prural form removes if it has
			for y1 in ("ies","ves","es","s"):
				if wrd.endswith(y1):
					sm.pop(tg)
					wrd = wrd[:-len(y1)]
					tg,x,wrd,sm = self.wrd_enc(wrd,sm)
					break
		return tg,x,wrd,sm
	
	def snt_enc(self,snt): # Replaces , Groups and Creates Sm and returns
		sm = {}
		txt = ""
		#replacing needed {
		snt = snt.lower()
		snt = RepDeltas(snt)
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
			if tgt.apnd and tgt.tg1 == ptgt.tg1:
				sm.pop(tg)
				sm[ptg] = sm[ptg] + " " + wrd2
			else:
				txt = txt + " " + tg
				ptgt,ptg = tgt,tg
		print(txt,sm)
		for ky in txt.split(" "): # To Aling the Word Numbers from sentence
			if ky.startswith("<num-c:"):
				sm["<num:"+ky[-2:]] = str(w2n.word_to_num(sm[ky]))
				sm.pop(ky)
		return txt.replace("-c","").strip(),sm
		# }

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
		return sym.join(ls)
		
	def print(self): #prints the value of current memorys
		for x,y in zip(self.tg_ls,self.mem_ls): print(f"{x[1:-1]} : {y}")
	
	def merge2(self,ls,rt="ky"): #Merges with replacing the variables it already has
		rep = []
		for wrd in ls:
			# if any of the wrd in any tag3 like(it,his,i) , put the value else wrd
			if wrd in (pr3.ptrn+pl3.ptrn+dt3.ptrn+tng3.ptrn):
				try: wrd2 = self.allmem[wrd]
				except: wrd2 = wrd
				rep.append(wrd2)
			else: rep.append(wrd)
		# while len(rep) == 1: merge first 2 elements and returns the value of it from meory and repets
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
		if rt=="vl": return self.merge(rep," ",False) # Returns to display
		else: return self.merge(rep) # Returns to save::
		
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
	
	def set_dt2(self,vr,it):
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
		except KeyError: ret = mr
		self.tng3["it"] = ret
		return ret


# } End of the class

if __name__ == "__main__":
	pre = Processer()
	t.start()
	print(pre.snt_enc("rahim kumar"))
	print(pre.snt_enc("twenty two"))
	t.stop("To end")