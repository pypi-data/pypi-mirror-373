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

import dopes.data_analysis.semiconductor as sc
import dopes.data_analysis.mechanics as mec
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# 2. Specify the strain to be studied
# =============================================================================

strain_type="uniaxial"
strain_direction="001"
long_direction=np.array([0,0,1])
trans_direction=np.array([0,1,0])

N=11 
emin=-1000e-6
emax=1000e-6
strain_principal=np.linspace(emin,emax,N)

strain_matrix=mec.straintensor(strain_type,strain_direction,N=N,emin=emin,emax=emax)

# =============================================================================
# 3. Calculate the mobility variations of undoped strained silicon
# =============================================================================

temperature = 300
piezo_ratio_n = sc.piezo_ratio_temperature(temperature,carrier="n")
piezo_ratio_p = sc.piezo_ratio_temperature(temperature,carrier="p")


pi11_n = -1022 * 1e-3 * piezo_ratio_n
pi12_n = 534 * 1e-3 * piezo_ratio_n
pi44_n = -136 * 1e-3 * piezo_ratio_n
pi11_p = 66 * 1e-3 * piezo_ratio_p
pi12_p = -11 * 1e-3 * piezo_ratio_p
pi44_p = 1381 * 1e-3 * piezo_ratio_p



resistivity_n_tensor=np.zeros((3,3,N))
resistivity_p_tensor=np.zeros((3,3,N))
for i in range(N):
    resistivity_n_voigt=sc.piezoresistivity_strain(strain_matrix[:,:,i],pi11_n,pi12_n,pi44_n)
    resistivity_p_voigt=sc.piezoresistivity_strain(strain_matrix[:,:,i],pi11_n,pi12_n,pi44_n)
    resistivity_n_tensor[:,:,i]=mec.voigt_to_matrix(resistivity_n_voigt)
    resistivity_p_tensor[:,:,i]=mec.voigt_to_matrix(resistivity_p_voigt)
    
    
# Klassen (1991) temperature model for the majority mobility
mu_n0 = 1417 * (temperature/300)**2.285
mu_p0 = 470.5 * (temperature/300)**2.247

mu_n_tensor=-resistivity_n_tensor * mu_n0 + mu_n0
mu_p_tensor=-resistivity_p_tensor * mu_p0 + mu_p0
    
mu_n_long = np.array([long_direction @ mu_n_tensor[:,:,i] @ np.transpose(long_direction) for i in range(N)])
mu_n_trans = np.array([trans_direction @ mu_n_tensor[:,:,i] @ np.transpose(trans_direction) for i in range(N)])

mu_p_long = np.array([long_direction @ mu_p_tensor[:,:,i] @ np.transpose(long_direction) for i in range(N)])
mu_p_trans = np.array([trans_direction @ mu_p_tensor[:,:,i] @ np.transpose(trans_direction) for i in range(N)])

fig,ax=plt.subplots(dpi=200)
ax.set_title("Temperature : %d K"%temperature)
ax.set_ylabel("Mobility (cm²/(V.s))")
ax.set_xlabel("[%s] %s strain (ppm)"%(strain_direction,strain_type))
ax.set_xlim((strain_principal[0]*1e6,strain_principal[-1]*1e6))
ax.plot(strain_principal*1e6,mu_n_long,color="tab:blue",label="long. (n)")
ax.plot(strain_principal*1e6,mu_n_trans,color="tab:red",label="trans. (n)")
ax.plot(strain_principal*1e6,mu_p_long,color="tab:green",label="long. (p)")
ax.plot(strain_principal*1e6,mu_p_trans,color="tab:orange",label="trans. (p)")
ax.legend(ncols=2)

# =============================================================================
# 4. Calculate the mobility variations of doped strained silicon
# =============================================================================
impurity_level=1e17

mu_n_long_doped=sc.mobility_impurity(mu_n_long,carrier='n',Ni=impurity_level,temp=temperature,dopant="phosphorus")
mu_n_trans_doped=sc.mobility_impurity(mu_n_trans,carrier='n',Ni=impurity_level,temp=temperature,dopant="phosphorus")
mu_p_long_doped=sc.mobility_impurity(mu_p_long,carrier='p',Ni=impurity_level,temp=temperature,dopant="boron")
mu_p_trans_doped=sc.mobility_impurity(mu_p_trans,carrier='p',Ni=impurity_level,temp=temperature,dopant="boron")

fig,ax=plt.subplots(dpi=200)
ax.set_title("Temperature : %d K - Impurity : %.1e cm-3"%(temperature,impurity_level))
ax.set_ylabel("Mobility (cm²/(V.s))")
ax.set_xlabel("[%s] %s strain (ppm)"%(strain_direction,strain_type))
ax.set_xlim((strain_principal[0]*1e6,strain_principal[-1]*1e6))
ax.plot(strain_principal*1e6,mu_n_long,ls=":",color="tab:blue",label="undoped")
ax.plot(strain_principal*1e6,mu_n_trans,ls=":",color="tab:red")
ax.plot(strain_principal*1e6,mu_p_long,ls=":",color="tab:green")
ax.plot(strain_principal*1e6,mu_p_trans,ls=":",color="tab:orange")
ax.plot(strain_principal*1e6,mu_n_long_doped,color="tab:blue",label="long. (n)")
ax.plot(strain_principal*1e6,mu_n_trans_doped,color="tab:red",label="trans. (n)")
ax.plot(strain_principal*1e6,mu_p_long_doped,color="tab:green",label="long. (p)")
ax.plot(strain_principal*1e6,mu_p_trans_doped,color="tab:orange",label="trans. (p)")

ax.legend(ncols=2)


plt.show()
