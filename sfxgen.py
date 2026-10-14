import numpy as np, wave, subprocess, os
SR=22050
def t(d): return np.linspace(0,d,int(SR*d),False)
def env(x,a=0.005,r=None):
    n=len(x); e=np.ones(n); na=max(1,int(a*SR)); e[:na]=np.linspace(0,1,na)
    if r: e*=np.exp(-np.arange(n)/SR/r)
    return x*e
def tone(f,d,r=0.3,w='sin'):
    x=t(d); s=np.sin(2*np.pi*f*x) if w=='sin' else np.sign(np.sin(2*np.pi*f*x))*0.5
    return env(s,r=r)
def noise(d,r=0.1): return env(np.random.randn(int(SR*d))*0.5,r=r)
def lp(x,k=8): return np.convolve(x,np.ones(k)/k,'same')
def mix(*parts):
    n=max(o+len(p) for o,p in parts); y=np.zeros(n)
    for o,p in parts: y[o:o+len(p)]+=p
    return y
def at(s): return int(s*SR)
def drum(f=60,d=0.8):
    x=t(d); fr=f*(1+1.5*np.exp(-x*25)); ph=2*np.pi*np.cumsum(fr)/SR
    return env(np.sin(ph),r=0.25)+lp(noise(d,0.03),20)*0.6
def gong(d=2.5):
    return sum(env(np.sin(2*np.pi*f*t(d)),r=d/2.5)*a for f,a in [(110,1),(167,0.6),(231,0.4),(298,.3),(415,.2)])
S={}
S['reveal']=mix((0,lp(noise(0.25,0.08),3)*0.6),(at(0.05),tone(880,0.3,0.12)*0.3))
S['resolve']=mix((0,tone(784,0.6,0.25)),(at(0.09),tone(1175,0.7,0.3)*0.7),(at(0.18),tone(1568,0.8,0.35)*0.5))
S['harsh']=mix((0,lp(noise(0.35,0.12),2)),(0,tone(140,0.4,0.15,'sq')),(at(0.05),tone(95,0.5,0.2,'sq')*0.8))
S['thud']=drum(55,0.6)
S['click']=mix((0,tone(1400,0.06,0.02)),(0,lp(noise(0.03,0.01),2)*0.4))
S['penalty']=mix((0,tone(330,0.35,0.2,'sq')),(at(0.18),tone(233,0.6,0.3,'sq')))
S['round']=mix((0,drum(70,0.9)),(at(0.25),drum(70,0.9)),(at(0.5),gong(2.0)*0.6))
S['fanfare']=mix(*[(at(i*0.16),tone(f,0.9 if i==4 else 0.3,0.4)*0.7+tone(f*2,0.9 if i==4 else 0.3,0.2)*0.2) for i,f in enumerate([523,659,784,659,1047])],(at(0.64),gong(2.0)*0.4))
S['act']=mix((0,gong(3.0)),(at(0.1),drum(50,1.0)))
S['win']=mix(*[(at(i*0.15),tone(f,0.8,0.4)) for i,f in enumerate([523,659,784,1047,1319])])
S['lose']=mix(*[(at(i*0.35),tone(f,0.9,0.4,'sq')*0.6) for i,f in enumerate([392,330,262,196])],(at(1.2),gong(2.5)*0.5))
S['dice']=mix(*[(at(i*0.07),lp(noise(0.05,0.02),2)) for i in range(6)])
S['appear']=mix((0,gong(1.6)*0.5),*[(at(0.1+i*0.08),tone(f,0.5,0.25)*0.5) for i,f in enumerate([659,784,988,1319])])
os.makedirs('sfx',exist_ok=True)
for k,y in S.items():
    y=y/np.max(np.abs(y))*0.85; d=(y*32767).astype(np.int16)
    with wave.open('/tmp/s.wav','wb') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(d.tobytes())
    subprocess.run(['ffmpeg','-y','-v','error','-i','/tmp/s.wav','-b:a','64k',f'sfx/{k}.mp3'],check=True)
print(sorted(S))
