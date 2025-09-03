import numpy as np
from scipy.interpolate import interp1d
import scipy.signal as signal
from scipy.optimize import curve_fit
import math

def finite_difference_coeff(stencil,order):
    """ Function to calculate the coefficient to calculate a finite difference for derivative calculation
        https://en.wikipedia.org/wiki/Finite_difference_coefficient
        
        args:
           \n\t- stencil (list of integer): the node point for the calculation of each derivation point. The size of the stencil depends on the accuracy and the order of the derivation. For central difference, the length of the stencil is odd and symetric around 0.
           \n\t- order (integer): the order of the derivation
    
        return:
           \n\t- coeff (numpy array): a column array of the coefficients to be used to calculate the finite difference
    """  
    N=len(stencil)
    stencil_matrix=np.zeros((N,N))
    for i in range(N):
        stencil_matrix[i]=np.array(stencil)**i
    delta=np.zeros((N,1))
    delta[order,0]= math.factorial(order)

    coeff=np.linalg.inv(stencil_matrix) @ delta
    return coeff

def finite_difference(x,h,order,accuracy=2,kind="central"):
    """ Function to calculate the coefficient to calculate a finite difference for derivative calculation
        
        args:
           \n\t- x (array): the 1D array for which to calculate the finite difference. The size of the array should be higher than the size of the stencil given by 2 * |_ (order + 1) / 2 _| - 1 + 2 * |_ accuracy / 2_|
           \n\t- h (scalar): the step size for an uniform grid spacing between each finite difference interval
           \n\t- order (integer): the order of the derivation
           \n\t- accuracy (integer): related to the number of points taken for the finite difference. see https://en.wikipedia.org/wiki/Finite_difference_coefficient
           \n\t- kind (string): the type of finite difference calculated. For now, only "central" finite difference is implemented.
    
        return:
           \n\t- results (numpy array): an array with the results of the calculation of the finite difference
           \n\t- x_results (numpy array): an array with the x value with the central value for each calculation of the finite difference
    """  
    if kind=="central":
        n_stencil=int(2*np.floor((order+1)/2)-1+2*np.floor(accuracy/2))
        
        stencil=range(-int(np.floor(n_stencil/2)),int(np.floor(n_stencil/2))+1)
        
    
    coeff=finite_difference_coeff(stencil,order)/h**order
    
    Nx=len(x)
    matrix_coeff=np.zeros((Nx-accuracy-order+1,Nx))
    for i in range(Nx-accuracy-order+1):
        matrix_coeff[i,i:n_stencil+i]=coeff[:,0]
        
    results=matrix_coeff @ x
    # x_results=x[int((n_stencil-1)/2):-int((n_stencil-1)/2)]
    return results
    
def moving_median(x,window_length=3):
    """ Function to perform a median filter on a array
    
        args:
           \n\t- x (array_like) : the input array.
           \n\t- window_length (scalar) : size of the median filter window.    
        return:
           \n\t- an array the same size as input containing the median filtered result.
    """
    return signal.medfilt(x,window_length)

def smooth(x, window_length=11, polyorder=2):
    """ Function to smooth an array by applying a Savitzky-Golay filter
    
        args:
           \n\t- x (array_like) : the data to be filtered.
           \n\t- window_length (scalar) : the length of the filter window.
           \n\t- polyorder (scalar) : the order of the polynomial used to fit the samples. polyorder must be less than window_length.   
        return:
           \n\t- an array the same size as input containing the filtered result.
    """    
    return signal.savgol_filter(x,window_length,polyorder)


def interpolate(x,y,x_interp,kind="cubic"):
    """ Function to interpolate an 1-D array
    
        args:
           \n\t- x (array_like) : a 1-D array of real values.
           \n\t- y (array_like) : a 1-D array of real values of the same dimension of x.
           \n\t- x_interp (array_like) : a 1-D array of real values of the any dimension but with all values include between the max and min value of x.
           \n\t- kind (string or integer) : Specifies the kind of interpolation as a string specifying the order of the spline interpolator to use. The string has to be one of ‘linear’, ‘nearest’, ‘nearest-up’, ‘zero’, ‘slinear’, ‘quadratic’, ‘cubic’, ‘previous’, or ‘next’. 
        return:
           \n\t- an array the same size as x_interp containing the interpolated result.
    """    
    f=interp1d(x, y,kind=kind)    
    return f(x_interp)

