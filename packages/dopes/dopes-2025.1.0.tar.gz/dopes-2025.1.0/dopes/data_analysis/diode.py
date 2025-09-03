import numpy as np
import dopes.data_analysis.semiconductor as sc
from scipy.optimize import fsolve,leastsq
def ideal_diode(Vbias,Is,n=1, temp=300):
  
    """ Function to calculate the current in an ideal diode 
        
        args:
           \n\t- Vbias (scalar or sequence): the bias voltage of the diode
           \n\t- Is (scalar): the saturation current of the diode
           \n\t- n (scalar): the ideality factor of the diode, 1 for radiative recombination, 2 for SRH recombination
           \n\t- temp (scalar): the temperature
                
        return:
           \n\t- a scalar or sequence with same dimension as Vbias
    """ 
    
    kB = 1.38e-23 # J/K
    q = 1.602e-19 # C

    return Is * (np.exp(q * Vbias / (n * kB * temp)) -1 )


def two_diodes(Vbias,Is1,Is2,n1=1,n2=2, temp=300):
    """ Function to calculate the current for a two diodes model 
        
        args:
           \n\t- Vbias (scalar or sequence): the bias voltage of the diode
           \n\t- Is1 (scalar): the saturation current of the first diode
           \n\t- Is2 (scalar): the saturation current of the second diode
           \n\t- n1 (scalar): the ideality factor of the first diode, 1 for radiative recombination, 2 for SRH recombination
           \n\t- n1 (scalar): the ideality factor of the second diode, 1 for radiative recombination, 2 for SRH recombination
           \n\t- temp (scalar): the temperature
                
        return:
           \n\t- a scalar or sequence with same dimension as Vbias
    """ 
    kB = 1.38e-23 # J/K
    q = 1.602e-19 # C

    return Is1 * (np.exp( q * Vbias / (n1 * kB * temp)) -1 ) + Is2 * (np.exp( q * Vbias / (n2 * kB * temp)) -1 )

def two_diodes_with_resistances(Vbias,Is1,Is2,n1=1,n2=2, temp=300, Rs=0, Rsh=float("inf")):
    """ Function to calculate the current for a two diodes model by taking into account the series and shunt resistances
        
        args:
           \n\t- Vbias (scalar or sequence): the bias voltage of the diode
           \n\t- Is1 (scalar): the saturation current of the first diode
           \n\t- Is2 (scalar): the saturation current of the second diode
           \n\t- n1 (scalar): the ideality factor of the first diode, 1 for radiative recombination, 2 for SRH recombination
           \n\t- n1 (scalar): the ideality factor of the second diode, 1 for radiative recombination, 2 for SRH recombination
           \n\t- temp (scalar): the temperature
           \n\t- Rs (scalar): the serie resistance 
           \n\t- Rsh (scalar): the shunt resistance 
                
        return:
           \n\t- a scalar or sequence with same dimension as Vbias
    """ 
    
    kB = 1.38e-23 # J/K
    q = 1.602e-19 # C
    

    if isinstance(Vbias, (int,float)):
        # x0=np.min((two_diodes(Vbias,Is1,Is2,n1,n2, temp),Vbias/Rs))
        I = fsolve(lambda x:Is1 * (np.exp( q * (Vbias - Rs * x) / (n1 * kB * temp)) -1 ) + Is2 * (np.exp( q * (Vbias - Rs * x) / (n2 * kB * temp)) -1 ) + (Vbias - Rs * x ) / Rsh - x,x0=0)
    else:
        I=np.zeros(len(Vbias))
        i=0
        i=0
        for v in Vbias:
            # x0=np.min((two_diodes(v,Is1,Is2,n1,n2, temp),v/Rs))
            I[i] = fsolve(lambda x : Is1 * (np.exp( q * (v - Rs * x) / (n1 * kB * temp)) -1 ) + Is2 * (np.exp( q * (v - Rs * x) / (n2 * kB * temp)) -1 ) + (v - Rs * x ) / Rsh - x,x0=0)
            i+=1
    return I

