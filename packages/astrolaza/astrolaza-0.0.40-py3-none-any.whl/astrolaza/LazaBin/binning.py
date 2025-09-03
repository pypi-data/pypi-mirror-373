#Mauro's binning version, modified by me

#==========================================================
#Importing packages

import os

import numpy as np

import matplotlib.pyplot as pp
import matplotlib.gridspec as gs
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import astropy
from astropy.wcs import WCS
from astropy.io import fits
from astropy.nddata.utils import Cutout2D
from astropy import units as u
from astropy.coordinates import Angle
from astropy.visualization import ZScaleInterval
from astropy.visualization.wcsaxes import add_beam, add_scalebar
from astropy.cosmology import FlatLambdaCDM
from astropy.modeling import models,fitting

from statistics import NormalDist

from scipy import ndimage
from scipy import stats
from scipy.ndimage import label

from ..LazaUtils.MPF import mkdirs, zoomin
from ..LazaVars.dics import BANDS

#==========================================================

def slicer(cube,bands,z,width=50,wl_start=6025,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Divides an IFU cube (MxNxS) in the given bands regions.
    ---------------------------------------------
    ARGS:
    cube:   MxNxS array with the cube data
    bands:  list of 1x2 lists, tuples or arrays with the lower and upper limit of each band. Alternatively, this list can contain string with the options: 'Ha', 'Hb', 'Ha+Hb', 'UVcont', 'UVcontR', 'UVcontB', '[OII]', '[OIII]', 'OPcontR','OPcontB','OPcont'. Note that these bands are in restframe wavelength
    z:  redshift associated to the cube's object
    ---------------------------------------------
    KWARGS:
    width:  wavelength separation, in AA, between slices of the cube. Default is 50 (JWST NIRSpec PRISM)
    wl_start:   starting wavelength, in AA, of the cube. This will be associated to the first slice of the cube (cube[0]), and following slices will be wl_start+i*width. Default is 6025 (JWST NIRSpec PRISM minimum wl)
    save:   save slices as FITS files. Can be either True or a string
    ---------------------------------------------
    """
    #association of slice number with wavelength
    l=len(cube)
    s=np.linspace(0,l-1,l,dtype=int)
    wl=np.linspace(wl_start,wl_start+(l-1)*width,l)
    a=np.stack((s,wl),1)
    #return a
    #dividing the cube in the desired regions
    slices=[]
    b_ran=[]
    for b in bands:
        if b in BANDS:
            lwl,uwl=int(a[a[:,1]>=BANDS[b][0]*(1+z),0][0]),int(a[a[:,1]<=BANDS[b][1]*(1+z),0][-1])
            sli=cube[lwl:uwl+1]
            slices.append(sli)
            b_ran.append('%s' % (b))
        elif type(b) in [list,tuple,np.ndarray]:
            lwl,uwl=int(a[a[:,1]>=b[0]*(1+z),0][0]),int(a[a[:,1]<=b[1]*(1+z),0][-1])
            sli=cube[lwl:uwl+1]
            b_ran.append([float(a[lwl,1]),float(a[uwl,1])])
        elif b=='Ha+Hb':
            lwl,uwl=int(a[a[:,1]>=BANDS['Hb'][0]*(1+z),0][0]),int(a[a[:,1]<=BANDS['Hb'][1]*(1+z),0][-1])
            sli1=cube[lwl:uwl+1]
            lwl,uwl=int(a[a[:,1]>=BANDS['Ha'][0]*(1+z),0][0]),int(a[a[:,1]<=BANDS['Ha'][1]*(1+z),0][-1])
            sli2=cube[lwl:uwl+1]
            sli=np.concatenate((sli1,sli2),axis=0)
            slices.append(sli)
            b_ran.append('Ha+Hb')
        elif b=='OPcont':
            lwl,uwl=int(a[a[:,1]>=BANDS['OPcontB'][0]*(1+z),0][0]),int(a[a[:,1]<=BANDS['OPcontB'][1]*(1+z),0][-1])
            sli1=cube[lwl:uwl+1]
            lwl,uwl=int(a[a[:,1]>=BANDS['OPcontR'][0]*(1+z),0][0]),int(a[a[:,1]<=BANDS['OPcontR'][1]*(1+z),0][-1])
            sli2=cube[lwl:uwl+1]
            sli=np.concatenate((sli1,sli2),axis=0)
            slices.append(sli)
            b_ran.append('OPcont')
        else:
            ValueError('The band %s is not in the bands list!' % (b))
        if save:
            hdu=fits.PrimaryHDU(np.zeros(1))
            hdui=fits.ImageHDU(slices[-1],name='SCI_cube_slice')
            hdul=fits.HDUList([hdu,hdui])
            if type(save)==str:
                hdul.writeto('Results/%s_%s_cube_slice.fits' % (save,b_ran[-1]), overwrite=True)
            elif type(save)==bool:
                hdul.writeto('Results/%s_cube_slice.fits' % (b_ran[-1]), overwrite=True)
    return slices,b_ran

#----------------------------------------------------------

def inv_var(f_sli,e_sli,band=None,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    works out the Inverse-variance weighting for a given set of slices, returing a single combined sliced. The process consists of 'adding', for a given position X,Y in a slice, all the pixels in that position using:
    F=sum(f/e**2)/sum(1/e**2)
    where f is the flux of the pixel, e its associated error and F the final resulting flux, with associated error:
    E=1/sum(1/e**2)
    ---------------------------------------------
    ARGS:
    f_sli:  slices (cube) with flux measurements. Shape must be the same as e_sli
    e_sli:  slices (cube) with error measurements. Shape must be the same as f_sli
    ---------------------------------------------
    """
    if f_sli.shape!=e_sli.shape:
        ValueError('flux and error cubes must have the same shape (dimensions)!')
    x,y=f_sli.shape[1],f_sli.shape[2]
    aver=np.zeros([x,y])*np.nan
    err=np.zeros([x,y])*np.nan
    for i in range(x):
        for j in range(y):
            aver[i,j]=np.nansum(f_sli[:,i,j]/e_sli[:,i,j]**2)/np.nansum(1/e_sli[:,i,j]**2)
            err[i,j]=np.sqrt(1/np.nansum(1/e_sli[:,i,j]**2))
            #if aver[i,j]==np.inf or aver[i,j]==0:
                #aver[i,j]=np.nan
            #elif err[i,j]==np.inf or err[i,j]==0:
                #err[i,j]=np.nan
    aver=np.nansum(f_sli/e_sli**2,axis=0)/np.nansum(1/e_sli**2,axis=0)
    err=np.sqrt(1/np.nansum(1/e_sli**2,axis=0))
    if save:
        hdu=fits.PrimaryHDU(np.zeros(1))
        hdua=fits.ImageHDU(aver,name='SCI')
        hdue=fits.ImageHDU(err,name='ERR')
        hdul=fits.HDUList([hdu,hdua,hdue])
        if type(save)==str and band:
            hdul.writeto('Results/%s_%s_InvVar.fits' % (save,band), overwrite=True)
        elif type(save)==str and not band:
            hdul.writeto('Results/%s_InvVar.fits' % (save), overwrite=True)
        elif type(save)==bool and band:
            hdul.writeto('Results/%s_InvVar.fits' % (band), overwrite=True)
    return aver,err

#----------------------------------------------------------

def slices_maps(slices,titles=None,suptitle=None,hist=False,show=False,save=False):
    """
    INSTRUCTIONS
    ---------------------------------------------
    Creates an image with multple plots, each of them with a map of slice included in the slices list
    ---------------------------------------------
    ARGS:
    slices: list of NxM images
    ----------------------------------------------
    KWARGS:
    titles: list of titles for each fo the subplots. It is assumed that they ar ein the same order that they appear in slices. If len(slices)>len(titles), tittles will be filled with 'None'
    suptitle:   super-title of the figure
    save:   save the resulting plot in the 'Results' directory. If save is bool, the figure will be saved as 'slices.svg'; if bool and suptitle is given, it will be saved as 'suptitle_slices.svg'; if a string, it will be saved as 'save.svg'
    -----------------------------------------------
    """
    l=len(slices)
    #vmin=np.nanmin([np.nanmin(sli) for sli in slices])
    #vmax=np.nanmax([np.nanmax(sli) for sli in slices])
    #Checking everything's ok
    if show:
        pp.close('all')
    if titles and type(titles) in [list,tuple]:
        while l>len(titles):
            titles.append(None)
    elif titles and type(titles) not in [list,tuple]:
        TypeError('titles must a be a list of strings including the titles of the subplots!')
    #This first part chooses the best distirbution for te subplots, taking into account a best shape is always a perfect square of side lenght the number of slices that will have its bottom rows removed if they are empty (i.e. 4 slices: 2x2, 5 slices: 2x3, 8 slices: 3x3, etc)
    i=1
    while i**2<l:
        i+=1
    n_cols,n_rows=i,i
    while n_rows*n_cols>=l:
        n_rows-=1
    n_rows=n_rows+1
    fig=pp.figure(figsize=(n_cols*3,n_rows*3))
    if hist:
        hfig=pp.figure(figsize=(16,9))
    if suptitle:
        fig.suptitle(suptitle)
    for i in range(l):
        bound=np.argwhere(~np.isnan(slices[i]))
        ax=fig.add_subplot(n_rows,n_cols,i+1)
        ax.imshow(slices[i],origin='lower')#,vmin=vmin,vmax=vmax)
        ax.set_xlim(min(bound[:, 1])-2, max(bound[:, 1])+2)
        ax.set_ylim(min(bound[:, 0])-2, max(bound[:, 0])+2)
        ax.set_xticks([])
        ax.set_yticks([])
        if titles:
            ax.set_title(titles[i])
        if hist:
            axh=hfig.add_subplot(n_rows,n_cols,i+1)
            edges=np.linspace(0,np.nanmax(slices[i]),6)
            axh.hist(slices[i].flatten(),rwidth=0.8,bins=edges)
            axh.set_xticks(edges)
            if titles:
                axh.set_title(titles[i])
    pp.subplots_adjust(wspace=0)
    if save:
        if type(save)==str:
            fig.savefig('Results/%s_slices.svg' % (save))
            if hist:
                hfig.savefig('Results/%s_hists.svg' % (save))
        elif suptitle:
            fig.savefig('Results/%s_slices.svg' % (suptitle))
            if hist:
                hfig.savefig('Results/%s_hists.svg' % (suptitle))
        else:
            fig.savefig('Results/slices.svg')
            if hist:
                hfig.savefig('Results/hists.svg')
    if show:
        pp.show(block=False)
    #return n_rows,n_cols

#----------------------------------------------------------

def slicer_pl(cube_path,bands,z,mask=None,hist=False,width=50,wl_start=6025,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Full pipeline to extract sliced regions (wavelength axis) from an IFU cube and create combined imaged of the regions, to later plot and show them.
    See 'slicer', 'inv_var' and 'slices_map' for more info
    ----------------------------------------------
    ARGS:
    cube_path: path to the FITS cube. It is assumed that this cube has at least 2 components, flux and error, in position 1 and 2 of the cube
    bands:  bands, from the BANDS dictionary or 2-element list (lower and upper wavelength limit), to extract from the cube and combine
    z:  redshift of the target in the cube
    -----------------------------------------------
    KWARGS:
    mask:   mask to applye to the cube, if any
    width:  width of each slice in the original cube. Default is 50 AA, as in JWST NIRSpec
    wl_start:   wavelength associted to the 1st slice of the cube. Default is 6025 AA, associated to JWST NIRSpec
    show:   shows the resulting combined slices
    save:   save the combined slices and the generated plot in teh 'Results' directory
    ---------------------------------------------
    """
    if type(save)==np.str_:
        save=str(save)
    f_cube=fits.open(cube_path)[1].data
    e_cube=fits.open(cube_path)[2].data
    if mask.any():
        f_cube=mask*f_cube
        e_cube=mask*e_cube
    f_slices,b_ran=slicer(f_cube,bands,z,width=width,wl_start=wl_start)
    e_slices,b_ran=slicer(e_cube,bands,z,width=width,wl_start=wl_start)
    #return f_slices,e_slices,f_slices,e_slices
    f_IV,e_IV=[],[]
    for i in range(len(f_slices)):
        aver,err=inv_var(f_slices[i],e_slices[i],band=bands[i],save=save)
    #return f_slices,e_slices,aver,err
        aver[aver==0]=np.nan
        err[~np.isfinite(err)]=np.nan
        f_IV.append(aver)
        e_IV.append(err)
    slices_maps(f_IV,titles=bands,suptitle=save,hist=hist,show=show,save=save)
    return f_cube,e_cube,f_IV,e_IV

#==========================================================

def binned_map_stats(path,bins,mask=None,suptitle=None,save=False,show=False):
    """
    ---------------------------------------------
    INSTRCUTIONS:
    Creates a figure that includes the number of pixel in each bin, the SNR of the bin and maps of the binned regions + SNR maps with bins' contours
    ---------------------------------------------
    ARGS:
    path:   path to the FITS image. This file must contain two 2D images, SCI and ERR, of same size. Check the function 'slicer' to see how to obtain such images
    bins:   list or array of bin limits (flux-wise). It is adviced that the 2 first elements of the list are -100 and <0 flux value (i.e. -1) to discard masked/wrong values
    ---------------------------------------------
    KWARGS:
    mask:   mask to apply to the data, if any. Default is None
    suptitle:   super title of the image. It must be a string
    save:   save the figure in the 'Results' directory. If True, it will be saved as 'suptitle_binned_map_stats.svg'; if a string is given it will be saved as that string in svg format. Default is False
    show:   shows the figure. Default is False
    ---------------------------------------------
    """
    if type(path)!=str:
        TypeError('path must be a string with the path to the FITS file!')
    if type(bins) not in [list,tuple,np.ndarray]:
        TypeError('bins must be a list, tuple or array including the edges of each flux bin!')
    if type(suptitle)!=str:
        suptitle=str(suptitle)
    F=fits.open(path)[1].data
    if mask.any():
        if mask.shape!=F.shape:
            ValueError('mask must have the same size as the image!')
        F[mask<=0]=-99 #from mauro
    E=fits.open(path)[2].data
    SNR=F*mask/E
    SNR[SNR==0]=np.nan
    #extracted from mauro's code
    stat,edges,ixbin=stats.binned_statistic(F.flatten(),F.flatten(),statistic='count',bins=bins)
    structure = np.ones((3, 3), dtype=int)
    lbl=F*0
    for b in range(2,len(edges)): # 2: skip the first bin, which is for NaNs and background
        im_n=ixbin.reshape(F.shape)*1+0
        im_n[im_n != b]=0
        im_n = im_n/b
        labels, nlabels = label(im_n, structure)
        if nlabels>0:
            lbl+=labels+np.max(lbl)*(labels>0)
    #up to this point

    #Creating the contours of the bins + working out the bin_SNR
    lbl[lbl==0]=np.nan
    u=np.unique(lbl)[:-1] #we do not want the nan values, which are always at the end of unique
    masks_lbl=[]
    SNR_bins=[]
    for i in u:
        l=np.copy(lbl)
        l[l!=i]=np.nan
        l=l/i
        masks_lbl.append(l)
        SNR_bins.append(binSNR(F,E,l))

    #plotting the results
    fig=pp.figure(100,figsize=(10,10))
    cmap=pp.get_cmap('rainbow',np.nanmax(lbl))
    if suptitle:
        fig.suptitle(suptitle)

    #Bar plot
    ax=fig.add_subplot(1,2,1)
    ax.set_title('Pixels per bin (bin SNR on top)')
    v,c=np.unique(lbl,return_counts=True)
    bar=ax.bar(v[:-1],c[:-1],align='center',color=[cmap(i) for i in np.linspace(0,1,int(np.nanmax(lbl)))])
    #ax.hist(lbl.flatten(),bins=np.linspace(np.nanmin(lbl),np.nanmax(lbl),int(np.nanmax(lbl)+1)),rwidth=0.8)
    ax.set_xticks(v[:-1])
    i=0
    for r in bar:
        h,w=r.get_height(),r.get_width()
        ax.text(r.get_x()+w/2,h,'%.2f' % SNR_bins[i],ha='center', va='bottom')
        i+=1

    #Map fo the bins
    bound=np.argwhere(~np.isnan(lbl))
    ax=fig.add_subplot(2,2,2)
    ax.set_title('Bin regions')
    ax.set_xlim(min(bound[:, 1])-2, max(bound[:, 1])+2)
    ax.set_ylim(min(bound[:, 0])-2, max(bound[:, 0])+2)
    im=ax.imshow(lbl,origin='lower',cmap=cmap)
    pp.colorbar(im,ticks=np.linspace(1,np.nanmax(lbl),int(np.nanmax(lbl)+1),dtype=int),fraction=0.043, pad=0.04)
    ax.set_yticks([])
    ax.set_xticks([])

    #SNR map + bins' contours
    ax=fig.add_subplot(2,2,4)
    ax.set_title('Flux map + bin contours')
    F[F==-99]=np.nan
    im=ax.imshow(F,origin='lower',cmap='copper')
    pp.colorbar(im,ticks=np.linspace(0,np.nanmax(F),5),fraction=0.043, pad=0.04) #fraction+pad taken from stackoverchange to make colorbars same size than maps: these values are valid for any plot
    #creating the contours
    s=F.shape
    x=np.linspace(0,s[1]-1,s[1])
    y=np.linspace(0,s[0]-1,s[0])
    x,y=np.meshgrid(x,y)
    for i in u:
        m=np.copy(lbl)
        m[m!=i]=0
        m=m/i
        zz=ndimage.zoom(m,5,order=0)
        ax.contour(np.linspace(x.min(),x.max(),zz.shape[1]),np.linspace(y.min(),y.max(),zz.shape[0]),np.where(zz!=0,0,1),colors=cmap(int(i-1)),linewidths=2,levels=[0,1],hatches='//',corner_mask=False)
    #we mark SNR<0 pixels with a white X
    bad=[]
    for i in range(len(F.flatten())):
        if F.flatten()[i]<0 and F.flatten()[i]!=-99:
            bad.append([x.flatten()[i],y.flatten()[i]])
    bad=np.asarray(bad)
    if len(bad)>0:
        ax.scatter(bad[:,0],bad[:,1],s=50,c='white',marker='x')
    ax.set_xlim(min(bound[:, 1])-2, max(bound[:, 1])+2)
    ax.set_ylim(min(bound[:, 0])-2, max(bound[:, 0])+2)
    ax.set_yticks([])
    ax.set_xticks([])

    if show:
        pp.show(block=False)
    if save:
        if type(save)==bool:
            if suptitle:
                fig.savefig('Results/%s_binned_map_stats.svg' % (suptitle))
            else:
                fig.savefig('Results/binned_map_stats.svg')
        elif type(suptitle)==str:
            pp.savefig('%s.svg' % (save))
        else:
            TypeError('save must be either bool or string!')
    #return lbl

#==========================================================


def bins2regs(paths,bins,mask,save=False,show=False):
    """
    ---------------------------------------------
    INSTRUCTIONS
    Puts all binned regions of each wavelength in a single figure and saves each region map for each wavelength into a FITS file
    ---------------------------------------------
    ARGS:
    paths:  list of paths to the FITS images of each wavelength
    bins:   dictionary including the flux bins of each wavelength
    mask:   mask to apply to the FITS images
    ---------------------------------------------
    """
    final=[]
    hdu=fits.PrimaryHDU(np.zeros(1))
    final.append(hdu)
    for i in range(len(bins)):
        F=fits.open(paths[i])[1].data
        E=fits.open(paths[i])[2].data
        F[mask<=0]=-99
        E[mask<=0]=-99
        stat,edges,ixbin=stats.binned_statistic(F.flatten(),F.flatten(),statistic='count',bins=bins[list(bins.keys())[i]])
        structure = np.ones((3, 3), dtype=int)
        lbl=F*0
        for b in range(2,len(edges)): # 2: skip the first bin, which is for NaNs and background
            im_n=ixbin.reshape(F.shape)*1+0
            im_n[im_n != b]=0
            im_n = im_n/b
            labels, nlabels = label(im_n, structure)
            if nlabels>0:
                lbl+=labels+np.max(lbl)*(labels>0)
    #up to this point

    #Creating the contours of the bins + working out the bin_SNR
        lbl[lbl==0]=np.nan
        u=np.unique(lbl)[:-1] #we do not want the nan values, which are always at the end of unique
        masks_lbl=[]
        SNR_bins=[]
        for j in u:
            l=np.copy(lbl)
            l[l!=j]=np.nan
            l=l/j
            masks_lbl.append(l)
            SNR_bins.append(binSNR(F,E,l))

    #plotting the results
        fig=pp.figure(100,figsize=(10,10))
        if save:
            pp.suptitle(save)
        cmap=pp.get_cmap('rainbow',np.nanmax(lbl))

    #Map of the bins
        bound=np.argwhere(~np.isnan(lbl))
        ax=fig.add_subplot(2,4,i+1)
        ax.set_title(list(bins.keys())[i])
        ax.set_xlim(min(bound[:, 1])-2, max(bound[:, 1])+2)
        ax.set_ylim(min(bound[:, 0])-2, max(bound[:, 0])+2)
        im=ax.imshow(lbl,origin='lower',cmap=cmap)
        #pp.colorbar(im,ticks=np.linspace(1,np.nanmax(lbl),int(np.nanmax(lbl)+1),dtype=int),fraction=0.043, pad=0.04)
        ax.set_yticks([])
        ax.set_xticks([])

        final.append(fits.ImageHDU(lbl,name=list(bins.keys())[i]))
    hdul=fits.HDUList(final)

    if save:
        hdul.writeto('Results/regs_%s.fits' % (save),overwrite=True)
    #hdul.writeto('Results/regs.fits',overwrite=True)
    pp.show(block=False)

#===========================================================

def join_bins(fits_path,ref=1,suptitle=None,save=False,show=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Joins flux-wise regions from several wavelength images and returns a the joined-regions map
    ---------------------------------------------
    ARGS:
    fits_path:  path to the fits file containing the images of each wavelength's region. It is adviced this file is generated using bins2regs
    ---------------------------------------------
    KWARGS:
    ref:    reference wavelength, i.e. the region map which will be used as canvas to join the rest of region maps.
    ---------------------------------------------
    """
    f=fits.open(fits_path) #loading the fits file
    l=len(f)
    cube=[f[ref].data] #putting first the references wavelength
    for i in range(1,l): #and then the rest, in the gits order
        if i!=ref:
            cube.append(f[i].data)
    cube=np.asarray(cube)
    mask=cube[0]/cube[0] #creating the 'shape' mask, which will be reduced recursively
    regs=[]
    #In the following loop, starting from the max value in the whole cube (which it is assumed it is found in the references wavelength), we go through all region values in descending order, get the region of that value in the reference image and see if the rest of wavelengths there is a region match with that same value, max-wise, this is, if that region in the the other maps has the maximum value available, as those will be eliminated recursively
    for i in range(int(np.nanmax(cube)),0,-1):
        ref_reg=np.where((mask*cube[0]==i)) #creating the reference region
        ref_reg=np.stack((ref_reg[0],ref_reg[1]),axis=1)
        tot_reg=np.copy(ref_reg) #array where the shape of joined reigons will be saved
        #print(tot_reg)
        reg_mask=np.zeros(mask.shape)
        for j in range(1,l-1): #going through the rest of the wavelengths
            check=0
            reg=np.where((cube[j]*mask==np.nanmax(cube[j]*mask))) #getting the max value region available in the map
            reg=np.stack((reg[0],reg[1]),axis=1)
            for p in reg.tolist(): #checking if there are positional matches between the reference region and the other region
                if p in ref_reg.tolist() and i>1: #if so, and it is not the minimum value reigon (i.e. 1), there is a match and both regions are added
                    check=1
            if check==1: #adding the regions
                tot_reg=np.vstack((tot_reg,reg))
            tot_reg=np.unique(tot_reg,axis=0)
            final_reg=(tot_reg[:,0],tot_reg[:,1]) #final region positions
        reg_mask[final_reg]=1 #creating a 'region mask' for this region specifically
        reg_mask=mask*reg_mask
        mask[final_reg]=np.nan #modifying the mask so it ignores pixels already consideren in other regions
        regs.append(reg_mask*i)
    regs=np.asarray(regs)
    regs=np.nansum(regs,axis=0) #creating the final regions map
    regs[regs==0]=np.nan
    u=np.unique(regs)[:-1] #the following loops helps eliminitaing gaps between regions
    u2=np.copy(u)
    for i in range(len(u)-1):
        if u[i+1]-u[i]>1:
            u[i+1]=u[i]+1
            regs[regs==u2[i+1]]=u[i]+1
    pp.close('all')
    fig=pp.figure(figsize=(16,9))
    pp.imshow(regs,origin='lower')
    bound=np.argwhere(~np.isnan(regs))
    pp.xlim(min(bound[:, 1])-2, max(bound[:, 1])+2)
    pp.ylim(min(bound[:, 0])-2, max(bound[:, 0])+2)
    if suptitle:
        pp.title(suptitle)
    pp.xticks([])
    pp.yticks([])
    if show:
        pp.show(block=False)
    if save:
        if suptitle:
            pp.savefig('Results/%s_join_regs.svg' % (suptitle))
        else:
            pp.savefig('Results/join_regs.svg')
    #pp.close('all')
    return regs

#==========================================================

def join_bins_1(paths,bins,mask=None,suptitle=None,show=False,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS
    Combines a set of binned regions (flux-wise) at different wavelengths
    ---------------------------------------------
    ARGS:
    paths:  list of paths to the FITS images associated to each binned region
    bins:   dictionary including lists of the flux bins for each wavelength
    ---------------------------------------------
    KWARGS:
    mask:   mask to apply to the images, if any
    suptitle:   suptitle of the resulting image
    show:   show the resulting image
    save:   save the resulting image
    ---------------------------------------------
    """
    F=fits.open(paths[0])[1].data
    S=F.shape
    mapa=np.zeros(S)
    i=0
    #m=[]
    for b in bins:
        F=fits.open(paths[i])[1].data
        F[np.isnan(F)]=-100
        F[F==0]=-100
        for l in bins[b][1:-1]:
            mask=F>=l
            mask[mask==True]=1
            mask[mask==False]=0
            mapa=mapa+mask
            #m.append(mask)
        i+=1
    mapa[mapa==0]=np.nan
    mapa=mapa-np.nanmin(mapa)+1
    if show:
        l=len(np.unique(mapa)[:-1])
        i=1
        while i**2<l:
            i+=1
        n_cols,n_rows=i,i
        while n_rows*n_cols>=l:
            n_rows-=1
        n_rows=n_rows+1
        fig1=pp.figure(figsize=(n_cols*3,n_rows*3))
        lista=[]
        for i in range(int(l)):
            m=mapa==np.unique(mapa)[i]
            if len(np.unique(m))>1:
                ax=fig1.add_subplot(n_rows,n_cols,i+1)
                ax.imshow(mapa*m,origin='lower')
                bound=np.argwhere(~np.isnan(mapa*m))
                ax.set_xlim(min(bound[:, 1])-2, max(bound[:, 1])+2)
                ax.set_ylim(min(bound[:, 0])-2, max(bound[:, 0])+2)
                ax.set_xticks([])
                ax.set_yticks([])
                lista.append(mapa*m)
        fig2=pp.figure(figsize=(10,10))
        pp.imshow(mapa,origin='lower',cmap='coolwarm')
        bound=np.argwhere(~np.isnan(mapa))
        pp.xlim(min(bound[:, 1])-2, max(bound[:, 1])+2)
        pp.ylim(min(bound[:, 0])-2, max(bound[:, 0])+2)
        pp.xticks([])
        pp.yticks([])

        pp.show(block=False)
    return mapa,lista


def binSNR(F,E,mask):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    works out the total SNR of a masked region of pixels using SNR_bin=sqrt(sum(snr_pix))
    ---------------------------------------------
    ARGS:
    F:  flux of the image
    E:  associated error of the flux
    mask:   mask to apply to the image
    ---------------------------------------------
    """
    F[~np.isfinite(F)]=0
    snr_map=F*mask/E
    snr_map[snr_map<0]=0 #bins w/ SNR<0 are converted into 0
    snr_bin=np.sqrt(np.nansum(snr_map**2))
    return snr_bin


def SNR_calc(F,E,snr,nbins=50):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    I don't know man, but returns the masks for each binned region and their respective SNR
    ---------------------------------------------
    ARGS:
    F:  flux array, NxM, of the image
    E:  error aray, NxM, of the image
    snr:    desired minimum signal-to-noise ratio for each bin
    ---------------------------------------------
    KWARGS:
    nbins:  initial numbers of bins. It will be reduced in order to obtained the desired bin SNR
    ---------------------------------------------
    """
    bins=np.linspace(np.nanmax(F),0,nbins+1) #creating edges of the bins, in flux values
    check=np.copy(F)
    masks,snrs=[],[]
    #initial values for the loops
    i,j=0,0
    snr_check=-1
    #this loops works by checking if all pixels have been associated to a region (i.e. masked from the general image). Regions are created by joining pixels in the same flux bin, and then the overal SNR is calcualted. If this is above the desired SNR, these pixels al descarted from the general image and the same operation is repeated for the next flux bin; on the other hand if the minimum SNR is nor achieved, pixels form the next bin are also added to the calcualtion, until the minimum SNR is achieved. If buy adding the remaining pixels the minimum SNR is not achieved, this will be considered the last bin
    edg=[bins[i]]
    while np.nansum(check)>0:
        mask=np.ones(F.shape)
        mask[F<=bins[i]]=0
        mask[F>bins[j]]=0
        snr_check=binSNR(F,E,mask)
        i+=1
        if snr_check>snr:
            masks.append(mask)
            snrs.append(snr_check)
            check=check*(1-mask)
            j=i-1
            snr_check=-1
            edg.append(bins[i])
        elif i==len(bins): #If we reach the maximum number of bins, we break the loop
            masks.append(mask)
            snrs.append(snr_check)
            edg.append(bins[-1])
            break
    #For my next trick, I will copy Mauro's code and apply it
    structure=np.ones((3, 3), dtype=int)
    labels,nlabels=[],[]
    lbl=np.zeros(F.shape)
    #return masks,snrs
    for i in range(len(masks)):
        l,nl=label(masks[i],structure)
        labels.append(l)
        nlabels.append(nl)
        lbl+=l+np.nanmax(lbl)*(l>0)
    return masks,snrs,labels,nlabels,lbl,edg

#----------------------------------------------------------

def bands_win(sp,bands,z):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Show the bands' ranges in a spectrum image
    ---------------------------------------------
    ARGS:
    sp: spectrum data, a Nx2 array with wavelength in um and flux in any unit
    bands:  list of bands inside de BANDS dictionary
    z: object's redshift, if sp is in observed frame
    ---------------------------------------------
    """
    #pp.close('all')
    cmap=['purple','b','cyan','olive','g','yellow','navajowhite','orange','r']
    spec=np.copy(sp)
    spec[:,0]=spec[:,0]*1e4 #asumimos input wl en um
    fig,ax=pp.subplots(1,1,figsize=(16,9))
    ax.plot(spec[:,0],spec[:,1],c='k')
    for i in range(len(bands)):
        ax.axvspan(BANDS[bands[i]][0]*(1+z),BANDS[bands[i]][1]*(1+z),color=cmap[i],alpha=0.5)
    pp.show(block=False)

#==========================================================

def SED_and_regs(sed,mask,ignore_bins=None,fact=20,labels=None,title=None,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    plots the SEDs and binned map of a galaxy that has been binned and has a distinct SED for each binned region.
    NOTE THAT THE FLUX IS RENORMALIZED SO FLUX_UV IS 1!!!!!
    ---------------------------------------------
    ARGS:
    sed:    list of SEDs. they can be either dictionaries obtained from BP_fit (see astrolaza.LazaPipes.fitting) or 2D array with columns wavelength, flux and flux error
    mask:   2D array including all the masks for each binned region. Usually, each region is associated with an integer
    ---------------------------------------------
    KWARGS:
    fact:   binning factor, in case a wavelength binning is desired, e.g. fact 5 implies the SED will be binned in groups 5 wavelengths.
    labels: list of 2 elements contianing the label name for the observed and fitted data
    title:  title of the plot
    save:   save the resulting figure. Can be either True or the string path to the save location + file name
    ----------------------------------------------
    """
    c=2.99792458e+18 #speed of light in AA/s
    bins=np.unique(mask)
    if not labels:
        labels=[None]*2*len(bins)
    while len(bins)>len(labels):
        labels.append(None)
    if np.isnan(bins[-1]):
        bins=bins[:-1]

    #Plotting the SED
    #Creating the color palette (for plots and maps)
    cmap=pp.colormaps['coolwarm_r']
    if ignore_bins:
        ignore_bins=np.asarray(ignore_bins)
        ib=True
        lbins=len(bins)-len(ignore_bins)
    else:
        ib=False
        lbins=len(bins)
    colors=cmap(np.linspace(0,1,lbins))
    mod_cmap=LCM([colors[i] for i in range(lbins)]) #recreating the colormap in case some bins must be ignored
    mod_cmap.set_under(color='k')
    #Creating the figure frame
    fig=pp.figure(figsize=(16,9))
    gs=GS(2,1,height_ratios=[3,1],hspace=0) #2 plots; top full height SEDs, bottom zoomed in SEDs
    ax=fig.add_subplot(gs[0])
    ax.set_ylim(bottom=-0.5,top=None,auto=True)
    ax.yaxis.get_major_ticks()[0].label1.set_visible(False)
    pp.setp(ax.get_xticklabels(which="both"),visible=False)
    ax2=fig.add_subplot(gs[1],sharex=ax)
    ax2.yaxis.get_major_ticks()[-1].label1.set_visible(False)
    #adding a small plot with a zoom in of the UV region (1.5-2.2 um)
    # ax.set_ylim([0,1])
    ins2=ax.inset_axes([0.16,0.5,0.28,0.25])
    ins2.set_xlim([1.4,2.3])
    ins2.set_xticks(np.arange(1.4,2.4,0.1))
    ins2.set_title('UV$_{obs}$')
    #Working out some necessary quantities
    minmax=[]
    UVflux_o=[]
    UVflux_f=[]
    for i in range(len(bins)):
        if type(sed[i])==str:
            data=LPdh.load_post(sed[i])
            wl=data['wavelength_obs']
            f=data['spectrum_obs']*wl**2/c*1e29
            e=data['err_spectrum_obs']*wl**2/c*1e29
            ff=(wl**2/c)*np.nanpercentile(data['spectrum'],(50),axis=0)*1e29
            fe=(wl**2/c)*np.nanpercentile(data['spectrum'],(16,84),axis=0)*1e29

            # print(np.nanmean(f[np.where((wl>=15000) & (wl<=22000))])
            UVflux_o.append(np.nanmean(f[np.where((wl>=15000) & (wl<=22000))]))
            UVflux_f.append(np.nanmean(ff[np.where((wl>=15000) & (wl<=22000))]))
    UVfact_o=[]
    UVfact_f=[]
    for i in range(len(bins)):
        UVfact_o.append(UVflux_o[-1]/UVflux_o[i])
        UVfact_f.append(UVflux_f[-1]/UVflux_f[i])
    # print(UVfact_o,UVfact_f)
    #Plotting the SEDs in each subplot
    j=0 #this is for colors in case some bins are ignored
    for i in range(len(bins)):
        if ib and i+1 in ignore_bins:
            mask[mask==i+1]=-99
            pass
        else:
            if type(sed[i])==str:
                data=LPdh.load_post(sed[i])
                wl=data['wavelength_obs']
                f=data['spectrum_obs']*wl**2/c*1e29
                e=data['err_spectrum_obs']*wl**2/c*1e29
                ff=(wl**2/c)*np.nanpercentile(data['spectrum'],(50),axis=0)*1e29
                fe=(wl**2/c)*np.nanpercentile(data['spectrum'],(16,84),axis=0)*1e29

                #renormalize to have a UVFlux=1
                """
                UVflux_o=trapezoid(data['spectrum_obs'][np.where((wl>=15000) & (wl<=22000))],wl[np.where((wl>=15000) & (wl<=22000))])
                UVflux_f=trapezoid(np.nanpercentile(data['spectrum'],(50),axis=0)[np.where((wl>=15000) & (wl<=22000))],wl[np.where((wl>=15000) & (wl<=22000))])
                """
                #f,e=f/UVflux_o,e/UVflux_o
                #ff,fe=ff/UVflux_f,fe/UVflux_f
            elif type(sed[i])==np.ndarray:
                wl=sed[i][:,0]
                f=(wl**2/c)*1e29*sed[i][:,1]
                e=(wl**2/c)*1e29*sed[i][:,2]
                ff=None
                fe=None
            # f,e=f/UVflux_o[i],e/UVflux_o[i]
            f,e=f*UVfact_o[i]/fact,e*UVfact_o[i]/fact
            ff,fe=ff*UVfact_f[i]/fact,fe*UVfact_f[i]/fact
            ax.fill_between(wl*1e-4,(f-e),(f+e),alpha=0.5,color=colors[j])
            ax.plot(wl*1e-4,f,c=colors[j],label=labels[0]+' bin %i' % (i+1))
            ax2.fill_between(wl*1e-4,(f-e),(f+e),alpha=0.5,color=colors[j])
            ax2.plot(wl*1e-4,f,c=colors[j])
            if ff.any() and fe.any():
                ax.fill_between(wl*1e-4,fe[0,:],fe[1,:],alpha=0.5,color=colors[j],step='mid')
                ax.step(wl*1e-4,ff,c=colors[j],ls='--',where='mid',label=labels[1]+' bin %i' % (i+1))
                ax2.fill_between(wl*1e-4,fe[0,:],fe[1,:],alpha=0.5,color=colors[j],step='mid')
                ax2.step(wl*1e-4,ff,c=colors[j],ls='--',where='mid')
            ins2.fill_between(wl*1e-4,(f-e),(f+e),alpha=0.5,color=colors[j])
            ins2.plot(wl*1e-4,f,c=colors[j],label=labels[0]+' bin %i' % (i+1))
            minmax.append([np.nanmin(f[(wl>=15000) & (wl<=22000)]),np.nanmax(f[(wl>=15000) & (wl<=22000)])])
            # ax.plot(wl*1e-4,wl*1e-4*cont(np.stack((wl,f,e),axis=1),[14000,23000])[0]+cont(np.stack((wl,f,e),axis=1),[14000,23000])[1],ls=':',c=colors[j])
            j+=1
    minmax=np.asarray(minmax)
    mid=(np.nanmin(minmax)+np.nanmax(minmax))/2
    ins2.set_ylim([mid-(mid-np.nanmin(minmax))*1.2,mid+(np.nanmax(minmax)-mid)*1.2])
    ax2.set_ylim([mid-(mid-np.nanmin(minmax))*1.2,mid+(np.nanmax(minmax)-mid)*2*np.sqrt(fact)])
    #ax2.set_ylim([2,10])
    ax2.set_xlabel('$\mathrm{\lambda}$ ($\mathrm{\mu}$m)',size=20)
    ax.set_ylabel(r'f$_{\mathrm{\nu}}$ ($\mathrm{\mu}$Jy)',size=20)
    ax.tick_params(axis='both',which='major',labelsize=20)
    ax2.tick_params(axis='both',which='major',labelsize=20)
    ax.set_title(title)
    ax.legend()
    #adding small map of the masked target
    ar=mask.shape[0]/mask.shape[1]
    ins=ax.inset_axes([0.39,0.5,0.35,0.35*ar])
    vmin=np.nanmin(mask[np.where(mask>0)])
    im=ins.imshow(mask,origin='lower',cmap=mod_cmap,vmin=vmin,vmax=np.nanmax(mask)+1)
    zoomin(mask,ins)
    ins.set_xticks([])
    ins.set_yticks([])
    ins.set_xlabel('Bins distribution')
    return mod_cmap
    if save:
        if type(save)==bool:
            if title:
                fig.savefig('%s_SEDs+regs.svg' % (title))
            else:
                fig.savefig('SEDs+regs.svg')
        elif type(save)==str:
            mkdirs(save,fil=True)
            fig.savefig(save)


        
