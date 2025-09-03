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

import numpy as np
import matplotlib.pyplot as plt

import dopes.data_analysis.raman as ram
import dopes.data_analysis.mechanics as mec


# =============================================================================
# 2. Specify the strain to be studied
# =============================================================================

strain_type="uniaxial"
strain_direction="001"
N=11 
emin=-1000e-6
emax=1000e-6
strain_principal=np.linspace(emin,emax,N)

strain_matrix=mec.straintensor(strain_type,strain_direction,N=N,emin=emin,emax=emax)

# =============================================================================
# 2. Calculate the raman shift of the three modes in silicon (LO, TO1 and TO2)
# =============================================================================
omega=np.zeros((N,3))

# Phonon deformation potential from Peng et al. (2009), the units are in omega_0**-2 (omega_0 = 520.7 cm-1 for silicon)
p = -1.56
q = -1.98
r = -0.96

for i in range(N):
    omega[i,:]=ram.phonon_deformation_silicon(strain_matrix[:,:,i], p, q, r,w0=520.7)

fig,ax=plt.subplots()
fig.set_dpi(200)
ax.set_title("[%s] %s strain"%(strain_direction,strain_type))
ax.set_xlim((strain_principal[0]*1e6,strain_principal[-1]*1e6))
ax.set_xlabel("Strain (ppm)")
ax.set_ylabel("Peak position (cm$^{-1}$)")
ax.plot(strain_principal*1e6,omega[:,0],color="tab:blue")    
ax.plot(strain_principal*1e6,omega[:,1],color="tab:red")    
ax.plot(strain_principal*1e6,omega[:,2],color="tab:orange")

# =============================================================================
# 3. Comparison between the PDP found in literature
# =============================================================================


pqr_list=np.array([[-1.25,-1.87,-0.66], # Anastassakis et al. (1970)
                [-1.49,-1.97,-0.61], # Chandrasekhar et al. (1978)
                [-1.63,-1.89,-0.6], # Nielsen et Martin (1985)
                [-1.85,-2.31,-0.71], # Anastassakis et al. (1990)
                [-1.56,-1.98,-0.96] # Peng et al. (2009)
                ])

omega=np.zeros((N,3,len(pqr_list)))
i=0
for j in range(len(pqr_list)):
    for i in range(N):
        p,q,r= pqr_list[j]
        omega[i,:,j]=ram.phonon_deformation_silicon(strain_matrix[:,:,i], p, q, r,w0=520.7)

fig,ax=plt.subplots()
fig.set_dpi(200)
ax.set_title("[%s] %s strain"%(strain_direction,strain_type))
ax.set_xlim((strain_principal[0]*1e6,strain_principal[-1]*1e6))
ax.set_xlabel("Strain (ppm)")
ax.set_ylabel("Peak position (cm$^{-1}$)")
for j in range(len(pqr_list)):
    ax.plot(strain_principal*1e6,omega[:,0,j],color="tab:blue")    
    ax.plot(strain_principal*1e6,omega[:,1,j],color="tab:red")    
    ax.plot(strain_principal*1e6,omega[:,2,j],color="tab:orange")
    

plt.show()