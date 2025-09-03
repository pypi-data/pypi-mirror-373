
# =============================================================================
# 1. Import classes and modules
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt

from tmm import *
from tmm.tmm_core import (coh_tmm, unpolarized_RT, ellips,
                       position_resolved, find_in_structure_with_inf)

from scipy.interpolate import interp1d



# =============================================================================
# 2. Each material layer is an object
# =============================================================================


class layer:
    def __init__(self):
        self.thickness=inf
        self.coherence="i"
        self.n=1
        self.k=0
       
    def add_n(self,wn,n):
        self.n=n
        self.wn=wn

    def add_k(self,wk,k):
        self.k=k
        self.wk=wk

    def add_thickness(self,thickness):
        self.thickness=thickness

    def add_coherence(self,coherence):
        self.coherence=coherence

    def nk_from_csv(self,path,nk="both"):
        data=np.loadtxt(path,skiprows=1,delimiter=";")
        if nk=="both":
            self.wn=data[:,0]
            self.wk=data[:,0]
            self.n=data[:,1]
            self.k=data[:,2]
        if nk=="n":
            self.wn=data[:,0]
            self.n=data[:,1]
        if nk=="k":
            self.wk=data[:,0]
            self.k=data[:,1]

    def nk_interp(self,w_interp):
        try:
            n_fn = interp1d(self.wn,self.n,kind="quadratic")    
            k_fn = interp1d(self.wk,self.k,kind="linear")  
            n_interp = n_fn(w_interp)
            k_interp = k_fn(w_interp)
        except AttributeError:
            n_interp = self.n
            k_interp = self.k
        return n_interp, k_interp

    def n_complex_interp(self,w_interp):
        try:
            n_fn = interp1d(self.wn,self.n,kind="quadratic")    
            k_fn = interp1d(self.wk,self.k,kind="linear")  
            n_interp = n_fn(w_interp)
            k_interp = k_fn(w_interp)
        except AttributeError:
            n_interp = self.n
            k_interp = self.k
        return n_interp + 1j*k_interp

# =============================================================================
# 3. Functions of transmission and reflection calculation
# =============================================================================


def TR(layer_list,lambda_list,theta_0,p="s"):
    T_list = []
    R_list = []
    d_list = []
    c_list = []

    for layer_i in stack:
        d_list.append(layer_i.thickness)
        c_list.append(layer_i.coherence)

    for lambda_vac in lambda_list:
        
        n_list = []
        for layer_i in stack:
            n_list.append(layer_i.n_complex_interp(lambda_vac))
        
        T_list.append(inc_tmm(p, n_list, d_list,c_list, theta_0/180*np.pi, lambda_vac)['T'])
        R_list.append(inc_tmm(p, n_list, d_list,c_list, theta_0/180*np.pi, lambda_vac)['R'])

    return np.array(T_list), np.array(R_list)

def TR_theta(layer_list,lambda_vac,theta_list,p="s"):
    T_list = []
    R_list = []
    d_list = []
    c_list = []
    n_list = []

    for layer_i in stack:
        d_list.append(layer_i.thickness)
        c_list.append(layer_i.coherence)
        n_list.append(layer_i.n_complex_interp(lambda_vac))

    for theta_0 in theta_list:
        
        
        T_list.append(inc_tmm(p, n_list, d_list,c_list, theta_0/180*np.pi, lambda_vac)['T'])
        R_list.append(inc_tmm(p, n_list, d_list,c_list, theta_0/180*np.pi, lambda_vac)['R'])

    return np.array(T_list), np.array(R_list)

# =============================================================================
# 4. Material definition
# =============================================================================

# 4.1 material instantiation

air=layer()
si=layer()
metal=layer()
antireflective=layer()

metal.n=0.05
antireflective.n=2.0

# 4.2 nk definition

si.nk_from_csv("data/silicon_green2008.csv")


# =============================================================================
# 5. Transmission/reflection of a single silicon layer
# =============================================================================


lambda_list = np.linspace(0.5, 1.1, 201) # wavelength in µm
theta=0 # incident angle for the light in degree
si_thickness=10 #in µm

# Stack and thickness definition in µm if wavelength in µm
stack=[air,si,air]
thickness_list=[inf,si_thickness,inf] 
coherence_list=["i","i","i"] # "c" for coherent, "i" for incoherent

i=0
for layer_i in stack:
    layer_i.add_thickness(thickness_list[i])
    layer_i.add_coherence(coherence_list[i])
    i+=1
    
T, R = TR(stack,lambda_list,theta_0=theta,p="s")

fig,ax=plt.subplots()
ax.set_xlabel('Wavelength (µm)')
ax.set_ylabel('Power ratio (%)')
ax.set_xlim(lambda_list[0],lambda_list[-1])
ax.set_ylim(0,100)
ax.set_xticks(np.linspace(lambda_list[0],lambda_list[-1],5))
ax.plot(lambda_list, (1-T-R)*1e2,zorder=10,clip_on=False,label="absorption")
ax.plot(lambda_list, T*1e2,zorder=10,clip_on=False,label="transmission")
ax.plot(lambda_list, R*1e2,zorder=10,clip_on=False,label="reflection")
ax.legend()

# ==================================================================================================
# 6. Transmission/reflection of a single silicon layer with antireflective coating and metal layer
# ===================================================================================================


lambda_list = np.linspace(0.5, 1.1, 201) # wavelength in µm
theta=0 # incident angle for the light in degree
si_thickness=10 #in µm
antireflective_thickness=0.125 #in µm
metal_thickness=0.2 #in µm


# Stack and thickness definition in µm if wavelength in µm
stack=[air,antireflective,si,metal,air]
thickness_list=[inf,antireflective_thickness,si_thickness,metal_thickness,inf] 
coherence_list=["i","c","i","i","i"] # "c" for coherent, "i" for incoherent

i=0
for layer_i in stack:
    layer_i.add_thickness(thickness_list[i])
    layer_i.add_coherence(coherence_list[i])
    i+=1
  
T, R = TR(stack,lambda_list,theta_0=theta,p="s")

fig,ax=plt.subplots()
ax.set_xlabel('Wavelength (µm)')
ax.set_ylabel('Power ratio (%)')
ax.set_xlim(lambda_list[0],lambda_list[-1])
ax.set_ylim(0,100)
ax.set_xticks(np.linspace(lambda_list[0],lambda_list[-1],5))
ax.plot(lambda_list, (1-T-R)*1e2,zorder=10,clip_on=False,label="absorption")
ax.plot(lambda_list, T*1e2,zorder=10,clip_on=False,label="transmission")
ax.plot(lambda_list, R*1e2,zorder=10,clip_on=False,label="reflection")
ax.legend()

plt.show()