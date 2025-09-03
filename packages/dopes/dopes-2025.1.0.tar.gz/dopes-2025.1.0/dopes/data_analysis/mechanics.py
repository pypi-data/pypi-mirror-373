import numpy as np
    
def voigt_to_matrix(voigt_vector):
    """ Function to convert a vector in Voigt notation to a matrix 
    
        args:
           \n\t- voigt_vector (numpy array): 1D vector with 6 elements
            
        return:
           \n\t- matrix (numpy array): 2D matrix with 3 x 3 elements
    """  
    matrix=np.zeros((3,3))
    
    matrix[0,0]=voigt_vector[0]
    matrix[1,1]=voigt_vector[1]
    matrix[2,2]=voigt_vector[2]
    matrix[1,2]=voigt_vector[3]
    matrix[2,1]=voigt_vector[3]
    matrix[0,2]=voigt_vector[4]
    matrix[2,0]=voigt_vector[4]
    matrix[0,1]=voigt_vector[5]
    matrix[1,0]=voigt_vector[5]
    
    return matrix
    
def stress_from_strain(strain_tensor,c11= 165.77,c12= 63.93,c44 = 79.62):
    """ Function to calculate the stress in silicon from a strain tensor 
    
        args:
           \n\t- strain_tensor (numpy array): the strain tensor for which the stress should be calculated. The voigt notation should be used with a 1 x 6 vector but the function can handle  3 x 3 matrix but only take the upper half in this case.
           \n\t- c11, c12 and c44 (scalar): the coefficient of the compliance matrix in GPa
            
        return:
           \n\t- stress_tensor (numpy array): the stress tensor calculated of dimension 1 x 6 using the voigt notation
    """  
    
    strain_voigt=np.zeros((6,1))
    strain_shape=np.shape(strain_tensor)
    
    if len(strain_shape)==2:
        if strain_shape[0]==3 and strain_shape[1]==3:
            strain_voigt[0]=strain_tensor[0,0]
            strain_voigt[1]=strain_tensor[1,1]
            strain_voigt[2]=strain_tensor[2,2]
            strain_voigt[3]=strain_tensor[1,2]
            strain_voigt[4]=strain_tensor[0,2]
            strain_voigt[5]=strain_tensor[0,1]
        if strain_shape[0]==1 and strain_shape[1]==6:
            strain_voigt=strain_tensor
    else:
        strain_voigt=np.transpose(np.array([strain_tensor]))
    
    compliance_tensor=np.array([[c11,c12,c12,0,0,0],
                                [c12,c11,c12,0,0,0],
                                [c12,c12,c11,0,0,0],
                                [0,0,0,c44,0,0],
                                [0,0,0,0,c44,0],
                                [0,0,0,0,0,c44]])
    
    stress_tensor=compliance_tensor @ strain_voigt
    return stress_tensor

