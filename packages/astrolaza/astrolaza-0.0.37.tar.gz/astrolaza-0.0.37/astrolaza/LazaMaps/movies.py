#
import numpy as np

import matplotlib.pyplot as pp
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import FormatStrFormatter

import matplotlib.gridspec as gs

import glob as glob
from natsort import natsorted as ns

import shutil as su
import os

import moviepy.video.io.ImageSequenceClip as ISC

from ..LazaUtils.get import get_index
from ..LazaUtils.MPF import mkdirs
from ..LazaVars.dics import index, lat_let, lat_labels
from ..LazaPipes.data_handling import load_post
from ..LazaFlux.SED import remove_bad_values, change_units, smooth_sed

#==========================================================

def mapSED_mov(pixarr,seds,fit_seds=None,param=False,map_title='',suptitle='',wl_unit='AA',f_unit='ergscma',smooth=None,save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a movie showing the resolved map of the object and the associated SED of each pixel
    ---------------------------------------------
    ARGS:
    pixarr: array containing the X and Y positions of the object. If 'param' is defined, a third column containing the associated values of the parameter is needed.
    seds:   list of paths or list of Nx2 arrays containing the SEDs associated to each pixel. First column must be wavelength in amstrongs (AA) and second column flux density, in erg s-1 cm-2 A-1 (ergscma) for all spectrum. This files can be either plain text or np5 files obtained from LazaPipes.BP_fit
    ---------------------------------------------
    KWARGS:
    fit_seds: list as seds, but containing the data for fitted seds (or whatever other seds needed to be plotted)
    param:  if True, it is assumed pixarr is (at least) a Nx3 array where the last column is the parameter value
    map_title:  pixel map title
    suptitle:  plot super title
    wl_unit:  wavelength unit for the SED plot. Default is amstrong (AA). It can also be any meter-derived unit (mm,um,nm,etc)
    f_unit: flux unit for the SED plot. Default is erg s-1 cm-2 A-1 (ergscma). It can also be any jansky-derive unit (ujy,njy,etc)
    smooth: smooth (bin) the spectras according to the smooth_sed function. It can be an int to smooth only the seds inputs, a list/tuple of 2 ints, to smooth both the seds and fit_seds or an array of Nx2 (N equal to the length of seds) containing the smoothing factor for seds and fit_seds for each spectra.
    save:   save the resulting movie. If True, it will be saved as mapSED_mov.mp4 in teh working directory; if a path, it will be saved in the given path
    ---------------------------------------------
    """
    #checking for input errors
    if type(pixarr)!=np.ndarray:
        print('pixarr must be either a Nx2 or a Nx3 array, with the first 2 columns the x and y pixel coordinates!')
        return
    elif param and pixarr.shape[1]<3:
        print('if you want to show a param value to be shown, pixarr must include a 3rd column with said values!')
        return
    if type(seds)!=list:
        print('seds must be a list containing the paths to the SEDs files or the SEDs themselves!')
        return
    elif type(seds[0]) not in [np.ndarray,str]:
        print('Each element in seds must be either the array with the wavelengths anf lux density or the path to the file!')
    if len(pixarr[:,0])!=len(seds):
        print('There must be as many SEDs as pixels in the object (lengths of pixarr and seds do not match)!')
        return
    if fit_seds and (type(fit_seds)!=list or len(seds)!=len(fit_seds)):
        print('fit_seds must have the same length (and order) that seds!')
        return
    #getting proper index
    index=index
    wl_ind,wl_unit=get_index(wl_unit)
    f_ind,f_unit=get_index(f_unit)
    #creating the map
    fig=pp.figure(figsize=(20,5))
    pp.suptitle(suptitle)
    margin=3
    x,y=pixarr[:,0],pixarr[:,1]
    xmin,xmax=np.nanmin(x),np.nanmax(x)
    ymin,ymax=np.nanmin(y),np.nanmax(y)
    mapa=np.ones([int(xmax-xmin+2*margin),int(ymax-ymin+2*margin)])*np.nan
    if not param:
        fit_spec=[]
        spec=[]
        GS=gs.GridSpec(1,2,width_ratios=[1,3])
        for i in range(len(x)):
            xi=int(x[i]-xmin+margin)
            yi=int(y[i]-ymin+margin)
            mapa[xi,yi]=1 #creating the pixel map
            sed=seds[i]
            if type(sed)==str: #we get the sed data
                if sed[-3:]=='npy':
                    l=load_post(sed)
                    sed=np.stack((l['wavelength_obs'],l['spectrum_obs']),axis=1)
                    sed=remove_bad_values(sed,1)
                else:
                    sed=np.loadtxt(sed,comments='#',usecols=(0,1))
                    sed=remove_bad_values(sed,1)
            if fit_seds:
                fit_sed=fit_seds[i]
                if type(fit_sed)==str:
                    if fit_sed[-3:]=='npy':
                        l=load_post(fit_sed)
                        fit_sed=np.stack((l['wavelength_obs'],np.nanmedian(l['spectrum'],axis=0)),axis=1)
                        fit_sed=remove_bad_values(fit_sed,1)
                    else:
                        fit_sed=np.loadtxt(fit_sed,comments='#',usecols=(0,1))
                        fit_sed=remove_bad_values(fit_sed,1)
            else:
                fit_sed=np.zeros([2,2])*np.nan
            if smooth:
                if type(smooth)==int:
                    sed=smooth_sed(sed,smooth)
                elif type(smooth) in [list,tuple]:
                    sed=smooth_sed(sed,smooth[0])
                    fit_sed=smooth_sed(fit_sed,smooth[1])
                elif type(smooth)== np.ndarray:
                    sed=smooth_sed(sed,smooth[i,0])
                    fit_sed=smooth_sed(fit_sed,smooth[i,1])
            spec.append(change_units(sed,wl_unit,f_unit))
            fit_spec.append(change_units(fit_sed,wl_unit,f_unit))
        mkdirs('mapsedmov/a') #creating a directory where save everything; it will be deleted later
        gsmap=pp.subplot(GS[0])
        gsmap.imshow(mapa,origin='lower',vmin=xmin,vmax=xmax,aspect='auto')
        gsmap.set_yticks([])
        gsmap.set_xticks([])
        gsmap.title.set_text(map_title)
        gsspec=pp.subplot(GS[1])
        for i in range(len(x)):
            gsspec.clear()
            gsspec.step(spec[i][:,0],spec[i][:,1],ls='-',c='k')
            if fit_seds:
                gsspec.plot(fit_spec[i][:,0],fit_spec[i][:,1],ls='-',c='r',label='Fit data')
            ax=pp.gca()
            pp.legend()
            gsspec.set_xscale('log')
            pp.tick_params(axis='x',which='minor')
            ax.xaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
            ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
            if wl_unit=='AA':
                pp.xlabel(r'$\mathrm{\lambda (\AA)}$',fontsize=15)
            elif wl_unit[-1]=='m':
                lat=lat_let
                pp.xlabel(r"$\mathrm{\lambda (%s m)}$" % (lat[wl_unit[0]]),fontsize=15)
            if f_unit=='ergscma':
                pp.ylabel(r'f$_{\lambda}$ (erg s$^{-1}$ cm$^{-2}$ $\mathrm{\AA^{-1}}$)',fontsize=15)
            elif f_unit[-2:]=='jy':
                pp.ylabel(r"$\mathrm{f_{\nu} (%s Jy)} $" % lat[f_unit[0]],fontsize=15)
            pp.ylim([-0.1*np.nanmax(spec[i][:,1]),0.1*np.nanmax(spec[i][:,1])])
            gsspec.title.set_text('Spectral Energy Distribution')
            rect=pp.Rectangle((int(y[i]-ymin+margin)-0.5,int(x[i]-xmin+margin)-0.5),1,1,fill=False,color='r') #adding a rectangle to show which pixel is associated to the given SED
            gsmap.add_patch(rect)
            pp.savefig('mapsedmov/%i_%i.png' % (x[i],y[i]),dpi=200)
            rect.remove()
    elif param:
        spec=[]
        fit_spec=[]
        param=pixarr[:,2]
        GS=gs.GridSpec(1,3,width_ratios=[0.05,1,3])
        for i in range(len(x)):
            xi=int(x[i]-xmin+margin)
            yi=int(y[i]-ymin+margin)
            mapa[xi,yi]=param[i]
            sed=seds[i]
            if type(sed)==str: #we get the sed data
                if sed[-3:]=='npy':
                    l=load_post(sed)
                    sed=np.stack((l['wavelength_obs'],l['spectrum_obs']),axis=1)
                    sed=remove_bad_values(sed,1)
                else:
                    sed=np.loadtxt(sed,comments='#',usecols=(0,1))
                    sed=remove_bad_values(sed,1)
            if fit_seds:
                fit_sed=fit_seds[i]
                if type(fit_sed)==str:
                    if fit_sed[-3:]=='npy':
                        l=load_post(fit_sed)
                        fit_sed=np.stack((l['wavelength_obs'],np.nanmedian(l['spectrum'],axis=0)),axis=1)
                        fit_sed=remove_bad_values(fit_sed,1)
                    else:
                        fit_sed=np.loadtxt(fit_sed,comments='#',usecols=(0,1))
                        fit_sed=remove_bad_values(fit_sed,1)
            else:
                fit_sed=np.zeros([2,2])*np.nan
            if smooth:
                if type(smooth)==int:
                    sed=smooth_sed(sed,smooth)
                elif type(smooth) in [list,tuple]:
                    sed=smooth_sed(sed,smooth[0])
                    fit_sed=smooth_sed(fit_sed,smooth[1])
                elif type(smooth)== np.ndarray:
                    sed=smooth_sed(sed,smooth[i,0])
                    fit_sed=smooth_sed(fit_sed,smooth[i,1])
            spec.append(change_units(sed,wl_unit,f_unit))
            fit_spec.append(change_units(fit_sed,wl_unit,f_unit))
        mkdirs('mapsedmov/a') #creating a directory where save everything; it will be deleted later
        gsmap=pp.subplot(GS[1])
        gsmap.imshow(mapa,origin='lower',vmin=xmin,vmax=xmax,aspect='auto')
        gsmap.set_yticks([])
        gsmap.set_xticks([])
        gsmap.title.set_text(map_title)
        val=gsmap.imshow(mapa,origin='lower',cmap='summer')
        bar=pp.subplot(GS[0])
        ticks=np.linspace(np.nanmin(mapa),np.nanmax(mapa),5)
        fig.colorbar(val,cax=bar,format='%.3f',location='left',ticks=ticks)
        gsspec=pp.subplot(GS[2])
        cmap=pp.get_cmap('summer')
        for i in range(len(x)):
            gsspec.clear()
            color=cmap((param[i]-np.nanmin(param))/(np.nanmax(param)-np.nanmin(param))) #cmap funciona con un vector de 0 a 1, así que tenemos que renormalizar para que vmin equivalga a 0 y vmax a 1. para ello, restamos al valor que tenemos vmin y dividimens entre la diferencia de vmax con vmin
            gsspec.step(spec[i][:,0],spec[i][:,1],ls='-',c=color,label='Raw data')
            gsspec.axhline(0,c='k',zorder=-1)
            if fit_seds:
                gsspec.plot(fit_spec[i][:,0],fit_spec[i][:,1],ls='-',c='r',label='Fit data')
            ax=pp.gca()
            pp.legend()
            #gsspec.set_xscale('log')
            pp.tick_params(axis='x',which='minor')
            ax.xaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
            ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
            ax.yaxis.tick_right()
            if wl_unit=='AA':
                pp.xlabel(r'$\mathrm{\lambda (\AA)}$',fontsize=15)
            elif wl_unit[-1]=='m':
                lat=lat_let
                pp.xlabel(r"$\mathrm{\lambda (%s m)}$" % (lat[wl_unit[0]]),fontsize=15)
            if f_unit=='ergscma':
                pp.ylabel(r'f$_{\lambda}$ (erg s$^{-1}$ cm$^{-2}$ $\mathrm{\AA^{-1}}$)',fontsize=15)
                ax.yaxis.set_label_position('right')
            elif f_unit[-2:]=='jy':
                pp.ylabel(r"$\mathrm{f_{\nu} (%s Jy)} $" % lat[f_unit[0]],fontsize=15)
                ax.yaxis.set_label_position('right')
            pp.ylim([-0.05*np.nanmax(spec[i][:,1]),0.5*np.nanmax(spec[i][:,1])])
            gsspec.title.set_text('Spectral Energy Distribution - X: %i, Y: %i' % (x[i],y[i]))
            rect=pp.Rectangle((int(y[i]-ymin+margin)-0.5,int(x[i]-xmin+margin)-0.5),1,1,fill=False,color='r') #adding a rectangle to show which pixel is associated to the given SED
            gsmap.add_patch(rect)
            pp.subplots_adjust(wspace=0.05,hspace=0)
            pp.savefig('mapsedmov/%i_%i.png' % (x[i],y[i]),dpi=200)
            rect.remove()
    if save:
        clips=ns(glob.glob('mapsedmov/*'))
        movie=ISC.ImageSequenceClip(clips,fps=1)
        movie.write_videofile('mapSED_mov.mp4')
        if type(save)==str:
            mkdirs(save)
            su.move('mapSED_mov.mp4',save)
            name=save.split('/')
            print('\n========================================\nA movie (mp4 file) named %s has been saved at %s!\n========================================' % (name[-1],save))
        else:
            print('\n========================================\nA movie (mp4 file) named mapDis_mov.mp4 has been saved at the working directory!\n========================================')
    su.rmtree('mapsedmov')
    return
    
#==========================================================

def mapDis_mov(pixarr,post,par_key,bins=100,map_title='',suptitle='',save=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Creates a movie including the map of a parameter of a resolved object and the distribution of the posterior fit of the parameter for each pixel
    ---------------------------------------------
    ARGS:
    pixarr: array containing the X and Y pixel coordinates and the parameter value of the resolved object, in that order. See get_from_cat to get this array
    post:   list of paths to the posterior files or list of 1D arrays containing the distirbution values of the parameter
    par_key:    parameter key inside the dictionary, if post are posterior files
    ---------------------------------------------
    KWARGS:
    bins:   number of bins to plot in the distribution
    map_title:  title of the map
    suptitle:   super title of the figure
    save:   save the resulting video. If True, it will be saved in the working directory as mapDis_mov.mp4; if a path, it will be saved in the given path with the given name.
    ---------------------------------------------
    """
    #checking for input errors
    if type(pixarr)!=np.ndarray:
        print('pixarr must be a Nx2 array containing the X and Y pixel coordinates!')
        return
    elif pixarr.shape[1]<3:
        print('pixarr must have at least 3 columns, containing the X and Y pixel positions and the parameter value, in that order. It is adviced to use get_from_cat to obtain this array')
        return
    if type(post)!=list:
        print('post must be a list containing either the paths to the post files or Nx1 arrays eith the values of the distribution of the parameter for each pixel!')
        return
    elif len(pixarr)!=len(post):
        print('xy and post must have the same length! (There must be one post file per pixel)')
        return
    #creating the map and the list to containg all pixels' data
    margin=3
    x,y=pixarr[:,0],pixarr[:,1]
    xmin,xmax=np.nanmin(x),np.nanmax(x)
    ymin,ymax=np.nanmin(y),np.nanmax(y)
    mapa=np.ones([int(xmax-xmin+2*margin),int(ymax-ymin+2*margin)])*np.nan
    param=pixarr[:,2]
    valueses=[]
    for i in range(len(x)):
        xi=int(x[i]-xmin+margin)
        yi=int(y[i]-ymin+margin)
        mapa[xi,yi]=param[i]
        if type(post[i])==str: #we get the distribution data
            if post[i][-3:]=='npy':
                l=load_post(post[i])
                try:
                    values=l[par_key]
                except KeyError:
                    print('par_key is not in the post file dcitionary! You can check the keys available using LazaPipes.load_post stating print_keys=True')
                    return
            else:
                values=np.loadtxt(p,comments='#')
        elif type(post[i])==np.ndarray():
            values=post[i]
        valueses.append(values)
    mkdirs('mapdismov/a') #creating a directory where save everything; it will be deleted later
    #Creating the figures
    fig=pp.figure(figsize=(20,5))
    pp.suptitle(suptitle)
    GS=gs.GridSpec(1,3,width_ratios=[0.05,1,3])
    gsmap=pp.subplot(GS[1])
    gsmap.imshow(mapa,origin='lower',vmin=xmin,vmax=xmax,aspect='auto')
    gsmap.set_yticks([])
    gsmap.set_xticks([])
    gsmap.title.set_text(map_title)
    val=gsmap.imshow(mapa,origin='lower',cmap='summer')
    bar=pp.subplot(GS[0])
    ticks=np.linspace(np.nanmin(mapa),np.nanmax(mapa),5)
    fig.colorbar(val,cax=bar,format='%.3f',location='left',ticks=ticks)
    gsdis=pp.subplot(GS[2])
    cmap=pp.get_cmap('summer')
    for i in range(len(x)):
        gsdis.clear()
        color=cmap((param[i]-np.nanmin(param))/(np.nanmax(param)-np.nanmin(param))) #cmap funciona con un vector de 0 a 1, así que tenemos que renormalizar para que vmin equivalga a 0 y vmax a 1. para ello, restamos al valor que tenemos vmin y dividimens entre la diferencia de vmax con vmin
        #See get_distribution for a better explanation fo this part (I copy-pasted)
        median=np.nanmedian(valueses[i])
        vmin,vmax=np.nanmin(valueses[i]),np.nanmax(valueses[i])
        edges=np.histogram(valueses[i],bins=bins,range=(vmin,vmax))[1]
        hist=gsdis.hist(valueses[i],bins=edges,range=(vmin,vmax),rwidth=0.8,histtype='step',color=color)
        gsdis.axvline(median,color='r',ls='--')
        ax=pp.gca()
        ax.annotate('Median: %.3f' % (median),(median+(edges[1]-edges[0])/2,np.percentile(np.histogram(valueses[i],bins=bins,range=(vmin,vmax))[0],80)),xycoords='data',weight='bold',color='k',rotation='vertical',)
        #print(median,vmin,vmax,(median-vmin)/(vmax-vmin))
        variables=lat_labels
        try:
            pp.xlabel(variables[par_key])
        except KeyError:
            pp.xlabel(par_key)
        pp.ylabel('Ocurrences (%i bins)' % (bins))
        ax.yaxis.set_label_position('right')
        ax.yaxis.tick_right()
        gsdis.title.set_text('Posterior Distribution - X: %i, Y: %i' % (x[i],y[i]))
        rect=pp.Rectangle((int(y[i]-ymin+margin)-0.5,int(x[i]-xmin+margin)-0.5),1,1,fill=False,color='r') #adding a rectangle to show which pixel is associated to the given SED
        gsmap.add_patch(rect)
        pp.subplots_adjust(wspace=0.05,hspace=0)
        pp.savefig('mapdismov/%i_%i.png' % (x[i],y[i]),dpi=200)
        rect.remove()
    if save:
        clips=ns(glob.glob('mapdismov/*'))
        movie=ISC.ImageSequenceClip(clips,fps=1)
        movie.write_videofile('mapDis_mov.mp4')
        if type(save)==str:
            mkdirs(save)
            su.move('mapDis_mov.mp4',save)
            name=save.split('/')
            print('\n========================================\nA movie (mp4 file) named %s has been saved at %s!\n========================================' % (name[-1],save))
        else:
            print('\n========================================\nA movie (mp4 file) named mapDis_mov.mp4 has been saved at the working directory!\n========================================')
    su.rmtree('mapdismov')
    return


