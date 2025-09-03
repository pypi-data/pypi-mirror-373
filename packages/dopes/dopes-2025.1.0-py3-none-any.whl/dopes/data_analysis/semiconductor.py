import numpy as np
import dopes.data_analysis.mechanics as mec
import scipy.interpolate as interp

def mobility_impurity(mu_0,carrier="n",Ni=1e15,temp=300, dopant="phosphorus"):
    """ Function to calculate the silicon mobility according to Masetti relation (1983)
    
        args:
           \n\t- carrier (string): "n" for electrons, "p" for holes
           \n\t- temp (scalar): the temperature 
           \n\t- Ni (scalar): the impurity cencentration in cm-3
           \n\t- dopant (string): the type of n-type dopant. "phosphorus" or "arsenic"
            
        return:
           \n\t- mu_LI (scalar): the electron or hole mobility with the impurity scattering taken into account
    """  
    
    # Values are taken from Masetti et al. (1983)
    if dopant=="phosphorus":
        param_300_n={"mu_min":68.5,"Cref":9.20e16,"alpha":0.711} 
        correction_n={"mu_min":56.1,"Cref":3.41e20,"alpha":1.98} 
        # mu_0=1414
    elif dopant=="arsenic":
        param_300_n={"mu_min":52.2,"Cref":9.68e16,"alpha":0.680} 
        correction_n={"mu_min":43.4,"Cref":3.43e20,"alpha":2.00} 
        # mu_0=1417

    param_300_p={"mu_min":44.9,"Cref":22.3e16,"alpha":0.72}
    correction_p={"mu_min":29.0,"Cref":6.1e20,"alpha":2.0}
    
    expon_temp={"mu_min":-0.45,"Cref":3.2,"alpha":0.065}
     
    if carrier=="n":
        param_300=param_300_n
        correction=correction_n["mu_min"]/(1+(correction_n["Cref"]/Ni)**correction_n["alpha"])
    else:
        param_300=param_300_p
        correction=correction_p["mu_min"]/(1+(correction_p["Cref"]/Ni)**correction_p["alpha"])
        # mu_0=470.5


    mu_min=param_300["mu_min"]*(temp/300)**expon_temp["mu_min"]
    Cref=param_300["Cref"]*(temp/300)**expon_temp["Cref"]
    alpha=param_300["alpha"]*(temp/300)**expon_temp["alpha"]
    
    mu_LI=mu_min+(mu_0-mu_min) / ( 1 + ( Ni / Cref )**alpha )-correction
    
    return mu_LI

def intrinsic_concentration(temp):
    """ Function to calculate the intrinsic concentration of silicon from K. Misiakos and Tsamakis, D., “Accurate measurements of the silicon intrinsic carrier density from 78 to 340 K”, Journal of Applied Physics, vol. 74, no. 5, p. 3293, 1993.
    
        args:
           \n\t- temp (scalar): the temperature 
            
        return:
           \n\t- ni (scalar): the intrinsic concentration in silicon
    """  
    
    return 5.29e19 * (temp/300)**2.54 * np.exp(-6726/temp)


def tau_srh(Ni, tau_0=5e-5,  Nc=5e16, A=1, B=1, C=0, E=0):
    """ Function to calculate the SRH lifetime of silicon. The default parameters, similar for electron and hole, are those from D'Avanzo, D. C., Vanzi, M., Dutton, R. W.: One-Dimensional Semiconductor Device Analysis
        (SEDAN). Report G-201-5, Stanford University, 1979.
        
        args:
           \n\t- Ni (scalar): the impurity density in the material 
           \n\t- tau_0 (scalar): intial value for the lifetime 
           \n\t- Nc (scalar): the critical impurity level 
           \n\t- A, B, C and D (scalar): the coefficient for the model 
            
        return:
           \n\t- the SRH lifetime in silicon
    """  
    
    return tau_0/(A+B*(Ni/Nc)+C*(Ni/Nc)**E)

def tau_trap(tau_n, tau_p, NA, ND, Etrap=0.56,Eg=1.12, temp=300):
    """ Function to calculate the lifetime of silicon due to a trap.
        
        args:
           \n\t- tau_n and tau_p (scalar): the life time of the electron and hole due to the trap density. 
              The lifetime can be calculated by tau_n = 1 / (sigma_n * v_th * Nt ) where sigma_n is the capture cross section, vth is the thermal velocity and Nt is the trap density. 
              Typical values for the thermal velocities are 2.3e7 and 1.65e7 cm/s for the electrons and holes, respectively. 
              Typical value for the capture cross section is 1e-15 cm² for a neutral defect. 
              Typical value for the trap density is 1e12 cm-3 for a neutral defect.  
           \n\t- NA and ND (scalar): the acceptor and donor density of the pn junction 
           \n\t- Etrap (scalar): the trap level referred to the maximum of the valence band 
           \n\t- Eg (scalar): the bandgap of the material 
           \n\t- temp (scalar): the temperature 
            
        return:
           \n\t- the trap lifetime 
    """  
    kB = 1.38e-23 # J/K
    q = 1.602e-19 # C
    
    nieff=intrinsic_concentration(temp)
    
    n_0 = nieff**2 / NA
    p_0 = nieff**2 / ND
    n1 = nieff * np.exp(- q * (Eg - Etrap) / (kB*temp))
    p1 = nieff * np.exp(- q * Etrap / (kB*temp))
    
    return (tau_p * (n_0 + n1) + tau_n * (p_0 + p1)) / (p_0 + n_0)

    
