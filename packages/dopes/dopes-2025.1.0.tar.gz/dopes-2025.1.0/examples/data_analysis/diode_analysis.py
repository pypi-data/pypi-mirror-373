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
temperature = 300 
n1 = 1
n2 = 2
Is1 = 1e-11
Is2 = 1e-6
Rs = 5
Rsh=10e4

vbias=np.linspace(-1,1,1001)

# =============================================================================
# 3. Current density calculation
# =============================================================================

Id1 = diode.ideal_diode(vbias, Is1, n=n1, temp=temperature)
Id2 = diode.ideal_diode(vbias, Is2, n=n2, temp=temperature)
Id12 = diode.two_diodes(vbias, Is1, Is2,n1 ,n2, temp=temperature)
Id12_R = diode.two_diodes_with_resistances(vbias, Is1, Is2,n1 ,n2, temp=temperature,Rs=Rs,Rsh=Rsh)

# =============================================================================
# 4. Plot
# =============================================================================

fig,ax=plt.subplots(dpi=200)
ax.set_yscale("log")
ax.set_xlabel("Vias (V)")
ax.set_ylabel("Current (A)")
ax.set_xlim((vbias[0],vbias[-1]))
ax.plot(vbias,abs(Id1),color="tab:blue",label="1 diode (Is1=%.1e A,n=%.1f)"%(Is1,n1))
ax.plot(vbias,abs(Id2),color="tab:red",label="1 diode (Is1=%.1e A,n=%.1f)"%(Is2,n2))
ax.plot(vbias,abs(Id12),color="tab:orange",label="2 diodes")
ax.plot(vbias,abs(Id12_R),color="black",label="2 diodes with R (Rs=%d $\Omega$,Rsh=%.1e $\Omega$)"%(Rs,Rsh))
ax.legend()


# =============================================================================
# 5. Example to find back the diode parameters
# =============================================================================

noise = np.random.normal(0,0.1e-6,len(Id12_R))
Id12_noise=Id12+noise



from scipy.optimize import curve_fit
def diode_current_wrapper(vbias, Is1, Is2,n1 ,n2):
    
    return diode.two_diodes(vbias, Is1, Is2,n1 ,n2, temp=300)

Is1_guess, Is2_guess, n1_guess, n2_guess=curve_fit(diode_current_wrapper,vbias,Id12_noise,p0=[1e-12,1e-6,1,2])[0]

fig,ax=plt.subplots(dpi=200)
ax.set_yscale("log")
ax.set_xlabel("Vias (V)")
ax.set_ylabel("Current (A)")
ax.set_xlim((vbias[0],vbias[-1]))
ax.plot(vbias,abs(Id12_noise),color="black")
ax.plot(vbias,abs(diode.two_diodes(vbias,Is1_guess, Is2_guess, n1_guess, n2_guess,300)),color="tab:blue")


