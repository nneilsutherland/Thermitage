# Vignetting Correction Image Generation:

# Import necessary packages
import os
import numpy as np
import glob
import matplotlib.pyplot as plt
from PIL import Image
from scipy.interpolate import griddata
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pandas as pd
