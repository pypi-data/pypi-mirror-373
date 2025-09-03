#

import numpy as np

from ..LazaUtils.get import get_phys_size

#==========================================================

def source_area(mask,z,ps):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    works out the surface area, in kpc**2, of a source at a given redshift from images with a given pixel scale
    ---------------------------------------------
    ARGS:
    mask:   path or 2D array of a binary mask marking the pixels belonging to the source
    z:  sourceś redshift
    ps: image pixel scale
    ---------------------------------------------
    """
    Dp=get_phys_size(z,ps)
    if type(mask)==str:
        mask=fits.open(mask)[1].data
    elif type(mask)==np.ndarray:
        pass
    else:
        raise TypeError('mask must be either a path to a fits file, or a 2D array!')
    area=np.nansum(mask)*Dp**2
    return area

#----------------------------------------------------------

def Eparam(param,mask,z,ps):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Works out the surface density (kpc**-2) of a given physical parameter
    ---------------------------------------------
    ARGS:
    param:  float value of the param
    mask:   path or 2D array of a binary mask marking the pixels belonging to the source
    z:  source's redshift
    ps: image pixel scale, in "/px
    ---------------------------------------------
    """
    area=source_area(mask,z,ps)
    return param/area