def strain_from_stress(stress_tensor,c11= 165.77,c12= 63.93,c44 = 79.62):
    """ Function to calculate the strain in silicon from a stress tensor 
    
        args:
           \n\t- stress_tensor (numpy array): the stress tensor for which the stress should be calculated. The voigt notation should be used with a 1 x 6 vector but the function can handle  3 x 3 matrix but only take the upper half in this case.
           \n\t- c11, c12 and c44 (scalar): the coefficient of the compliance matrix in GPa
            
        return:
           \n\t- strain_tensor (numpy array): the strain tensor calculated of dimension 1 x 6 using the voigt notation
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
        stress_voigt=np.transpose(np.array([stress_tensor]))
    
    compliance_tensor=np.array([[c11,c12,c12,0,0,0],
                                [c12,c11,c12,0,0,0],
                                [c12,c12,c11,0,0,0],
                                [0,0,0,c44,0,0],
                                [0,0,0,0,c44,0],
                                [0,0,0,0,0,c44]])
    
    strain_tensor=np.linalg.inv(compliance_tensor) @ stress_tensor
    return strain_tensor
    
def straintensor(strain_type,strain_direction,N=11,emin=-0.05,emax=0.05,c11=165.77,c12=63.93,c44=79.62, poisson=True):
    
    """ Function to calculate the strain tensor for various strain type and direction
    
        args:
           \n\t- strain_type (string): the type of strain. Choice between uniaxial ("uni"), biaxial ("bi"), shear ("shear") and hydrostatic ("hydro").
           \n\t- strain_direction (string): the crystal direction and orientation of the strain. Choice between [001], [110] and [111]. For uniaxial strain, the principal strain is oriented along strain_direction while the principal stresses are perpendicular for biaxial strain.
           \n\t- N (int): the number of strain tensor calculated linearly between emin and emax
           \n\t- emin (scalar): the minimal value for the principal strain direction
           \n\t- emax (scalar): the maximal value for the principal strain direction
           \n\t- c11, c12 and c44 (scalar): the coefficient of the compliance matrix in GPa
           \n\t- poisson (boolean): if True, take into account the poisson effect to calculate the strain tensor
            
        return:
           \n\t- strain_tensor (numpy array): array of dimensions ( 3 x 3 x N ) with the strain tensors calculated
    """  
    
    strain_tensor=np.zeros((3,3,N))
    
    eps=np.linspace(emin,emax,N)
    
    # Initiation
    uniepsilon001=np.zeros((3,3,N))
    uniepsilon110=np.zeros((3,3,N))
    uniepsilon111=np.zeros((3,3,N))
    biepsilon001=np.zeros((3,3,N))
    biepsilon110=np.zeros((3,3,N))
    biepsilon111=np.zeros((3,3,N))
    shear001=np.zeros((3,3,N))
    shear110=np.zeros((3,3,N))
    shear111=np.zeros((3,3,N))
    hydro=np.zeros((3,3,N))    
    # Matrix computation
    # Uniaxial
    if poisson:
      uniepar001=-c12/(c11+c12)*eps
    else:
      uniepar001=0
    
    uniepsilon001[0][0]=uniepar001
    uniepsilon001[0][1]=np.zeros(N)
    uniepsilon001[0][2]=np.zeros(N)
    uniepsilon001[1][0]=np.zeros(N)
    uniepsilon001[1][1]=uniepar001
    uniepsilon001[1][2]=np.zeros(N)
    uniepsilon001[2][0]=np.zeros(N)
    uniepsilon001[2][1]=np.zeros(N)
    uniepsilon001[2][2]=eps

    if poisson:    
      uniepar110=- ( 4*c12*c44 ) / ( 2*c11*c44+(c11+2*c12)*(c11-c12) )*eps 
    else:
      uniepar110=0
    
    uniepsilon110[0][0]=0.5*(eps+uniepar110)
    uniepsilon110[0][1]=0.5*(eps-uniepar110)
    uniepsilon110[0][2]=np.zeros(N)
    uniepsilon110[1][0]=0.5*(eps-uniepar110)
    uniepsilon110[1][1]=0.5*(eps+uniepar110)
    uniepsilon110[1][2]=np.zeros(N)
    uniepsilon110[2][0]=np.zeros(N)
    uniepsilon110[2][1]=np.zeros(N)
    uniepsilon110[2][2]=uniepar110

    if poisson:     
      uniepar111 = - (c11 + 2*c12 - 2*c44) / (c11 + 2*c12 + 2*c44)*eps
    else:
      uniepar111 = 0
      
    uniepsilon111[0][0] = (eps + 2*uniepar111) / 3
    uniepsilon111[0][1] = (eps - uniepar111) / 3
    uniepsilon111[0][2] = (eps - uniepar111) / 3
    uniepsilon111[1][0] = (eps - uniepar111) / 3
    uniepsilon111[1][1] = (eps + 2*uniepar111) / 3
    uniepsilon111[1][2] = (eps - uniepar111) / 3
    uniepsilon111[2][0] = (eps - uniepar111) / 3
    uniepsilon111[2][1] = (eps - uniepar111) / 3
    uniepsilon111[2][2] = (eps + 2*uniepar111) / 3
    
    # Biaxial
    if poisson:
      bieper001 = -2 * c12 / c11 * eps        
    else:
      bieper001=0
          
    biepsilon001[0][0] = eps
    biepsilon001[0][1] = np.zeros(N)
    biepsilon001[0][2] = np.zeros(N)
    biepsilon001[1][0] = np.zeros(N)
    biepsilon001[1][1] = eps
    biepsilon001[1][2] = np.zeros(N)
    biepsilon001[2][0] = np.zeros(N)
    biepsilon001[2][1] = np.zeros(N)
    biepsilon001[2][2] = bieper001

    if poisson:     
      bieper110 = -(c11+3*c12-2*c44)/(c11+c12+2*c44)*eps
    else:
      bieper110 = 0
    
    biepsilon110[0][0] = 0.5*(bieper110+eps)
    biepsilon110[0][1] = 0.5*(bieper110-eps)
    biepsilon110[0][2] = np.zeros(N)
    biepsilon110[1][2] = np.zeros(N)
    biepsilon110[1][1] = 0.5*(bieper110+eps)
    biepsilon110[1][0] = 0.5*(bieper110-eps)
    biepsilon110[2][0] = np.zeros(N)
    biepsilon110[2][1] = np.zeros(N)
    biepsilon110[2][2] = eps
    
    if poisson:     
      bieper111 = -2*(c11+2*c12-2*c44)/(c11+2*c12+4*c44)* eps
    else:
      bieper111=0
    biepsilon111[0][0] = (bieper111+2*eps)/3 
    biepsilon111[0][1] = (bieper111-eps)/3 
    biepsilon111[0][2] = (bieper111-eps)/3 
    biepsilon111[1][0] = (bieper111-eps)/3 
    biepsilon111[1][1] = (bieper111+2*eps)/3 
    biepsilon111[1][2] = (bieper111-eps)/3 
    biepsilon111[2][0] = (bieper111-eps)/3 
    biepsilon111[2][1] = (bieper111-eps)/3 
    biepsilon111[2][2] = (bieper111+2*eps)/3

    # Shear

    shear001[0][2] = eps
    shear001[2][0] = eps

    shear110[0][2] = eps/np.sqrt(2)
    shear110[2][0] = eps/np.sqrt(2)
    shear110[1][2] = eps/np.sqrt(2)
    shear110[2][2] = eps/np.sqrt(2)

    shear111[0][1] = eps/np.sqrt(3)
    shear111[0][2] = eps/np.sqrt(3)
    shear111[1][0] = eps/np.sqrt(3)
    shear111[1][2] = eps/np.sqrt(3)
    shear111[2][0] = eps/np.sqrt(3)
    shear111[2][1] = eps/np.sqrt(3)

    # hydro

    hydro[0][0] = eps/3
    hydro[1][1] = eps/3
    hydro[2][2] = eps/3
    if (strain_type == "uniaxial") or (strain_type == "uni"):
        if strain_direction == "001":
            strain_tensor=uniepsilon001
        elif strain_direction == "110":
            strain_tensor=uniepsilon110         
        elif strain_direction == "111":
            strain_tensor=uniepsilon111      
    elif (strain_type == "biaxial") or (strain_type == "bi"):
        if strain_direction == "001":
            strain_tensor=biepsilon001
        elif strain_direction == "110":
            strain_tensor=biepsilon110         
        elif strain_direction == "111":
            strain_tensor=biepsilon111
    elif strain_type == "shear":
        if strain_direction == "001":
            strain_tensor=shear001
        elif strain_direction == "110":
            strain_tensor=shear110         
        elif strain_direction == "111":
            strain_tensor=shear111
    elif (strain_type =="hydro") or (strain_type =="hydrostatic") :
            strain_tensor = hydro
      
            
    return strain_tensor
    
def straintensor_scalar(strain_type,strain_direction,eps=0,c11=16.577,c12=6.393,c44=7.962,poisson=True):
    
    """ Function to calculate the strain tensor for various strain type and direction
    
        args:
           \n\t- strain_type (string): the type of strain. Choice between uniaxial ("uni"), biaxial ("bi"), shear ("shear") and hydrostatic ("hydro").
           \n\t- strain_direction (string): the crystal direction and orientation of the strain. Choice between [001], [110] and [111]. For uniaxial strain, the principal strain is oriented along strain_direction while the principal stresses are perpendicular for biaxial strain.
           \n\t- eps (scalar): the value of strain in the principal strain direction
           \n\t- c11, c12 and c44 (scalar): the coefficient of the compliance matrix in GPa
           \n\t- poisson (boolean): if True, take into account the poisson effect to calculate the strain tensor
            
        return:
           \n\t- strain_tensor (numpy array): array of dimensions ( 3 x 3 ) with the strain tensor calculated
    """  
    
    strain_tensor=np.zeros((3,3))
    
    
    # Initiation
    uniepsilon001=np.zeros((3,3))
    uniepsilon110=np.zeros((3,3))
    uniepsilon111=np.zeros((3,3))
    biepsilon001=np.zeros((3,3))
    biepsilon110=np.zeros((3,3))
    biepsilon111=np.zeros((3,3))
    shear001=np.zeros((3,3))
    shear110=np.zeros((3,3))
    shear111=np.zeros((3,3))
    hydro=np.zeros((3,3))    
    # Matrix computation
    # Uniaxial
    if poisson:
      uniepar001=-c12/(c11+c12)*eps
    else:
      uniepar001=0
      
    uniepsilon001[0][0]=uniepar001
    uniepsilon001[0][1]=0
    uniepsilon001[0][2]=0
    uniepsilon001[1][0]=0
    uniepsilon001[1][1]=uniepar001
    uniepsilon001[1][2]=0
    uniepsilon001[2][0]=0
    uniepsilon001[2][1]=0
    uniepsilon001[2][2]=eps

    if poisson:
      uniepar110=- ( 4*c12*c44 ) / ( 2*c11*c44+(c11+2*c12)*(c11-c12) )*eps 
    else:
      uniepar110=0
          

    uniepsilon110[0][0]=0.5*(eps+uniepar110)
    uniepsilon110[0][1]=0.5*(eps-uniepar110)
    uniepsilon110[0][2]=0
    uniepsilon110[1][0]=0.5*(eps-uniepar110)
    uniepsilon110[1][1]=0.5*(eps+uniepar110)
    uniepsilon110[1][2]=0
    uniepsilon110[2][0]=0
    uniepsilon110[2][1]=0
    uniepsilon110[2][2]=uniepar110
    
    if poisson:
      uniepar111 = - (c11 + 2*c12 - 2*c44) / (c11 + 2*c12 + 2*c44)*eps 
    else:
      uniepar111=0    

    uniepsilon111[0][0] = (eps + 2*uniepar111) / 3
    uniepsilon111[0][1] = (eps - uniepar111) / 3
    uniepsilon111[0][2] = (eps - uniepar111) / 3
    uniepsilon111[1][0] = (eps - uniepar111) / 3
    uniepsilon111[1][1] = (eps + 2*uniepar111) / 3
    uniepsilon111[1][2] = (eps - uniepar111) / 3
    uniepsilon111[2][0] = (eps - uniepar111) / 3
    uniepsilon111[2][1] = (eps - uniepar111) / 3
    uniepsilon111[2][2] = (eps + 2*uniepar111) / 3
    
    # Biaxial
    if poisson:
      bieper001 = -2 * c12 / c11 * eps
    else:
      bieper001=0      
    
    

    biepsilon001[0][0] = eps
    biepsilon001[0][1] = 0
    biepsilon001[0][2] = 0
    biepsilon001[1][0] = 0
    biepsilon001[1][1] = eps
    biepsilon001[1][2] = 0
    biepsilon001[2][0] = 0
    biepsilon001[2][1] = 0
    biepsilon001[2][2] = bieper001
    
    if poisson:
      bieper110 = -(c11+3*c12-2*c44)/(c11+c12+2*c44)*eps
    else:
      bieper110=0      
        
    
    biepsilon110[0][0] = 0.5*(bieper110+eps)
    biepsilon110[0][1] = 0.5*(bieper110-eps)
    biepsilon110[0][2] = 0
    biepsilon110[1][2] = 0
    biepsilon110[1][1] = 0.5*(bieper110+eps)
    biepsilon110[1][0] = 0.5*(bieper110-eps)
    biepsilon110[2][0] = 0
    biepsilon110[2][1] = 0
    biepsilon110[2][2] = eps

    if poisson:
      bieper111 = -2*(c11+2*c12-2*c44)/(c11+2*c12+4*c44)* eps
    else:
      bieper111=0     
          
    
    biepsilon111[0][0] = (bieper111+2*eps)/3 
    biepsilon111[0][1] = (bieper111-eps)/3 
    biepsilon111[0][2] = (bieper111-eps)/3 
    biepsilon111[1][0] = (bieper111-eps)/3 
    biepsilon111[1][1] = (bieper111+2*eps)/3 
    biepsilon111[1][2] = (bieper111-eps)/3 
    biepsilon111[2][0] = (bieper111-eps)/3 
    biepsilon111[2][1] = (bieper111-eps)/3 
    biepsilon111[2][2] = (bieper111+2*eps)/3

    # Shear

    shear001[0][2] = eps
    shear001[2][0] = eps

    shear110[0][2] = eps/np.sqrt(2)
    shear110[2][0] = eps/np.sqrt(2)
    shear110[1][2] = eps/np.sqrt(2)
    shear110[2][2] = eps/np.sqrt(2)

    shear111[0][1] = eps/np.sqrt(3)
    shear111[0][2] = eps/np.sqrt(3)
    shear111[1][0] = eps/np.sqrt(3)
    shear111[1][2] = eps/np.sqrt(3)
    shear111[2][0] = eps/np.sqrt(3)
    shear111[2][1] = eps/np.sqrt(3)

    # hydro

    hydro[0][0] = eps/3
    hydro[1][1] = eps/3
    hydro[2][2] = eps/3
    if (strain_type == "uniaxial") or (strain_type == "uni"):
        if strain_direction == "001":
            strain_tensor=uniepsilon001
        elif strain_direction == "110":
            strain_tensor=uniepsilon110         
        elif strain_direction == "111":
            strain_tensor=uniepsilon111      
    elif (strain_type == "biaxial") or (strain_type == "bi"):
        if strain_direction == "001":
            strain_tensor=biepsilon001
        elif strain_direction == "110":
            strain_tensor=biepsilon110         
        elif strain_direction == "111":
            strain_tensor=biepsilon111
    elif strain_type == "shear":
        if strain_direction == "001":
            strain_tensor=shear001
        elif strain_direction == "110":
            strain_tensor=shear110         
        elif strain_direction == "111":
            strain_tensor=shear111
    elif (strain_type =="hydro") or (strain_type =="hydrostatic") :
            strain_tensor = hydro
      
            
    return strain_tensor