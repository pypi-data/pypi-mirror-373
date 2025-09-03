#Functions to get some specific data from catalogues, post files, etc.
#==========================================================

#==========================================================
from ..LazaVars import dics

import numpy as np

from astropy.cosmology import FlatLambdaCDM

#from ..LazaPipes.data_handling import load_post

def get_z(fit):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Obtain redshift from a dictionary exclusively obtained with BP_fit (see LazaPipes/fitting.py) or loaded from a post file obtained from the same function
    ---------------------------------------------
    ARGS:
    fit:    dictionary obtained with the BP_fit. This requisite must be true as it is assumed the redshift parameters is stored in 1 of 2 specific dict keys.
    ---------------------------------------------
    """
    if type(fit)!=dict:
        raise TypeError('fit must be a dictionary!')
    try:
        z=np.nanmedian(fit['redshift'])
    except KeyError:
        try:
            z=fit['info']['fit_params']['redshift']
        except KeyError:
            raise KeyError('The dictionary must contain either the "redshift" or the "fit_params"->"redshift" keys!')
    if type(z) not in [int,float,np.float64]:
        t=type(z)
        raise TypeError('redshift must be a number! The redshift inside the fit dictionary is %s!' % (t))
    else:
        return z

#==========================================================

def get_index(units):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Returns the numerical index value of a string unit (i.e. transform mm in 1e-3 m, uJy in 1e-6 Jy, etc.)
    ---------------------------------------------
    ARGS:
    units:  string units. Must be either jansky-related, meter-related or ergscma
    ----------------------------------------------
    """
    if units=='AA' or units=='aa':
        ind=1
        units='AA'
    elif units[-1]=='m':
        if len(units)==1:
            ind=1
        else:
            if units[0] in dics.index:
                ind=dics.index[units[0]]
            else:
                keys=tuple(dics.index.keys())
                raise KeyError('The index unit must be in the index dictionary: %s' % (keys,))
    elif units[-2:]=='jy' or units[-2:]=='Jy':
        if len(units)==2:
            ind=1
            units='jy'
        else:
            if units[0] in dics.index:
                ind=dics.index[units[0]]
                units=units[:-2]+'jy'
            else:
                keys=tuple(dics.index.keys())
                raise KeyError('The index unit must be in the index dictionary: %s' % (keys,))
    elif units=='ergscma' or units=='ergscmA':
        ind=1
        units='ergscma'
    else:
        errmes='For flux units, input must be either "ergscma" or "jy" (or jansky-related, i.e. mjy, njy, etc). For wavelength units, input must be either "AA" or "m" (or meter-related, i.e. mm, um, nm, etc.)'
        raise ValueError(errmes)
        return 0,errmes
    return ind, units

#==========================================================

