from .corrections import *
from .data_handling import *

import numpy as np

import matplotlib.pyplot as pp
from matplotlib.ticker import FormatStrFormatter
from matplotlib import gridspec as gs

import glob as glob

from natsort import natsorted as ns

import bagpipes as bp

import os

import shutil as su

import threading as th
import subprocess as sp

import time as tm

from datetime import timedelta

from scipy.integrate import trapezoid

from ..LazaUtils.MPF import choose_var
from ..LazaVars.dics import index, lat_let
from ..LazaGal.mass import ageX, btime

#==========================================================

def plot_figs(fit,plots,xaxis='AA',yaxis=None,box=None,save_plots=None,show=False):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    Plot figures using the bagpipes pipeline, as in the original software
    ---------------------------------------------
    ARGS:
    fit:    path to the data to fit. It must a be a dict loaded from the load_post function
    plots:  list including the desired plots. Elements of the list can be 'fv', 'fy', 'sfh'
    ---------------------------------------------
    KWARGS:
    xaxis:  x-axis units of the SED plots. Default is amstrongs ('AA'). Other options are meter-derived units (i.e. 'nm' - nanometers, 'um' - micrometers', etc.)
    yaxis:  y-axis units of the SED plots. Default is erg s-1 cm-2 AA-1 ('ergscma'). Other options are Jansky-related units (i.e. 'jy' - jansky, 'ujy' - microjansky, etc
    box:    list of fit.keys(). Draws a box in the SED plots including the results of the given keys. If None, the box won't be drawn
    save_plots: save the plots. Can be either a path or True to save in the same directory from where the data was taken
    show:   bool. Shows the plots. Default is False
    ---------------------------------------------
    """
    if 'fv' in plots:
        if yaxis:
            fig_fv=plotSED(fit,box=box,xaxis=xaxis,yaxis=yaxis)
        else:
            fig_fv=plotSED(fit,box=box,xaxis=xaxis,yaxis='ujy')
        if show:
            pp.show(block=False)
        if type(save_plots)==str:
            pp.savefig(save_plots,dpi=200)
            print('==============================================\nSED plot (f_nu vs wavelength) saved at %s\n==============================================\n' % (save_plots))
        elif type(save_plots)==bool and save_plots:
            pp.savefig('%s/SED_fv_%s_%s.svg' % (fit['info']['path'],fit['info']['ID'],fit['info']['run']))
            print('==============================================\nSED plot (f_nu vs wavelength) saved at %s/SED_fv_%s_%s.svg\n==============================================\n' % (fit['info']['path'],fit['info']['ID'],fit['info']['run']))
    if 'fy' in plots:
        fig_fy=plotSED(fit,box=box,xaxis=xaxis,yaxis='ergscma')
        if show:
            pp.show(block=False)
        if type(save_plots)==str:
            pp.savefig(save_plots,dpi=200)
            print('==============================================\nSED plot (f_lambda vs wavelength) saved at %s\n==============================================\n' % (save_plots))
        elif type(save_plots)==bool and save_plots:
            pp.savefig('%s/SED_fy_%s_%s.svg' % (fit['info']['path'],fit['info']['ID'],fit['info']['run']))
            print('==============================================\nSED plot (f_lambda vs wavelength) saved at %s/SED_fy_%s_%s.svg\n==============================================\n' % (fit['info']['path'],fit['info']['ID'],fit['info']['run']))
    if 'sfh' in plots:
        sfr=np.flip(np.percentile(fit["sfh"],(50,84,16),axis=0).T,axis=0)
        bt=btime(fit)
        i20=ageX(fit,0.2)[0]
        i50=ageX(fit,0.5)[0]
        fig=pp.figure(figsize=(14,8))
        pp.plot(bt,sfr[:,0],c='k',ls='-',marker=None,label='SFH')
        pp.yscale('log')
        pp.tick_params(axis='y',which='minor')
        ax=pp.gca()
        ax.set_yscale('log')
        #ax.yaxis.set_major_formatter(FormatStrFormatter())
        pp.fill_between(bt,sfr[:,1],sfr[:,2],color='gray',linewidth=0,alpha=0.5)
        pp.axvline(i20,color='r',ls='--',label=r'Age$_{20}$')
        pp.axvline(i50,color='b',ls=':',label=r'Age$_{50}$')
        pp.xlim([np.nanmax(bt[bt>=0]),np.nanmin(bt[bt>=0])])
        pp.legend()
        pp.xlabel('Time (Gyr)',fontsize=20)
        pp.ylabel(r'SFR (M$_{\odot}$ yr$^{-1}$)',fontsize=20)
        pp.xticks(fontsize=20)
        pp.yticks(fontsize=20)
        pp.title('Star Formation History - %s (%s)' %(fit['info']['ID'],fit['info']['run']),fontsize=20)
        #pp.
        if show:
            pp.show(block=False)
        if type(save_plots)==str:
            pp.savefig(save_plots)
            print('==============================================\nStar Formation History plot saved at %s\n==============================================\n' % (save_plots))
        elif type(save_plots)==bool and save_plots:
            pp.savefig('%s/SFH_%s_%s.svg' % (fit['info']['path'],fit['info']['ID'],fit['info']['run']))
            print('==============================================\nStar Formation History plot saved at %s/SFH_%s_%s.svg\n==============================================\n' % (fit['info']['path'],fit['info']['ID'],fit['info']['run']))
    return

#plot Spectral energy distribution (flux vs wl)
def plotSED(fit,box=None,xaxis='AA',yaxis='ergscma'):
    c=2.99792458e+18 #speed of light in AA/s
    if xaxis[-1]=='m':
        try:
            xindex=index[xaxis[0]]
        except IndexError:
            xindex=1
            xaxis='ergscma'
    elif xaxis!='AA':
        print('Units must be either amstrongs ("AA") or meter-relatd units ("nm", "um", "mm",...)!')
        return
    else:
        xindex=1
    if yaxis[-2:]=='jy':
        try:
            yindex=index[yaxis[0]]*1e-23
        except IndexError:
            yindex=1e-23
            yaxis=' jy'
    elif yaxis!='ergscma':
        print('Units must be either erg s-1 cm-2 AA-1 ("ergscma") or jansky-relatd units ("njy", "ujy", "mjy",...)!')
        return
    else:
        yindex=1
    if fit['info']['dtype']=='spec':
        wlAA=fit['wavelength_obs']
        wl=fit['wavelength_obs']*(1e-10/xindex)
        if yaxis[-2:]=='jy':
            spec=(wlAA**2/c)*fit['spectrum_obs']/yindex
            err_spec=(wlAA**2/c)*fit['err_spectrum_obs']/yindex
            spec_post=(wlAA**2/c)*fit['spectrum']/yindex
        elif yaxis=='ergscma':
            spec=fit['spectrum_obs']/yindex
            err_spec=fit['err_spectrum_obs']/yindex
            spec_post=fit['spectrum']/yindex
        spec16,spec50,spec84=np.nanpercentile(spec_post,(16,50,84),axis=0)
        fig=pp.figure(figsize=(18,10))
        fig.add_subplot(111, frameon=False)
        pp.tick_params(labelcolor="none", which="both", top=False, bottom=False, left=False, right=False)
        if yaxis=='ergscma':
            pp.ylabel(r'f$_{\lambda}$ (erg s$^{-1}$ cm$^{-2}$ $\mathrm{\AA^{-1}}$)',fontsize=15)
        elif yaxis[-2:]=='jy':
            pp.ylabel(r"$\mathrm{f_{\nu} (%s Jy)} $" % lat_let[yaxis[0]],fontsize=15)
        gsv=gs.GridSpec(2,1,height_ratios=[3,1])
        #upper subplot, full spectrum
        gsv0=pp.subplot(gsv[0])
        z=get_z(fit)
        if 'info' in list(fit.keys()):
            if 'ID' and 'run' in list(fit['info'].keys()):
            	tit=fit['info']['ID']+' ('+fit['info']['run']+')'
            elif 'ID' in list(fit['info'].keys()):
                tit=fit['info']['ID']
            else:
                tit='Unknown object'
        elif 'ID' in list(fit.keys()):
                tit=fit['ID']
        else:
            tit='Unknown object'
        if 'xy' in list(fit.keys()):
            tit=tit+' (pixel x=%03i, y=%03i)' % (fit['xy'])
        gsv0.title.set_text(tit+' - z='+str(z))
        #gsv0.title.set_text(fit['info']['ID']+' - z='+str(z))
        ax=pp.gca()
        gsv0.set_xscale('log')
        pp.tick_params(axis='x',which='minor')
        ax.xaxis.set_minor_formatter(FormatStrFormatter("%.1f"))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        #pp.xticks(np.linspace(0.5,5.5,11))
        #pp.xlim([np.round(0.1215*(1+z)*0.9,1),np.round(0.7070*(1+z),1)])
        #plotting original data
        gsv0.plot(wl,spec,ls="--",c="dodgerblue",zorder=2,label="JWST")
        gsv0.fill_between(wl,spec-err_spec,spec+err_spec,color="dodgerblue",zorder=3,linewidth=0,alpha=0.5)
        #plotting best fitting spectrum
        gsv0.plot(wl,spec50,ls="-",c="darkorange",zorder=4,label="Best fit (BP)")
        gsv0.fill_between(wl,spec16,spec84,color="navajowhite",zorder=3,linewidth=0,alpha=0.5)
        ax.set_ylim(bottom=-0.25*np.nanmax(spec),top=np.nanmax(spec)*1.1)
        gsv0.yaxis.get_major_ticks()[0].label1.set_visible(False)
        pp.legend()
        #lower subplot, zoomed spectrum/continuum
        gsv1=pp.subplot(gsv[1],sharex=gsv0)
        if xaxis=='AA':
            pp.xlabel(r'$\mathrm{\lambda (\AA)}$',fontsize=15)
        elif xaxis[-1]=='m':
            pp.xlabel(r"$\mathrm{\lambda (%s m)}$" % (lat_let[xaxis[0]]),fontsize=15)
        pp.ylim([-0.1*np.nanmedian(spec50),np.nanmedian(spec50)*1.5])
        #plotting original data
        gsv1.plot(wl,spec,ls="--",c="dodgerblue",zorder=2,label="JWST")
        gsv1.fill_between(wl,spec-err_spec,spec+err_spec,color="dodgerblue",zorder=3,linewidth=0,alpha=0.5)
        #plotting best fitting spectrum
        gsv1.plot(wl,spec50,ls="-",c="darkorange",zorder=4,label="Best fit (BP)")
        gsv1.fill_between(wl,spec16,spec84,color="navajowhite",zorder=3,linewidth=0,alpha=0.5)
        pp.setp(gsv0.get_xticklabels(which="both"),visible=False)
        gsv1.yaxis.get_major_ticks()[-1].label1.set_visible(False)
        pp.subplots_adjust(hspace=0)
        #box including the fitting results
        if box:
            text,props=make_box(fit,box)
            gsv0.text(0.01,0.95,text,fontsize=14, va="top",ha="left", bbox=props,transform=ax.transAxes)
        return fig
    elif fit['info']['dtype']=='phot':
        print('Work in progress! Come back in a future update :)')
        return
    elif fit['info']['dtype']=='both':
        print('Work in progress! Come back in a future update :)')
        return

#draw box object in SED plots
def make_box(fit,params):
    res_val,res_uerr,res_lerr=[],[],[]
    for p in params:
        if p not in list(fit.keys()):
            print('%s was not part of the fit or had a fixed value. This parameter will be not shown in the plot\n' % (p))
        else:
            res_val.append(np.percentile(fit[p],(50)))
            res_uerr.append(np.percentile(fit[p],(84))-res_val[-1])
            res_lerr.append(res_val[-1]-np.percentile(fit[p],(16)))
    #res_val=np.array([np.percentile(fit[p],(50)) for p in params])
    #res_uerr=np.array([np.percentile(fit[p],(84))-np.percentile(fit[p],(50)) for p in params])
    #res_lerr=np.array([np.percentile(fit[p],(50))-np.percentile(fit[p],(16)) for p in params])
    box_lab=params
    text=''
    for i in range(len(box_lab)):
        var=choose_var(box_lab[i])
        text=text+"%s=$%.4f^{+%.4f}_{-%.4f}$" % (var,res_val[i],res_uerr[i],res_lerr[i])
        if i!=len(box_lab)-1:
            text=text+" \n"
    props = dict(boxstyle="round", facecolor="lightgray", alpha=0.5)
    return text, props
