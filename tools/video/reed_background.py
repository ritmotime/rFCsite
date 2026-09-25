"""Registered reed plate and source-frame foreground mask utility.

The current renderer calls this on real native frames before layered person
interpolation. The legacy direct composite is retained for reproducibility;
post-interpolation segmentation must not be used for the current welcome clip.
Only the bank above the shoreline is eligible for replacement.
"""
from pathlib import Path
import json
import cv2
import numpy as np

class ReedBank:
 def __init__(self,project,assets,motion):
  self.motion=motion
  project=Path(project);assets=Path(assets)
  self.plate=cv2.LUT(cv2.cvtColor(cv2.imread(str(assets/'background_plate_native.png')),cv2.COLOR_BGR2RGB),motion.LUT)
  self.transforms=np.load(assets/'registration_transforms.npz')['similarity']
  self.rows=json.loads((project/'work_v4/boat_tracking.json').read_text())['rows']
  yy,xx=np.mgrid[:self.plate.shape[0],:self.plate.shape[1]]
  y=yy.astype(np.float32)/2
  # Stop above the shoreline so oars, boat and all water stay fully dynamic.
  self.bank=(1-np.clip((y-390)/18,0,1)).astype(np.float32)
  self.bank=self.bank*self.bank*(3-2*self.bank)
 def frame(self,film,f):
  j=min(int(np.floor(f)),120);t=f-j
  M=(1-t)*self.motion.camera_matrix(j,'follow')+t*self.motion.camera_matrix(j+1,'follow')
  H=(1-t)*self.transforms[j]+t*self.transforms[j+1]
  T=np.eye(3);T[:2]=M
  warp=T@np.linalg.inv(H)@np.diag([.5,.5,1])
  bg=cv2.warpPerspective(self.plate,warp,(2130,1440),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_CONSTANT)
  bank=cv2.warpPerspective(self.bank,warp,(2130,1440),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  # Coordinates used by the existing source-frame camera are analysis pixels.
  box=(1-t)*np.array(self.rows[j]['red_shirt_bbox'],float)+t*np.array(self.rows[j+1]['red_shirt_bbox'],float)
  x,y,w,h=box
  corners=np.array([[x-35,y-120,1],[x+w+70,y+h+10,1]],float)@M.T
  x0,y0=np.floor(corners[0]).astype(int);x1,y1=np.ceil(corners[1]).astype(int)
  x0=max(0,x0);y0=max(0,y0);x1=min(2130,x1);y1=min(1440,y1)
  a=film[y0:y1,x0:x1];b=bg[y0:y1,x0:x1]
  aa=cv2.GaussianBlur(a,(0,0),1.2).astype(float);bb=cv2.GaussianBlur(b,(0,0),1.2).astype(float)
  diff=np.mean(np.abs(aa-bb),axis=2)
  candidate=(diff>23).astype(np.uint8)
  kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
  candidate=cv2.morphologyEx(candidate,cv2.MORPH_OPEN,kernel)
  candidate=cv2.morphologyEx(candidate,cv2.MORPH_CLOSE,kernel)
  num,labels,stats,_=cv2.connectedComponentsWithStats(candidate,8)
  # Retain substantial foreground structures; tiny reed-texture islands drop.
  keep=[k for k in range(1,num) if stats[k,cv2.CC_STAT_AREA]>150]
  candidate=np.isin(labels,keep).astype(np.uint8)
  gc=np.full(candidate.shape,cv2.GC_BGD,np.uint8)
  wide=cv2.dilate(candidate,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
  inside=cv2.erode(candidate,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
  gc[wide>0]=cv2.GC_PR_BGD;gc[candidate>0]=cv2.GC_PR_FGD;gc[inside>0]=cv2.GC_FGD
  # Match local person colours to a narrow boundary rather than retaining
  # the smeared/interpolated reeds that happen to border the person.
  cv2.grabCut(cv2.cvtColor(a,cv2.COLOR_RGB2BGR),gc,None,np.zeros((1,65)),np.zeros((1,65)),2,cv2.GC_INIT_WITH_MASK)
  matte=np.isin(gc,[cv2.GC_FGD,cv2.GC_PR_FGD]).astype(np.uint8)
  count,parts,areas,_=cv2.connectedComponentsWithStats(matte,8)
  if count>1:
   largest=1+int(np.argmax(areas[1:,cv2.CC_STAT_AREA]))
   matte=(parts==largest).astype(np.uint8)
  # Close only tiny internal pinholes; preserve the real space between arms.
  count,holes,areas,_=cv2.connectedComponentsWithStats(1-matte,8)
  for k in range(1,count):
   if areas[k,cv2.CC_STAT_AREA]<64:matte[holes==k]=1
  # Head colour can resemble the reeds in deep cheek/neck shadows. A small
  # closing within the head region prevents transient bites out of that edge;
  # all restored pixels still come from the existing foreground movie.
  head_end=int((M@np.array([x+w*.25,y+75,1]))[1])-y0
  head_end=max(0,min(head_end,matte.shape[0]))
  if head_end>0:
   closed=cv2.morphologyEx(matte,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15)))
   matte[:head_end]=closed[:head_end]
  matte=cv2.GaussianBlur(matte.astype(np.float32),(0,0),.65)
  alpha=np.zeros(bank.shape,np.float32);alpha[y0:y1,x0:x1]=matte
  replace=bank*(1-alpha)
  output=np.clip(np.rint(film*(1-replace[...,None])+bg*replace[...,None]),0,255).astype(np.uint8)
  return output,replace,alpha,bg

