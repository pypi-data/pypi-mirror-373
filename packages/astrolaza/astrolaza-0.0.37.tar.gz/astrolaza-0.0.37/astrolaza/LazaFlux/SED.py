#Functions to work with Spectral Energy Distribution arrays
#==========================================================

import numpy as np

from ..LazaUtils.get import get_index
from ..LazaPipes.data_handling import load_post


#==========================================================
def change_units(sed,wl_unit,f_unit):
    """
    ---------------------------------------------
    INSTRUCTIONS
    Converts AA-ergscma seds into whatever unit you want, for each axis
    ---------------------------------------------
    ARGS:
    sed: Nx2 or Nx3 array with wavelength in AA in the first column and flux density in ergscma in the second column and, optionally, flux error in the third column^
    wl_unit:    output wavelength unit. Can be AA or meter-related (mm,um,nm,etc)
    f_unit: output flux unit. Can be ergscma or jansky related (mjy.ujy,njy,etc)
    ---------------------------------------------
    """
    wl=sed[:,0]
    f=sed[:,1]
    wl_ind,wl_unit=get_index(wl_unit)
    f_ind,f_unit=get_index(f_unit)
    c=2.99792458e+8 #speed of light in m/s
    if wl_unit!='AA' and wl_unit[-1]!='m' and f_unit!='ergscma' and f_unit[-2:]!='jy':
        raise ValueError('Wavelength units must eb either AA or m related, and flux units must be either ergscma or jy related!')
    else:
        if f_unit[-2:]=='jy':
            f=f/(1e-23*f_ind)*((wl)**2/(c*1e10))
        if sed.shape[1]>2:
            e=sed[:,2]
            if f_unit[-2:]=='jy':
                e=e/(1e-23*f_ind)*((wl)**2/(c*1e10))
        else:
            e=ones(len(f))*-99e99
        if wl_unit[-1]=='m':
            wl=wl*(1e-10/wl_ind)
    sed=np.stack((wl,f,e),axis=1)
    print(wl_ind,wl_unit,f_ind,f_unit)
    return sed

#==========================================================

def smooth_sed(sed,bins):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Smooths (i.e., rebins) a given SED
    ---------------------------------------------
    ARGS:
    sed:    Nx2 or Nx3 array, containing the wavelength and the flux and associated error of the SED
    bins:   rebinning vaulue. Must be an integer
    ---------------------------------------------
    """
    wl,f,e=[],[],[]
    lim=np.floor(len(sed[:,0])/bins)
    for i in range(int(lim-1)):
        wl.append(sed[int(bins*i+np.floor(bins/2)),0])
        f.append(np.nansum(sed[bins*i:bins*(i+1),1])/bins)
        if sed.shape[1]>2:
            e.append(np.sqrt(np.nansum(sed[bins*i:bins*(i+1),2]**2))/bins)
        else:
            e.append(-99e99)
    bin_sed=np.stack((wl,f,e),axis=1)
    return bin_sed

#----------------------------------------------------------


def smoothSED_IV(sed,bins):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    smooths (i.e. rebins) a given SED using an inverse variance calculation
    ---------------------------------------------
    ARGS:
    sed:    Nx2 or Nx3 array, containing the wavelength and the flux and associated error of the SED
    bins:   rebinning vaulue. Must be an integer
    ---------------------------------------------
    """
    wl,f,e=[],[],[]
    lim=np.floor(len(sed[:,0])/bins)
    for i in range(int(lim)+1):
        #wl.append(sed[int(bins*i+np.floor(bins/2)),0])
        wl.append(np.nanmean(sed[bins*i:bins*(i+1),0]))
        f.append(np.nansum(sed[bins*i:bins*(i+1),1]/sed[bins*i:bins*(i+1),2]**2)/np.nansum(1/sed[bins*i:bins*(i+1),2]**2))
        if sed.shape[1]>2:
            e.append(np.sqrt(1/np.nansum(1/sed[bins*i:bins*(i+1),2]**2)))
        else:
            e.append(-99e99)
    #rest2=sed[(i)*bins,:]
    #print(i,bins,len(sed),i*bins,len(rest2))
    #wl.append(sed[int(bins*i+np.floor(bins/2)),0])
    #f.append(
    bin_sed=np.stack((wl,f,e),axis=1)
    return bin_sed

#==========================================================