def piezoresistivity_stress(stress_tensor, pi11, pi12, pi44):
    """ Function to calculate the relative change due to stress in silicon
        
        args:
           \n\t- stress_tensor (numpy array): the stress tensor for which the stress should be calculated. The voigt notation should be used with a 1 x 6 vector but the function can handle  3 x 3 matrix but only take the upper half in this case.
           \n\t- pi11, pi12 and pi44 (scalar): piezoresistive coefficients used to calculate the variations in the relative resistivity. 
              Values from Smith (1954) are pi11 = -1022 TPa-1, pi12 = 534 TPa-1 and pi44 = -136 TPa-1 for the electrons,
              and pi11 = 66 TPa-1, pi12 = -11 TPa-1 and pi44 = 1381 TPa-1 for the holes.
                
        return:
           \n\t- an 1 x 6 tensor using the Voigt notation with the relative variation of the resistivity.
    """  
    
    stress_voigt=np.zeros((6,1))
    stress_shape=np.shape(stress_tensor)
    
    if len(stress_shape)==2:
        if stress_shape[0]==3 and stress_shape[1]==3:
            stress_voigt[0]=stress_tensor[0,0]
            stress_voigt[1]=stress_tensor[1,1]
            stress_voigt[2]=stress_tensor[2,2]
            stress_voigt[3]=stress_tensor[1,2]
            stress_voigt[4]=stress_tensor[0,2]
            stress_voigt[5]=stress_tensor[0,1]
        if stress_shape[0]==1 and stress_shape[1]==6:
            stress_voigt=stress_tensor
    else:
        stress_voigt=np.array([stress_tensor])
    
    piezo_tensor=np.array([[pi11,pi12,pi12,0,0,0],
                                [pi12,pi11,pi12,0,0,0],
                                [pi12,pi12,pi11,0,0,0],
                                [0,0,0,pi44,0,0],
                                [0,0,0,0,pi44,0],
                                [0,0,0,0,0,pi44]])
    
    return piezo_tensor @ stress_voigt
    
def piezoresistivity_strain(strain_tensor, pi11, pi12, pi44):
    """ Function to calculate the relative change due to stress in silicon
        
        args:
           \n\t- stress_tensor (numpy array): the stress tensor for which the stress should be calculated. The voigt notation should be used with a 1 x 6 vector but the function can handle  3 x 3 matrix but only take the upper half in this case.
           \n\t- pi11, pi12 and pi44 (scalar): piezoresistive coefficients used to calculate the variations in the relative resistivity. 
              Values from Smith (1954) are pi11 = -1022 TPa-1, pi12 = 534 TPa-1 and pi44 = -136 TPa-1 for the electrons,
              and pi11 = 66 TPa-1, pi12 = -11 TPa-1 and pi44 = 1381 TPa-1 for the holes.
                
        return:
           \n\t- an 1 x 6 tensor using the Voigt notation with the relative variation of the resistivity.
    """  

    piezo_tensor=np.array([[pi11,pi12,pi12,0,0,0],
                                [pi12,pi11,pi12,0,0,0],
                                [pi12,pi12,pi11,0,0,0],
                                [0,0,0,pi44,0,0],
                                [0,0,0,0,pi44,0],
                                [0,0,0,0,0,pi44]])
    
    stress_tensor= mec.stress_from_strain(strain_tensor)
    
    return piezo_tensor @ stress_tensor

def piezo_ratio_temperature(temp,carrier="n"):
    """ Function to calculate the correcting ratio due to temperature variations for the piezoresistive coefficients. The data are taken from Kanda (1982) between 200 K and 400K.
        The correction is refered to the 300K coefficients. The new piezoresistive coefficients can be calculated by piezo_coefficient(temp) = ratio * piezo_coefficient(300K)
        
        args:
           \n\t- temp (scalar or sequence): the temperatures for which the correting ratio has to be calculated
           \n\t- carrier (string): "n" for electrons, "p" for holes
                
        return:
           \n\t- a scalar or sequence with the same dimension as temp with the correcting ratio
    """  

    temp_kanda1982=np.linspace(125, -75,9)+273
    dpi_kanda1982_n=np.array([0.7547318611987381,0.8067823343848579,0.8611987381703468,0.9298107255520504,1.0007886435331228,1.0977917981072554,1.2113564668769716,1.3438485804416402,1.5165615141955835])
    dpi_kanda1982_p=np.array([0.7523342983957861,0.8037360206464299,0.8598127702627387,0.922894558591104,0.995324258126102,1.0934548187864221,1.205601887444947,1.3411219494071012,1.5093457676819353])
    
    fn=interp.interp1d(temp_kanda1982,dpi_kanda1982_n,kind="linear",fill_value="extrapolate" )
    fp=interp.interp1d(temp_kanda1982,dpi_kanda1982_p,kind="linear",fill_value="extrapolate" )

    if carrier=="n":
        return fn(temp)
    elif carrier =="p":
        return fp(temp)
    else:
        return 0
    
