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
base_dt = now.replace(hour=0,minute=0,second=0,microsecond=0)
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
	match = re.findall(r"\b((last|this|next) (\w+))\b",txt) + re.findall(r"\b((day|month|year) is (this|next))\b",txt)+re.findall(r"\b(()("+'|'.join(weekdays)+"))\\b",txt)+re.findall(r"\b((yesterday|today|tommorrow)())\b",txt)
	for ful,to,delta in match:
		if delta in ["this","next","last"]: to,delta = delta,to
		if to in ["yesterday","today","tommorrow"]: delta = "date"
		to = -1 if to in ("last","yesterday") else 0 if to in ("this","","today") else 1
		if delta == "month": txt = txt.replace(ful,now.replace(month=(now.month+to) if now.month != 12 else 1).strftime("%B"))
		elif delta == "year": txt = txt.replace(ful,now.replace(year=now.year+to).strftime("%Y"))
		elif delta == "day": txt = txt.replace(ful,(now+dt.timedelta(days=to)).strftime("%A"))
		elif delta == "date": txt = txt.replace(ful,(now+dt.timedelta(days=to)).strftime("d:%Y_%B_%d"))
		else: txt = txt.replace(ful,FindWeekDate(delta,to).strftime("d:%Y_%B_%d"))
	txt = txt.lower()
	for ptr,frm in DtPatterns.items():
		all1 = re.findall(ptr,txt)
		for al in all1: txt = txt.replace(al[0],frm.format(*[y.strip() for y in al]))
	return txt

def Tg2Tg(tg):
	if ":" not in tg: return tg
	else: return tg.replace(tg[-3:-1],"")
	
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
			for num,wrd in enumerate(ptrn):
				if " " in wrd:
					wrd = wrd.lower()
					wrd_ = wrd.replace(" ","_")
					self.rep_[wrd] = wrd_
					ptrn[num] = wrd_
			self.ptrn = ptrn
		elif self.ptyp == str: self.ptrn = ("^"+ptrn+"$").lower()
	
	def __str__(self): return self.tg1
	
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
pr2 = wtags(["mother","father","friend","brother","sister","wife","husband","founder","owner","son","daughter","grandma","grandfather","student","friend","creator","boss","assistant","teacher","baby","child","boy","girl","male","female"],"<pr2>",True,True,["<pr2>","<pr1>","<pr3>","<adj>"])
pr3 = wtags(["i","me","my","you","your","his","her","hers","she","he","we","our","they","us"],"<pr3>",True,True,False)
pr4 = wtags(["who","whom"],"<pr4>",False,False,False)

pl1 = wtags(["bangalore","india","tamil nadu","karnataka","udangudi","thoothkudi","thirunelvelai","chennai","madras","mallaswaram","soldevanahalli","mejastic"],"<pl1>",True,True,False)
pl2 = wtags(["school","collage","home","factory","company","office","bustop","bustand","institute","state","district","country","place","city","village"],"<pl2>",True,True,["<pl2>","<pr1>","<pr2>","<pr3>","<adj>"])
pl3 = wtags(["here","there"],"<pl3>",True,True,False)
pl4 = wtags(["where"],"<pl4>",False,False,False)

dt1 = wtags(r"\b[dt]:\w{3,20}\b","<dt1>",True,True,True)
dt2 = wtags(["birthday","deathday","wedding day","independence day"],"<dt2>",True,True,["<pl2>","<pr1>","<pr2>","<pr3>"])
dt3 = wtags(["year","month","weak","day","hour","minute","second"],"<dt3>",True,True,False)
dt4 = wtags(["when"],"<dt4>",False,False,False)

tng2 = wtags(["book","mobile","watch","tv","computer","laptop","mouse","bulb","planet","number","phone","fan","charger","game","age","gender","height","weight","ram","name","dob","capital","date of birth","place","date","time","color"],"<tng2>",True,True,["<pl1>","<pl2>","<pl3>","<pr1>","<pr2>","<pr3>","<adj>"])
tng3 = wtags(["it"],"<tng3>",True,True,False)
tng4 = wtags(["which","what","how many"],"<tng4>",False,False,False)

vrb1 = wtags("Verb","<vrb1>",True,True,["<pl1>","<pl2>","<pr1>","<pr2>","<pr3>","<tng2>","<tng3>"])
vrb3 = wtags(["is","are","was","were","am","will","did","do"],"<vrb3>",False,False,False)

