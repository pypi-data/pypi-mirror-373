# =============================================================================
# 1. Import classes and modules
# =============================================================================


# =============================================================================
# #If local installation of dopes instead of using PyPI (https://pypi.org/project/dopes/)
# import sys
# important_path = 'D:\\Roisin\\Documents\\dopes'        
# if important_path not in sys.path:
#     sys.path.insert(0, important_path)
# =============================================================================

import dopes.data_analysis.transistor as trans
import dopes.data_analysis.semiconductor as sec
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 2. Variables
# =============================================================================

w = 10 # µm
l = 3# µm
tox=25e-9
epsilon_r=11.7
epsilon0=8.85e-12
Cox=epsilon_r*epsilon0/tox

vdd=3.3

vth_n=0.8
vth_p=-0.8

vea=100

mu_n=sec.mobility_impurity(1450,carrier="n",Ni=1e18,temp=300,dopant="phosphorus")
mu_p=sec.mobility_impurity(450,carrier="p",Ni=1e18,temp=300,dopant="boron")

k_n=mu_n*1e-4*Cox*w/l
k_p=mu_p*1e-4*Cox*w/l

# =============================================================================
# 3. Id-Vg Transistor curves
# =============================================================================
vg=np.linspace(0,vdd,int(vdd*100+1))
vs_n=0
vs_p=vdd
vd_list=np.linspace(0,vdd,11)

# NMOS
fig,ax=plt.subplots(dpi=200)
ax.set_xlabel("Vgs (V)")
ax.set_ylabel("Ids (A)")
ax.set_xlim((0,vdd))
for vd in vd_list:
    ids=trans.mos_transistor_current(vg, vd,vs_n,vth=vth_n,k=k_n,vea=vea,mos_type="nmos")
    ax.plot(vg-vs_n,ids)
   
# PMOS
fig,ax=plt.subplots(dpi=200)
ax.set_xlabel("Vsg (V)")
ax.set_ylabel("Isd (A)")
ax.set_xlim((0,vdd))
for vd in vd_list:
    isd=trans.mos_transistor_current(vg, vd,vs_p,vth=vth_p,k=k_p,vea=vea,mos_type="pmos")
    ax.plot(vs_p-vg,isd)

# =============================================================================
# 3. Id-Vs Transistor curves
# =============================================================================
vd=np.linspace(0,vdd,int(vdd*100+1))
vs_n=0
vs_p=vdd
vg_list=np.linspace(0,vdd,11)

# NMOS
fig,ax=plt.subplots(dpi=200)
ax.set_xlabel("Vgs (V)")
ax.set_ylabel("Ids (A)")
ax.set_xlim((0,vdd))
for vg in vg_list:
    ids=trans.mos_transistor_current(vg, vd,vs_n,vth=vth_n,k=k_n,vea=vea,mos_type="nmos")
    ax.plot(vd-vs_n,ids)

# PMOS
fig,ax=plt.subplots(dpi=200)
ax.set_xlabel("Vsg (V)")
ax.set_ylabel("Isd (A)")
ax.set_xlim((0,vdd))
for vg in vg_list:
    isd=trans.mos_transistor_current(vg, vd,vs_p,vth=vth_p,k=k_p,vea=vea,mos_type="pmos")
    ax.plot(vs_p-vd,isd)
    
plt.show()