def get_IDpixels(path):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Returns ID and x&y pixel position of a resolved spectrum
    ---------------------------------------------
    ARGS:
    path:   path to the spectrum file. IT IS ASSUMED IT WAS OBTAINED USING correct_input_resolved, OR THAT FOLLOWS DE ID_X_Y.dat FORMAT. If not, this won't be usefull at all
    ---------------------------------------------
    """
    if type(path)==str:
        fname=path.split('/')[-1]
        fsplit=fname.split('_')
        IDpix=[fsplit[0],fsplit[1],fsplit[2][:-4]]
        return IDpix
    else:
        raise ValueError('path must be a str!')

#==========================================================

def get_from_cat(catalogue,param,header_exists=True,pixels=False,parampos=None,xy=None):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Get an array containing the the X and Y coordinates of the pixels of a resolved object and the values plus upper and lower bounds of the desired params from a catalogue. Overall, it is assumed that the input catalogue has been obtained using previous funcitons of this package
    ---------------------------------------------
    ARGS:
    catalogue:  path to the catalogue file. It must be a NxM, where N must the number of objects and M must be the number of column, with at least 3 columns per paramenter (value, upper and lower error, in that order)
    param:  param name to get. It must be a string. In case the catalogue header is missing, write any string
    ---------------------------------------------
    pixels: if True, the catalogue will correpsond to a resolved object, and thus X and Y pixel positions must be given
    header_exists:  if False, one must give the position of the parameter and the X and Y coordinates
    parampos:   column position of the desired parameter to get, in case a header is missing. It must be an integer
    xy: column positions of the X and Y coordinates, in case their name in the header is not 'x' and 'y'. It must be a list or tuple
    ---------------------------------------------
    """
    if type(catalogue)!=str:
        raise TypeError('catalogue must be the string path to the catalogue file!')
    elif type(param)!=str:
        raise TypeError('param must be a string with the name of the variable as it appears in the header!')
    if header_exists:
        header=list(np.loadtxt(catalogue,dtype=str,comments='cacahuete',max_rows=1))
        if header[0] in ['#','%']:#,'#ID','#id','%ID','%id']:
            header.pop(0)
        try:
            parampos=header.index(param)
        except ValueError:
            text='param must in the header! Here is a list of all params in header:\n'
            for h in header:
                text=text+'%s\n' % (h)
            raise ValueError(text)
        if pixels:
            x=header.index('x')
            y=header.index('y')
            cat=np.loadtxt(catalogue,comments='#',usecols=(x,y,parampos,parampos+1,parampos+2))
            shape=cat.shape
            print('======================================================\nAn array of shape %ix%i with columns x, y, %s, upper bound and lower bound has been created. Each row is a pixel of the object.\n======================================================' % (shape[0],shape[1],param))
            return cat
        elif not pixels:
            cat=np.loadtxt(catalogue,comments='#',usecols=(parampos,parampos+1,parampos+2))
            shape=cat.shape
            print('======================================================\nAn array of shape %ix%i with columns %s, upper bound and lower bound has been created. Each row is an object form teh catalogue.\n======================================================' % (shape[0],shape[1],param))
            return cat
    elif not header_exists:
        if parampos==None or type(parampos)!=int:
            raise ValueError('If the file has no header, you must specify in which column the parameter is found (set parampos to a integer)!')
        if pixels:
            if xy==None or type(xy) not in [list,tuple]:
                raise TypeError('If the file has no heather, you must specify the column where the X and Y pixel positions are! (set xy to a tuple/list with the x and y column positions)')
            else:
                x,y=xy[0],xy[0]
                cat=np.loadtxt(catalogue,comments='#',usecols=(x,y,parampos,parampos+1,parampos+2))
                shape=cat.shape
                print('======================================================\nAn array of shape %ix%i with columns x, y, %s, upper bound and lower bound has been created. Each row is a pixel of the object.\n======================================================' % (shape[0],shape[1],param))
                return cat
        elif not pixels:
            cat=np.loadtxt(catalogue,comments='#',usecols=(parampos,parampos+1,parampos+2))
            shape=cat.shape
            print('======================================================\nAn array of shape %ix%i with columns %s, upper bound and lower bound has been created. Each row is an object form teh catalogue.\n======================================================' % (shape[0],shape[1],param))
            return cat

#==========================================================