pre = wtags(["in","on","under","inside","outside","above","across","to","from"],"<pre>",False,False,False)
cnj = wtags(["and","but","therefore","so"],"<cnj>",False,False,False)
adj = wtags(["favorite","favourite","good","bad","random","beautiful"],"<adj>",True,True,["<pl1>","<pl2>","<pl3>","<pr1>","<pr2>","<pr3>","<tng2>","<tng3>"])
art = wtags(["the","an","a"],"<art>",False,False,False)
num = wtags(r"\d+","<num>",True,True,False)
numc = wtags(list(w2n.american_number_system.keys()),"<num-c>",True,True,True)
lv = wtags(r"\d+(st|nd|rd|th)","<lv>",True,True,False)
st = wtags(["on","off"],"<st>",True,False,False)
sw = wtags(["flash","torch","internet","bluetooth","wifi","hotspot","net","gps","aeroplane mode"],"<sw>",True,False,False)
mt = wtags(["+","-","*","x","/","^","add","subtract","multiply","divide","square","cube","sum","square root","cube root","difference","product","times","are there in","power","raises","^"],"<mt>",True,False,False)
of = wtags("of","<of>",False,False,False)
# } End of the Word tag Dicts 

# List of all the Wtags
wts = [pr1,pr2,pr3,pr4,pl1,pl2,pl3,pl4,dt1,dt2,dt4,tng2,tng3,tng4,vrb3,art,num,numc,cnj,adj,lv,st,sw,mt,pre,vrb1,of,unk]
tgs = [y.tg1 for y in wts] # List of all the Wtags Names


# Words or Phases wanted to replace from the Input text
rep = {"mom&momy":"mother","dad&daddy":"father","bro":"brother","this":"it","sis":"sister","there in":"are there in","wi-fi":"wifi","@please&can you&'s&was":"","date of birth":"born","@'m":" am"}
rep.update({f"@{y}":f" {y} " for y in "+-*/%^"}) # Adds the Maths symbols with their space to Replace Dict
for y in wts: rep.update(y.rep_) # Adds All the Replaceing words from the All Wtag classes to Replace Dict

class Processer:
	#This class is used to Preprocess the texts link Grouping the texts and Replacing the words
	def __init__(self): pass
	
	def wrd_enc(self,wrd,sm=None): # Encodes  the single word by checking
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
		if tg=="<art>": tg,wrd = "",""
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
		txt = []
		for wrd in snt.split(" "):
			if wrd.strip() == "": continue
			tg,tgt,wrd2,sm = self.wrd_enc(wrd,sm)
			if not tg: continue
			if len(txt) >= 1:
				ptg1 = Tg2Tg(txt[-1])
				if ptg1 in tgt.apnd:
					ptg = txt[-1]
					if ptg1 == tgt.tg1:
						sm.pop(tg)
						sm[ptg] = sm[ptg]+" "+wrd2
					else:
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
				sm.pop,(nxt_of)
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
		if type(vr) == str: vr = self.demerge(vr)
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
		self.tng3["it"] = Dt2Sdt(it)
			
	def get_pr(self,vr):
		ret = self.merge2(vr,demerge=True)
		self.tng3["it"] = ret
		if "&" not in ret: return ret
			
	def get_pl(self,vr):
		ret = self.merge2(vr,demerge=True)
		try: ret = self.pl2[ret]
		except KeyError: return None
		self.tng3["it"] = ret
		if "&" not in ret: return ret
		
	def get_dt(self,vr):
		ret = self.merge2(vr)
		if type(ret) != str: ret = ret.strftime("%d %B %Y")
		self.tng3["it"] = ret
		if "&" not in ret: return ret
		
	def get_tng(self,vr):
		ret = self.merge2(vr,demerge=True).replace("&name","") # is ls has name pops it out
		self.tng3["it"] = ret
		if "&" not in ret: return ret


# } End of the class

if __name__ == "__main__":
	pre = Processer()
	mem = Memory()
	t.start()
	mem.set_pr2("i","rahim")
	mem.set_pl2("i","udangudi")
	mem.set_pl2("udangudi","tamilnadu")
	mem.print()
	#mem.set_pr2("i","rahim")
	print(mem.get_pl("udangudi"))
	t.stop("To end")