def remove_bad_values(arr,col,ratio=1e4):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Removes the rows from an array if a column of an array contains an absolute value larger than ratio*median(abs). This criteria is completely arbitary yet useful for the working data
    ---------------------------------------------
    ARGS:
    arr:    input array, must have at least 2 columns
    col:    column index from which apply the criteria
    ---------------------------------------------
    KWARGS:
    ratio:  ratio between values and median(abs). If a value is above this ratio, that value is removed
    ---------------------------------------------
    """
    ab_arr=abs(arr[:,col])
    ab_med=np.nanmedian(ab_arr)
    new_arr=arr[ab_arr<ab_med*ratio,:]
    return new_arr

#==========================================================

def mean_cont(sed,z,band):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Works out the median value of a continuum in a SED
    ---------------------------------------------
    ARGS:
    sed:    path to the SEDs file (npy or txt) or array with 3 columns (wavelength, flux and flux error). If it is an npy file, it is assumed it comes from LazaPipes.fitting and has units of AA and ergscma. If a txt file or an array, it is assumed the first column is waleventhg in AA, the second flux in uJy and the third its error in the same units
    z:  redshift of the object
    band:   list, tuple or array of 2 eleemtns containing the lower and upper limits of the continuum band, in rest-frame and the same unit as the wavelength in the sed
    ---------------------------------------------
    """
    c=2.99792458e+18 #speed of light in AA/s
    if type(sed)==np.ndarray:
        wl=sed[:,0]
        f=sed[:,1]
        e=sed[:,2]
    elif type(sed)==str:
        if sed[-4:]=='.npy':
            data=load_post(sed)
            wl=data['wavelength_obs']
            f=data['spectrum_obs']*wl**2/c*1e29
            e=data['err_spectrum_obs']*wl**2/c*1e29
        else:
            wl,f,e=np.loadtxt(sed,usecols=(0,1,2))
    else:
        TypeError('sed must be either an npy file obtained from LazaPipes.fitting.BP_fit, a txt file with 3 columns (wavelength, flux and flux error) or an array with 3 columns (wavelength, flux and error)!')
    band_flux=f[np.where((wl>=band[0]*(1+z)) & (wl<=band[1]*(1+z)))]
    band_err=e[np.where((wl>=band[0]*(1+z)) & (wl<=band[1]*(1+z)))]
    cosa=[]
    cosa_e=[]
    for i in range(100): #generating 100 flux values to get a better estimation
        ff=np.random.normal(band_flux,band_err)
        cosa.append([np.nanmean(ff),np.nanmedian(ff)])
        #cosa_e.append([np.sqrt(np.nansum(band_err**2))/len(band_err),np.nanmean(np.nanpercentile(ff,(16,84)))])
    cosa=np.asarray(cosa)
    #cosa_e=np.asarray(cosa_e)
    mean=np.nanmean(cosa[:,0]) #average of the generated fluxes
    #mean_e=np.nanmean(cosa_e[:,0])
    mean_e=np.nanmean(band_err) #average of its error
    median=np.nanmedian(cosa[:,1])
    meadian_e=np.nanpercentile(cosa[:,1],(16,84))
    return mean, mean_e, median, meadian_e

#==========================================================

def apply_cont(sed,z,bands,lines):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Removes emission lines from a SED and subtitites them with their continuum. The continuums are calculated as the interpolated mean values of the adjacent continuums; see mean_cont for mor info
    ---------------------------------------------
    ARGS:
    sed:    path to the SEDs file (npy or txt) or array with 3 columns (wavelength, flux and flux error). If it is an npy file, it is assumed it comes from LazaPipes.fitting and has units of AA and ergscma. If a txt file or an array, it is assumed the first column is waleventhg in AA, the second flux in uJy and the third its error in the same units
    bands:  conitnuum bands. This must be a list with each element a list, tuple or array of 2 elements, the lower and upper limits of the continuums, in restframe and the same unit as the wavelength in sed (preferably AA)
    lines:  list of line ranges. It follows the same behaviour as bands.
    NOTE THAT BANDS AND LINES MUST BE IN ASCENDING ORDER
    ---------------------------------------------
    """
    c=2.99792458e+18 #speed of light in AA/s
    conts=[]
    if type(sed)==np.ndarray:
        wl=sed[:,0]
        f=sed[:,1]
        e=sed[:,2]
    elif type(sed)==str:
        if sed[-4:]=='.npy':
            data=load_post(sed)
            wl=data['wavelength_obs']
            f=data['spectrum_obs']*wl**2/c*1e29
            e=data['err_spectrum_obs']*wl**2/c*1e29
        else:
            wl,f,e=np.loadtxt(sed,usecols=(0,1,2))
    else:
        TypeError('sed must be either an npy file obtained from LazaPipes.fitting.BP_fit, a txt file with 3 columns (wavelength, flux and flux error) or an array with 3 columns (wavelength, flux and error)!')
    for b in bands:
        # y=np.split(wl,[b[0]*(1+z),b[1]*(1+z)])[1]
        y=wl[np.where((wl>=b[0]*(1+z)) & (wl<=b[1]*(1+z)))]
        mc=mean_cont(sed,z,b)[:2]
        # print(mc)
        # y=np.linspace(b[0],b[1],100)
        conts.append(np.vstack((y,np.ones(len(y))*mc[0],np.ones(len(y))*mc[1])).T)
    # return conts
    # conts=np.asarray(conts)
    i=0
    for l in lines:
        index=np.where((wl>=l[0]*(1+z)) & (wl<=l[1]*(1+z)))
        y=np.linspace(l[0]*(1+z),l[1]*(1+z),len(index[0]))
        if l==lines[0] and l[1]*(1+z)<=conts[0][0,0]:
            # print('a')
            wl[index]=y
            f[index]=np.interp(y,conts[0][:,0],conts[0][:,1])
            e[index]=np.interp(y,conts[0][:,0],conts[0][:,2])
            #e[index]=np.ones(len(index))*4e-3
            f[index]=np.random.normal(f[index],e[index])
        elif l==lines[-1] and l[0]*(1+z)>=conts[-1][-1,0]:
            # print('b')
            wl[index]=y
            f[index]=np.interp(y,conts[-1][:,0],conts[-1][:,1])
            e[index]=np.interp(y,conts[-1][:,0],conts[-1][:,2])
            #e[index]=np.ones(len(index))*13e-3
            f[index]=np.random.normal(f[index],e[index])
        else:
            # print('c')
            wl[index]=y
            cosa=np.vstack((conts[i],conts[i+1]))
            f[index]=np.interp(y,cosa[:,0],cosa[:,1])
            e[index]=np.interp(y,cosa[:,0],cosa[:,2])
            #e[index]=np.ones(len(index))*5e-3
            f[index]=np.random.normal(f[index],e[index])
            i+=1
    new_data=np.stack((wl,f,e),axis=1)
    return new_data
