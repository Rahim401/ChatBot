from utils import inputclr
import json as js
from control import ctl
from word2number import w2n

prs = ["<pr>","who","i","me","my","you","your","his","her","she","he","we","our","they","us","haja","kamaldeen","kamaliya","rahim","rafeel","santhosh","vishal","naveen","rahul","nithish","nithin","stephen","tony","stark","robert","chris","peter","vijay","kumar","jai","subramani","priya","divya","sakthi","thilak","yogeash","suriya","jayam","ravi"]
pr2s = ["<pr2>","mother","father","sister","brother","founder","owner","wife","husband","son","daughter","grandma","grandfather","student","friend","creator","boss","assistant","teacher"]
pls = ["<pl>","where","there","bangalore","india","tamil","nadu","karnataka","udangudi","thoothkudi","thirunelvelai","chennai","madras","mallaswaram","soldevanahalli","mejastic"]
pl2s = ["<pl2>","school","collage","home","factory","company","office","bustop","bustand","institute","state","district","country"]
vrbs = js.loads(open("vrbs.json","r").read())
vrb2s = ["<vrb2>","am","is","are","was","were","do"]
tgs = ["<tg>","what","which","pubg","samsung","apple","microsoft","mi","nokia","lg","youtube"]
tg2s = ["<tg2>","book","mobile","watch","tv","computer","laptop","mouse","bulb","planet","number","phone","fan","charger","game","age","gender","height","weight","ram","name","dob","capital","dob"]
art = ["<art>","the","an","a"]
con = ["<con>",",","and","but"]
com = ["<com>","this","that","next","last","with","of","for"]
pre = ["<pre>","in","on","at","under","above","across","from","to"]
mns = ["<mn>","january","febraury","march","april","may","june","july","august","september","november","december"]
days = ["<dy>","sunday","monday","tuesday","wednesday","thursday","friday","saturday"]
dt2 = ["<dt2>","today","now","yesterday","tommorrow","date","time","day","month","year"]
state = ["<st>","on","off"]
trn = ["<trn>","flash","torch","internet","bluetooth","wifi","hotspot","net","gps","arpln"]
math = ["<mt>","+","-","*","X","x","/","^","add","subtract","multiply","divide","square","cube","sum","squrt","cubrt","difference","product","times","ati","power","raises","^"]
ls = ["","<unk>","<art>","<pre>","<con>","<com>","<st>","<mt>","<vrb2>"]
_ = [ls.extend([x.replace("0",str(a)) for a in range(y)]) for x,y in {"<unk:0>":3,"<pr:0>":3,"<pr2:0>":3,"<pl:0>":3,"<pl2:0>":3,"<tg:0>":3,"<tg2:0>":3,"<vrb:0>":2,"<mn:0>":2,"<dy:0>":2,"<dt2:0>":2,"<dt:0>":2}.items()]

ls  = list(set(ls))
pos = [prs,pr2s,pls,pl2s,tgs,tg2s,vrbs,vrb2s,pre,con,com,mns,days,dt2,state,math,art]
						
def get_ky(ls,ky):
	while ky in ls:
		nm = ky[-2]
		try: ky = ky.replace(nm,str(int(nm)+1))
		except ValueError: break
	return ky
	
class preprocesser:
	def __init__(self):
		pass
	
	def wrd_enc(self,wrd):
		wrd = wrd.replace("#","").replace("$","").replace("'s","").lower().strip()
		try: wrd = str(w2n.word_to_num(wrd))
		except:pass
		for y in [prs,pr2s,pls,pl2s,tgs,tg2s,dt2,math,state,trn,pre,art,con,com,mns,days,vrb2s]:
			if wrd in y:
				if y in [con,com,art,pre,math,trn,state,vrb2s]: return y[0],wrd
				else: return y[0].replace(">",":0>"),wrd
		else:
			for x in vrbs:
				if wrd in x: return "<vrb:0>",x[0]
			else:
				if str.isnumeric(wrd.replace("-","")) or wrd=="<nm>": return "<nm:0>",wrd
				elif wrd[:-2].isdigit() and any([str.endswith(wrd,x) for x in ["st","nd","rd","th"]]): return "<lv:0>",wrd
				else: return "<unk:0>",wrd
			
	def do(self,txt,on="test"):
		if type(txt) == str:
			ptyp = ""
			sm = {}
			ret = ""
			rep = {"date of birth":"dob","mom":"mother","dad":"father","bro":"brother","sis":"sister","square root":"squrt","cube root":"cubrt","can you":"","are there in":"ati","there in":"ati","please":"","Wi-Fi":"wifi","+":" + ","-":" - ","*":" * ","/":" / ","^":" ^ ","x":" x ","hi":"","hello":"","aeroplane mode":"arpln","how many":""}
			for a,b in rep.items():
				if any([y in txt for y in (a+" "," "+a+" "," "+a)]) or any([y in txt for y in ("+","-","*","x","/","^")]): txt = txt.replace(a,b)
			for wrd in txt.strip().split(" "):
				if wrd.strip() == "":continue
				typ,wrd2 = self.wrd_enc(wrd)
				typ = get_ky(sm,typ)
				if ptyp[:-2] != typ[:-2]:
					if typ not in ["<con>","<pre>","<art>","<vrb2>","<com>"]: sm[typ] = wrd2
					ret+= " "+typ
					ptyp = typ
				else:
					sm[ptyp] = sm[ptyp]+" "+wrd2
			if on=="train": return ret.strip()
			else: return [ret.strip(),sm]
		else: return [self.do(y,on) for y in txt]
	
	@staticmethod	
	def create_data(path=""):
		try: dic = js.loads(open(path,"r").read())
		except: dic = {"data":{},"lst":ls,"raw":{}}
		while True:
			cls = inputclr("\nWhich class : ","+")
			if cls in ("end","e","quit"): break
			inp  = inputclr("Inputs : ","+")
			dta = preprocesser().do(inp.split(","),"train")
			if cls in dic["data"].keys():
				dic["data"][cls] += dta
				dic["raw"][cls] += ","+inp
			else:
				dic["data"][cls] = dta
				dic["raw"][cls] = inp
			if path: open(path,"w").write(js.dumps(dic))
		return dic
			
	@staticmethod
	def get_data(cls,data="Data.json"):
		return js.loads(open(data,"r").read())

class one_hot:
	def __init__(self,ls1=None,pd=16):
		if ls1: self.ls = ls1
		else: self.ls = ls
		self.pad = pd
		self.prepo = preprocesser()
	
	def inp_enc(self,txt,pro=True):
		typ =type(txt)
		if typ == str:
			if pro:
				tx,sm = self.prepo.do(txt)
				return self.inp_enc(tx,False),sm
			else:
				ret = [self.ls.index(y) for y in txt.split(" ")]
				return ret+[0 for _ in range(self.pad-len(ret))]
		else: return [self.inp_enc(txt,pro) for x in txt]
		
	def inp_dec(self,ls):
		try:
			_ = ls[0] + 1
			ret = ""
			for y in ls: ret += " "+self.ls[y]
			return ret.strip()
		except: return [self.inp_dec(y) for y in ls]

if __name__ == "__main__":
	print(preprocesser().do("switch on the internet"))