def remove_baseline(x,y,xmin_baseline,xmax_baseline,polyorder=2):
    """ Function to remove the baseline a 1-D array
    
        args:
           \n\t- x (array_like) : a 1D input array.
           \n\t- y (array_like) : a 1D  input array with the same dimension of x.
           \n\t- xmin_baseline (scalar or array) : a scalar or array of values to set the minimum value of the data ranges on which the baseline is calculated. Several windows can be specified by specifying an array of values
           \n\t- xmax_baseline (scalar or array) : a scalar or array of values to set the maximum value of the data ranges on which the baseline is calculated. Several windows can be specified by specifying an array of values.
           \n\t- polyorder (scalar) : the order of the polynome to calculate the baseline    
        return:
           \n\t- a tuple (corrected_data, baseline) with the corrected data and the baseline calculated.
    """       
    if isinstance(xmin_baseline,(int,float)):
        xmin_baseline=[xmin_baseline]
        xmax_baseline=[xmax_baseline]
        
    index=[False]*len(x)
    for i in range(len(xmin_baseline)):
        index = index | ((x>=xmin_baseline[i]) & (x<=xmax_baseline[i]) )
    p=np.polyfit(x[index],y[index],deg=polyorder)
    baseline=np.polyval(p,x)
    return y-baseline, baseline

def lorentzian(x,x0,A,W):
    """ Lorentzian function 
    
        args:
           \n\t- x (array_like) : a 1D input array.
           \n\t- x0 (scalar) : the position of the Lorentzian function
           \n\t- A (scalar) : the amplitude of the Lorentzian function
           \n\t- W (scalar) : the full width at half maximum (FWHM) of the Lorentzian function
        return:
           \n\t- an array of the same dimension as x
    """ 
    return A/(1+((x-x0)/(W/2))**2)

def lorentzian2(x,x0,x01,A,A1,W,W1):
    """ Function with the sum of two Lorentzian 
    
        args:
           \n\t- x (array_like) : a 1D input array.
           \n\t- x01 (scalar) : the position of the first Lorentzian function
           \n\t- A1 (scalar) : the amplitude of the first Lorentzian function
           \n\t- W1 (scalar) : the full width at half maximum (FWHM) of the first Lorentzian function
           \n\t- x02 (scalar) : the position of the second Lorentzian function
           \n\t- A2 (scalar) : the amplitude of the second Lorentzian function
           \n\t- W2 (scalar) : the full width at half maximum (FWHM) of the second Lorentzian function
        return:
           \n\t- an array of the same dimension as x
    """ 
    return A/(1+((x-x0)/(W/2))**2)+A1/(1+((x-x01)/(W1/2))**2)

def fit_lorentzian(x,y,xmin=None,xmax=None,x0=520.7,A0=1,W0=3):
    """ Function to fit the data with a Lorentzian function 
    
        args:
           \n\t- x (array_like) : a 1D input array.
           \n\t- y (array_like) : a 1D  input array with the same dimension of x.
           \n\t- xmin (scalar) : a scalar or array of values to set the minimum value of the data range on which the Lorentzian is calculated. 
           \n\t- xmax (scalar) : a scalar or array of values to set the maximum value of the data range on which the Lorentzian is calculated. .
           \n\t- x0 (scalar) : the starting position of the Lorentzian function for the fit
           \n\t- A (scalar) : the starting amplitude of the Lorentzian function for the fit
           \n\t- W (scalar) : the starting full width at half maximum (FWHM) of the Lorentzian function for the fit
        return:
           \n\t- a tuple (parameter_dictionary, data_lorentzian) with the a dictionary containing the fitting parameters ("position", "amplitude" and "width") and the corresponding Lorentzian function evaluated in x.
    """
    if (xmin is None) and (xmax is None):
        x_fit=x
        y_fit=y
    else:
        index=(x>=xmin) & (x<=xmax) 
        x_fit=x[index]
        y_fit=y[index]
    p_lorentzian=curve_fit(lorentzian, x_fit, y_fit, p0=[x0,A0,W0])[0]
    return {"position":p_lorentzian[0],"amplitude":p_lorentzian[1],"width":p_lorentzian[2]}, lorentzian(x,*p_lorentzian)