def get_distribution(post,param,bins=100,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Get the histogram distribution of a parameter inside a posterior file (see LazaPipes/fitting.py-->BP_fit)
    ---------------------------------------------
    ARGS:
    post:   npy post file, which will be transformed into a dictionary, or dicionary containing the distribution inside a key named as param. Alternatively, it can be the path to a file containing a single column with said values or the array itself
    param:  param name (key name) inside post file or dictionary that contains the values of the distribution
    ---------------------------------------------
    KWARGS:
    bins:   number of bins for the distribution. Default is 100
    show:   show the resulting histogram
    save:   if True, the plot will be save as 'param_dist.svg' in the working directory. If it is a path, it will be saved in the given path
    ---------------------------------------------
    """
    def load_post(path,frmt='npy',print_keys=False):
        if frmt=='npy':
            data=np.load(path,allow_pickle=True)[()]
            #print('\n==============================================\nData from %s successfully loaded\n==============================================\n' % (path))
            if type(print_keys)==bool and print_keys:
                print('\n------------------------------------\nKeys of the data are:\n')
                for k in list(data.keys()):
                    print('%s' % (k))
                print('\n------------------------------------\n')
                return data
            return data
    #checking post, the rest maybe later xd
    if type(post)==str:
        if post[-3:]=='npy':
            post=load_post(post)
            values=post[param]
        else:
            post=np.loadtxt(post,comments='#')
    elif type(post)==dict:
        values=post[param]
    elif type(post)==np.ndarray and len(post.shape)==1:
        post=post
    else:
        raise TypeError('post must be either a path to a file, dictionary or row array!')
        return
    median=np.nanmedian(values)
    mean=np.nanmean(values)
    vmin,vmax=np.nanmin(values),np.nanmax(values)
    edges=np.histogram(values,bins=bins,range=(vmin,vmax))[1]
    fig=pp.figure()
    hist=pp.hist(values,bins=edges,range=(vmin,vmax),rwidth=0.8,histtype='step')
    pp.axvline(median,color='r',ls='--')
    ax=pp.gca()
    ax.annotate('Median: %.3f' % (median),((median-vmin+2*(edges[1]-edges[0]))/(vmax-vmin),0.7),xycoords='axes fraction',weight='bold',color='k',rotation='vertical',)
    variables=dics.variables
    try:
        pp.xlabel(variables[param])
    except KeyError:
        pp.xlabel(str(param))
    pp.ylabel('Ocurrences (%i bins)' % (bins))
    if show:
        pp.show(block=False)
    if save:
        if type(save)==str:
            pp.savefig(save,dpi=200)
            print('======================================================\nDistribution plot succesfully saved at %s\n======================================================' % (save))
        else:
            pp.savefig('%s_distribution.svg' % (str(param)))
            print('======================================================\nDistribution plot succesfully saved at the working directory as %s_distribution.svg\n======================================================' % (str(param)))
    return

#==========================================================

def get_phys_size(z,ps,cosmo='FLCDM'):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Work out the physical size, in kpc, of an object given its redshift and the pixel size of the instrument
    ---------------------------------------------
    ARGS:
    z:  redshift. Can be either a number, a list or an array
    ps: pixel size of the instrument, in arcsec per pixel (''/px). It can be a number, a list or an array, the latter in case results with several pixel sizes are wanted to be worked out; in this case, the size must be the same as z
    ---------------------------------------------
    KWARGS:
    cosmo:  cosmology to be used. Default is 'FLCDM', which refers to flat lambda Cold Dark Matter, and uses the FlatLambdaCDM astropy.cosmology function wth values H0=70 and Om0=0.3. Any other astropy.cosmology can be given, however they must eb created outside this function.
    ---------------------------------------------
    """
    if type(z) in [int,float,list,np.ndarray,np.float64]:
        z=np.asarray(z)
    else:
        raise TypeError('z must be either a number, a list or an array!')
    if type(ps) in [list,np.ndarray]:
        ps=np.asarray(ps)
        if z.shape!=ps.shape:
            raise ValueError('If z and ps are both list or arrays, the must have the same size! (z.shape=(%i,%i),ps.shape=(%i,%i))' % (z.shape[0],z.shape[1],ps.shape[0],ps.shape[1]))
    else:
        try:
            ps=ps*np.ones(len(z))
        except TypeError:
            ps=ps*np.ones(len([z]))
    import abc #just importing for the data type
    if cosmo=='FLCDM': #Flat lambda Cold Dark Matter model (FRLW)
        cosmo=FlatLambdaCDM(H0=70., Om0=0.3)
        DL=cosmo.luminosity_distance(z).value*1e3
    else: #any other model given by the user but coming from astropy
        try:
            DL=cosmo.luminosity_distance(z).value*1e3
        except AttributeError:
            raise ValueError('cosmo must be either the default value "FLCDM" (H0=70, Om0=0.3) or another cosmology model taken from astropy.cosmology!')
    dtheta=np.pi*ps/3600/180 #delta theta (angular size), in rads
    Dp=DL*dtheta/(1+z)**2 #physical size
    return Dp
