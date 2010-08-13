classdef convert_units
    %CONVERT Converts data generated by CLUBB to the form required for
    %output.
    %
    %   As the number and variety of conversion methods increases over time
    %   this class may have to be split up into several classes.
    %
    
    
    % These are constants that may be used by any function.
    properties(Constant)
        g0 = 9.8;
        p0 = 1e5;
        R  = 287.04;
        Cp = 1004.67;
        Lv = 2.5e6;
    end
    
    methods(Static)
        
        function time_height = create_time_height_series( height, sizet )
        % CREATE_TIME_HEIGHT_SERIES Copies the same height profile for the number of iterations specified by sizet.
        % Essentially this creates a 2D array
            col = reshape(height,max(size(height)),1);
            multiplier(1:sizet) = 1;
            time_height = col * multiplier;
            
        end

        function height = pressure_in_hPa_to_height_m( T_in_K, p_in_hPa, p_sfc )
        % PRESSURE_IN_HPA_TO_HEIGHT_M Converts temperature and pressure
        % profiles into a height profile.
        %
	%   Input(s)
	%     T_in_K Absolute Temperature [K]
	%     p_in_hPa Pressure [hPa]
	%
        %   Reference;
        %
        %     setdata.f90 from SAM
        %
          
          T_in_K = T_in_K .* (p_in_hPa/1000).^(convert_units.R/convert_units.Cp);

	  height(1) = convert_units.R/convert_units.g0*T_in_K(1)*log( p_sfc/p_in_hPa(1));
	    
          for i=2:length(p_in_hPa)
	      
              height(i) = height(i-1) + 0.5 * convert_units.R / convert_units.g0 * ...
                ( T_in_K(i) + T_in_K(i-1) ) * ... 
                                         log( p_in_hPa(i-1) / p_in_hPa(i) );
          
          end
        end
	    
        function exner = pressure_in_hPa_to_exner( p_in_hPa )
		exner = (p_in_hPa/1000).^(convert_units.R/convert_units.Cp);
	end

        function specific_humidity = total_water_mixing_ratio_to_specific_humidity ...
                ( total_water_mixing_ratio )
        % TOTAL_WATER_MIXING_RATIO_TO_SPECIFIC_HUMIDITY Converts total water mixing ratio to specific humidity.
        %
        %   Input(s)
        %       total_water_mixing_ratio Total Water Mixing Ratio [kg/kg]
        %
        %   Output(s)
        %       specific_humidity Specific Humdity [kg/kg]
        %
            specific_humidity = total_water_mixing_ratio ./ (1 + total_water_mixing_ratio);
            
        end
        
        function T_forcing = thlm_f_to_T_f(thlm_f, radht, exner)
        % THLM_F_TO_T_F Converts thlm_f to T_f using exner
        %
        %   Input(s)
        %       thlm_f Potential Temperature Forcing [K/s]
        %       exner Exner function                 [-]
        %
        %   Output(s)
        %       T_forcing Temperature forcing        [K/s]
        
            T_forcing = (thlm_f - radht) .* exner;
            
        end
        
        function vertical_movement_in_Pas = w_wind_in_ms_to_Pas( wm, rho)
        % W_WIND_IN_MS_TO_PAS Converts w_wind from m/s to Pa/s
        %
        %   Input(s)
        %       wm  w           [m/s]      
        %       rho Density     [kg/m^3]
        %
        %   Output(s)
        %       vertical_movement_in_Pas [Pa/s]
        %
            
            vertical_movement_in_Pas = -(wm .* convert_units.g0 .* rho);
            
        end

	function vertical_movement_in_ms = w_wind_in_Pas_to_ms(wm, rho)
        % W_WIND_IN_MS_TO_PAS Converts w_wind from m/s to Pa/s
        %
        %   Input(s)
        %       wm  w           [Pa/s]      
        %       rho Density     [kg/m^3]
        %
        %   Output(s)
        %       vertical_movement_in_Pas [Pa/s]
        %
            
            vertical_movement_in_ms = -wm ./ (convert_units.g0 .* rho);
            
        end

        function temperature = potential_temperature_to_temperature( potential_temperature, exner )
        % POTENTIAL_TEMPERATURE_TO_TEMPERATURE Converts potential
        % temperature to temperature using the exner function.
        %
        %   Input(s)
        %       potential_temperature Potential Temperatue [K]
        %       exner   Exner Function                     [-]
        %
        %   Output(s)
        %       temperature Temperature                    [K]
        %
            
            temperature = potential_temperature .* exner;
            
        end
	
	function potential_temperature = temperature_to_potential_temperature( temperature, exner )
        % POTENTIAL_TEMPERATURE_TO_TEMPERATURE Converts potential
        % temperature to temperature using the exner function.
        %
        %   Input(s)
        %       temperature	Temperature 		   [K]
        %       exner   Exner Function                     [-]
        %
        %   Output(s)
        %       potential_temperature Potential Temperature [K]
        %
            
            potential_temperature = temperature ./ exner;
            
        end

	function rho = pressure_to_rho( p_in_Pa, thvm, exner )
        % PRESSURE_TO_RHO Converts pressure to rho using
        % the exner function and potential temperature.
        %
        %   Input(s)
        %       p_in_Pa	Pressure 		   	   [Pa]
	%	thvm 	Potential Temperature		   [K]
        %       exner   Exner Function                     [-]
        %
        %   Output(s)
        %       rho 	Density				 [Kg/m^3]
        %
            
            rho = p_in_Pa ./ (convert_units.R .* thvm .* exner);
            
        end

	function in_Kms = flux_in_W_m_sq_to_Kms( in_W_m_sq, rho )
	%FLUX_IN_W_M_SQ_TO_KMS Converts flux in W/m^2 to Km/s
	%
	%   Input(s)
	%	in_W_m_sq	Flux of temperature	[W/m^2]
	%	rho		Density			[kg/m^3]
	%   Output(s)
	%	in_Kms		Flux of temperature	[Km/s]
	%	

	    in_Kms = in_W_m_sq ./ (rho * convert_units.Cp);

	end

	function in_kgkgms = flux_in_W_m_sq_to_kgkgms( in_W_m_sq, rho )
	%FLUX_IN_W_M_SQ_TO_KMS Converts flux in W/m^2 to Km/s
	%
	%   Input(s)
	%	in_W_m_sq	Flux of moisture	[W/m^2]
	%	rho		Density			[kg/m^3]
	%   Output(s)
	%	in_kgkgms	Flux of moisture	[(kg*kg)/s]
	%	

	    in_kgkgms = in_W_m_sq ./ (rho * convert_units.Lv);

       end
 
    end
    
end
