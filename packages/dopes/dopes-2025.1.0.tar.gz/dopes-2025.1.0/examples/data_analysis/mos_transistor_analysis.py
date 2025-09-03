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
import dopes.data_analysis.data_processing as proc
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
theta=0.2

vdd=3.3

vth_n=0.8
vth_p=-0.8

vea=100

mu_n=sec.mobility_impurity(1450,carrier="n",Ni=1e18,temp=300,dopant="phosphorus")
mu_p=sec.mobility_impurity(450,carrier="p",Ni=1e18,temp=300,dopant="boron")

k_n=mu_n*1e-4*Cox*w/l
k_p=mu_p*1e-4*Cox*w/l

# =============================================================================
# 3. Generation of the current signal for an nmos transistor
# =============================================================================

vg=np.linspace(0,vdd,int(vdd*100+1))
vg_step=np.mean(vg[1:]-vg[:-1])
vs=0
vd=50e-3
ids=trans.mos_transistor_current(vg, vd,vs,vth=vth_n,k=k_n,vea=vea,theta=theta,mos_type="nmos")
noise = np.random.normal(0,0.05e-6,len(ids))
ids_noise=ids+noise
ids_smooth=proc.smooth(ids_noise,window_length=21,polyorder=3)
# =============================================================================
# 4. Calculation of the transconductance gm using finite difference derivation
# =============================================================================

gm_noise=proc.finite_difference(ids_noise, vg_step, 1,accuracy=4)
gm_ideal=proc.finite_difference(ids, vg_step, 1,accuracy=4)
gm_smooth=proc.finite_difference(ids_smooth, vg_step, 1,accuracy=4)

dn=len(vg)-len(gm_noise)

# =============================================================================
# 5. Figures
# =============================================================================

fig,ax=plt.subplots(dpi=200)
ax.set_xlabel("Vgs (V)")
ax.set_ylabel("Ids (A)")
ax.set_xlim((0,vdd))
secax=ax.twinx()
secax.set_ylabel("gm (A/V)")
ax.plot(vg-vs,ids_noise)
ax.plot(vg-vs,ids_smooth)
ax.plot(vg-vs,ids)
secax.plot(vg[int(dn/2):-int(dn/2)]-vs,gm_noise,ls="--")
secax.plot(vg[int(dn/2):-int(dn/2)]-vs,gm_smooth,ls="--")
secax.plot(vg[int(dn/2):-int(dn/2)]-vs,gm_ideal,ls="--")

# =============================================================================
# 6. Exemple to find the transistor properties
# =============================================================================

# 6.0 Definition of the bias point and the wrapper functions used in the curve fitting
vs_bias=0
vg_bias=3.3
vd_bias=50e-3

def ids_vgs_wrapper(vg,vth,k,theta):
    vd=vd_bias
    vs=vs_bias
    return trans.mos_transistor_current(vg,vd,vs,vth=vth,k=k,vea=0,theta=theta,mos_type="nmos",early=False)
from scipy.optimize import curve_fit
def ids_vds_wrapper(vd,vea):
    vg=vg_bias
    vs=vs_bias
    return trans.mos_transistor_current(vg,vd,vs,vth=vth_guess,k=k_guess,vea=vea,theta=theta_guess,mos_type="nmos",early=True)
from scipy.optimize import curve_fit


# 6.1 vg sweep for mobility, mobility degradation and threshold voltage
vg=np.linspace(0,vdd,int(vdd*100+1))
ids=trans.mos_transistor_current(vg, vd_bias,vs_bias,vth=vth_n,k=k_n,vea=vea,theta=theta,mos_type="nmos")
noise = np.random.normal(0,0.5e-6,len(ids))
ids_noise=ids+noise

vth_guess, k_guess, theta_guess=curve_fit(ids_vgs_wrapper, vg-vs_bias, ids_noise)[0]
mu_n_guess=k_guess / (Cox * w/l) * 1e4 # cm²/(V s)

fig,ax=plt.subplots(dpi=200)
ax.set_xlabel("Vgs (V)")
ax.set_ylabel("Ids (A)")
ax.set_xlim((0,vdd))
ax.plot(vg-vs,ids_noise)
ax.plot(vg-vs,ids_vgs_wrapper(vg,vth_guess, k_guess, theta_guess))



# 6.2 for the early voltage determination, a vds sweep is needed once the other parameters have been found.

vd=np.linspace(0,vdd,int(vdd*100+1))
ids=trans.mos_transistor_current(vg_bias, vd,vs_bias,vth=vth_n,k=k_n,vea=vea,theta=theta,mos_type="nmos")
noise = np.random.normal(0,1e-6,len(ids))
ids_noise=ids+noise

vea_guess=curve_fit(ids_vds_wrapper, vd-vs_bias, ids_noise)[0][0]

fig,ax=plt.subplots(dpi=200)
ax.set_xlabel("Vds (V)")
ax.set_ylabel("Ids (A)")
ax.set_xlim((0,vdd))
ax.plot(vd-vs,ids_noise)
ax.plot(vd-vs,ids_vds_wrapper(vd, vea_guess))

plt.show()