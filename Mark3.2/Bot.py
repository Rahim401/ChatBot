#pylint:disable=W0621
#pylint:disable=W0120
#from utils import timer
from Bot_utils import Processer,Memory,predict_gnd,re
from Protocals import protocals,ctl

#The bot class
class Bot:
	def __init__(self,name="alpha",user="rahim",do=False):
		self.ltm = Memory()
		self.ltm.__pr3__["you"] = name
		self.ltm.__pr3__["i"] = user
		self.ltm.__pr2__[f"{name}&boss"] = user
		self.pre = Processer()
		self.protocals = protocals(ltm=self.ltm,do=do)
	
	@property
	def user_gnd(self): # Used to predict the users gender
		gnd = predict_gnd(self.ltm.__pr3__["i"])[0]
		return ["male","sir"] if gnd=="male"else  ["female","mam"] if gnd=="female" else ["unk",""]
		
	def PredictDo(self,txt1):
		try:
			txt1 = txt1.lower()
			if "it" in self.ltm.__tng3__ and "it" in txt1:
				txt1 = re.sub(r"\bit\b",self.ltm.__tng3__["it"],txt1)
			(txt2,txt3),sm = self.pre.snt_enc(txt1)
			ret = self.protocals.FindCallProto((txt1,txt2,txt3),sm)
			if ret: return ret.replace("u_gnd",self.user_gnd[-1])
			else: pass
		except: pass
		return self.protocals.say(["Sorry i didn't got that","I can't able to understand that","I didn't got that right"])
	
	def Assist(self):
		Todo = ctl.chk
		while True:
			if Todo:
				inp,_ = ctl.spc_rec2(th=0.80)
				try: print("\nYou : "+inp)
				except TypeError: continue
			else: inp = input("\nYou : ")
			if inp in ("end","quit"): break
			elif inp == "ltm": self.ltm.print()
			else:
				out = self.PredictDo(inp)
				print("Bot : "+out)
				if Todo: ctl.spk(out)
		
		

if __name__ =="__main__":
	Alpha = Bot(do=True)
	Alpha.ltm.__tng2__["rahim&age"] = "17"
	Alpha.Assist()