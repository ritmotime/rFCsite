"""Interpolate observed foreground separately from the registered reed bank.

Native person masks are repaired before any optical flow. Premultiplied RGB
and alpha share a single motion field. Robust source-feature motion controls
the silhouette; dense motion handles the interior. Water keeps its existing
motion interpolation. No generated scenery or post-interpolation segmentation.
"""
from pathlib import Path
from functools import lru_cache
import cv2,numpy as np,sys,json
from reed_background import ReedBank
from native_person_matte import improve_native_alpha

def remap(img,xy):
 return cv2.remap(img,xy[...,0],xy[...,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)

class PersonPair:
 def __init__(self,a,aa,b,ba,head_end_a,head_end_b):
  self.a=a.astype(np.float32)*aa[...,None];self.aa=aa
  self.b=b.astype(np.float32)*ba[...,None];self.ba=ba
  yy,xx=np.mgrid[:a.shape[0],:a.shape[1]];self.grid=np.stack([xx,yy],-1).astype(np.float32)
  ga=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY);gb=cv2.cvtColor(b,cv2.COLOR_RGB2GRAY)
  ga=np.rint(ga*aa).astype('uint8');gb=np.rint(gb*ba).astype('uint8')
  A,HA,diag=self.affine(ga,gb,aa,ba,head_end_a,head_end_b)
  B=cv2.invertAffineTransform(A);HB=cv2.invertAffineTransform(HA)
  self.diag=diag
  dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
  f=dis.calc(ga,gb,None)
  dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
  bw=dis.calc(gb,ga,None)
  self.f=self.constrain(f,aa,A,HA,head_end_a)
  self.bw=self.constrain(bw,ba,B,HB,head_end_b)
 def affine(self,ga,gb,aa,ba,heada,headb):
  mask=cv2.erode((aa>.995).astype('uint8'),np.ones((13,13),np.uint8))*255
  mask[750:]=0
  p=cv2.goodFeaturesToTrack(ga,700,.006,5,mask=mask,blockSize=5)
  q,status,err=cv2.calcOpticalFlowPyrLK(ga,gb,p,None,winSize=(21,21),maxLevel=4,criteria=(3,40,.001))
  back,status2,err2=cv2.calcOpticalFlowPyrLK(gb,ga,q,None,winSize=(21,21),maxLevel=4,criteria=(3,40,.001))
  x=np.clip(np.rint(q[:,0,0]).astype(int),0,ba.shape[1]-1);y=np.clip(np.rint(q[:,0,1]).astype(int),0,ba.shape[0]-1)
  good=(status[:,0]>0)&(status2[:,0]>0)&(np.linalg.norm(back[:,0]-p[:,0],axis=1)<.9)&(err[:,0]<24)&(ba[y,x]>.99)
  src=p[good,0];dst=q[good,0]
  A,inliers=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=1.5,refineIters=20)
  if A is None:raise RuntimeError('No person motion fit')
  head=(src[:,1]<heada)&(dst[:,1]<headb)
  HA,hi=cv2.estimateAffinePartial2D(src[head],dst[head],method=cv2.RANSAC,ransacReprojThreshold=1.1,refineIters=20) if head.sum()>=8 else (None,None)
  if HA is None:HA=A
  e=np.linalg.norm((np.c_[src,np.ones(len(src))]@A.T)-dst,axis=1)
  return A,HA,{'person_points':len(src),'inliers':int(inliers.sum()),'median_inlier_error':float(np.median(e[inliers[:,0]>0])),'head_points':int(head.sum())}
 def field(self,A):
  return self.grid@A[:,:2].T+A[:,2]-self.grid
 def constrain(self,f,alpha,A,HA,headend):
  base=self.field(A);head=self.field(HA)
  h=np.clip((headend+8-self.grid[...,1])/16,0,1)[...,None]
  base=base*(1-h)+head*h
  dist=cv2.distanceTransform((alpha>.5).astype('uint8'),cv2.DIST_L2,5)
  # Use robust rigid tracking at the silhouette, never the background flow.
  weight=np.clip((dist-5)/18,0,1)[...,None]
  # Reject large local flow departures even inside poorly textured clothing.
  delta=np.linalg.norm(f-base,axis=2)
  weight=weight*np.clip((18-delta)/10,0,1)[...,None]
  return (base*(1-weight)+f*weight).astype(np.float32)
 def inverse(self,flow,t):
  xy=self.grid-t*flow
  for _ in range(3):xy=.5*(xy+self.grid-t*remap(flow,xy))
  return xy.astype(np.float32)
 def frame(self,t):
  qa=self.inverse(self.f,t);qb=self.inverse(self.bw,1-t)
  premul=(1-t)*remap(self.a,qa)+t*remap(self.b,qb)
  alpha=(1-t)*remap(self.aa,qa)+t*remap(self.ba,qb)
  return premul,np.clip(alpha,0,1)

class LayeredPerson:
 def __init__(self, project, background, motion, last=121):
  self.motion=motion
  self.last=int(last)
  self.bank=ReedBank(Path(project),Path(background),motion)
 @lru_cache(maxsize=3)
 def native(self,j):
  film,M=self.motion.get_film(j,'follow');out,rep,alpha,bg=self.bank.frame(film,j)
  alpha=improve_native_alpha(film,alpha,j,self.bank,self.motion)
  x,y,w,h=self.bank.rows[j]['red_shirt_bbox']
  headend=(M@np.array([x+w*.25,y+75,1]))[1]
  return film,alpha,headend
 @lru_cache(maxsize=1)
 def pair(self,j):
  a,aa,heada=self.native(j);b,ba,headb=self.native(j+1)
  return PersonPair(a,aa,b,ba,heada,headb)
 def background(self,f):
  j=min(int(f),self.last-1);t=f-j
  M=(1-t)*self.motion.camera_matrix(j,'follow')+t*self.motion.camera_matrix(j+1,'follow')
  H=(1-t)*self.bank.transforms[j]+t*self.bank.transforms[j+1]
  T=np.eye(3);T[:2]=M
  warp=T@np.linalg.inv(H)@np.diag([.5,.5,1])
  bg=cv2.warpPerspective(self.bank.plate,warp,(2130,1440),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_CONSTANT)
  bank=cv2.warpPerspective(self.bank.bank,warp,(2130,1440),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  return bg,bank
 def frame(self,base,f):
  j=min(int(f),self.last-1);t=f-j;pair=self.pair(j)
  foreground,alpha=pair.frame(t);bg,bank=self.background(f)
  composite=foreground+bg*(1-alpha[...,None])
  out=np.clip(np.rint(composite*bank[...,None]+base*(1-bank[...,None])),0,255).astype('uint8')
  return out,alpha,pair.diag

