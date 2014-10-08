% $Id$
function PDF_scatter_contour_plotter( input_file_sam, input_file_clubb )

% SAM LES 3D NetCDF filename.
if ( strcmp( input_file_sam, 'default' ) )
   filename_sam = '../../output/LES_output/RICO_128x128x100_drizzle_128_0000255600_micro.nc';
else
   filename_sam = input_file_sam;
end

% CLUBB zt NetCDF filename.
if ( strcmp( input_file_clubb, 'default' ) )
   filename_clubb = '../../output/rico_zt.nc';
else
   filename_clubb = input_file_clubb;
end

% Declare the CLUBB vertical level index.
% CLUBB contour and line plots will be generated from PDF parameters from
% this level.  SAM LES data will be interpolated to the altitude of this
% level and then displayed in scatterplots and histograms.
clubb_height_idx = 19;

% Information to be printed on the plots.
casename = 'RICO';
print_note = 'Input fields (predictive fields)';

%==========================================================================

% SAM LES 3D file variables
global idx_3D_w
global idx_3D_rr
% CLUBB variables
global idx_w_1
global idx_w_2
global idx_mu_rr_1_n
global idx_mu_rr_2_n
global idx_varnce_w_1
global idx_varnce_w_2
global idx_sigma_rr_1_n
global idx_sigma_rr_2_n
global idx_corr_w_rr_1_n
global idx_corr_w_rr_2_n
global idx_mixt_frac
global idx_precip_frac_1
global idx_precip_frac_2

% Read SAM NetCDF file and obtain variables.
[ z_sam, time_sam, var_sam, units_corrector_type_sam, ...
  nx_sam, ny_sam, nz_sam, num_t_sam, num_var_sam ] ...
= read_SAM_3D_file( filename_sam );

% Read CLUBB zt NetCDF file and obtain variables.
[ z_clubb, time_clubb, var_clubb, units_corrector_type_clubb, ...
  nz_clubb, num_t_clubb, num_var_clubb ] ...
= read_CLUBB_file( filename_clubb );

% Use appropriate units (SI units).
[ var_sam ] ...
   = unit_corrector( num_var_sam, var_sam, units_corrector_type_sam, -1 );
[ var_clubb ] ...
   = unit_corrector( num_var_clubb, var_clubb, ...
                     units_corrector_type_clubb, -1 );

% Find the time in the CLUBB zt output file that is equal (or closest) to
% the SAM LES output time.
time_sam_sec = time_sam * 86400.0;
time_diff_clubb_sam_sec = abs( time_clubb - time_sam_sec );
% Initialize the minimum time difference and its (CLUBB) index.
idx_min_time_diff = 1;
min_time_diff = time_diff_clubb_sam_sec(idx_min_time_diff);
% Find the index of the minimum time difference between CLUBB output time
% and the requested SAM 3D file output time.
for iter = 2:1:num_t_clubb
   if ( time_diff_clubb_sam_sec(iter) < min_time_diff )
      min_time_diff = time_diff_clubb_sam_sec(iter);
      idx_min_time_diff = iter;
   end
end
% The CLUBB output index is the index that corresponds with the minimum
% time difference between the CLUBB output time and the SAM LES 3D file
% output time.
clubb_time_idx = idx_min_time_diff;

% Print the time of the SAM LES output.
fprintf( 'Time of SAM LES output (seconds): %d\n', time_sam_sec );

% Print the CLUBB output time index and the associated time.
fprintf( [ 'Time index of CLUBB output: %d;', ...
           ' Time of CLUBB output (seconds): %d\n' ], ...
           clubb_time_idx, time_clubb(clubb_time_idx) );

% Print the altitude at the CLUBB vertical level index.
fprintf( 'Altitude of CLUBB zt grid level (meters): %d\n', ...
         z_clubb(clubb_height_idx) );

% Place the SAM variables from the same location in the same 1-D index for
% use in a scatterplot.
w_sam  = zeros( nx_sam*ny_sam, 1 );
rr_sam = zeros( nx_sam*ny_sam, 1 );

