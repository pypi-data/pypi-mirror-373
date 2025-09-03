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

from ..LazaGal.mass import ageX, btime
from ..LazaUtils.get import get_z
from ..LazaUtils.MPF import mkdirs

#==========================================================

def BP_fit(ID,dtype,fit_params,load_data=None,data_dir=None,filters=None,run='.',save_post=False,save_res=None,overwrite=False,verbose=False):
    """
    --------------------------------------------
    INSTRUCTIONS:
    This functions loads and fits data using the Bagpipes pipeline, and desired, saves the results in a directory called BP_ID or BP_run directory (if run is given).
    All input files must have data stored in columns with each column one of the variables (e.g. a file containin 2 columns with wavelenght on the first column, flux in the second, etc.)
    It is assumed that data is aleady prepared using the 'correct_input' data or that a custom load_data functions that prepares the data is given for everything to work smoothly
    Input data must be a file with photometry data (flux and flux error in microJanskys) and/or a spectroscopy data (wavelength in AA and flux and flux error erg s-1 cm-2 AA-1)
    --------------------------------------------
    ARGS:
    ID: object id; used for naming and data location
    dtype:  data type; can be 'spec','phot' or 'both'
    fit_params: dictionary containing the fitting parameters according to the Bagpipes documentation
    --------------------------------------------
    KWARGS:
    load_data:  the load data function to use to input the data. This functions must return an array containing wavelengths in AA and flux and flux err in erg s-1 cm-2 AA-1 if spectroscopy data is given, flux and flux err in uJy if photometry is given, or both arrays in this same order if both types of data are given. Input must be only the ID of the object, which must match the ID given to this function. An example can be found at the Bagpipes documentation
    data_dir:   directory path where the data will be taken from. Default is the same directory where this functions is called from
    filters:    list containing the paths to the files of the filters used if photometry data is given. Filters must be files wavelength in AA and its associated transmission
    run:    name of the fit run; will be used to save data with an specific name so BP does not run the fit again. If given, everything will be named after the run
    save_post:  to save the fitting results (posterior file). It can be set to True, in which case it will be saved in the directory BP_ID_runs/run/ if run is given, or directly in BP_ID_runs if run is not given, and saved as a ID_run_post.h5 and ID_run_post.npy files (_run will not appear if run is not given). If a path is given, this MUST NOT include the file name in it; a file with the aforementioned name will be said in the given location
    save_res:   list containing the dictionary keys to save into a txt file. More info at save_results function
    overwrite:  if save_post is True, checks if previous file exists in the given output directory, and if True, it will delete it and do the fitting again. CURRENTLY NOT IMPLEMENTED
    ---------------------------------------------
    """
    #First, check if all inputs are correct:
    if type(ID)!=str:
        print('\nID of the object must a be a string!\n')
        return
    if dtype not in ['spec','phot','both']:
        print('\nData type must be "spec", "phot" or "both"!\n')
    if type(fit_params)!=dict:
        print('\nFitting paramaters (fit_params) must be a dictionary!\n')
        return
    #Creating the load_data function, in case one is not given
    if dtype=='both' and load_data==None:
        if data_dir and type(data_dir)==str: #THIS IS WRONG, I NEED SOME WAY TO INCLUDE 2 PATHS IN DATA_DIR, MAYBE A LIST?
            def load_data(ID):
                spec=np.loadtxt(data_dir,comments='#')
                phot=np.loadtxt(data_dir,comments='#')
                return spec, phot
        elif data_dir==None:
            def load_data(ID):
                spec=np.loadtxt('%s_%s.dat' % (ID,'spec'),comments='#')
                phot=np.loadtxt('%s_%s.dat' % (ID,'phot'),comments='#')
                return spec, phot
        else:
            print('data_dir must be the string path to the data file!\n')
            return
    elif dtype=='spec' and load_data==None:
        if data_dir and type(data_dir)==str:
            def load_data(ID):
                spec=np.loadtxt(data_dir,comments='#')
                return spec
        elif data_dir==None:
            def load_data(ID):
                spec=np.loadtxt('%s_%s.dat' % (ID,'spec'),comments='#')
                return spec
        else:
            print('data_dir must be the string path to the data file!\n')
            return
    elif dtype=='phot' and load_data==None:
        if data_dir and type(data_dir)==str:
            def load_data(ID):
                phot=np.loadtxt(data_dir,comments='#')
                return phot
        elif data_dir==None:
            def load_data(ID):
                phot=np.loadtxt('%s_%s.dat' % (ID,'phot'),comments='#')
                return phot
        else:
            print('data_dir must be the string path to the data file!\n')
            return
    #Creating the directory where results will be saved
    if save_post:
        if type(save_post)==str:
            if not os.path.exists(save_post):
                paths=save_post.split('/')
                path=[]
                for p in paths:
                    path.append(p)
                    pp=os.path.join(*path)
                    if not os.path.exists(pp):
                        os.mkdir(pp)
            if run!='.':
                if not os.path.exists('%s/%s' % (save_post,run)):
                    os.mkdir('%s/%s' % (save_post,run))
                ori_path='pipes/posterior/%s/%s.h5' % (run,ID)
                saved_path='%s/%s' % (save_post,run)
                fname='%s_%s_post.h5' %(ID,run)
            else:
                ori_path='pipes/posterior/%s.h5' % (ID)
                saved_path='%s' % (save_post)
                fname='%s_post.h5' % (ID)
        elif type(save_post)==bool:
            if not os.path.exists('BP_%s_runs' % (ID)):
                os.mkdir('BP_%s_runs' % (ID))
            if run!='.':
                if not os.path.exists('BP_%s_runs/%s' % (ID,run)):
                    os.mkdir('BP_%s_runs/%s' % (ID,run))
                ori_path='pipes/posterior/%s/%s.h5' % (run,ID)
                saved_path='BP_%s_runs/%s' % (ID,run)
                fname='%s_%s_post.h5' % (ID,run)
            else:
                ori_path='pipes/posterior/%s.h5' % (ID)
                saved_path='BP_%s_runs' % (ID)
                fname='%s_post.h5' % (ID)
    else:
        saved_path='.'
    #Running bagpipes
    time_start=tm.time()
    print('\n===================================================\nFitting \033[1m%s\033[0m (\x1B[3mrun: %s\x1B[0m) started at ' % (ID,run)+tm.strftime('%H:%M:%S')+'\n===================================================')
    if data_dir and dtype in ['spec','phot']:
    	print('Path of the data used for this fit:\n %s\n' % (data_dir))
    elif data_dir and dtype=='both':
    	print('Showing the path of origin is a work in progress! This will be added in a future update :)\n')
    elif not data_dir and dtype in ['spec','phot']:
    	print('Path of the data used for this fit:\n %s_%s.dat\n' % (ID,dtype))
    else:
    	print('Showing the path of origin is a work in progress! This will be added in a future update :)\n')
    if dtype=='spec':
        galaxy=bp.galaxy(ID=ID,load_data=load_data,photometry_exists=False)
        fit=bp.fit(galaxy,fit_instructions=fit_params,run=run)
        fit.fit(verbose=False)
    elif dtype=='phot':
        galaxy=bp.galaxy(ID=ID,load_data=load_data,spectrum_exists=False,filt_list=filters)
        fit=bp.fit(galaxy,fit_instructions=fit_params,run=run)
        fit.fit(verbose=False)
    elif dtype=='both':
        galaxy=bp.galaxy(ID=ID,load_data=load_data,filt_list=filters)
        fit=bp.fit(galaxy,fit_instructions=fit_params,run=run)
        fit.fit(verbose=False)
    fit.posterior.get_advanced_quantities()
    post=fit.posterior.samples
    if dtype=='spec':
        post['wavelength_obs']=fit.galaxy.spectrum[:,0]
        post['spectrum_obs']=fit.galaxy.spectrum[:,1]
        post['err_spectrum_obs']=fit.galaxy.spectrum[:,2]
    elif dtype=='phot':
        post['wavelength_obs']=fit.posterior.model_galaxy.wavelengths*(1+fit_params['redshift']) #This returns the FULL SPECTRUM RANGE, i.e. ~9k points
        post['eff_phot_wl']=fit.galaxy.filter_set.eff_wavs
    elif dtype=='both':
        post['wavelength_obs']=fit.galaxy.spectrum[:,0]
        post['spectrum_obs']=fit.galaxy.spectrum[:,1]
        post['err_spectrum_obs']=fit.galaxy.spectrum[:,2]
        post['eff_phot_wl']=fit.galaxy.filter_set.eff_wavs
    info={'ID':ID,'run':run,'dtype':dtype,'fit_params':fit_params,'galaxy':galaxy,'path':saved_path}
    post['info']=info
    post['age20']=ageX(post,0.2)
    post['age50']=ageX(post,0.5)
    if save_res:
        save_results(post,save_res)
    time_fin=np.ceil(tm.time()-time_start) #only to print the total runtime
    print('\n___________________________________________________\n\n\033[1m%s\033[0m (\x1B[3mrun: %s\x1B[0m) fitting finished at ' % (ID,run)+tm.strftime('%H:%M:%S')+' (Running time: %s)\n___________________________________________________\n' % (str(timedelta(seconds=time_fin))))
    if save_post:
        su.copy(ori_path,saved_path+'/'+fname)
        np.save(saved_path+'/'+fname[:-3],post)
        print('\n===================================================\nResults succesfully saved at: \n%s\nYou will find a h5 file and a npy file in that directory\n===================================================\n' % (saved_path+'/'))
    #else:
        #save_path='.'
    return post

