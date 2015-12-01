# $Id$
#
# plot_sam_clubb_joint_pdf
#   Description:
#     Plots and compares SAM's and CLUBB's joint pdf for some variable

import numpy as np
import matplotlib.pyplot as plt
import netCDF4

#----------------------------------------------------------------------------------------    
# User input
#----------------------------------------------------------------------------------------

case_dir = 'RICO'

# Directory for SAM's 3D files 
sam_3D_dir = '/home/griffinb/Brian_special_input_fields_r7465/sam_benchmark_runs/RICO_256x256x100_drizzle/3D_output/'

# Note: SAM outputs 3D files in NSTEPS, so it is dependent on timestep. Therefore, 
#   this script must do some gymnastics to ensure we are comparing the correct times.
#   Only supply 'a' filename upto the NSTEP counter.  
sam_3D_file = 'RICO_256x256x100_drizzle_128_'
# e.g.        LBA_128kmx1kmx128_1km_Morrison_64_0000000150_micro.nc

sam_dt = 1. # [s] SAM's model timestep, not output frequency. 

# SAM's stat file 
sam_stat_file = '/home/griffinb/Brian_special_input_fields_r7465/sam_benchmark_runs/RICO_256x256x100_drizzle/RICO_256x256x100_drizzle.nc'

# Directory for CLUBB's sample points file
clubb_3D_dir = '/home/griffinb/Brian_special_input_fields_r7465/output/'

# CLUBB's file names
clb_nl_file = clubb_3D_dir + 'rico_nl_lh_sample_points_2D.nc'
clb_u_file = clubb_3D_dir + 'rico_u_lh_sample_points_2D.nc'
clubb_stat_file = clubb_3D_dir + 'rico_zt.nc' # The statistics file and sample points
                                           # files are output from CLUBB into the 
                                           # same directory by default

# Variable name, time, and height
sam_abs_var_name = 'RR'         # SAM's name for abscissa
sam_abs_file_suffix = '_micro.nc' # SAM outputs 2 different 3D files. One is '.nc' 
                                 # and the other is written out from Morrison 
                                 # Micro and has a '_micro.nc'

sam_ord_var_name = 'NR'   # SAM's name for ordinate
sam_ord_file_suffix = '_micro.nc'

sam_abs_unit_conversion = 1.
sam_ord_unit_conversion = 1.

clubb_abs_var_name = 'rr' # CLUBB's name for abscissa
clubb_ord_var_name = 'Nr' # CLUBB's name for ordinate

abs_name = '$r_{r}$' # Fancy names for title
ord_name = '$N_{r}$'

abs_units = '$\mathrm{kg \ kg^{-1}}$'  # How the variable looks when it is plotted
ord_units = '$\mathrm{kg^{-1}}$'  # The plotted units

# Analysis height and time                   
z0_array = [380]           # Analysis height [m]
t0_in_min = 4200           # Analysis time [min] 
                           # Note: This exact time must exist for SAM's output.
                           # CLUBB will use the closest available.

# Plot every "samp"th SAM LES data point and every "samp"th CLUBB PDF SILHS
# sample data point.
# Note:  to produce the best results, set the number of SILHS sample points
#        equal to the number of SAM LES grid horizontal points.  For example,
#        SAM uses a 256 x 256 horizontal domain, set CLUBB's number of SILHS
#        sample points to 65536.  The sample points need to be unweighted, so
#        turn off importance sampling.  In this code, samp plots every "samp"th
#        LES and CLUBB PDF point.
samp=10

# Figure output directory.
out_dir = '/home/griffinb/Brian_special_input_fields_r7465/output/'

#----------------------------------------------------------------------------------------
# Should not have to edit below this line
#----------------------------------------------------------------------------------------

def pull_samples(nc, varname):
    var = nc.variables[varname]
    var_u = nc.variables[varname].units
    var = np.squeeze(var)
    return var, var_u

def reshape_sam_slice(var, idx_z0):
    var = np.squeeze(var)
    var = np.swapaxes(var,2,0)
    var = var[:,:,idx_z0]
    var = np.reshape(var,(np.size(var,0)*np.size(var,1)))
    return var
    
def reshape_clubb_samples(var, idx_z0, idx_t0):
    var = var[idx_t0,idx_z0,:]
    return var
    
def calc_precip_frac(rain, threshold):
    total_num = len(rain)
    rain_pts = np.where(rain > threshold)
    rain_num = len(rain[rain_pts])
    precip_frac = float(rain_num) / float(total_num)
    return precip_frac    

