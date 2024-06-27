import os
import time
import json as js
import datetime as dt

class ControlError(Exception): pass
	
class control:
	def __init__(self,path = "InOut.json",syn = 0.1):
		self.io_path = path
		self.io_clr()
		self.io_r = open(self.io_path,"r").read()
		self.io_js = js.loads(self.io_r)
		self.io_id = -1
		self.syn = syn
		self.dic = {
		"telephony":["call","dial","ussd","call_ar"],
		"media": ["aud_rec","aud_srec","get_vlm","set_vlm","fls_on","fls_off","fls_tm","scrn_sht","aud_ply","aud_sply","vib","svib","spk","sspk","spc_rec","vid","svid","pho"],
		"apps":["apps_lst","app_open","app_pick"],
		"check":["get_btry","get_net","get_wifi","get_htspt","get_bt","get_arpln","is_ply","get_pwr","get_aux","get_vol","get_ori","get_btrysv"],
		"interface":["inp_win","web_win","touch","touch_lst","toast"],"from":["chk"]
		}
		self.data = js.loads(open("control.json","r").read())
		
		
	
	#Main Frame Methods
	def dly(self): time.sleep(self.syn)
	def io_w(self,txt): open(self.io_path,"w").write(txt) #To Write on file
	def io_d(self): self.io_w(js.dumps(self.io_js)) # To write the json to the file
	def io_clr(self): self.io_w('{"in":[],"out":[]}') # To initialize the file
	def io_ref(self): #To update the file
		self.io_r = open(self.io_path,"r").read()
		try: self.io_js =  js.loads(self.io_r)
		except js.JSONDecodeError: pass
	def io_in(self,ary): # To append a cmd to input
		time.sleep(self.syn)
		self.io_js["in"].append([ke for ke,vl in self.dic.items() if ary[0] in vl]+ary)
		self.io_id += 1
		self.io_d()
	def io_out(self): #to get the output from the file
		while  True:
			try: return self.io_js["out"][self.io_id]
			except IndexError: self.io_ref()
	def save(self): open("/data/data/ru.iiec.pydroid3/files/aarch64-linux-android/lib/python3.7/control.json","w").write(js.dumps(self.data))
	
	@property
	def chk(self): #chk 
		self.io_in(["chk"])
		time.sleep(self.syn)
		self.io_ref()
		try: self.io_js["out"][self.io_id]
		except IndexError: return False
		return True
			
	
	#Telephony methods
	def call(self,num,si=1): #To call
		num = str(num).replace("-","").lower()
		if not str.isnumeric(num):
			if num not in self.data["contacts"].keys(): self.data["contacts"][num] = input(f"Phone number of {num} : ")
			self.save()
			num = self.data["contacts"][num]
		self.io_in(["call",num,int(si),int(si)])
		return self.io_out()
	
	def dial(self,num,si=1): #To dial
		self.io_in(["dial",num,int(si),int(si)])
		return self.io_out()
	
	def ussd(self,num,si=1): #To get ussd response
		self.io_in(["ussd",num,int(si)])
		return self.io_out()
	
	def call_ar(self,des): #To attend or reject call
		if des in ("ans","a",True): des = "ans"
		elif des in ("rej","r",False): des = "rej"
		else: des = "none"
		self.io_in(["call_ar",des])
		return self.io_out()
		
		
	#Media methods
	def aud_rec(self,path):
		self.io_in(["aud_rec",path])
		return self.io_out()
		
	def aud_srec(self):
		self.io_in(["aud_srec"])
		return self.io_out()
	
	def aud_tm(self,path="/storage/emulated/0/control/Audio/",tm=300):
		self.aud_rec(path)
		time.sleep(tm)
		self.aud_srec()
	
	def get_vlm(self):
		self.io_in(["get_vlm"])
		return self.io_out()
	
	def set_vlm(self,vlm,stm=0x1,shw=0):
		self.io_in(["set_vlm",stm,vlm,shw])
		return self.io_out()
		
	def fls_on(self):
		self.io_in(["fls_on"])
		return self.io_out()
		
	def fls_off(self):
		self.io_in(["fls_off"])
		return self.io_out()
	
	def fls_tm(self,tm=25):
		self.io_in(["fls_tm",tm])
		return self.io_out()
	
	def scrn_sht(self,path="/storage/emulated/0/Control/Images/"):
		self.io_in(["scrn_sht",path])
		return self.io_out()
		
	def aud_ply(self,path,start=0):
		self.io_in(["aud_ply",path,start])
		return self.io_out()
		
	def aud_sply(self):
		self.io_in(["aud_sply"])
		return self.io_out()
		
	def vib(self,ptr):
		self.io_in(["vib",ptr])
		return self.io_out()
		
	def svib(self):
		self.io_in(["svib"])
		return self.io_out()
		
	def spk(self,txt,lang="en_US",sp=100):
		self.io_in(["spk",txt,lang,sp])
		return self.io_out()
		
	def sspk(self):
		self.io_in(["sspk"])
		return self.io_out()
		
	def spc_rec(self,lang="en_US",gp=1):
		self.io_in(["spc_rec",lang,gp])
		return self.io_out()
	
	def vid_rec(self,cam=0,fls="auto",path="/storage/emulated/0/Control/Video/"):
		self.io_in(["vid",cam,fls,path])
		return self.io_out()
	
	def vid_srec(self):
		self.io_in(["svid"])
		return self.io_out()
	
	def vid_tm(self,tm=300,cm=0,fs="auto",pth="/storage/emulated/0/Control/Video/"):
		self.vid_rec(cam=cm,fls=fs,path=pth)
		time.sleep(tm+2)
		self.vid_srec()
		
	def pho(self,path="/storage/emulated/0/Control/Images/",fls="auto",cam=1,qul=100):
		self.io_in(["pho",cam,qul,fls,path])
		return self.io_out()
	
	#Apps Method
	def apps_lst(self):
		self.io_in(["apps_lst"])
		return self.io_out()
		
	def app_open(self,app,act=None,uri=None):
		try: app = self.data["apps"][app.lower()]
		except:
			try: app = sorted([y for y in self.apps_lst() if app.lower() in y])[0]
			except:
				self.spk(f"Select {app}")
				pkg = self.app_pick()
				self.data["apps"][app.lower()] = pkg
				if pkg: self.save()
				app = pkg
		if app:
			self.io_in(["app_open",app,act,uri])
			return self.io_out()
		else: return ""
	
	def app_pick(self):
		self.io_in(["app_pick"])
		return self.io_out()
	
	
	#Interface
	def inp_win(self,title="",ityp="text",hint="",pre=""):
		try: ityp = {"text":0x1,"num":0x1002,"email":0x21,"pnum":0x3,"dt":0x4,"date":0x14,"time":0x24,"pass":0x81,"pin":0x12}[ityp.lower()]
		except: pass
		self.io_in(["inp_win",title,ityp,hint,pre])
		return self.io_out()
		
	def web_win(self,url="www.google.com"):
		self.io_in(["web_win",url])
		return self.io_out()
	
	def touch(self,act="click",a=(0,0),b=(0,0),dpi=500,lst=0):
		ax,ay = a
		bx,by = b
		actl = lambda ky: {"click":0x1,"long":0x2,"double":0x3,"swipe":0x4}[ky.lower()]
		if not lst: self.io_in(["touch",actl(act),ax,ay,bx,by,dpi])
		else:
			ls = []
			for y in lst: ls.append([actl(y[0]),y[1][0],y[1][1],y[2][0],y[2][1],y[3]])
			self.io_in(["touch_lst",ls])
		return self.io_out()
		
	
	#Cheaks
	def get_btry(self):
		self.io_in(["get_btry"])
		return self.io_out()
	
	def get_vol(self):
		self.io_in(["get_vol"])
		return self.io_out()
	
	def get_aux(self):
		self.io_in(["get_aux"])
		return self.io_out()
	
	def get_bt(self):
		self.io_in(["get_bt"])
		return self.io_out()
	
	def get_wifi(self):
		self.io_in(["get_wifi"])
		return self.io_out()
	
	def get_htspt(self):
		self.io_in(["get_htspt"])
		return self.io_out()
	
	def get_arpln(self):
		self.io_in(["get_arpln"])
		return self.io_out()
	
	def get_net(self):
		self.io_in(["get_net"])
		return self.io_out()
	
	def get_pwr(self):
		self.io_in(["get_bwr"])
		return self.io_out()
	
	def is_ply(self):
		self.io_in(["is_ply"])
		return self.io_out()
	
	def get_ori(self):
		self.io_in(["get_ori"])
		return self.io_out()
	
	def get_btrysv(self):
		self.io_in(["get_btrysv"])
		return self.io_out()
		
	
	#Hybrid
	def spc_rec2(self,title="",th=0.5):
		pre = self.spc_rec()
		txt,pre = pre[0],pre[-1]
		if txt:
			if pre < th: return self.inp_win(title,pre=txt),pre
			else: return txt,pre
		else: return None,None
	
	def search(self,txt,on="win"):
		url = "https://www.google.com/search?q="+txt
		if on=="chrome": self.io_in(["app_open","com.android.chrome","org.chromium.chrome.browser.document.ChromeLauncherActivity",url])
		else: self.io_in(["web_win",url])
		return self.io_out()
		
	def turn(self,sw,st="off"):
		sw_dic = {
		"net":((16,20),(28,20)),
		"wifi":((38,20),(40,20)),
		"fls":((62,20),(50,20)),
		"mute":((84,20),(60,20)),
		"bt":((38,32),(28,43)),
		"arpln":((84,32),(50,43)),
		"lock":((16,44),(60,43)),
		"gps":((38,44),(72,43)),
		"rota":((62,44),(28,20)),
		"read":((84,44),(40,20)),
		"htspt":((84,20),(28,43)),
		"btrysv":((16,20),(50,20)),
		"vib":((64,20),(72,20)),
		"scr_rec":((16,32),(40,43)),
		"gray":((38,32),(50,43))
		}
		if self.get_ori(): co,qud,c1,c2 = sw_dic[sw][0],("htspt","btrysv","vib","scr_rec","gray"),(84,32),(0,32)
		else: co,qud,c1,c2 = sw_dic[sw][1],("htspt","btrysv","vib","scr_rec","gray","rota","read"),(72,43),(28,43)
		ls = [["swipe",(50,0),(50,100),1000],["swipe",(50,0),(50,100),10000]]
		if sw in qud: ls.append(["swipe",c1,c2,10000])
		ls.append(["click",co,(0,0),10000])
		ls.extend([["swipe",(50,100),(50,0),10000],["swipe",(50,100),(50,0),10000]])
		ctl.touch(lst=ls)
		
		
ctl = control()
if __name__ == '__main__':
	ctl.turn("htspt")
	