if ( z_clubb(clubb_height_idx) > z_sam(nz_sam) )

   % The height of the CLUBB grid level is above the highest SAM LES grid
   % level.  Use SAM values from the highest SAM LES grid level.
   fprintf( [ 'The altitude of the CLUBB zt grid level is higher ', ...
              'than the highest SAM LES grid level.  The highest ', ...
              'SAM LES grid level will be used.\n' ] );
   fprintf( 'Altitude of SAM LES grid level (meters): %d\n', ...
            z_sam(nz_sam) );

   for i = 1:1:nx_sam
      for j = 1:1:ny_sam
         w_sam((i-1)*nx_sam+j)  = var_sam(idx_3D_w,i,j,nz_sam,1);
         rr_sam((i-1)*nx_sam+j) = var_sam(idx_3D_rr,i,j,nz_sam,1);
      end % j = 1:1:ny_sam
   end % i = 1:1:nx_sam

elseif ( z_clubb(clubb_height_idx) < z_sam(1) )
         
   % The height of the CLUBB grid level is below the lowest SAM LES grid
   % level.  Use SAM values from the lowest SAM LES grid level.
   fprintf( [ 'The altitude of the CLUBB zt grid level is lower ', ...
              'than the lowest SAM LES grid level.  The lowest ', ...
              'SAM LES grid level will be used.\n' ] );
   fprintf( 'Altitude of SAM LES grid level (meters):  %d\n', ...
            z_sam(1) );

   for i = 1:1:nx_sam
      for j = 1:1:ny_sam
         w_sam((i-1)*nx_sam+j)  = var_sam(idx_3D_w,i,j,1,1);
         rr_sam((i-1)*nx_sam+j) = var_sam(idx_3D_rr,i,j,1,1);
      end % j = 1:1:ny_sam
   end % i = 1:1:nx_sam

else % z_sam(1) <= z_clubb(clubb_height_idx) <= z_sam(nz_sam)

   % The height of the CLUBB grid level is found within the SAM LES
   % vertical domain.
   exact_lev_idx = -1;
   lower_lev_idx = -1;
   upper_lev_idx = -1;
   for k = 1:1:nz_sam

      if ( z_sam(k) == z_clubb(clubb_height_idx) )

         % The SAM LES grid level is at the exact same altitude as the
         % requested CLUBB grid level.
         exact_lev_idx = k;
         break

      elseif ( z_sam(k) < z_clubb(clubb_height_idx) )

         % The SAM LES grid level is below the requested CLUBB grid level.
         lower_lev_idx = k;

      else % z_sam(k) > z_clubb(clubb_height_idx)

         % The SAM LES grid level is above the requested CLUBB grid level.
         upper_lev_idx = k;

      end

      if ( upper_lev_idx == lower_lev_idx + 1 )
         break
      end

   end % k = 1:1:nz_sam

   if ( exact_lev_idx > 0 )

      fprintf( [ 'The altitude of the SAM LES grid level is the same ', ...
                 'as the CLUBB zt grid level.\n' ] );

      for i = 1:1:nx_sam
         for j = 1:1:ny_sam
            w_sam((i-1)*nx_sam+j)  = var_sam(idx_3D_w,i,j,exact_lev_idx,1);
            rr_sam((i-1)*nx_sam+j) = var_sam(idx_3D_rr,i,j,exact_lev_idx,1);
         end % j = 1:1:ny_sam
      end % i = 1:1:nx_sam

   else % interpolate between two levels.
 
      interp_weight ...
      = ( z_clubb(clubb_height_idx) - z_sam(lower_lev_idx) ) ...
        / ( z_sam(upper_lev_idx) - z_sam(lower_lev_idx) );

      fprintf( [ 'The altitude of the CLUBB zt grid level is between ', ...
                 'two SAM LES grid levels.\n' ] );
      fprintf( [ 'Altitude of the SAM LES grid level above the ', ...
                 'CLUBB zt grid level (meters):  %d\n' ], ...
                 z_sam(upper_lev_idx) );
      fprintf( [ 'Altitude of the SAM LES grid level below the ', ...
                 'CLUBB zt grid level (meters):  %d\n' ], ...
                 z_sam(lower_lev_idx) );

      for i = 1:1:nx_sam
         for j = 1:1:ny_sam

            w_sam((i-1)*nx_sam+j) ...
            = interp_weight ...
              * var_sam(idx_3D_w,i,j,upper_lev_idx,1) ...
              + ( 1.0 - interp_weight ) ...
                * var_sam(idx_3D_w,i,j,lower_lev_idx,1);

            rr_sam((i-1)*nx_sam+j) ...
            = interp_weight ...
              * var_sam(idx_3D_rr,i,j,upper_lev_idx,1) ...
              + ( 1.0 - interp_weight ) ...
                * var_sam(idx_3D_rr,i,j,lower_lev_idx,1);

         end % j = 1:1:ny_sam
      end % i = 1:1:nx_sam

   end % exact_lev_idx > 0

