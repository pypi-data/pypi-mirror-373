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

import dopes.data_analysis.diode as diode
import dopes.data_analysis.semiconductor as sc
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 2. Variables
# =============================================================================

w = 100 # µm
d = 0.3 # µm
lp = 15 # µm
ln = 15 # µm
ND = 1e19 # cm-3
NA = 1e18 # cm-3
mu_n0 = 1450 # cm2 / V s
mu_p0 = 450 # cm2 / V s
tau_n0 = 1e-5 # s 
tau_p0 = 1e-5 # s
temperature = 300 # K

vbias=np.linspace(-1,1,1001)

# =============================================================================
# 2. Current density calculation
# =============================================================================


tau_n = sc.tau_srh(Ni=ND,tau_0=tau_n0)
tau_p = sc.tau_srh(Ni=NA,tau_0=tau_p0)

mu_n=sc.mobility_impurity(mu_n0,Ni=ND,carrier="n",temp=temperature,dopant="phosphorus")
mu_p=sc.mobility_impurity(mu_p0,Ni=NA,carrier="p",temp=temperature,dopant="boron")


tau= 1 / (1/tau_n + 1/tau_p)


isrh=w*d*diode.j_srh(vbias,ND=ND,NA=NA,tau=tau,temp=temperature)
irad=w*d*diode.j_radiative(vbias,mu_n,mu_p,tau_n,tau_p,ND,NA,ln,lp,temp=temperature)

# =============================================================================
# 3. Plot
# =============================================================================

fig,ax=plt.subplots(dpi=200)
ax.set_yscale("log")
ax.set_xlabel("Vias (V)")
ax.set_ylabel("Current (A)")
ax.set_xlim((vbias[0],vbias[-1]))
ax.plot(vbias,abs(irad),color="tab:blue",label="SRH")
ax.plot(vbias,abs(isrh),color="tab:red",label="Radiative")
ax.plot(vbias,abs(isrh+irad),color="black",label="SRH + Radiative")
ax.legend()

plt.show()