for i in np.arange(0,len(z0_array)):
    z0 = z0_array[i]

    # Find the correct SAM 3D file.
    t0_in_s = t0_in_min*60.

    # Find which NSTEP corrosponds to our desired t0
    t0_filename = str(int((t0_in_s)/sam_dt))

    # SAM's nstep counter is a fixed 10 digits long.
    sam_nstep_counter='0000000000'

    # Find how many digits the desire NSTEP takes up
    place = len(t0_filename)

    # From the beginning of the nstep counter, find how many places until we insert our 
    # NSTEP
    end_zeros = len(sam_nstep_counter) - place

    # Combine SAM's nstep counter and our desired NSTEP
    t0_filename = sam_nstep_counter[0:end_zeros] + t0_filename
    
    # Paste the strings together and call it a filename.
    sam_abs_file = sam_3D_dir+sam_3D_file+t0_filename+sam_abs_file_suffix
    sam_ord_file = sam_3D_dir+sam_3D_file+t0_filename+sam_ord_file_suffix

    print "Extract SAM's RHO for this level"
    nc = netCDF4.Dataset(sam_stat_file)
    time, time_u = pull_samples(nc, 'time')
    z, z_u = pull_samples(nc, 'z')
    rho, rho_u = pull_samples(nc, 'RHO')
    idx_z0 = (np.abs(z[:] - z0)).argmin()
    idx_t0 = (np.abs(time[:] - t0_in_min)).argmin()
    rho = rho[idx_t0, idx_z0]
    
    print "Extract SAM abscissa"
    nc = netCDF4.Dataset(sam_abs_file)
    sam_z, z_u = pull_samples(nc, 'z')
    sam_abs, sam_abs_u = pull_samples(nc, sam_abs_var_name)
    nc.close()
    
    print "Extract SAM ordinate"
    nc = netCDF4.Dataset(sam_ord_file)
    sam_ord, sam_ord_u = pull_samples(nc, sam_ord_var_name)
    nc.close()
    
    print "Find Time and Height Indicies for SAM Slice"
    idx_z0 = (np.abs(sam_z[:] - z0)).argmin()
    
    sam_abs = reshape_sam_slice(sam_abs, idx_z0)
    sam_ord = reshape_sam_slice(sam_ord,  idx_z0)
    

    print "Extract CLUBB Data"
    nc = netCDF4.Dataset(clb_nl_file)
    clb_z, z_u = pull_samples(nc, 'altitude')
    clb_time, clb_time_u = pull_samples(nc, 'time')
    clb_abs, clb_abs_u = pull_samples(nc, clubb_abs_var_name)
    clb_ord, clb_ord_u = pull_samples(nc, clubb_ord_var_name)
    nc.close()

    nc = netCDF4.Dataset(clubb_stat_file)
    mixt_frac, mixt_frac_u = pull_samples(nc, 'mixt_frac')
    nc.close()

    nc = netCDF4.Dataset(clb_u_file)
    dp1, dp1_u = pull_samples(nc, 'dp1')
    nc.close()
    
    idx_t0 = (np.abs(clb_time[:] - t0_in_s)).argmin()
    idx_z0 = (np.abs(clb_z[:] - z0)).argmin()
    
    clb_abs = reshape_clubb_samples(clb_abs, idx_z0,idx_t0)
    clb_ord = reshape_clubb_samples(clb_ord, idx_z0,idx_t0)
    dp1 = dp1[idx_t0,idx_z0]
    mixt_frac = mixt_frac[idx_t0,idx_z0]
    
    idx_comp_1 = np.where(dp1 < mixt_frac)
    idx_comp_2 = np.where(dp1 >= mixt_frac)
    clb_abs_1 = clb_abs[idx_comp_1]
    clb_abs_2 = clb_abs[idx_comp_2]

    clb_ord_1 = clb_ord[idx_comp_1]
    clb_ord_2 = clb_ord[idx_comp_2]
    
    print "Convert Units"
    sam_abs = sam_abs*sam_abs_unit_conversion
    sam_ord = sam_ord*sam_ord_unit_conversion
    

    print "Plot"
    out_name = '%s_joint_pdf_%s_%s_%smin_%sm.eps'%(case_dir,clubb_abs_var_name,clubb_ord_var_name,t0_in_min,z0)

    f, (ax1, ax2) = plt.subplots(1,2,sharey=True, sharex=True)
    f.subplots_adjust(bottom=.2)
    
    ax1.scatter(sam_abs[0::samp], sam_ord[0::samp], c='r', alpha=.3)
    ax1.set_xlim([.9*min(min(clb_abs[0::samp]),min(sam_abs[0::samp])),1.1*max(max(clb_abs[0::samp]),max(sam_abs[0::samp]))])
    ax1.set_ylim([.9*min(min(clb_ord[0::samp]),min(sam_ord[0::samp])),1.1*max(max(clb_ord[0::samp]),max(sam_ord[0::samp]))])
    ax1.grid()
    ax1.set_title('SAM LES')
    plt.setp(ax1.get_xticklabels(),rotation=45)
    
    # Light sky blue: #87CEFA
    # Dark blue: #00008B
    ax2.scatter(clb_abs_1[0::samp], clb_ord_1[0::samp], c='#87CEFA', alpha=.3, label='PDF Component 1')
    ax2.scatter(clb_abs_2[0::samp], clb_ord_2[0::samp], c='#00008B', alpha=.3, label='PDF Component 2')
    plt.legend()
    plt.setp(ax2.get_xticklabels(),rotation=45)
    ax2.set_title('CLUBB\'s PDF')
    ax2.grid()

    ax1.set_xlabel(abs_name+'     '+abs_units)
    ax1.set_ylabel(ord_name+'     '+ord_units)
    ax2.set_xlabel(abs_name+'     '+abs_units)
    text_str = '%s: Joint PDF of %s and %s'%(case_dir, abs_name, ord_name)
    plt.suptitle(text_str)
    plt.savefig(out_dir + out_name)
    plt.close()
