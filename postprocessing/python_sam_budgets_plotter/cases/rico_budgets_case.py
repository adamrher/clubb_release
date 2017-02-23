#-------------------------------------------------------------------------------
# G E N E R E L   D E F A U L T   S E T T I N G S
#-------------------------------------------------------------------------------
name = 'RICO_BUDGETS'
enabled = True
type = 'budget'
startTime = 0.0      # [minutes]
endTime = 180.0      # [minutes]
startHeight = 100.0    # [m]
endHeight = 2500.0   # [m]
headerText = 'RICO Budgets Minutes ' + str(startTime) + '-' + str(endTime) + ', 100m-2500m'

case = 'RICO'
out_dir = './clubb/plotsSam/%s/'%(case)
sam_file = '/home/ckrome/clubb/outputSam/RICO_256x256x100_drizzle.nc'
plot_case_name = '%s_'%(case)

#-------------------------------------------------------------------------------
# G E N E R E L   P L O T   S E T T I N G S
#-------------------------------------------------------------------------------
lineWidth = 2
color = 'nipy_spectral'
yLabel = 'Height [m]'