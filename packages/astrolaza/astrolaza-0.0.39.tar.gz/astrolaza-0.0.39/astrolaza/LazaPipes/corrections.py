#Functions to transform your data into the input data required by BagPipes
#==========================================================
#from ..LazaUtils.get import *
#import ..LazaUtils.MPF as MPF

import numpy as np

from ..LazaUtils.MPF import mkdirs
from ..LazaUtils.get import get_index

#==========================================================
def correct_input(data,dtype,flux_units,usecols=None,wl_units=None,wl_range=[0,np.inf],bad=1e4,out=None):
    """
    --------------------------------------------
    INSTRUCTIONS:
    This will take your spectroscopy or photometry data and will return and save an array in the correct format for Bagpipes to use
    --------------------------------------------
    ARGS:
    data:   array containing the data. Can be either an array or the path to the array
    dtype:  type of data. Can be spectroscopy data (spec) or photometry data (phot)
    flux_units: can be either ergs s-1 cm-2 AA-1 (ergscma) or Jansky (jy)
    --------------------------------------------
    KWARGS
    usecols:    columns to use when loading the data from path. If left as None, it is assumed that the loaded data is in correct order and in the first 2-3 columns, i.e. wl, f and ef for spec and f and ef for phot
    wl_units:   units of the walenght in case spectroscopy data is inputted. Can be either Amstrongs (AA) or meters (m)
    wl_range:   wavelength range, in amstrongs that will be returned. Input must be a list, tuple or array containing the lower and upper limits, in that order. If none is given, it will return whole given range
    bad:    criteria to remove bad data points. If the mean absolute signal-to-noise ratio of the data is bad times larger than the median absolute signal-to-noise ratio, points with a 10*bad signal-to-noise ratio will be removed. Default is 1e4. Points with NaN values will be removed nevertheless.
    out: output path where the corrected data will be saved, if wanted. The name of the file will be the given filename + '_dtype.dat'
    --------------------------------------------
    """
    if type(data)==str:
        if not usecols:
            if dtype=='phot':
                usecols=(0,1)
                shape=2
            elif dtype=='spec':
                usecols=(0,1,2)
                shape=3
        data=np.loadtxt(data,comments='#',usecols=usecols)
    elif type(data)!=np.ndarray:
        raise TypeError('Input data must be either array or path to a file contaning the array data')
    c=2.99792458e+8 #speed of light in m/s
    if dtype=='phot':
        f=data[:,0]*get_index(flux_units[0])/1e-6
        e=data[:,1]*get_index(flux_units[0])/1e-6
        new_data=np.stack((f,e),1)
        new_data=new_data[abs(new_data[:,0]/new_data[:,1])<bad]
        if out:
            np.savetxt(out+'_%s.dat' % (dtype),new_data,header='flux (uJy) flux_error (uJy)')
        return new_data
    elif dtype=='spec':
        flux_index,flux_units=get_index(flux_units)
        wl_index,wl_units=get_index(wl_units)
        if not wl_units:
            raise ValueError('When using spectroscopy data, you need to state both, the wavelength unit (AA, m) and its scientific index (1eX)!\n')
            return
        if wl_units=='AA':
            wl=data[:,0]
        elif wl_units[-1]=='m':
            wl=data[:,0]*(wl_index/1e-10)
        if flux_units=='ergscma':
            f=data[:,1]
            e=data[:,2]
        elif flux_units[-2:]=='jy':
            f=data[:,1]*(1e-23*flux_index*(c/1e-10)/wl**2)
            e=data[:,2]*(1e-23*flux_index*(c/1e-10)/wl**2)
        else:
            print(flux_units)
            return
        new_data=np.stack((wl,f,e),1)
        if wl_range:
            new_data=new_data[new_data[:,0]>wl_range[0]]
            new_data=new_data[new_data[:,0]<wl_range[1]]
        new_data=new_data[abs(new_data[:,1]/new_data[:,2])<bad]
        if out:
            np.savetxt(out+'_%s.dat' % (dtype),new_data,header='wavelength (AA) flux (erg s-1 cm-2 AA-1) flux_error (erg s-1 cm-2 AA-1)')
        return new_data
    else:
        raise ValueError('Data must be either photometry (phot) or spectroscopy (spec)\n')


#==========================================================

def correct_input_resolved(data,IDpixel,flux_units,wl_units,usecols=None,wl_range=[0,np.inf],bad=1e4,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Transforms a given data file into the correct format to use in BagPipes.
    Main difference with correct_input is that this is meant for resolved targets, this is, spectroscopy data for each pixel/spaxel of the target
    ---------------------------------------------
    ARGS:
    data:   array containing the data. Can be either an array or the path to the array
    IDpixel:   list containing the ID of the object, the X coordinate and the Y coordinate of the pixel associated to the spectra, in that same order
    flux_units: can be either ergs s-1 cm-2 AA-1 (ergscma) or Jansky (jy)
    --------------------------------------------
    KWARGS
    usecols:    columns to use when loading the data from path. If left as None, it is assumed that the loaded data is in correct order and in the first 2-3 columns, i.e. wl, f and ef for spec and f and ef for phot
    wl_units:   units of the walenght in case spectroscopy data is inputted. Can be either Amstrongs (AA) or meters (m)
    wl_range:   wavelength range, in amstrongs that will be returned. Input must be a list, tuple or array containing the lower and upper limits, in that order. If none is given, it will return whole given range
    bad:    criteria to remove bad data points. If the mean absolute signal-to-noise ratio of the data is bad times larger than the median absolute signal-to-noise ratio, points with a 10*bad signal-to-noise ratio will be removed. Default is 1e4. Points with NaN values will be removed nevertheless.
    save:    output path where the corrected data will be saved. For better synergy with this package, it is adviced for the name of the file to be 'ID_X_Y.dat'. If not given, a directory of name ID_pixels_spec_data will be created, where the files with the previous name will be included.
    save:   can be either a path to where the file is wanted to be saved, or True. If the later, the file will be saved as 'ID_X_Y.dat' in a directory named './ID_pixels_spec_data'. For better synergy with this package, it is advised to save your files using this same format (this is, only set save=True)
    --------------------------------------------
    """
    new_data=correct_input(data,'spec',flux_units,usecols=usecols,wl_units=wl_units,wl_range=wl_range,bad=bad)
    if save:
        if type(save)==str:
            mkdirs(save)
            np.savetxt(save,new_data,header='wavelength (AA) flux (erg s-1 cm-2 AA-1) flux_error (erg s-1 cm-2 AA-1)')
        else:
            out='%s_pixels_spec_data' % (IDpixel[0])
            mkdirs(out,fil=False)
            np.savetxt(out+'/%s_%04i_%04i.dat' % (IDpixel[0],int(IDpixel[1]),int(IDpixel[2])),new_data,header='wavelength (AA) flux (erg s-1 cm-2 AA-1) flux_error (erg s-1 cm-2 AA-1)')
    return new_data

#==========================================================
