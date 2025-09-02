#Arrays
import numpy as np
import random as rd

#Science (Scipy, mostly)
from scipy.integrate import trapezoid
from scipy.interpolate import interpn as i2d
from scipy.integrate import simpson

#Astronomy (Astropy, mostly)
from astropy.io import fits
from astropy.wcs import WCS
from astropy import units as u
from astropy.coordinates import SkyCoord as SC

#Figures and video
import matplotlib.pyplot as pp
from matplotlib.ticker import FormatStrFormatter
from matplotlib import gridspec as gs
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import moviepy.video.io.ImageSequenceClip as ISC

#Data handling
from natsort import natsorted as ns
import glob as glob

import os
import shutil as su

#MPI
import threading as th
import subprocess as sp

#Others
import time as tm
from datetime import timedelta

#Self-package import
#from .LazaUtils.get import *run
#from .LazaVars import dics