#==========================================================

def mpi(IDs,dtypes,params,paths,n_proc,filters=None,runs=None,save_post=False,save_plots=None,save_res=None,xaxis='AA',yaxis=None,box=None):
    """
    INSTRUCTIONS:
    Runs several fits at the same time
    ---------------------------------------------
    ARGS:
    IDs:    list of IDs. It can be either a string with a single object (for different runs) or a list of IDs
    dtypes: list of data types. If all data type is the same, this can be set to the string 'spec','phot' or 'both'
    params: list of dictionaries of fitting parameters. This can be either 1 dictionary for all fits or a list containing the dictionary of parameters for each ID/run
    paths:  list of paths to the data
    n_proc:     number of processes to be carried at the same time
    ---------------------------------------------
    KWARGS:
    filters:    list of the lsit of filters, in case phot is fit
    runs:   list of runs associated to each object
    save_post:  save the posterior file
    save_plots: list of plots to be drawn and saved
    save_res:   list of keys of post. Values + errors of these keys will be saved in BP_ID_runs/run/ID_run.res
    xaxis:  xaxis units for SED plots. Go to plotSED/plot_figs for more info
    yaxis:  yaxis units for SED plots. Go to plotSED/plot_figs for more info
    box:    results to include in SED plots. . Go to plotSED/plot_figs for more info
    ---------------------------------------------
    """
    if not os.path.exists('LP_MPI_1'):
        os.mkdir('LP_MPI_1')
        number=1
    else:
        number=int(ns(glob.glob('LP_MPI*'))[-1][-1])+1
        os.mkdir('LP_MPI_%i' % (number))
    if type(IDs)==str and runs:
        objs=runs
        n_obj=len(runs)
        IDs=[IDs for i in range(n_obj)]
    elif type(IDs)==list and len(IDs)==1 and runs:
        objs=runs
        n_obj=len(runs)
        IDs=[IDs for i in range(n_obj)]
    else:
        objs=IDs
        n_obj=len(IDs)
    if type(dtypes)==str:
        dtypes=[dtypes for i in range(n_obj)]
    elif type(dtypes)==str and len(dtypes)==1:
        dtypes=[dtypes for i in range(n_obj)]
    if type(params)==list and len(params)==1:
        params=[params for i in range(n_obj)]
        for p in range(n_obj):
            np.save('LP_MPI_%i/params%i' % (number,p),params[p])
    elif type(params)==dict: #AÑADIR CONDICIÓN DICTS COMO EN MPI_RESOLVED
        params=[params for i in range(n_obj)]
        for p in range(n_obj):
            np.save('LP_MPI_%i/params%i' % (number,p),params[p])
    elif type(params)==list and len(params)!=n_obj:
        print('Either every object has their own fitting parameters or all use the same dictionary!\n')
        return
    else:
        for p in range(n_obj):
            np.save('LP_MPI_%i/params%i' % (number,p),params[p])
    if type(paths)==list and len(paths)==1:
        paths=[paths for i in range(n_obj)]
    elif type(paths)==str:
        paths=[paths for i in range(n_obj)]
    print('==============================================\nStarting multi-process fitting! Total fits to do: %s\n==============================================\n' % (n_obj))
    time_start=tm.time()
    if n_obj<=n_proc:
        num=1
        n_proc=n_obj
    else:
        num=int(np.floor(n_obj/n_proc))
        #---------------
    for i in range(n_proc):
        fil=open('LP_MPI_resolved_%i/MPI_%i.py' % (number,i),'w')
        fil.write('from astrolaza.LazaPipes.fitting import BP_fit \nfrom astrolaza.LazaPipes.plotting import plot_figs \nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        fil.close()
    n_fits=len(paths)
    check=len(paths)
    i,k=0,0
    while check!=0:
        fp="np.load('LP_MPI_%i/params%i.npy',allow_pickle=True)[()]" % (number,k)
        if runs:
            run=runs[k]
        else:
            run='unnamed_run'
        if save_post:
            save='True'
        else:
            save='False'
        if verbose:
            verbose='True'
        else:
            verbose='False'
        fil=open('LP_MPI_%i/MPI_%i.py' % (number,i),'a')
        fil.write('fit=BP_fit("%s","%s",%s,data_dir="%s",run="%s",save_post=%s)\n' % (IDs[k],dtypes[k],fp,paths[k],run,save))
        if save_plots:
            for plot in save_plots:
                fil.write('plot_figs(fit,["%s"],save_plots=True,xaxis="%s",box=%s)\n' % (plot,xaxis,str(box)))
        fil.write('pp.close("all")\n')
        i+=1
        k+=1
        check-=1
        if i>n_proc-1:
            i=0
        fil.close()
        #--------------------
    """
    for i in range(n_proc):
        j=0
        fil=open('LP_MPI_%i/MPI_%i.py' % (number,i),'w')
        fil.write('from astrolaza.LazaPipes.fitting import BP_fit \nfrom astrolaza.LazaPipes.plotting import plot_figs \nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        #fil.write('import sys\nsys.path.append("/home/alr/PhD/Py")\nimport LazaPipes as LP\nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        while j!=num:
            k=i*num+j
            fp="np.load('LP_MPI_%i/params%i.npy',allow_pickle=True)[()]" % (number,k)
            if runs:
                run=runs[k]
            else:
                run='unnamed_run'
            #if filters:
                #filt=filters[k]
            #else:
                #filt=None
            if save_post:
                save='True'
            else:
                save='False'
            if verbose:
            	verbose='True'
            else:
            	verbose='False'
            fil.write('fit=BP_fit("%s","%s",%s,data_dir="%s",run="%s",save_post=%s,verbose=%s)\n' % (IDs[k],dtypes[k],fp,paths[k],run,save,verbose))
            if save_plots:
                for plot in save_plots:
                    fil.write('plot_figs(fit,["%s"],save_plots=True,xaxis="%s",box=%s)\n' % (plot,xaxis,str(box)))
            j+=1
        fil.close()
    if n_obj%n_proc!=0:
        fil=open('LP_MPI_%i/MPI_%i.py' % (number,i+1),'w')
        fil.write('from astrolaza.LazaPipes.fitting import BP_fit \nfrom astrolaza.LazaPipes.plotting import plot_figs \nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        #fil.write('import sys\nsys.path.append("/home/alr/PhD/Py")\nimport LazaPipes as LP\nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        for i in range(1,n_obj-num*n_proc+1):
            k=k+1
            fp="np.load('LP_MPI_%i/params%i.npy',allow_pickle=True)[()]" % (number,k)
            if runs:
                run=runs[k]
            else:
                run='unnamed_run'
            if save_post:
                save='True'
            else:
                save='False'
            if verbose:
            	verbose='True'
            else:
            	verbose='False'
            fil.write('fit=BP_fit("%s","%s",%s,data_dir="%s",run="%s",save_post=%s,verbose=%s)\n' % (IDs[k],dtypes[k],fp,paths[k],run,save,verbose))
            if save_plots:
                for plot in save_plots:
                    fil.write('plot_figs(fit,["%s"],save_plots=True,xaxis="%s",box=%s)\n' % (plot,xaxis,str(box)))
        fil.close()
    """
    #Creating the running script
    scripts=ns(glob.glob('LP_MPI_%i/MPI*' % (number)))
    fil=open('LP_MPI_%i/run_mpi.py' % (number),'w')
    fil.write('import threading as th\nimport subprocess as sp\nimport time\ndef run_mpi(script):\n sp.run(["python3",script])\nif __name__=="__main__":')
    for i in range(len(scripts)):
        fil.write('\n     S%i=th.Thread(target=run_mpi,args=("LP_MPI_%i/MPI_%i.py",))' % (i,number,i))
    fil.write('\n')
    for i in range(len(scripts)):
        fil.write('     S%i.start()\n     time.sleep(5)\n' % (i))
    fil.write('\n')
    for i in range(len(scripts)):
        fil.write('     S%i.join()\n' % (i))
    fil.close()
    run_all=sp.check_call(['python3','LP_MPI_%i/run_mpi.py' % (number)])
    su.rmtree('LP_MPI_%i' % (number))
    if save_res:
        if runs:
            for i in range(len(runs)):
                path=glob.glob('BP_%s_runs/%s/*.npy' % (IDs[i],runs[i]))[0]
                save_results(path,save_res,out='BP_%s_runs/%s/%s_%s.res' % (IDs[i],runs[i],IDs[i],runs[i]))
        else:
            for i in range(len(IDs)):
                path=glob.glob('BP_%s_runs/unnamed_run/*.npy' % (IDs[i]))[0]
                save_results(path,save_res,out='BP_%s_runs/unnamed_run/%s_unnamed_run.res' % (IDs[i],IDs[i]))
    time_fin=np.ceil(tm.time()-time_start)
    print('==============================================\nAll %s fits are finished!\nTotal runtime: %s\n==============================================\n' % (n_obj,time_fin))
    return


#==========================================================

def mpi_resolved(paths,params,n_proc,IDpix=None,save_plots=None,runs=None,save_res=None,xaxis='AA',yaxis=None,box=None):
    """
    ---------------------------------------------
    INSTRUCTIONS:
    ---------------------------------------------
    ARGS:
    paths:  list of paths to the data files
    params: either list containing the parameters dictionary for each file in path or a dictionary containing the params dictionary for each object. The former mode is meant to be used when each pixel has its own parameters for the fit, while the latter mode is meant to be used when all pixels in an object are fit to the same parameters
    n_proc: number of precessors (kernels) to use at the same time
    ---------------------------------------------
    KWARGS:
    IDpix:  list or tuple containing the ID and X and Y positions of the pixel spectrum in paths. If None, it will be assumed that paths contain the file as returned from the correct_input_resolved function; if given it is assumed that the data is taken from custom files
    plots:  plot to be saved. options are 'fy', 'fv' and 'sfh'
    runs:   string or list of strings of the runs to be carried out. There must be either 1 per object or 1 for all objects (all objects will have the same run)
    save_res:   list of keys of post. Values + errors of these keys will be saved in BP_ID_runs/run/ID_run.res
    xaxis:  xaxis units for SED plots. Go to plotSED/plot_figs for more info
    yaxis:  yaxis units for SED plots. Go to plotSED/plot_figs for more info
    box:    results to include in SED plots. . Go to plotSED/plot_figs for more info
    ---------------------------------------------
    """
    #checking inputs
    if not os.path.exists('LP_MPI_resolved_1'):
        os.mkdir('LP_MPI_resolved_1')
        number=1
    else:
    	number=int(ns(glob.glob('LP_MPI_resolved*'))[-1][-1])+1
    if IDpix and (type(IDpix)==list or type(IDpix)==tuple):
        IDpix=np.asarray(IDpix)
        IDs=IDpix[:,0]
        xy=IDpix[:,1:]
    elif IDpix and type(IDpix)!=list and type(IDpix)!=tuple:
        print('IDpixels must be a list or tuple containing the ID of the object, X position of the pixel and the Y position of the pixel, in that order\n')
        return
    elif not IDpix:
        IDs=[]
        xy=[]
        for p in paths:
            IDs.append(IDpixels(p)[0])
            xy.append(IDpixels(p)[1:])
        IDs=np.asarray(IDs)
        xy=np.asarray(xy)
    if type(params)==dict and len(paths)!=len(params):
        IDs_u=np.unique(IDs)
        if len(IDs_u)<=len(params):
            for key in IDs_u:
                if not key in params.keys():
                    print('ID %s is not in the params dictionary! Check the params dictionary and the IDs of the objects\n' % (key))
                    return
                np.save('LP_MPI_resolved_%i/params_%s.npy' % (number,key),params[key])
        elif len(IDs_u)>len(params):
            print('There cannot be more objects than parameters! Check the params dictionary and the IDs of the objects\n')
            return
    elif type(params)==dict and len(paths)==len(params):
        IDs_u=np.unique(IDs)
        for key in IDs_u:
            if not key in params.keys():
                print('ID %s is not in the params dictionary! Check the params dictionary and the IDs of the objects\n' % (key))
                return
            np.save('LP_MPI_resolved_%i/params_%s.npy' % (number,key),params[key])
    elif type(params)==list and len(paths)!=len(params):
        print('There must be as many parameters dictionaries as pixels (one per pixel)\n')
        return
    elif type(params)!=list and type(params)!=dict:
        print('params must be either a list containing as many parameters dictionaries as spectrum in paths or a dictionary containing one parameter dictionary for each object ID (being the ID the key)\n')
    else:
        for i in range(len(params)):
            np.save('LP_MPI_resolved_%i/params%i.npy' % (number),params[i])
    if runs:
        if type(runs)==list and len(runs)>1 and len(runs)!=len(IDs_u):
            print('There must be either as many runs as objects (one per object) or one run only (all runs are named the same)\n')
        elif type(runs)==list and len(runs)==1:
            runs=np.asarray([runs[0] for i in range(len(IDs_u))])
        elif type(runs)==str:
            runs=np.asarray([runs for i in range(len(IDs_u))])
    elif not runs:
        runs=np.asarray(['unnamed_run' for i in range(len(IDs_u))])
    #creating scripts
    for i in range(n_proc):
        fil=open('LP_MPI_resolved_%i/MPI_%i.py' % (number,i),'w')
        fil.write('from astrolaza.LazaPipes.fitting import BP_fit \nfrom astrolaza.LazaPipes.plotting import plot_figs \nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        fil.close()
    n_fits=len(paths)
    check=len(paths)
    i,k=0,0
    while check!=0:
        mkdirs('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0]),fil=False)
        fp='np.load("LP_MPI_resolved_%i/params_%s.npy",allow_pickle=True)[()]' % (number,IDs[k])
        fil=open('LP_MPI_resolved_%i/MPI_%i.py' % (number,i),'a')
        fil.write('fit=BP_fit("%s","spec",%s,data_dir="%s",run="%s_%s_%s_%s",save_post=False)\n' % (IDs[k],fp,paths[k],IDs[k],xy[k,0],xy[k,1],runs[IDs_u==IDs[k]][0]))
        fil.write('fit["xy"]=(%i,%i)\n' % (int(xy[k,0]),int(xy[k,1])))
        fil.write('np.save("BP_%s_runs/Resolved/%s/posteriors/%s_%s_%s_post.npy",fit)\n' % (IDs[k],runs[IDs_u==IDs[k]][0],IDs[k],xy[k,0],xy[k,1]))
        if save_plots:
            if not os.path.exists('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                os.mkdir('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0]))
            for plot in save_plots:
                box=str(box)
                fil.write('plot_figs(fit,["%s"],save_plots="BP_%s_runs/Resolved/%s/plots/%s_%s_%s.svg",xaxis="%s",box=%s)\n\n' % (plot,IDs[k],runs[IDs_u==IDs[k]][0],plot,xy[k,0],xy[k,1],xaxis,box))
        fil.write('pp.close("all")\n')
        i+=1
        k+=1
        check-=1
        if i>n_proc-1:
            i=0
        fil.close()
    """
    n_obj=len(paths)
    if n_obj<=n_proc:
        num=1
        n_proc=n_obj
    else:
        num=int(np.floor(n_obj/n_proc))
    for i in range(n_proc):
        j=0
        fil=open('LP_MPI_resolved/MPI_%i.py' % (i),'w')
        fil.write('from astrolaza.LazaPipes.fitting import BP_fit \nfrom astrolaza.LazaPipes.plotting import plot_figs \nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        #fil.write('import sys\nsys.path.append("/home/alr/PhD/Py")\nimport LazaPipes as LP\nimport numpy as np\nimport bagpipes as bp\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        if type(params)==dict:
            while j!=num:
                k=i*num+j
                fp='np.load("LP_MPI_resolved/params_%s.npy",allow_pickle=True)[()]' % (IDs[k])
                if not os.path.exists('BP_%s_runs' % (IDs[k])):
                    os.mkdir('BP_%s_runs' % (IDs[k]))
                if not os.path.exists('BP_%s_runs/Resolved' % (IDs[k])):
                    os.mkdir('BP_%s_runs/Resolved' % (IDs[k]))
                if not os.path.exists('BP_%s_runs/Resolved/%s' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                    os.mkdir('BP_%s_runs/Resolved/%s' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                if not os.path.exists('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                    os.mkdir('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                fil.write('fit=BP_fit("%s","spec",%s,data_dir="%s",run="%s_%s_%s_%s",save_post=False)\n' % (IDs[k],fp,paths[k],IDs[k],xy[k,0],xy[k,1],runs[IDs_u==IDs[k]][0]))
                fil.write('fit["xy"]=(%i,%i)\n' % (int(xy[k,0]),int(xy[k,1])))
                fil.write('np.save("BP_%s_runs/Resolved/%s/posteriors/%s_%s_%s_post.npy",fit)\n' % (IDs[k],runs[IDs_u==IDs[k]][0],IDs[k],xy[k,0],xy[k,1]))
                if save_plots:
                    if not os.path.exists('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                        os.mkdir('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                    for plot in save_plots:
                        box=str(box)
                        fil.write('plot_figs(fit,["%s"],save_plots="BP_%s_runs/Resolved/%s/plots/%s_%s_%s.png",xaxis="%s",box=%s)\n\n' % (plot,IDs[k],runs[IDs_u==IDs[k]][0],plot,xy[k,0],xy[k,1],xaxis,box))
                fil.write('pp.close("all")\n')
                j+=1
            fil.close()
        elif type(params)==list:
            while j!=num:
                k=i*num+j
                fp='np.load("LP_MPI_resolved/params_%i.npy",allow_pickle=True)[()]' % (k)
                if not os.path.exists('BP_%s_runs' % (ID)):
                    os.mkdir('BP_%s_runs' % (IDs[k]))
                if not os.mkdir.exists('BP_%s_runs/Resolved' % (ID)):
                    os.mkdir('BP_%s_runs/Resolved' % (IDs[k]))
                if not os.mkdir.exists('BP_%s_runs/Resolved/%s' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                    os.mkdir('BP_%s_runs/Resolved/%s' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                if not os.mkdir.exists('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                    os.mkdir('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                fil.write('fit=BP_fit("%s","spec",%s,data_dir="%s",run="%s_%s_%s_%s",save_post=False)\n' % (IDs[k],fp,paths[k],IDs[k],xy[k,0],xy[k,1],runs[IDs_u==IDs[k]][0]))
                fil.write('fit["xy"]=(%i,%i)\n' % (int(xy[k,0]),int(xy[k,1])))
                fil.write('np.save("BP_%s_runs/Resolved/%s/posteriors/%s_%s_%s_post.npy",fit)\n' % (IDs[k],runs[IDs_u==IDs[k]],IDs[k],xy[k,0],xy[k,1]))
                if save_plots:
                    if not os.path.exists('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                        os.mkdir('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                    for plot in save_plots:
                        fil.write('plot_figs(fit,["%s"],save_plots="BP_%s_runs/Resolved/%s/plots/%s_%s_%s.png",xaxis="%s",box=%s)\n\n' % (plot,IDs[k],runs[IDs_u==IDs[k]][0],plot,xy[k,0],xy[k,1],xaxis,box))
                fil.write('pp.close("all")\n')
                j+=1
            fil.close()
    if n_obj%n_proc!=0:
        fil=open('LP_MPI_resolved/MPI_%i.py' % (i+1),'w')
        fil.write('from astrolaza.LazaPipes.fitting import BP_fit \nfrom astrolaza.LazaPipes.plotting import plot_figs \nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        #fil.write('import sys\nsys.path.append("/home/alr/PhD/Py")\nimport LazaPipes as LP\nimport numpy as np\nimport matplotlib.pyplot as pp\npp.close("all")\n')
        if type(params)==dict:
            for i in range(1,n_obj-num*n_proc+1):
                k=k+1
                fp='np.load("LP_MPI_resolved/params_%s.npy",allow_pickle=True)[()]' % (IDs[k])
                if not os.path.exists('BP_%s_runs' % (IDs[k])):
                    os.mkdir('BP_%s_runs' % (IDs[k]))
                if not os.path.exists('BP_%s_runs/Resolved' % (IDs[k])):
                    os.mkdir('BP_%s_runs/Resolved' % (IDs[k]))
                if not os.path.exists('BP_%s_runs/Resolved/%s' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                    os.mkdir('BP_%s_runs/Resolved/%s' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                if not os.path.exists('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                    os.mkdir('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                fil.write('fit=BP_fit("%s","spec",%s,data_dir="%s",run="%s_%s_%s_%s",save_post=False)\n' % (IDs[k],fp,paths[k],IDs[k],xy[k,0],xy[k,1],runs[IDs_u==IDs[k]][0]))
                fil.write('fit["xy"]=(%i,%i)\n' % (int(xy[k,0]),int(xy[k,1])))
                fil.write('np.save("BP_%s_runs/Resolved/%s/posteriors/%s_%s_%s_post.npy",fit)\n' % (IDs[k],runs[IDs_u==IDs[k]][0],IDs[k],xy[k,0],xy[k,1]))
                if save_plots:
                    if not os.path.exists('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                        os.mkdir('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                    for plot in save_plots:
                        fil.write('plot_figs(fit,["%s"],save_plots="BP_%s_runs/Resolved/%s/plots/%s_%s_%s.png",xaxis="%s",box=%s)\n\n' % (plot,IDs[k],runs[IDs_u==IDs[k]][0],plot,xy[k,0],xy[k,1],xaxis,box))
                fil.write('pp.close("all")\n')
            fil.close()
        if type(params)==list:
            for i in range(1,n_obj-num*n_proc+1):
                k=k+1
                fp='np.load("LP_MPI_resolved/params_%s.npy",allow_pickle=True)[()]' % (k)
                if not os.path.exists('BP_%s_runs' % (IDs[k])):
                    os.mkdir('BP_%s_runs' % (IDs[k]))
                if not os.path.exists('BP_%s_runs/Resolved' % (IDs[k])):
                    os.mkdir('BP_%s_runs/Resolved' % (IDs[k]))
                if not os.path.exists('BP_%s_runs/Resolved/%s' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                    os.mkdir('BP_%s_runs/Resolved/%s' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                if not os.path.exists('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                    os.mkdir('BP_%s_runs/Resolved/%s/posteriors' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                fil.write('fit=BP_fit("%s","spec",%s,data_dir="%s",run="%s_%s_%s_%s",save_post=False)\n' % (IDs[k],fp,paths[k],IDs[k],xy[k,0],xy[k,1],runs[IDs_u==IDs[k]][0]))
                fil.write('fit["xy"]=(%i,%i)\n' % (int(xy[k,0]),int(xy[k,1])))
                fil.write('np.save("BP_%s_runs/Resolved/%s/posteriors/%s_%s_%s_post.npy",fit)\n' % (IDs[k],runs[IDs_u==IDs[k]][0],IDs[k],xy[k,0],xy[k,1],box))
                if save_plots:
                    if not os.path.exists('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0])):
                        os.mkdir('BP_%s_runs/Resolved/%s/plots' % (IDs[k],runs[IDs_u==IDs[k]][0]))
                    for plot in save_plots:
                        fil.write('plot_figs(fit,["%s"],save_plots="BP_%s_runs/Resolved/%s/plots/%s_%s_%s.png",xaxis="%s",box=%s)\n\n' % (plot,IDs[k],runs[IDs_u==IDs[k]][0],plot,xy[k,0],xy[k,1],xaxis,box))
                fil.write('pp.close("all")\n')
            fil.close()
    """
    #Creating the running script
    print('==============================================\nStarting multi-process fitting! Total fits to do: %s\n==============================================\n' % (n_fits))
    scripts=ns(glob.glob('LP_MPI_resolved_%i/MPI*' % (number)))
    fil=open('LP_MPI_resolved_%i/run_mpi.py' % (number),'w')
    fil.write('import threading as th\nimport subprocess as sp\nimport time\ndef run_mpi(script):\n sp.run(["python3",script])\nif __name__=="__main__":')
    for i in range(len(scripts)):
        fil.write('\n     S%i=th.Thread(target=run_mpi,args=("LP_MPI_resolved_%i/MPI_%i.py",))' % (i,number,i))
    fil.write('\n')
    for i in range(len(scripts)):
        fil.write('     S%i.start()\n     time.sleep(2)\n' % (i))
    fil.write('\n')
    for i in range(len(scripts)):
        fil.write('     S%i.join()\n' % (i))
    fil.close()
    run_all=sp.check_call(['python3','LP_MPI_resolved_%i/run_mpi.py' % (number)])
    su.rmtree('LP_MPI_resolved_%i' % (number))
    print('==============================================\nAll %s fits are finished!\n==============================================\n' % (n_fits))
    #creating the catalogue
    if save_res:
        for i in range(len(IDs_u)):
            paths=ns(glob.glob('BP_%s_runs/Resolved/%s/posteriors/*.npy' % (IDs_u[i],runs[i])))
            join_results(paths,save_res,out='BP_%s_runs/Resolved/%s/%s_%s_pixels_results.res' % (IDs_u[i],runs[i],IDs_u[i],runs[i]))
            print('==============================================\nA catalogue containing the fitting values for each pixel can be found at BP_%s_runs/Resolved/%s/%s_%s_pixels_results.res\n==============================================\n' % (IDs_u[i],runs[i],IDs_u[i],runs[i]))

    return