def depletion_length(doping_in, doping_out, Vbias=0,temp=300):
    """ Function to calculate the depletion length in a pn junction
        
        args:
           \n\t- doping_in (scalar): the doping in the region for which the depletion length has to be calculated
           \n\t- doping_out (scalar): the doping in the adjacent region for which the depletion length has to be calculated
           \n\t- Vbias (scalar): the bias voltage of the pn junction
           \n\t- temp (scalar): the temperature
                
        return:
           \n\t- a scalar with the depletion length calculated in one region
    """ 
    
    kB = 1.38e-23 # J/K
    q = 1.602e-19 # C
    epsilon_0 = 8.8542e-12 # F/m
    epsilon_si = 11.7
    
    phi_0 = kB * temp / q * np.log(doping_in * doping_out / sc.intrinsic_concentration(temp)**2 )
    return np.sqrt(2 * epsilon_si * epsilon_0 / q * doping_out / doping_in / (doping_in + doping_out) * (phi_0 - Vbias))


def j_srh(Vbias,ND,NA,tau=1e-7,temp=300):
    """ Function to calculate the Shockley-Read-Hall contribution to the current density in a pn junction
        
        args:
           \n\t- Vbias (scalar): the bias voltage of the pn junction
           \n\t- ND (scalar): the donor doping concentration in the n region 
           \n\t- NA (scalar): the acceptor doping concentraion in the p region 
           \n\t- tau (scalar): the global lifetime associated to the SRH mechanism
           \n\t- temp (scalar): the temperature

        return:
           \n\t- a scalar with the SRH current density calculated 
    """  
    kB = 1.38e-23 # J/K
    q = 1.602e-19 # C

    ld_n = depletion_length(ND, NA, Vbias)
    ld_p = depletion_length(NA, ND, Vbias)
    ni = sc.intrinsic_concentration(temp)
    x=(ld_p + ld_n) # approximation by considering only the depletion region without diffusion mechanism, gives an upper limit as the effective length is always below
    
    coeff_SRH = q * ni * x / (2 * tau)
    
    return ( coeff_SRH * (np.exp(q * Vbias/ (2 * kB * temp)) - 1 ) )



def j_radiative(Vbias,mu_n,mu_p,tau_n,tau_p,ND,NA,ln,lp,temp=300):
    """ Function to calculate the radial contribution to the current density in a silicon pn junction
        
        args:
           \n\t- Vbias (scalar): the bias voltage of the pn junction
           \n\t- mu_n (scalar): the mobility of the electrons
           \n\t- mu_p (scalar): the mobility of the holes
           \n\t- tau_n (scalar): the lifetime of the electrons
           \n\t- tau_p (scalar): the lifetime of the holes
           \n\t- ND (scalar): the donor doping concentration in the n region 
           \n\t- NA (scalar): the acceptor doping concentraion in the p region 
           \n\t- ln (scalar): the length of the cathode (n-doped region)
           \n\t- lp (scalar): the length of the anode (p-doped region)
           \n\t- temp (scalar): the temperature

        return:
           \n\t- a scalar with the radiative current density calculated 
    """  
    b_rad = 4.76e-15 # cm3/s - low-impurity value entre 1 et 10

    kB = 1.38e-23 # J/K
    q = 1.602e-19 # C

    Dn = kB * temp / q * mu_n
    Dp = kB * temp / q * mu_p
    
    Ln = np.sqrt( Dn * tau_n )
    Lp = np.sqrt( Dp * tau_p )
    
    ld_n = depletion_length(ND, NA, Vbias)
    ld_p = depletion_length(NA, ND, Vbias)
    
    ni = sc.intrinsic_concentration(temp)
    n_p0=ni**2/NA
    p_n0=ni**2/ND
        
    coeff_radial = Dn * n_p0 / Ln / np.tanh( (lp-ld_p) / Ln ) + Dp * p_n0 / Lp / np.tanh( (ln-ld_n) / Lp ) + ni**2 *b_rad* (ld_p + ld_n)
    
    
    return q * ( coeff_radial * (np.exp(q * Vbias/ ( kB * temp)) - 1 ) )