def fit_lorentzian_2peaks(x,y,xmin=None,xmax=None,x0=(520,520.7),A0=(1,1),W0=(3,3)):
    """ Function to fit the data with a Lorentzian function 
    
        args:
           \n\t- x (array_like) : a 1D input array.
           \n\t- y (array_like) : a 1D  input array with the same dimension of x.
           \n\t- xmin (scalar) : a scalar or array of values to set the minimum value of the data range on which the Lorentzian is calculated. 
           \n\t- xmax (scalar) : a scalar or array of values to set the maximum value of the data range on which the Lorentzian is calculated. .
           \n\t- x0 (tuple) : the two starting position of the double Lorentzian function for the fit
           \n\t- A (tuple) : the two starting amplitude of the double Lorentzian function for the fit
           \n\t- W (tuple) : the two starting full width at half maximum (FWHM) of the double Lorentzian function for the fit
        return:
           \n\t- a tuple (parameter_dictionary, data_lorentzian) with the a dictionary containing the fitting parameters ("position", "amplitude" and "width") and the corresponding double Lorentzian function evaluated in x.
        """
    if (xmin is None) and (xmax is None):
        x_fit=x
        y_fit=y
    else:
        index=(x>=xmin) & (x<=xmax) 
        x_fit=x[index]
        y_fit=y[index]
    p_lorentzian=curve_fit(lorentzian2, x_fit, y_fit, p0=np.reshape([x0,A0,W0],newshape=6))[0]
    return {"position":p_lorentzian[:2],"amplitude":p_lorentzian[2:4],"width":p_lorentzian[4:]}, lorentzian(x,*p_lorentzian)


def gaussian(x, x0, A, W):
    """ Faussian function 
    
        args:
           \n\t- x (array_like) : a 1D input array.
           \n\t- x0 (scalar) : the position of the Gaussian function
           \n\t- A (scalar) : the amplitude of the Lorentzian function
           \n\t- W (scalar) : the full width at half maximum (FWHM) of the Lorentzian function
        return:
           \n\t- an array of the same dimension od x
    """ 
    return A*np.exp(-np.power(x - x0, 2.) / (2 * np.power(W, 2.))) / (W * np.sqrt(2*np.pi))

def fit_gaussian(x,y,xmin=None,xmax=None,x0=0,A=1,W=1):
    """ Function to fit the data with a Lorentzian function 
    
        args:
           \n\t- x (array_like) : a 1D input array.
           \n\t- y (array_like) : a 1D  input array with the same dimension of x.
           \n\t- xmin (scalar) : a scalar or array of values to set the minimum value of the data range on which the Gaussian is calculated. 
           \n\t- xmax (scalar) : a scalar or array of values to set the maximum value of the data range on which the Gaussian is calculated. .
           \n\t- x0 (scalar) : the starting position of the Gaussian function for the fit
           \n\t- A (scalar) : the starting amplitude of the Gaussian function for the fit
           \n\t- W (scalar) : the starting full width at half maximum (FWHM) of the Gaussian function for the fit
        return:
           \n\t- a tuple (parameter_dictionary, data_gaussian) with the a dictionary containing the fitting parameters ("position", "amplitude" and "width") and the corresponding Gaussian function evaluated in x.
    """
    if (xmin is None) and (xmax is None):
        x_fit=x
        y_fit=y
    else:
        index=(x>=xmin) & (x<=xmax) 
        x_fit=x[index]
        y_fit=y[index]

    p_gaussian=curve_fit(gaussian, x_fit, y_fit, p0=[x0,A,W])[0]
    return {"position":p_gaussian[0],"width":p_gaussian[1],"amplitude":p_gaussian[2]}, gaussian(x,*p_gaussian)
