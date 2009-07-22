function PlotCreator( caseName, plotTitle, plotNum, plotType, startTime, endTime, startHeight, endHeight, plotUnits, tickCount, varargin )

%Display the variables that were passed in (debug output)
caseName
plotTitle
plotUnits
plotNum
plotType
startTime
endTime
startHeight
endHeight

%Define a padding
maxTextLength = 20;

%Figure out the number of optional arguments passed in
optargin = size(varargin,2);

%Optional argument format is as follows:
%'/PATH/TO/FILE', 'timeseries or profile', 'varname', 'title', 'units', 'lineWidth', 'lineType', 'lineColor'

%This means we can easily figure out the number of lines on the plot by dividing by 8
numLines = optargin / 7;

%Create a blank plot of the proper type so we have somewhere to draw lines
fig_height = 328;
fig_width = 312;

% Open figure to set size.
figure('Position',[ 0 0 fig_width fig_height ])
set(gcf, 'PaperPositionMode', 'manual')
set(gcf, 'PaperUnits', 'points')
set(gcf, 'PaperPosition', [ 0.0 0.0 fig_width fig_height ])

%Pre-allocate minimum and maximum values
minVals(1:numLines) = 0;
maxVals(1:numLines) = 0;

%Preallocate the arrays needed for legend construction
lines(1:numLines) = 0; %This is the collection where lines are stored
clear legendText;

%Loop through each line on the plot
for i=1:numLines
	filePath = varargin{1 + ((i - 1) * 7)};
	varName = varargin{2 + ((i - 1) * 7)};
	varExpression = varargin{3 + ((i - 1) * 7)};
	lineName = varargin{4 + ((i - 1) * 7)};
	lineWidth = varargin{5 + ((i - 1) * 7)};
	lineType = varargin{6 + ((i - 1) * 7)};
	lineColor = varargin{7 + ((i - 1) * 7)};

	%Determine the type of file being read in
	extension = DetermineExtension(filePath);

	%Determine the variables that need to be read in
	varsToRead = ParseVariablesFromExpression(varExpression);

	%Read in the necessary variables
	for j=1:size(varsToRead,2);
		%We need to convert the variable name to read from a cell array to a string
		varString = cell2mat(varsToRead(j));
		disp(['Reading variable ', varString]);

		if strcmp(extension, 'ctl')
			[variableData, levels] = VariableReadGrADS(filePath, varString, startTime, endTime, plotType);
		elseif strcmp(extension, 'nc')
			[variableData, levels] = VariableReadNC(filePath, varString, startTime, endTime, plotType);
		end

		%Store the read in values to the proper variable name (ex. variable rtm will be read in to the variable named rtm,
		%this allows the expression to be used as is).
		eval([varString, '= variableData;']);
	end

	%Figure out indicies for start and end height
	if strcmp(plotType, 'profile')	
		bottomIndex = 0;
		topIndex = 0;
		
		%Max is used to prevent hangs caused by failed variable reading
		for j=1:max(size(levels))
			if levels(j) <= startHeight
				bottomIndex = j;
			end
			if levels(j) <= endHeight
				topIndex = j;
			end
		end
	end

	%Create a time array
	if strcmp(extension, 'ctl')
		[dummy, dummy , dummy, t_time_steps, time_step_length, dummy, dummy] = header_read_expanded(filePath);
	elseif strcmp(extension, 'nc')
		[dummy, dummy , dummy, t_time_steps, time_step_length, dummy, dummy] = header_read_expanded_netcdf(filePath);
	end

	for j=1:(ceil((endTime - startTime) / time_step_length) + 1)
		times(j) = startTime + ((j - 1) * time_step_length);
	end

	%Now evaluate the expression using the read in values,
	eval(['valueToPlot =', varExpression, ';']);
	
	%At this point, the value of the expression is contained in valueToPlot

	%Add a the line to the plot
	if strcmp(plotType, 'profile')
		lines(i) = ProfileFunctions.addLine(lineName, levels, valueToPlot, lineWidth, lineType, lineColor);
	elseif strcmp(plotType, 'timeseries')
		lines(i) = TimeseriesFunctions.addLine(lineName, times, valueToPlot, lineWidth, lineType, lineColor);
	end
	
	%Store values needed for axis scaling
	if strcmp(plotType, 'profile')
		minVals(i) = min(valueToPlot(bottomIndex:topIndex));
		maxVals(i) = max(valueToPlot(bottomIndex:topIndex));
	elseif strcmp(plotType, 'timeseries')
		minVals(i) = min(valueToPlot);
		maxVals(i) = max(valueToPlot);
	end

	%Set the text for the legend
	legendText(i,1:size(lineName,2)) = lineName;
end

%Add a legend and scale the axis
if strcmp(plotType, 'profile')	
	ProfileFunctions.setTitle(plotTitle);
	ProfileFunctions.setAxisLabels(plotUnits, 'Height [m]'); 
	ProfileFunctions.addLegend(lines, legendText);
	ProfileFunctions.setAxis(min(minVals), max(maxVals), startHeight, endHeight);
elseif strcmp(plotType, 'timeseries')		
	TimeseriesFunctions.setTitle(plotTitle);
	TimeseriesFunctions.setAxisLabels('Time [min]', plotUnits); 	
	TimeseriesFunctions.addLegend(lines, legendText);
	TimeseriesFunctions.setAxis(min(minVals), max(maxVals), startTime, endTime);
end

%Output the EPS file
mkdir([ 'output_', int2str(tickCount)]);
output_file_name = [ 'output_', int2str(tickCount), '/', caseName, '_', int2str(plotNum), '.eps' ];
print( '-depsc2', output_file_name );