end % z_clubb(clubb_height_idx)

% Unpack CLUBB variables (PDF parameters).
mu_w_1 = var_clubb( idx_w_1, 1, 1, clubb_height_idx, clubb_time_idx );
mu_w_2 = var_clubb( idx_w_2, 1, 1, clubb_height_idx, clubb_time_idx );
mu_rr_1_n = var_clubb( idx_mu_rr_1_n, 1, 1, ...
                       clubb_height_idx, clubb_time_idx );
mu_rr_2_n = var_clubb( idx_mu_rr_2_n, 1, 1, ...
                       clubb_height_idx, clubb_time_idx );
sigma_w_1 = sqrt( var_clubb( idx_varnce_w_1, 1, 1, ...
                             clubb_height_idx, clubb_time_idx ) );
sigma_w_2 = sqrt( var_clubb( idx_varnce_w_2, 1, 1, ...
                             clubb_height_idx, clubb_time_idx ) );
sigma_rr_1_n = var_clubb( idx_sigma_rr_1_n, 1, 1, ...
                          clubb_height_idx, clubb_time_idx );
sigma_rr_2_n = var_clubb( idx_sigma_rr_2_n, 1, 1, ...
                          clubb_height_idx, clubb_time_idx );
corr_w_rr_1_n = var_clubb( idx_corr_w_rr_1_n, 1, 1, ...
                           clubb_height_idx, clubb_time_idx );
corr_w_rr_2_n = var_clubb( idx_corr_w_rr_2_n, 1, 1, ...
                           clubb_height_idx, clubb_time_idx );
mixt_frac = var_clubb( idx_mixt_frac, 1, 1, ...
                       clubb_height_idx, clubb_time_idx );
precip_frac_1 = var_clubb( idx_precip_frac_1, 1, 1, ...
                           clubb_height_idx, clubb_time_idx );
precip_frac_2 = var_clubb( idx_precip_frac_2, 1, 1, ...
                           clubb_height_idx, clubb_time_idx );

% Information to be printed on the plots.
print_alt = int2str( round( z_clubb(clubb_height_idx) ) );
print_time = int2str( round( time_clubb(clubb_time_idx) / 60.0 ) );
                       
% Plot the CLUBB PDF and LES points.
plot_CLUBB_PDF_LES_pts_NL( w_sam, rr_sam, nx_sam, ...
                           ny_sam, 100, 100, ...
                           mu_w_1, mu_w_2, mu_rr_1_n, mu_rr_2_n, ...
                           sigma_w_1, sigma_w_2, sigma_rr_1_n, ...
                           sigma_rr_2_n, corr_w_rr_1_n, ...
                           corr_w_rr_2_n, precip_frac_1, ...
                           precip_frac_2, mixt_frac, ...
                           'w    [m/s]', 'r_{r}    [kg/kg]', ...
                           [ '\bf ', casename ], 'w vs. r_{r}', ...
                           [ 'Time = ', print_time, ' minutes' ], ...
                           [ 'Altitude = ', print_alt, ' meters' ], ...
                           print_note )
