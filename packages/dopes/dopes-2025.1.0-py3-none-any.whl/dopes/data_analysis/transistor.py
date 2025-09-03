import dopes.data_analysis.data_processing as proc 
import numpy as np
import scipy.interpolate as interp

def threshold_voltage_extraction(ids,vgs,accuracy=4): 
    """ Function to find the threshold voltage of a transistor defined as the voltage where the transconductance gm is maximum, i.e., when the first derivative of the current is maximum or when the second derivative is zero.
        The method is based on the second-derivative method from Wong HS, White MH, Krutsick TJ, Booth RV. "Modeling of transconductance degradation and extraction of threshold voltage in thin oxide MOSFET’s." Solid-State Electron (1987).
        The transistor should be put in linear region (VDS <= VGS-Vth), i.e., with low VDS bias.
        The implementation is based on central finite difference to limit the impact of noise for the determination of the threshold voltage.
        The numerical derivative is done on accuracy + 1 points, but accuracy should be even
        
        args:
           \n\t- ids (scalar): the source to drain current of the transistor (nmos or pmos)
           \n\t- vgs (scalar): the voltage between the gate and the source of the transistor (nmos or pmos) 
           \n\t- accuracy (integer): related to the number of points taken for the finite difference. For central finite difference, the number of points for a first order derivation is accuracy + 1 but accuracy should be even to guarantee a centered interval.
            
        return:
           \n\t- a tuple of two scalars with the threshold voltage found and the transconductance value found at this voltage
    """  

    v_step=np.mean(vgs[1:]-vgs[:-1])
    gm=proc.finite_difference(ids, v_step,order=1,accuracy=accuracy)
    
    dn=len(vgs)-len(gm)
    f = interp.InterpolatedUnivariateSpline(vgs[int(dn/2):-int(dn/2)], gm, k=4)
    
    cr_pts = f.derivative().roots()
    cr_pts = np.append(cr_pts, (vgs[int(dn/2)], vgs[-int(dn/2)]))  # also check the endpoints of the interval
    cr_vals = f(cr_pts)
    max_index = np.argmax(cr_vals)
    vth=cr_pts[max_index]
    gm_max=cr_vals[max_index]
    
    return vth, gm_max
    
def mos_transistor_current(vg,vd,vs=0,vth=0.8,k=1e-4,vea=50,theta=0,mos_type="nmos",early=True):
    """ Function to calculate the current in a MOS transistor:
            \n\t- cutoff (vgs < vth) : ids = 0
            \n\t- triode (vgs\n\t- vth >= vds) : ids = k * ( (vgs-vth) * vds\n\t- vds**2/2) * (1+(vds)/vea)
            \n\t- saturation (vgs\n\t- vth < vds)  : ids = k/2 * ( (vgs-vth)**2) * (1+(vds)/vea)
        \n with k = "mobility" * "oxide capacitance" * "width" / "length" where the oxide capacitance is given by the ratio between the permittivity and the oxide thickness, i.e., Cox = epsilon_r * epsilon_0 / t_ox
        The mobility degradation is taken into account by replacing k by k / (1 + theta * (vgs\n\t- vth)) in the current equation.
        
        args:
           \n\t- vg (scalar or sequence): gate voltage of the transistor. Maximum one parameter among vg, vd and vs can be a sequence.
           \n\t- vd (scala or sequence): drain voltage of the transistor. Maximum one parameter among vg, vd and vs can be a sequence.
           \n\t- vs (scalar or sequence): source voltage of the transistor. Maximum one parameter among vg, vd and vs can be a sequence.
           \n\t- vth (scalar): threshold voltage of the transistor
           \n\t- k (scalar): the gain factor of the transistor
           \n\t- vea (scalar) : early voltage of the transistor
           \n\t- theta (scalar) : mobility degradation factor
            
        return:
           \n\t- a scalar or sequence with the value of current calculated
    """  
    
    if mos_type=="nmos":
        vth=abs(vth)
        vds=vd-vs
        vgs=vg-vs
    if mos_type=="pmos":
        vth=abs(vth)
        vds=vs-vd
        vgs=vs-vg
    
    
    index_cutoff=(vgs<=vth)
    index_saturation=(vgs-vth<vds)
    
    # if vgs<vth:
    #     mode="cutoff"
    # elif vgs-vth<vds:
    #     mode="triode"
    # elif vgs-vth>=vds:
    #     mode="saturation"

    k_theta=k/(1+theta*(vgs-vth))

    jd=k_theta*((vgs-vth)*(vds)-(vds)**2/2)

    
    if not isinstance(vgs, (int,float)): # vgs is a list  
        jd[index_saturation]=k_theta[index_saturation]/2*(vgs[index_saturation]-vth)**2 
        jd[index_cutoff]=0
    else: # vgs is not a list
        if not isinstance(vds, (int,float)): # vds is a list
            jd[index_saturation]=k_theta/2*(vgs-vth)**2 * np.ones(len(vds[index_saturation]))
            if vgs<=vth:
                jd=np.zeros(len(vds))
        else: # vds is not a list
            if vgs<=vth:
                jd=0 
            elif (vgs-vth<vds):
                jd=k_theta/2*(vgs-vth)**2 
                
    if early:
        jd=jd*(1+(vds)/vea)                
    
    return jd