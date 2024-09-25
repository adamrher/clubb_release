# -*- coding: utf-8 -*-

# Run this app with `python3 sens_matrix_dashboard.py` and
# view the plots at http://127.0.0.1:8050/ in your web browser.
# (To open a web browser on a larson-group computer,
# login to malan with `ssh -X` and then type `firefox &`.)

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
#import pca
import dash
from dash import dcc
#import dash_core_components as dcc
from dash import html
#import dash_html_components as html




def createFigs(metricsNames, 
               paramsNames, transformedParamsNames, paramsScales,
               metricsWeights, obsMetricValsCol, normMetricValsCol, magParamValsRow,
               defaultBiasesCol, defaultBiasesApproxNonlin, defaultBiasesApproxElastic, 
               defaultBiasesApproxNonlinNoCurv, defaultBiasesApproxNonlin2xCurv,
               normlzdDefaultBiasesCol,
               normlzdCurvMatrix, normlzdSensMatrixPoly, normlzdConstMatrix,
               normlzdOrdDparamsMin, normlzdOrdDparamsMax,
               normlzdWeightedSensMatrixPoly,
               dnormlzdParamsSolnNonlin,
               defaultParamValsOrigRow,
               linSolnBiasesCol, normlzdLinplusSensMatrixPoly,
               paramsSolnLin, dnormlzdParamsSolnLin,
               paramsSolnNonlin,
               paramsSolnElastic, dnormlzdParamsSolnElastic,
               sensNcFilenames, sensNcFilenamesExt, defaultNcFilename):

    ##############################################
    #
    #    Create plots
    #
    ##############################################


    print("Creating plots . . .")


    # Calculate symmetric error bars on fitted parameter values,
    #    based on difference in sensitivity matrix, i.e., based on size of nonlinear terms.
    #    For use in figures such as paramsErrorBarsFig.
    paramsLowValsPCBound, paramsHiValsPCBound = \
        calcParamsBounds(metricsNames, paramsNames, transformedParamsNames,
                     metricsWeights, obsMetricValsCol, normMetricValsCol,
                     magParamValsRow,
                     sensNcFilenames, sensNcFilenamesExt, defaultNcFilename)

    threeDotFig = \
        createThreeDotFig(metricsNames, paramsNames, transformedParamsNames,
                               metricsWeights, obsMetricValsCol, normMetricValsCol, magParamValsRow,
                               normlzdCurvMatrix, normlzdSensMatrixPoly, normlzdConstMatrix,
                               normlzdOrdDparamsMin, normlzdOrdDparamsMax,
                               sensNcFilenames, sensNcFilenamesExt, defaultNcFilename)

    # Create plot showing how well the regional biases are actually removed
    metricsSens = np.linalg.norm(normlzdWeightedSensMatrixPoly, axis=1) # measure of sensitivity of each metric
    # metricsSensOrdered = (rankdata(metricsSens) - 1).astype(int)  # this ordering doesn't work as an index
    metricsSensOrdered = metricsSens.argsort()
    metricsNamesOrdered = metricsNames[metricsSensOrdered]  # list of metrics names, ordered from least to most sensitive


    biasesOrderedArrowFig = \
        createBiasesOrderedArrowFig(metricsSensOrdered, metricsNamesOrdered,
                                    defaultBiasesCol, normMetricValsCol, 
                                    defaultBiasesApproxNonlinNoCurv, defaultBiasesApproxNonlin2xCurv,
                                    defaultBiasesApproxNonlin,
                                    linSolnBiasesCol)


    normlzdSensMatrixOrdered = normlzdSensMatrixPoly[metricsSensOrdered,:]
    ## Form matrix of parameter perturbations, for later multiplication into the sensitivity matrix
    dnormlzdParamsSolnNonlinMatrix = np.ones((len(metricsNames),1)) @ dnormlzdParamsSolnNonlin.T
    normlzdSensParamsMatrixOrdered = normlzdSensMatrixOrdered * dnormlzdParamsSolnNonlinMatrix


    # Create plot showing lumped linear+nonlinear contributions to each metric
    # Form matrix of parameter perturbations, for later multiplication into the sensitivity matrix
    dnormlzdParamsSolnNonlinMatrix = np.ones((len(metricsNames),1)) @ dnormlzdParamsSolnNonlin.T
    curvParamsMatrixOrdered = 0.5 * normlzdCurvMatrix[metricsSensOrdered,:] * dnormlzdParamsSolnNonlinMatrix**2
    #print("Sum rows=", np.sum(-normlzdSensParamsMatrixOrdered-curvParamsMatrixOrdered, axis=1))
    minusNonlinMatrixOrdered = -1*curvParamsMatrixOrdered + -1*normlzdSensParamsMatrixOrdered


    biasTotContrbBarFig = \
          createBarChart( minusNonlinMatrixOrdered, index=metricsNamesOrdered, columns=paramsNames,
           #               barBase = np.zeros(numMetrics),
                          #barBase = -defaultBiasesCol[metricsSensOrdered]/np.abs(normMetricValsCol[metricsSensOrdered]) @ np.ones((1,len(paramsNames))),
                          orientation = 'v',
                          title="""Linear + nonlinear contributions of parameters to actual removal of regional biases""",
                          xlabel="Regional metric", ylabel="Contribution to bias removal",
                          width=800, height=500 )

    paramsTotContrbBarFig = \
          createBarChart( minusNonlinMatrixOrdered.T, index=paramsNames, columns=metricsNamesOrdered,
                          orientation = 'v',
                          title="""Linear + nonlinear contributions of regional metrics to columns of sens matrix""",
                          xlabel="Parameter", ylabel="Contribution to bias removal",
                          width=800, height=500 )

    linplusSensMatrixBarFig = \
          createBarChart( normlzdLinplusSensMatrixPoly[metricsSensOrdered,:].T, index=paramsNames, columns=metricsNamesOrdered,
          #                barBase = np.zeros_like(paramsScales),
                          orientation = 'v',
                          title="""Linplus contributions of parameters to actual removal of regional biases""",
                          xlabel="Parameter", ylabel="Contribution to bias removal",
                          width=800, height=500 )

    metricsCorrArrayFig = createCorrArrayFig( normlzdLinplusSensMatrixPoly, metricsNames,
                          title='cos(angle) among metrics (i.e., rows of sens matrix)' )

    minusNormlzdDefaultBiasesCol = \
             -defaultBiasesCol[metricsSensOrdered,0]/np.abs(normMetricValsCol[metricsSensOrdered,0])
    residBias = (-defaultBiasesApproxNonlin-defaultBiasesCol)[metricsSensOrdered,0] \
                       / np.abs(normMetricValsCol[metricsSensOrdered,0])
    metricsBarChart = createMetricsBarChart(metricsNames[metricsSensOrdered],paramsNames,
                                            minusNormlzdDefaultBiasesCol, residBias, minusNonlinMatrixOrdered,
                                            title='Removal of biases in each metric by each parameter')


    biasLinNlIndivContrbBarFig = \
    createBiasLinNlIndivContrbBarFig( normlzdSensParamsMatrixOrdered, curvParamsMatrixOrdered,
                                          metricsNamesOrdered, paramsNames )


    biasVsBiasApproxScatterplot = \
    createBiasVsBiasApproxScatterplot(defaultBiasesApproxNonlin, defaultBiasesCol,
                                          normMetricValsCol,
                                          metricsNames )


    biasSensMatrixScatterFig = \
    createBiasSensMatrixScatterFig(defaultBiasesCol, defaultBiasesApproxElastic,
                                       normMetricValsCol, metricsNames)

    dpMinMatrixScatterFig = \
    createDpMinMatrixScatterFig(defaultBiasesCol, normlzdSensMatrixPoly,
                                    normMetricValsCol, metricsNames)

    maxSensMetricsFig = \
    createMaxSensMetricsFig(normlzdSensMatrixPoly, metricsNames)

    biasesVsSensMagScatterplot = \
    createBiasesVsSensMagScatterplot(normlzdLinplusSensMatrixPoly, defaultBiasesCol,
                                         normMetricValsCol, metricsNames)


    biasesVsSensArrowFig = \
    createBiasesVsSensArrowFig(normlzdWeightedSensMatrixPoly, defaultBiasesCol,
                               defaultBiasesApproxNonlin,
                               normMetricValsCol, metricsNames)


    normlzdSensMatrixColsFig = \
    createNormlzdSensMatrixColsFig( defaultBiasesCol, normlzdSensMatrixPoly,
                                       normMetricValsCol, metricsNames, paramsNames )


    normlzdSensMatrixRowsFig = \
    createNormlzdSensMatrixRowsFig( normlzdSensMatrixPoly,
                                    metricsNames, paramsNames )



    paramsErrorBarsFig = \
    createParamsErrorBarsFig(paramsNames, defaultParamValsOrigRow, paramsScales,
                             paramsLowValsPCBound, paramsHiValsPCBound,
                             paramsSolnLin, dnormlzdParamsSolnLin,
                             paramsSolnNonlin, dnormlzdParamsSolnNonlin,
                             paramsSolnElastic, dnormlzdParamsSolnElastic)


    #pdb.set_trace()

    # Create figure that shows the sensitivity matrix and bias column, both color coded.
    sensMatrixBiasFig = createMatrixPlusColFig( matrix = normlzdLinplusSensMatrixPoly,
                         matIndexLabel = metricsNames,
                         matColLabel = paramsNames,
                         colVector = -np.around(defaultBiasesCol/np.abs(normMetricValsCol), decimals=2),
                         colVectIndexLabel = metricsNames,
                         colVectColLabel = ['-Normalized Biases'],
                         plotTitle='Color-coded normalized sensitivity matrix',
                         reversedYAxis = 'reversed' )


    # Create figure that plots color-coded parameter correlation matrix plus parameter-bias correlation column.
    XT_dot_X_Linplus = normlzdLinplusSensMatrixPoly.T @ normlzdLinplusSensMatrixPoly
    #XT_dot_X_Linplus = normlzdSensMatrixPoly.T @ normlzdSensMatrixPoly
    #XT_dot_X_Linplus = normlzdWeightedLinplusSensMatrixPoly.T @ normlzdWeightedLinplusSensMatrixPoly
    (XT_dot_X_Linplus_corr, stdMatrixInv ) = covMatrix2corrMatrix( XT_dot_X_Linplus, returnStd=True )
    normlzdStdDefaultBiasesCol = stdMatrixInv @ normlzdLinplusSensMatrixPoly.T @ normlzdDefaultBiasesCol
    #normlzdStdDefaultBiasesCol = stdMatrixInv @ normlzdSensMatrixPoly.T @ normlzdDefaultBiasesCol
    #normlzdStdDefaultBiasesCol = stdMatrixInv @ normlzdWeightedLinplusSensMatrixPoly.T @ normlzdWeightedDefaultBiasesCol
    paramsCorrArrayBiasFig = createMatrixPlusColFig( matrix = XT_dot_X_Linplus_corr,
                         matIndexLabel = paramsNames,
                         matColLabel = paramsNames,
                         colVector = -np.around(normlzdStdDefaultBiasesCol, decimals=2),
                         colVectIndexLabel = paramsNames,
                         colVectColLabel = ['Projection onto -biases'],
                         plotTitle='Cosines of angles between columns of sensitivity matrix',
                         reversedYAxis = 'reversed' )

    # Create figure that plots color-coded projection matrix plus bias column.
    XT_dot_X_Linplus_inv = np.linalg.inv( XT_dot_X_Linplus )
    projMatrix = normlzdLinplusSensMatrixPoly @ XT_dot_X_Linplus_inv @ normlzdLinplusSensMatrixPoly.T
    #print("projMatrix rows=", np.linalg.norm( projMatrix, axis=1))
    projectionMatrixFig = createMatrixPlusColFig( matrix = projMatrix,
                         matIndexLabel = metricsNames,
                         matColLabel = metricsNames,
                         colVector = -np.around(normlzdDefaultBiasesCol, decimals=2),
                         colVectIndexLabel = metricsNames,
                         colVectColLabel = ['-Normalized Biases'],
                         plotTitle='Projection matrix',
                         reversedYAxis = 'reversed' )


    paramsCorrArrayFig = \
    createParamsCorrArrayFig(normlzdLinplusSensMatrixPoly, normlzdDefaultBiasesCol,
                                 paramsNames)


    dpMin2PtFig = \
    createDpMin2PtFig( normlzdSensMatrixPoly, defaultBiasesCol,
                          normMetricValsCol, metricsNames )

    # Create scatterplot to look at outliers
    #createPcaBiplot(normlzdLinplusSensMatrixPoly, defaultBiasesCol, normMetricValsCol, metricsNames, paramsNames)

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    sensMatrixDashboard = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    sensMatrixDashboard.layout = html.Div(children=[
        html.H1(children='Sensitivity matrix diagnostics'),

        html.Div(children=''' '''),

        dcc.Graph( id='paramsErrorBarsFig', figure=paramsErrorBarsFig ),
        dcc.Graph( id='biasesOrderedArrowFig', figure=biasesOrderedArrowFig ),
        dcc.Graph( id='metricsBarChart', figure=metricsBarChart ),
        dcc.Graph( id='biasTotContrbBarFig', figure=biasTotContrbBarFig ),
        dcc.Graph( id='paramsTotContrbBarFig', figure=paramsTotContrbBarFig ),
        dcc.Graph( id='linplusSensMatrixBarFig', figure=linplusSensMatrixBarFig ),
        dcc.Graph( id='biasLinNlIndivContrbBarFig', figure=biasLinNlIndivContrbBarFig ),
        dcc.Graph( id='biasesVsSensMagScatterplot', figure=biasesVsSensMagScatterplot ),
        dcc.Graph( id='biasVsBiasApproxScatterplot', figure=biasVsBiasApproxScatterplot ),
       #config= { 'toImageButtonOptions': { 'scale': 6 } }
        dcc.Graph( id='sensMatrixBiasFig', figure=sensMatrixBiasFig ),
        dcc.Graph( id='paramsCorrArrayBiasFig', figure=paramsCorrArrayBiasFig ),
        dcc.Graph( id='paramsCorrArrayFig', figure=paramsCorrArrayFig ),
        dcc.Graph( id='metricsCorrArrayFig', figure=metricsCorrArrayFig ),
        dcc.Graph( id='projectionMatrixFig', figure=projectionMatrixFig ),
        dcc.Graph( id='dpMin2PtFig', figure=dpMin2PtFig ),
        dcc.Graph( id='threeDotFig', figure=threeDotFig ),
        dcc.Graph( id='biasSensScatterFig', figure=biasSensMatrixScatterFig ),
        dcc.Graph( id='dpMinMatrixScatterFig', figure=dpMinMatrixScatterFig ),
        dcc.Graph( id='maxSensMetricsFig', figure=maxSensMetricsFig ),
        dcc.Graph( id='normlzdSensMatrixColsFig', figure=normlzdSensMatrixColsFig ),
        dcc.Graph( id='normlzdSensMatrixRowsFig', figure=normlzdSensMatrixRowsFig ),

        #dcc.Graph( id='biasesVsSensArrowFig', figure=biasesVsSensArrowFig ),

    ])

    sensMatrixDashboard.run_server(debug=True)


    return ( paramsLowValsPCBound, paramsHiValsPCBound, threeDotFig )

def covMatrix2corrMatrix( covMatrix, returnStd=False ):

    # https://gist.github.com/wiso/ce2a9919ded228838703c1c7c7dad13b

    import numpy as np

    stdVector = np.sqrt( np.diag( covMatrix ) )
    stdMatrixInv = np.diag( 1.0 / stdVector )
    corrMatrix = stdMatrixInv @ covMatrix @ stdMatrixInv
    if returnStd:
        return ( corrMatrix, stdMatrixInv )
    else:
        return corrMatrix



def createMatrixPlusColFig( matrix, matIndexLabel, matColLabel,
                            colVector, colVectIndexLabel, colVectColLabel,
                            plotTitle, reversedYAxis=None ):
    '''Creates a figure that displays a color-coded matrix and an accompanying column vector.'''

    import numpy as np
    import pandas as pd
    import plotly.figure_factory as ff
    import plotly.express as px
    from plotly.subplots import make_subplots
    import pdb

    # First create a sub-figure that displays color-coded matrix
    roundedNormlzdSensMatrix = np.around( matrix, decimals=2)
    df_sensmat = pd.DataFrame(roundedNormlzdSensMatrix,
                  index=matIndexLabel,
                  columns=matColLabel)
    matMaxAbs = np.max(np.abs(roundedNormlzdSensMatrix))
    matSubfig = px.imshow(
                   df_sensmat.to_numpy(),
                   x=df_sensmat.columns.tolist(),
                   y=df_sensmat.index.tolist(),
                   text_auto=True
                   )
    matSubfig.update_xaxes(side="bottom")
    matSubfig.update_layout(
    title_text=plotTitle,
    title_x=0.5,
    #width=800,
    #height=1400,
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_zeroline=False,
    yaxis_zeroline=False,
    )

    # Now create a sub-figure showing a color-coded column matrix
    df_biasArray = pd.DataFrame( colVector,
                   index=colVectIndexLabel,
                   columns= colVectColLabel)
    colVectSubfig = px.imshow(
                   df_biasArray.to_numpy(),
                   x=df_biasArray.columns.tolist(),
                   y=df_biasArray.index.tolist(),
                   text_auto=True
                   )
    colVectSubfig.update_layout(
    title_text='', 
    title_x=0.5, 
    #width=10, 
    #height=1400,
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_zeroline=False,
    yaxis_zeroline=False,
    )

    # Now combine the matrix and column sub-figures into one figure
    matrixPlusColFig = make_subplots(
    rows=1, cols=2,
    column_widths=[0.9, 0.1],
    horizontal_spacing=0.3,
    )
    matrixPlusColFig.add_trace(matSubfig.data[0], row=1, col=1)
    matrixPlusColFig.add_trace(colVectSubfig.data[0], row=1, col=2)
    matrixPlusColFig.update_layout(
        title_text=plotTitle,
        height=700,
        width= 1000,
        template='plotly_white')
    matrixPlusColFig.update_layout(coloraxis=dict(colorscale='RdBu_r',cmin=-matMaxAbs,cmax=matMaxAbs), showlegend=False)
    matrixPlusColFig.update_yaxes( autorange=reversedYAxis, row=1, col=2 ) 
    matrixPlusColFig.update_yaxes( autorange=reversedYAxis, row=1, col=1 ) 

    #pdb.set_trace()

    return ( matrixPlusColFig )


def createMetricsBarChart( metricsNames, paramsNames, biases, residBias, sensMatrix, title ):


    import plotly.graph_objects as go
    import numpy as np
    import pdb

    biases = np.reshape(biases, (-1,1))
    barBase = np.copy(biases)  # np.copy prevents biases variable from changing
    rightEnd = np.copy(biases)
    leftEnd = np.copy(biases)
    barsData = []
    for col in range(len(paramsNames)):
        #print("paramsNames[col]=", paramsNames[col])
        sensCol = sensMatrix[:,[col]]
        #print("sensCol=", sensCol )
        #print("rightEnd=", rightEnd )
        for row in range( len(sensCol) ):
            if ( np.sign(sensCol[row]) > 0 ):
                barBase[row] = rightEnd[row]
            else:
                barBase[row] = leftEnd[row]

        #print("barBase=", barBase)
        #print("biases during=", biases)
        barsData.append( go.Bar(name=paramsNames[col], y=metricsNames, x=sensCol[:,0],
            base=barBase[:,0], orientation="h" ) )
        rightEnd = rightEnd + np.maximum( np.zeros_like(sensCol), sensCol )
        leftEnd  = leftEnd + np.minimum( np.zeros_like(sensCol), sensCol )

    # Insert a narrow black horizontal line in each bar to denote the improvement wrought by tuning
    residBias = np.reshape(residBias, (-1,1))
    barsData.append( go.Bar(name='+ tuning correction',
                            y=metricsNames, x=-residBias[:,0]+biases[:,0], base=residBias[:,0],
                            orientation="h",
                            width = 0.2,
                            marker_line_color = 'black', marker_color='black', marker_line_width = 2,
                            opacity = 1.0
                           )
                   )

    # Insert a black vertical line in each bar to denote default biases that we want to remove
    barsData.append( go.Bar(name='default bias',
                            y=metricsNames, x=np.zeros(len(metricsNames)), base=biases[:,0],
                            orientation="h",
                            marker_line_color = 'black', marker_color='black', marker_line_width = 5
                            )
                   )

    metricsBarChart = go.Figure(data=barsData)

    # Change the bar mode
    metricsBarChart.update_layout(title = title)
    metricsBarChart.update_layout(barmode='stack')
    metricsBarChart.update_xaxes(visible=True,zeroline=True,zerolinewidth=4,zerolinecolor='gray') # Plot y axis
    metricsBarChart.update_layout( width=800, height=50*len(metricsNames)  )
    metricsBarChart.update_xaxes(title="-Normalized biases")

    #pdb.set_trace()

    return metricsBarChart


def createBarChart( matrix, index, columns, 
     #                   barBase,
                        orientation,
                        title, 
                        xlabel, ylabel,
                        width, height):

    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    df = pd.DataFrame(matrix,
                      index=index,
                      columns=columns)
    barChart = px.bar(df, x=df.index, y=df.columns,
                          #base=barBase,
                          #offset=1,
                          orientation=orientation,
                          title = title)
    barChart.update_xaxes(title=xlabel)
    barChart.update_yaxes(title=ylabel)
    barChart.update_layout(hovermode="x")
    barChart.update_layout(showlegend=True)
    barChart.update_yaxes(visible=True,zeroline=True,zerolinewidth=1,zerolinecolor='gray') # Plot x axis
    barChart.update_layout( width=width, height=height  )
    #barChart.update_layout(barmode='relative')

    return barChart

def createThreeDotFig(metricsNames, paramsNames, transformedParamsNames,
                               metricsWeights, obsMetricValsCol, normMetricValsCol, magParamValsRow,
                               normlzdCurvMatrix, normlzdSensMatrixPoly, normlzdConstMatrix,
                               normlzdOrdDparamsMin, normlzdOrdDparamsMax,
                               sens1NcFilenames, sens2NcFilenames, defaultNcFilename):

    """
    For nonlinear 2nd-order term of Taylor series: 0.5*dp^2*d2m/dp2+...,
    construct a numMetrics x numParams matrix of 2nd-order derivatives, d2m/dp2.
    Each row is a different metric.  Each column is a different parameter.
    The matrix is nondimensionalized by the observed values of metrics
    and maximum values of parameters.
    """
    import numpy as np
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    import sys
    import netCDF4
    #import matplotlib.pyplot as plt
    import pdb

    from analyze_sensitivity_matrix import setupSensArrays
    from set_up_dashboard_inputs import setupDefaultParamVectors, \
                                        setupDefaultMetricValsCol
    from scipy.interpolate import UnivariateSpline

    if ( len(paramsNames) != len(sens1NcFilenames)   ):
        print("Number of parameters must equal number of netcdf files.")
        quit()

    # Number of tunable parameters
    numParams = len(paramsNames)

    # Number of metrics
    numMetrics = len(metricsNames)

    # Based on the default simulation,
    #    set up a column vector of metrics and a row vector of parameter values.
    defaultParamValsRow, defaultParamValsOrigRow = \
        setupDefaultParamVectors(paramsNames, transformedParamsNames,
                                 numParams,
                                 defaultNcFilename)

    # Set up a column vector of metric values from the default simulation
    defaultMetricValsCol = \
        setupDefaultMetricValsCol(metricsNames, defaultNcFilename)
    defaultMetricValsMatrix = defaultMetricValsCol @ np.ones((1,numParams))

    # Based on the numParams sensitivity simulations,
    #    set up a row vector of modified parameter values.
    # Also set up numMetrics x numParams matrix,
    #    each column of which lists the metrics
    #    from one of the sensitivity simulations
    sens1MetricValsMatrix, sens1ParamValsRow, sens1ParamValsOrigRow = \
        setupSensArrays(metricsNames, paramsNames, transformedParamsNames,
                        numMetrics, numParams,
                        sens1NcFilenames,
                        beVerbose=False)

    # Set up sensitivity-simulation matrices from the extended sensitivity simulation
    sens2MetricValsMatrix, sens2ParamValsRow, sens2ParamValsOrigRow = \
        setupSensArrays(metricsNames, paramsNames, transformedParamsNames,
                        numMetrics, numParams,
                        sens2NcFilenames,
                        beVerbose=False)

    threeDotFig = make_subplots( rows=numMetrics, cols=numParams,
                                shared_xaxes=True
                                #horizontal_spacing = 0.1/numParams,
                                #vertical_spacing = 0.1/numMetrics
                                )
    for arrayCol in np.arange(numParams):
        for arrayRow in np.arange(numMetrics):

            paramVals = [defaultParamValsRow[0][arrayCol], 
                         sens1ParamValsRow[0][arrayCol], 
                         sens2ParamValsRow[0][arrayCol]]
            metricVals = [defaultMetricValsMatrix[arrayRow][arrayCol], 
                          sens1MetricValsMatrix[arrayRow][arrayCol],
                          sens2MetricValsMatrix[arrayRow][arrayCol]]

            # Plot 3 dots at metric values
            threeDotFig.add_trace(
                go.Scatter(x=paramVals, y=metricVals, 
                               mode='markers',
                               marker=dict(color='black', size=5)),
                           row=arrayRow+1, 
                           col=arrayCol+1
                                  )

            # Plot quadratic curve passing through 3 dots
            paramPts = np.linspace( np.min(paramVals), np.max(paramVals), num=60 )
            #print("paramPts =", paramPts)
            dnormlzdParamPts = np.linspace( normlzdOrdDparamsMin[arrayRow,arrayCol],
                                            normlzdOrdDparamsMax[arrayRow,arrayCol], num=60 )
            metricPts = np.zeros_like(dnormlzdParamPts)
            for idx, dnormlzdParamPt in enumerate(dnormlzdParamPts):
                metricPts[idx] = 0.5 * normlzdCurvMatrix[arrayRow,arrayCol] * dnormlzdParamPt**2 \
                                 + normlzdSensMatrixPoly[arrayRow,arrayCol] * dnormlzdParamPt \
                                 + normlzdConstMatrix[arrayRow,arrayCol]
                metricPts[idx] = metricPts[idx] * np.abs(normMetricValsCol[arrayRow])

            #print("metricPts =", metricPts)
            threeDotFig.add_trace(
                        go.Scatter(x=paramPts, y=metricPts,
                               mode='lines',
                               line=dict(color='blue', width=2)),
                        row=arrayRow+1,
                        col=arrayCol+1
                                  )

            # Calculate horizontal line at observed value
            threeObsMetricVals = np.squeeze(obsMetricValsCol[arrayRow][0]*np.ones((3,1)))
            #threeObsMetricValsList = threeObsMetricVals.tolist()
            #print("obsMetricVals=", threeObsMetricValsList)
            #print("paramVals=", paramVals)            
            threeDotFig.add_trace(
                go.Scatter(x=paramVals, y=threeObsMetricVals, 
                               mode='lines',
                               line=dict(color='red', width=2)),
                           row=arrayRow+1,
                           col=arrayCol+1
                                  )

            # Label the metric and parameter for the subplots
            if (arrayRow == numMetrics-1):  # Put params labels along bottom of plot
                threeDotFig.update_xaxes(title_text=paramsNames[arrayCol]\
                                         .replace('clubb_','').replace('c_invrs_tau_','')\
                                         .replace('wpxp_n2','n2').replace('threshold','thresh'),
                                         #title_font_size=8,
                                         tickangle=45,
                                         row=arrayRow+1, col=arrayCol+1
                                         )
            if (arrayRow == 0):  # Put params labels along top of plot
                threeDotFig.update_xaxes(title_text=paramsNames[arrayCol]\
                                         .replace('clubb_','').replace('c_invrs_tau_','')\
                                         .replace('wpxp_n2','n2').replace('threshold','thresh'),
                                         row=arrayRow+1, col=arrayCol+1,
                                         #side="top", title_standoff=100
                                         )
            if (arrayCol == 0): # Insert metrics label only along left edge of plot
                threeDotFig.update_yaxes(title_text=metricsNames[arrayRow], row=arrayRow+1, col=arrayCol+1)
            threeDotFig.update_layout(showlegend=False,
                    title_text="Simulated metric values vs. parameter values",
                    height=2500)
            
    threeDotFig.update_xaxes(tickangle=45) # Put params label at 45-degree angle

    return ( threeDotFig )

def createCorrArrayFig( matrix, indexLabels, title ):

    import numpy as np
    import pandas as pd
    import plotly.figure_factory as ff
    import plotly.express as px
    import pdb

    cosAnglesMatrix = calcMatrixAngles( matrix )
    #cosAnglesMatrix = np.copy( matrix )
    roundedCosAnglesMatrix = np.around(cosAnglesMatrix, decimals=2)

    df = pd.DataFrame(roundedCosAnglesMatrix,
                  index=indexLabels,
                  columns=indexLabels)
    # Display only the lower-triangular elements of the matrix
    upTriMask = np.logical_not( np.tril(np.ones_like(roundedCosAnglesMatrix, dtype=bool)) )
    df_mask = df.mask(upTriMask)
    #maskedRoundedCosAnglesMatrix = np.ma.masked_array(roundedCosAnglesMatrix, mask=upTriMask)
    #maskedRoundedCosAnglesMatrix.filled(np.nan)
    #print("maskedAngles =", maskedRoundedCosAnglesMatrix)
    #print("cosAnglesMatrix =", cosAnglesMatrix)
    #print("upTriMask =", upTriMask)
    corrArrayFig = ff.create_annotated_heatmap(
                   z=df_mask.to_numpy(),
                   x=df_mask.columns.tolist(),
                   y=df_mask.columns.tolist(),
                   colorscale=px.colors.diverging.balance,
                   showscale=True, ygap=1, xgap=1
                   )
    #metricsCorrArrayFig = go.Figure(data=go.Heatmap(
    #                z=roundedCosAnglesMatrix,  
    ##                labels=dict(x="Metrics", y="Metrics")x=['SWCF_GLB', 'SWCF_DYCOMS', 'SWCF_HAWAII', 'SWCF_VOCAL', 'SWCF_VOCAL_near', 'SWCF_LBA', 'SWCF_WP', 'SWCF_EP', 'SWCF_NP', 'SWCF_SP', 'SWCF_CAF', 'SWCF_Nambian', 'SWCF_Nambian_near', 'LWCF_GLB', 'PRECT_GLB'])
    ##                 labels=dict(x="hullo")
    #                x=metricsNames.tolist(),
    #                y=metricsNames.tolist() )
    ##                text_auto=True  )
    #                )
    #    metricsCorrArrayFig = px.imshow(
    #                   img=roundedCosAnglesMatrix,
    #                   x=metricsNames.tolist(),
    #                   y=metricsNames.tolist(),
    #                   color_continuous_scale=px.colors.diverging.balance
    #                    )
    #    metricsCorrArrayFig.update_traces(text=roundedCosAnglesMatrix)
    corrArrayFig.update_xaxes(side="bottom")
    corrArrayFig.update_layout(
    title_text=title, 
    title_x=0.5, 
    width=800, 
    height=700,
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_zeroline=False,
    yaxis_zeroline=False,
    yaxis_autorange='reversed',
    template='plotly_white'
    )

    #pdb.set_trace()

    return ( corrArrayFig )

def calcParamsBounds(metricsNames, paramsNames, transformedParamsNames,
                          metricsWeights, obsMetricValsCol, normMetricValsCol,
                          magParamValsRow,
                          sensNcFilenames, sensNcFilenamesExt, defaultNcFilename):

    """
    Calculate the maximum parameter perturbations based on the non-linearity of the global model
    simulation.
    """
    import numpy as np
    import sys
    import netCDF4
    #import matplotlib.pyplot as plt
    import pdb

    from analyze_sensitivity_matrix import setupSensArrays, calcSvdInvrs, calcParamsSoln
    from set_up_dashboard_inputs import setupDefaultParamVectors, \
                                        setupDefaultMetricValsCol

    if ( len(paramsNames) != len(sensNcFilenames)   ):
        print("Number of parameters must equal number of netcdf files.")
        quit()

    # Number of tunable parameters
    numParams = len(paramsNames)

    # Number of metrics
    numMetrics = len(metricsNames)

    # Set up a column vector of metric values from the default simulation
    defaultMetricValsCol = \
        setupDefaultMetricValsCol(metricsNames, defaultNcFilename)

    # Based on the default simulation,
    #    set up a column vector of metrics and a row vector of parameter values.
    defaultParamValsRow, defaultParamValsOrigRow = \
        setupDefaultParamVectors(paramsNames, transformedParamsNames,
                                 numParams,
                                 defaultNcFilename)

    defaultMetricValsMatrix = defaultMetricValsCol @ np.ones((1,numParams))

    defaultBiasesCol, sensMatrix, normlzdWeightedSensMatrix = \
        calcParamsBoundsHelper(metricsNames, paramsNames, transformedParamsNames,
                           metricsWeights, obsMetricValsCol, normMetricValsCol,
                           numMetrics, numParams,
                           magParamValsRow,
                           defaultMetricValsCol, defaultParamValsRow, defaultParamValsOrigRow,
                           sensNcFilenames)

    defaultBiasesColExt, sensMatrixExt, normlzdWeightedSensMatrixExt = \
        calcParamsBoundsHelper(metricsNames, paramsNames, transformedParamsNames,
                           metricsWeights, obsMetricValsCol, normMetricValsCol,
                           numMetrics, numParams,
                           magParamValsRow,
                           defaultMetricValsCol, defaultParamValsRow, defaultParamValsOrigRow,
                           sensNcFilenamesExt)

    normlzdWeightedSensMatrixDiff = normlzdWeightedSensMatrixExt-normlzdWeightedSensMatrix
    sensMatrixDiff = sensMatrixExt-sensMatrix


    # sValsRatio = a threshold ratio of largest singular value to a smaller singular value.
    # If sValsRatio is large enough, then all singular vectors will be kept.
    # If sValsRatio is 1, then only the first singular vector will be kept.
    sValsRatio = 300.

    # Calculate inverse of the singular value decomposition.
    # This gives the recommended changes to parameter values.
    svdInvrsNormlzdWeighted, svdInvrsNormlzdWeightedPC, \
    sValsTruncInvNormlzdWeighted, sValsTruncInvNormlzdWeightedPC, \
    vhNormlzdWeighted, uNormlzdWeighted, sNormlzdWeighted = \
         calcSvdInvrs(normlzdWeightedSensMatrixDiff, sValsRatio, beVerbose=False)

    paramsSolnPC, paramsLowValsPC, paramsHiValsPC, dparamsSolnPCBound, dnormlzdParamsSolnPC, \
    defaultBiasesApproxPC, defaultBiasesApproxLowValsPC, \
    defaultBiasesApproxHiValsPC = \
             calcParamsSoln(svdInvrsNormlzdWeightedPC, metricsWeights, magParamValsRow, \
                            sensMatrixDiff, normlzdWeightedSensMatrixDiff, \
                            obsMetricValsCol, normMetricValsCol, defaultBiasesCol,
                            defaultParamValsOrigRow, \
                            sValsTruncInvNormlzdWeightedPC,
                            vhNormlzdWeighted, \
                            numParams, paramsNames,
                            transformedParamsNames )

    paramsLowValsPCBound = defaultParamValsOrigRow.T - 0.5*np.abs(dparamsSolnPCBound)
    paramsHiValsPCBound  = defaultParamValsOrigRow.T + 0.5*np.abs(dparamsSolnPCBound)

    #pdb.set_trace()

    return ( paramsLowValsPCBound, paramsHiValsPCBound )

def calcParamsBoundsHelper(metricsNames, paramsNames, transformedParamsNames,
                           metricsWeights, obsMetricValsCol, normMetricValsCol,
                           numMetrics, numParams,
                           magParamValsRow,
                           defaultMetricValsCol, defaultParamValsRow, defaultParamValsOrigRow,
                           sensNcFilenames):

    """
    Calculate the maximum parameter perturbations based on the non-linearity of the global model
    simulation.
    """
    import numpy as np
    import sys
    import netCDF4
    #import matplotlib.pyplot as plt
    import pdb

    from analyze_sensitivity_matrix import setupSensArrays, \
                                           constructSensMatrix, calcSvdInvrs, calcParamsSoln
    from set_up_dashboard_inputs import setupDefaultMetricValsCol

    # Based on the numParams sensitivity simulations,
    #    set up a row vector of modified parameter values.
    # Also set up numMetrics x numParams matrix,
    #    each column of which lists the metrics
    #    from one of the sensitivity simulations
    sensMetricValsMatrix, sensParamValsRow, sensParamValsOrigRow = \
        setupSensArrays(metricsNames, paramsNames, transformedParamsNames,
                        numMetrics, numParams,
                        sensNcFilenames,
                        beVerbose=False)

    # Matrix of metric values from default simulation
    # Each column in the matrix is repeated numParams times, for later multiplication
    defaultMetricValsMatrix = defaultMetricValsCol @ np.ones((1,numParams))

    # Calculate the sensitivity matrix and the sensitivity matrix
    # normalized by the discrepancies from observations in default simulation.
    # Use transformed parameter values.
    defaultBiasesCol, sensMatrix, normlzdSensMatrix, biasNormlzdSensMatrix = \
             constructSensMatrix(sensMetricValsMatrix, sensParamValsRow,
                                 defaultMetricValsMatrix, defaultParamValsRow,
                                 defaultMetricValsCol,
                                 magParamValsRow,
                                 obsMetricValsCol, normMetricValsCol,
                                 numMetrics, numParams,
                                 beVerbose=False)

    # In order to weight certain metrics, multiply each row of normlzdSensMatrix
    # by metricsWeights
    normlzdWeightedSensMatrix = np.diag(np.transpose(metricsWeights)[0]) @ normlzdSensMatrix

    # Calculate inverse of the singular value decomposition.
    # This gives the recommended changes to parameter values.
    #svdInvrsNormlzdWeighted, svdInvrsNormlzdWeightedPC, \
    #sValsTruncInvNormlzdWeighted, sValsTruncInvNormlzdWeightedPC, \
    #vhNormlzdWeighted, uNormlzdWeighted, sNormlzdWeighted = \
    #     calcSvdInvrs(normlzdWeightedSensMatrix)

    #paramsSolnPC, paramsLowValsPC, paramsHiValsPC, dparamsSolnPC, dnormlzdParamsSolnPC, \
    #defaultBiasesApproxPC, defaultBiasesApproxLowValsPC, \
    #defaultBiasesApproxHiValsPC = \
    #         calcParamsSoln(svdInvrsNormlzdWeightedPC, metricsWeights, magParamValsRow, \
    #                        sensMatrix, normlzdWeightedSensMatrix, \
    #                        obsMetricValsCol, normMetricValsCol, defaultBiasesCol,
    #                        defaultParamValsOrigRow, \
    #                        sValsTruncInvNormlzdWeightedPC,
    #                        vhNormlzdWeighted, \
    #                        numParams, paramsNames,
    #                        transformedParamsNames )


    #pdb.set_trace()

    return ( defaultBiasesCol, sensMatrix, normlzdWeightedSensMatrix )


def createParamsErrorBarsFig(paramsNames, defaultParamValsOrigRow, paramsScales,
                             paramsLowValsPCBound, paramsHiValsPCBound,
                             paramsSolnLin, dnormlzdParamsSolnLin,
                             paramsSolnNonlin, dnormlzdParamsSolnNonlin,
                             paramsSolnElastic, dnormlzdParamsSolnElastic):

    # Plot box and whiskers plot of optimal parameter values.
    # Multiply in the user-designated scale factors before plotting.
    paramsAbbrv = np.char.replace( paramsNames, 'clubb_', '' )
    paramsAbbrv = np.char.replace( paramsAbbrv, 'c_invrs_tau_', '' )
    paramsAbbrv = np.char.replace( paramsAbbrv, 'wpxp_n2', 'n2' )
    paramsAbbrv = np.char.replace( paramsAbbrv, 'wpxp_n2', 'n2' )
    paramsAbbrv = np.char.replace( paramsAbbrv, 'threshold', 'thresh' )
    df = pd.DataFrame( np.hstack( defaultParamValsOrigRow[0,:]*paramsScales ),
                  index=paramsAbbrv, columns=["Default plus error bars"] )
    df["err_minus"] = ( defaultParamValsOrigRow[0,:] -  paramsLowValsPCBound[:,0] ) * paramsScales
    df["err_plus"]  = ( paramsHiValsPCBound[:,0] - defaultParamValsOrigRow[0,:] ) * paramsScales
    paramsErrorBarsFig = px.scatter(df, x=df.index, y=df.columns,
              error_y="err_plus", error_y_minus="err_minus",
              title =  """Best-fit parameter values""" )
    paramsErrorBarsFig.update_traces( go.Scatter(
                            mode='markers',
                            marker=dict(color='black', size=14),
                            error_y=dict( color='black', thickness=2, width=10 )
                                    ))
    #paramsErrorBarsFig.add_trace(go.Scatter(x=paramsNames, y=paramsLowValsPCBound[:,0]*paramsScales,
    #                               name=r'$paramsSolnPC - \sigma$',
    #                               line=dict(color='white', width=0), mode='lines', showlegend=False))
    #paramsErrorBarsFig.add_trace(go.Scatter(x=paramsNames, y=paramsHiValsPCBound[:,0]*paramsScales, fill='tonexty',
    #                           name='Default Parameter Values +- sigma', mode='none',
    #                               fillcolor='rgba(253,253,150,1.0)'))
    #paramsErrorBarsFig.add_trace(go.Scatter(x=paramsNames, y=defaultParamValsOrigRow[0,:]*paramsScales,
    #                               name='Default Parameter Values', line=dict(color='black', width=6) ))
    paramsErrorBarsFig.add_trace(go.Scatter(x=paramsAbbrv, y=paramsSolnLin[:,0]*paramsScales,
                                   mode='markers',
                                   marker=dict(color='green', size=8),
                                   name='Linear regression, |dp|='
                                       + '{:.2e}'.format(np.linalg.norm(dnormlzdParamsSolnLin)) ))
    paramsErrorBarsFig.add_trace(go.Scatter(x=paramsAbbrv, y=paramsSolnNonlin[:,0]*paramsScales,
                                   mode='markers',
                                   marker_symbol='x',
                                   marker=dict(color='orange',  size=12),
                                   name='paramsSolnNonlin, |dpPC|='
                                       + '{:.2e}'.format(np.linalg.norm(dnormlzdParamsSolnNonlin)) ))
    paramsErrorBarsFig.add_trace(go.Scatter(x=paramsAbbrv, y=paramsSolnElastic[:,0]*paramsScales,
                                   mode='markers',
                                   marker_symbol='square',
                                   marker=dict(color='cyan', size=8),
                                   name='Lasso regression, |dpLasso|='
                                        + '{:.2e}'.format(np.linalg.norm(dnormlzdParamsSolnElastic)) ,
                                   line=dict(color='red', width=2)  ))
    #paramsFig.add_trace(go.Scatter(x=paramsNames, y=paramsSolnPCBound[:,0]*paramsScales,
    #                                name='paramsSolnPCBound, |dpBound|='
    #                               + '{:.2e}'.format(0.0) ))
    paramsErrorBarsFig.update_yaxes(title="User-scaled parameter value")
    paramsErrorBarsFig.update_xaxes(title="Parameter Name")
    paramsErrorBarsFig.update_layout(hovermode="x")
    paramsErrorBarsFig.update_layout( width=1000, height=500  )

    return paramsErrorBarsFig

def createParamsCorrArrayFig(normlzdLinplusSensMatrixPoly, normlzdDefaultBiasesCol,
                             paramsNames):

    # Create color-coded matrix that displays correlations among parameter vectors
    normlzdSensMatrixConcatBiases = np.hstack((normlzdLinplusSensMatrixPoly, normlzdDefaultBiasesCol))
    #normlzdSensMatrixConcatBiases = np.hstack((normlzdWeightedLinplusSensMatrixPoly, -1*normlzdWeightedDefaultBiasesCol))
    cosAnglesMatrix = calcMatrixAngles( normlzdSensMatrixConcatBiases.T )
    roundedCosAnglesMatrix = np.around(cosAnglesMatrix, decimals=2)
    df = pd.DataFrame(roundedCosAnglesMatrix,
                  index=np.concatenate((paramsNames,['bias vector'])),
                  columns=np.concatenate((paramsNames,['bias vector'])))
    upTriMask = np.logical_not( np.tril(np.ones_like(roundedCosAnglesMatrix, dtype=bool)) )
    df_mask = df.mask(upTriMask)
    paramsCorrArrayFig = ff.create_annotated_heatmap(
                   z=df_mask.to_numpy(),
                   x=df_mask.columns.tolist(),
                   y=df_mask.columns.tolist(),
                   colorscale=px.colors.diverging.balance,
                   showscale=True, ygap=1, xgap=1
                   )
    paramsCorrArrayFig.update_xaxes(side="bottom")
    paramsCorrArrayFig.update_layout(
    title_text='cos(angle) among parameters (i.e., columns of sens matrix)',
    title_x=0.5,
    width=800,
    height=700,
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_zeroline=False,
    yaxis_zeroline=False,
    yaxis_autorange='reversed',
    template='plotly_white'
        )

    return paramsCorrArrayFig

def createDpMin2PtFig( normlzdSensMatrixPoly, defaultBiasesCol,
                      normMetricValsCol, metricsNames ):

    cosAnglesMatrix = calcMatrixAngles( normlzdSensMatrixPoly )
    invrsCosFactorMinusMatrix = np.power( np.maximum( np.finfo(float).eps, 2. * ( 1. - cosAnglesMatrix ) ) , -0.5 )
    invrsCosFactorPlusMatrix = np.power( np.maximum( np.finfo(float).eps, 2. * ( 1. + cosAnglesMatrix ) ), -0.5 )
    dbOnAbsSensVector = \
        -defaultBiasesCol/np.abs(normMetricValsCol) \
            / np.linalg.norm(normlzdSensMatrixPoly, axis=1).reshape(-1, 1)
    dbOnAbsSensMatrix1 = np.ones((len(metricsNames),1)) @ dbOnAbsSensVector.T
    dbOnAbsSensMatrix2 = dbOnAbsSensVector @ np.ones((1,len(metricsNames)) )
    dpMin2PtMinusMatrix = invrsCosFactorMinusMatrix * \
        np.abs( dbOnAbsSensMatrix2 - dbOnAbsSensMatrix1 )
    dpMin2PtPlusMatrix = invrsCosFactorPlusMatrix * \
        np.abs( dbOnAbsSensMatrix2 + dbOnAbsSensMatrix1 )
    dpMin2PtMatrix = np.maximum( dpMin2PtMinusMatrix, dpMin2PtPlusMatrix )
    roundedDpMin2PtMatrix = np.around(dpMin2PtMatrix, decimals=2)
    dpMin2PtMatrix = np.fill_diagonal(roundedDpMin2PtMatrix, np.nan)
    df = pd.DataFrame(roundedDpMin2PtMatrix,
                  index=metricsNames,
                  columns=metricsNames)
    #upTriMask = np.logical_not( np.tril(np.ones_like(roundedDpMin2PtMatrix, dtype=bool)) )
    upTriMask = np.triu(np.ones_like(roundedDpMin2PtMatrix, dtype=bool))
    df_mask = df.mask(upTriMask)
    dpMin2PtFig = ff.create_annotated_heatmap(
                   z=df_mask.to_numpy(),
                   x=df_mask.columns.tolist(),
                   y=df_mask.columns.tolist(),
                   colorscale=px.colors.sequential.Bluered,
                   showscale=True, ygap=1, xgap=1
                   )
    dpMin2PtFig.update_xaxes(side="bottom")
    dpMin2PtFig.update_layout(
    title_text='dpMin between 2 metrics (i.e., rows of sens matrix)',
    title_x=0.5,
    width=800,
    height=700,
    xaxis_showgrid=False,
    yaxis_showgrid=False,
    xaxis_zeroline=False,
    yaxis_zeroline=False,
    yaxis_autorange='reversed',
    template='plotly_white'
    )

    return dpMin2PtFig



def createNormlzdSensMatrixColsFig(defaultBiasesCol, normlzdSensMatrixPoly,
                                   normMetricValsCol, metricsNames, paramsNames ):

    # Plot each column of normalized sensitivity matrix as a separate line.
    # Each column tells us how all metrics vary with a single parameter.
    df = pd.DataFrame( np.hstack( (-defaultBiasesCol/np.abs(normMetricValsCol),normlzdSensMatrixPoly) ),
                  index=metricsNames,
                  columns=np.append('Norm bias', paramsNames) )
    normlzdSensMatrixColsFig = px.line(df, x=df.index, y=df.columns,
              title =  """Columns of normalized, unweighted sensitivity matrix (plus the bias vector).<br>
                       Each column (line) shows how sensitive the metrics are to a change in a single parameter value.<br>
                       (A positive value means that an increase in parameter value brings the default simulation closer to obs.)""" )
    normlzdSensMatrixColsFig.update_yaxes(title="Norml sens, (|param|/|obsmetric|) * dmetric/dparam")
    normlzdSensMatrixColsFig.update_xaxes(title="Regional metric")
    normlzdSensMatrixColsFig.layout.legend.title = "Parameter"
    normlzdSensMatrixColsFig.update_layout(hovermode="x")
    #pdb.set_trace()

    return normlzdSensMatrixColsFig

def createNormlzdSensMatrixRowsFig( normlzdSensMatrixPoly,
                                    metricsNames, paramsNames ):

    # Plot each row of normalized sensitivity matrix as a separate line.
    # Each row tells us how a single metric varies with all parameters.
    df = pd.DataFrame(np.transpose(normlzdSensMatrixPoly),
                  index=paramsNames,
                  columns=metricsNames)
    normlzdSensMatrixRowsFig = px.line(df, x=df.index, y=df.columns,
              title = """Rows of normalized, unweighted sensitivity matrix.<br>
                       Each row (line) tells us how a single metric varies with all parameters.<br>
                       (A positive value means that an increase in parameter value brings the default simulation closer to obs.)""" )
    normlzdSensMatrixRowsFig.update_yaxes(title="Norml sens, (|param|/|obsmetric|) * dmetric/dparam")
    normlzdSensMatrixRowsFig.update_xaxes(title="Parameter")
    normlzdSensMatrixRowsFig.layout.legend.title = "Metric"
    normlzdSensMatrixRowsFig.update_layout(hovermode="x")

    return normlzdSensMatrixRowsFig




def createBiasesOrderedArrowFig(metricsSensOrdered, metricsNamesOrdered,
                                defaultBiasesCol, normMetricValsCol, 
                                defaultBiasesApproxNonlinNoCurv, defaultBiasesApproxNonlin2xCurv,
                                defaultBiasesApproxNonlin,
                                linSolnBiasesCol):

    # Plot a black dot for each default-run bias
    biasesOrderMatrix = np.dstack(( -defaultBiasesCol[metricsSensOrdered] )).squeeze()
    fracBiasesOrderMatrix = np.diagflat(np.reciprocal(np.abs(normMetricValsCol[metricsSensOrdered]))) @ biasesOrderMatrix
    df = pd.DataFrame(fracBiasesOrderMatrix,
                      index=metricsNamesOrdered,
                      columns= ['fracDefBias'])
    biasesOrderedArrowFig = px.line(df, x=df.index, y=df.columns,
              title = """<span style='color:blue'>Predicted</span> and <span style='color:red'>actual</span> removal of regional biases""")
    biasesOrderedArrowFig.update_yaxes(title="-Normalized bias")
    biasesOrderedArrowFig.update_xaxes(title="Regional metric")
    biasesOrderedArrowFig.update_layout(hovermode="x")
    biasesOrderedArrowFig.update_layout(showlegend=False)
    biasesOrderedArrowFig.update_traces(mode='markers', line_color='black')  # Plot default biases as black dots
    biasesOrderedArrowFig.update_yaxes(visible=True,zeroline=True,zerolinewidth=1,zerolinecolor='gray') # Plot x axis
    biasesOrderedArrowFig.update_layout( width=700, height=500  )
    # Now plot an arrow for each region that points from default-run bias to new bias after tuning
    xArrow = np.arange(len(metricsNamesOrdered)) # x-coordinate of arrows
    yArrow = -defaultBiasesCol[metricsSensOrdered,0]/np.abs(normMetricValsCol[metricsSensOrdered,0])
    gap = 0.2  # horizontal spacing between arrows
    # Plot error bar on prediction arrow.  Bar runs between 0- and 2x-curvature solns.
    for i, item in enumerate(metricsNamesOrdered):
        biasesOrderedArrowFig.add_annotation(
        x =  xArrow[i]-gap,  # ith arrow's head
        # ith arrow's head:
        y = (-defaultBiasesApproxNonlinNoCurv-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]), 
        ax =  xArrow[i]-gap,  # ith arrow's head
        # ith arrow's head:
        ay = (-defaultBiasesApproxNonlin2xCurv-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]), 
        font = dict(family="bold", color="blue", size=30),
        showarrow=True,
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        text='',  # blank because we want only the arrow
        arrowhead=0,
        arrowsize=1,
        arrowwidth=6,
        arrowcolor='lightskyblue' # https://stackoverflow.com/questions/72496150/user-friendly-names-for-plotly-css-colors
        )
    #biasesOrderedArrowFig.add_scatter(x=df.index, y=df.columns, line_color='pink')  # attempt to make black dot appear on top
    biasesOrderedArrowFig.update_traces(mode='markers', line_color='black')
    # Plot arrows showing the tuner's nonlinear predicted bias removal
    for i, item in enumerate(metricsNamesOrdered):
        biasesOrderedArrowFig.add_annotation(
        x=  xArrow[i] - gap,  # ith arrow's head
        # ith arrow's head:
        y= (-defaultBiasesApproxNonlin-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]),
        #y= (-defaultBiasesApproxNonlinNoCurv-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]),
        ax= xArrow[i] - gap,  # ith arrow's tail
        ay=  yArrow[i],  # ith arrow's tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        text='',  # blank because we want only the arrow
        showarrow=True,
        arrowhead=3,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='blue'
        )
    # Add a hand-made legend
    biasesOrderedArrowFig.add_annotation(text='Tuner prediction of bias removal',
                                  font=dict(color='blue'),
                                  align='left', xref='paper', yref='paper',
                                  x=0.05, y=0.98, showarrow=False)
    biasesOrderedArrowFig.add_annotation(text='Error bar on tuner prediction',
                                  font=dict(color='skyblue'),
                                  align='left', xref='paper', yref='paper',
                                  x=0.05, y=0.91, showarrow=False)
    biasesOrderedArrowFig.add_annotation(text='Realized E3SM bias removal',
                                  font=dict(color='red'),  # keep E3SM legend 
                                  #font=dict(color='rgba(255,0,0,0.0)'), # omit E3SM legend
                                  align='left', xref='paper', yref='paper',
                                  x=0.05, y=0.84, showarrow=False)
    # Plot arrows showing the bias removal of E3SM's solution
    for i, item in enumerate(metricsNamesOrdered):
        biasesOrderedArrowFig.add_annotation(
        x=  xArrow[i]+gap,  # ith arrow's head
        # ith arrow's head:
        #y= (-linSolnBiasesCol-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]),
        y= (-linSolnBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]),
        ax= xArrow[i]+gap,  # ith arrow's tail
        ay=  yArrow[i],  # ith arrow's tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        text='',  # blank because we want only the arrow
        showarrow=True,
        arrowhead=3,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='red'
        #,opacity=0.0  # omit arrow for E3SM's solution
        )
#     # Plot 0-curvature error bars on prediction arrow
#     for i, item in enumerate(metricsNamesOrdered):
#         biasesOrderedArrowFig.add_annotation(
#         x =  xArrow[i]-gap,  # ith arrow's head
#         # ith arrow's head:
#         y = (-defaultBiasesApproxNonlinNoCurv-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]),
#         text ='-',  # plot horizontal line
#         font = dict(family="bold", color="blue", size=30),        
#         showarrow=False
#       )
#     # Plot 2x-curvature error bars on prediction arrow
#     for i, item in enumerate(metricsNamesOrdered):
#         biasesOrderedArrowFig.add_annotation(
#         x =  xArrow[i]-gap,  # ith arrow's head
#         # ith arrow's head:
#         y = (-defaultBiasesApproxNonlin2xCurv-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]),
#         text ='-',  # plot horizontal line
#         font = dict(family="bold", color="blue", size=30),        
#         showarrow=False
#       )               


    #biasesOrderedArrowFig.add_trace(go.Scatter(x=xArrow, y=yArrow,
    #                      name='Region of improvement', mode='markers',
    #                       marker=dict(color='green', size=14)))
    #pdb.set_trace()

#biasesOrderedArrowFig.write_image('biasesOrderedArrowFig.png', scale=6)

    return biasesOrderedArrowFig

def createBiasLinNlIndivContrbBarFig( normlzdSensParamsMatrixOrdered, curvParamsMatrixOrdered,
                                      metricsNamesOrdered, paramsNames ):

    #dnormlzdParamsSolnNonlinMatrix = np.ones((len(metricsNames),1)) @ dnormlzdParamsSolnNonlin.T
    #curvParamsMatrixOrdered = 0.5 * normlzdCurvMatrix[metricsSensOrdered,:] * dnormlzdParamsSolnNonlinMatrix**2
    #print("Sum rows=", np.sum(-normlzdSensParamsMatrixOrdered-curvParamsMatrixOrdered, axis=1))
    dfLin = pd.DataFrame(-1*normlzdSensParamsMatrixOrdered,
                      index=metricsNamesOrdered,
                      columns=paramsNames)
    # biasLinNlIndivContrbBarFig = go.Figure()
    # biasLinNlIndivContrbBarFig.add_trace( go.Bar(x=df.index, y=list(curvParamsMatrixOrdered[:,2:3])) )
    #df_long = pd.wide_to_long( df, i=df.index, j=df.columns, stubnames=[''] )
    dfLin = dfLin.reset_index()
    dfLin.rename(columns = {'index':'metricsNamesOrdered'}, inplace = True)
    #print("biasContrGrouped df=", df.to_string())
    #print("df.columns.values=", df.columns.values)
    #df.columns[1] = ['metricsNamesOrdered']

    dfLin_long = dfLin.melt( id_vars='metricsNamesOrdered',
                            var_name='paramsNames', value_name='Contribution to bias removal')
    dfLin_long.insert(0, 'isNonlin', ['linear'] * len(paramsNames) * len(metricsNamesOrdered) )
    #print("df_long=", df_long.to_string())
 
    dfNonlin = pd.DataFrame(-1*curvParamsMatrixOrdered,
                      index=metricsNamesOrdered,
                      columns=paramsNames)
    # biasLinNlIndivContrbBarFig = go.Figure()
    # biasLinNlIndivContrbBarFig.add_trace( go.Bar(x=df.index, y=list(curvParamsMatrixOrdered[:,2:3])) )
    #df_long = pd.wide_to_long( df, i=df.index, j=df.columns, stubnames=[''] )
    dfNonlin = dfNonlin.reset_index()
    dfNonlin.rename(columns = {'index':'metricsNamesOrdered'}, inplace = True)
    #print("biasContrGrouped df=", df.to_string())
    #print("df.columns.values=", df.columns.values)
    #df.columns[1] = ['metricsNamesOrdered']

    dfNonlin_long = dfNonlin.melt( id_vars='metricsNamesOrdered',
                            var_name='paramsNames', value_name='Contribution to bias removal')
    dfNonlin_long.insert(0, 'isNonlin', ['nonlinear'] * len(paramsNames) * len(metricsNamesOrdered) )
    #print("df_long=", df_long.to_string())    

    dfLinNonlin_long = pd.concat([dfLin_long, dfNonlin_long], ignore_index=True)

    biasLinNlIndivContrbBarFig = px.bar(dfLinNonlin_long,
                                 facet_col='metricsNamesOrdered', y='Contribution to bias removal',
                                 facet_col_spacing=0.005, # default 0.03
                                 x='isNonlin', color='paramsNames') #,
              #title = """Long: Linear ++ nonlinear contributions to actual removal of regional biases""")
    #biasLinNlIndivContrbBarFig.update_yaxes(title="-(Def-Sim) / abs(obs metric value)")
    #biasLinNlIndivContrbBarFig.update_xaxes(title="Regional metric")
    ##biasLinNlIndivContrbBarFig.update_xaxes(visible=False)
    ##biasLinNlIndivContrbBarFig.update_yaxes(visible=False)
    biasLinNlIndivContrbBarFig.update_layout(hovermode="x")
    biasLinNlIndivContrbBarFig.update_layout(showlegend=True)
    ##biasLinNlIndivContrbBarFig.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
    #biasLinNlIndivContrbBarFig.for_each_annotation(lambda a: a.update(text=''))
    biasLinNlIndivContrbBarFig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    biasLinNlIndivContrbBarFig.update_annotations(textangle=-90)
    biasLinNlIndivContrbBarFig.update_layout(margin = dict(t = 160))
    for axis in biasLinNlIndivContrbBarFig.layout:
        #if type(biasLinNlIndivContrbBarFig.layout[axis]) == go.layout.YAxis:
        #    biasLinNlIndivContrbBarFig.layout[axis].title.text = 'Contribution to bias removal'
        if type(biasLinNlIndivContrbBarFig.layout[axis]) == go.layout.XAxis:
            biasLinNlIndivContrbBarFig.layout[axis].title.text = ''
    #biasLinNlIndivContrbBarFig.layout.title.text = ''
    #biasLinNlIndivContrbBarFig.update_yaxes(visible=True,zeroline=True,zerolinewidth=1,zerolinecolor='gray') # Plot x axis
    biasLinNlIndivContrbBarFig.update_layout( width=1000, height=450  )
    #print("curvParams =", -1*curvParamsMatrixOrdered)
    #print("normlzdSens =", -1*normlzdSensParamsMatrixOrdered)

    return biasLinNlIndivContrbBarFig


def createBiasVsBiasApproxScatterplot(defaultBiasesApproxNonlin, defaultBiasesCol,
                                      normMetricValsCol,  
                                      metricsNames ):

    # Plot a scatterplot of default-simulation bias and SVD approximation of that bias.
    # Each column tells us how all metrics vary with a single parameter.
    biasSensDirMatrix = np.concatenate((defaultBiasesApproxNonlin/np.abs(normMetricValsCol),
                                       (-defaultBiasesCol/np.abs(normMetricValsCol))), axis=1)
    biasAndParamsNames = ["biasApproxNonlin", "bias"]
    #biasAndParamsNames = np.append(["bias", "bias_approx_pc"], paramsNames)
    df = pd.DataFrame(biasSensDirMatrix,
                  index=metricsNames,
                  columns=biasAndParamsNames)
    biasSensDirMatrixScatter = px.scatter(df, x="biasApproxNonlin", y="bias", 
                                          text=metricsNames, title="Bias approx vs bias" )
    biasSensDirMatrixOneOneLine = px.line(df, x="bias", y="bias")
    #biasSensDirMatrixOneMOneLine = px.line(df, x="bias", y=-df.loc[:,"bias"])
    biasVsBiasApproxScatterplot = go.Figure(data=biasSensDirMatrixScatter.data
                                              + biasSensDirMatrixOneOneLine.data)
    #biasRange = (max(df.loc[:,"bias"]), min(df.loc[:,"bias"]))
    #biasVsBiasApproxScatterplot.add_trace(go.Scatter(x=biasRange, y=biasRange, fill='tozeroy',
    #                           name='Region of improvement', mode='none',
    #                           fillcolor='rgba(253,253,150,0.7)'))
    biasVsBiasApproxScatterplot.update_xaxes(title="(defaultBiasesApproxNonlin)/obs")
    biasVsBiasApproxScatterplot.update_yaxes(title="-defaultBiasesCol/obs")
    biasVsBiasApproxScatterplot.update_traces(textposition='top center')
    biasVsBiasApproxScatterplot.update_yaxes(visible=True,zeroline=True,zerolinewidth=2,zerolinecolor='lightblue') # Plot x axis
    biasVsBiasApproxScatterplot.update_layout( width=800, height=500  )
    biasVsBiasApproxScatterplot.update_layout(title="Bias approx vs bias")

    return biasVsBiasApproxScatterplot

def createBiasSensMatrixScatterFig(defaultBiasesCol, defaultBiasesApproxElastic,
                                   normMetricValsCol, metricsNames):

    # Plot a scatterplot of default-simulation bias and SVD approximation of that bias.
    # Each column tells us how all metrics vary with a single parameter.
    biasSensMatrix = np.concatenate((-defaultBiasesCol/np.abs(normMetricValsCol),
                                    (-defaultBiasesApproxElastic-defaultBiasesCol)/np.abs(normMetricValsCol)), axis=1)
                                     #defaultBiasesApproxElastic/np.abs(normMetricValsCol)), axis=1)
    biasAndParamsNames = ["bias", "bias_approx_pc"]
    #biasAndParamsNames = np.append(["bias", "bias_approx_pc"], paramsNames)
    df = pd.DataFrame(biasSensMatrix,
                  index=metricsNames,
                  columns=biasAndParamsNames)
    biasSensMatrixScatter = px.scatter(df, x="bias", y="bias_approx_pc", text=metricsNames,
    #biasSensMatrixScatter = px.scatter(df, x=np.append(["bias_approx_pc"], paramsNames), y="bias",
              title = """Columns of normalized sensitivity matrix.<br>
                       vs. bias vector.<br>
                       """ )
    biasSensMatrixOneOneLine = px.line(df, x="bias", y="bias")
    biasSensMatrixOneMOneLine = px.line(df, x="bias", y=-df.loc[:,"bias"])
    biasSensMatrixScatterFig = go.Figure(data=biasSensMatrixScatter.data
                                              + biasSensMatrixOneOneLine.data
                                              + biasSensMatrixOneMOneLine.data)
    biasRange = (max(df.loc[:,"bias"]), min(df.loc[:,"bias"]))
    biasSensMatrixScatterFig.add_trace(go.Scatter(x=biasRange, y=biasRange, fill='tozeroy',
                               name='Region of improvement', mode='none',
                               fillcolor='rgba(253,253,150,0.7)'))
    biasSensMatrixScatterFig.update_yaxes(title="(-defaultBiasesApproxElastic-defaultBiasesCol)/obs")
    biasSensMatrixScatterFig.update_xaxes(title="-defaultBiasesCol/obs")
    biasSensMatrixScatterFig.update_traces(textposition='top center')

    return biasSensMatrixScatterFig

def createDpMinMatrixScatterFig(defaultBiasesCol, normlzdSensMatrixPoly, 
                                normMetricValsCol, metricsNames):

    # Plot a scatterplot of minimum parameter perturbation vs. fractional default bias approximation
    # Calculate lower bound on normalized parameter perturbations
    #normlzdDefaultBiasesCol = ( metricsWeights * (-defaultBiasesCol) /
    normlzdDefaultBiasesCol = ( (defaultBiasesCol) /
                                np.abs(normMetricValsCol) )
    #sensMatrixRowMag = np.linalg.norm(normlzdWeightedSensMatrixPoly, axis=1)
    sensMatrixRowMag = np.linalg.norm(normlzdSensMatrixPoly, axis=1)
    #sensMatrixRowMag = np.amax(np.abs(normlzdSensMatrixPoly), axis=1)
    dpMin = np.abs(normlzdDefaultBiasesCol) / np.atleast_2d(sensMatrixRowMag).T
    #u_dot_b = np.atleast_2d(sensMatrixRowMag).T * -normlzdDefaultBiasesCol
    dpMinMatrix = np.dstack((np.reciprocal(dpMin),
    #dpMinMatrix = np.dstack((np.abs(u_dot_b),
    ##dpMinMatrix = np.dstack((np.atleast_2d(sensMatrixRowMag).T,
    #                      np.abs(defaultBiasesApproxElastic)/np.abs(normMetricValsCol)
                          np.abs(defaultBiasesCol)/np.abs(normMetricValsCol)
                         )).squeeze()
    biasAndParamsNames = ["dpMinInvrs", "bias_approx"]
    df = pd.DataFrame(dpMinMatrix,
                  index=metricsNames,
                  columns=biasAndParamsNames)
    dpMinMatrixScatter = px.scatter(df, x="dpMinInvrs", y="bias_approx", text=metricsNames,
              title = """dpMinInvrs  vs. |approx bias vector|.<br>
                       """ )
    dpMinMatrixScatterFig = go.Figure(data=dpMinMatrixScatter.data)
    dpMinMatrixScatterFig.update_yaxes(title="|defaultBiasesApproxElastic|")
    dpMinMatrixScatterFig.update_xaxes(title="dpMinInvrs")
    dpMinMatrixScatterFig.update_traces(textposition='top center')

    return dpMinMatrixScatterFig


def createBiasesVsSensMagScatterplot(normlzdLinplusSensMatrixPoly, defaultBiasesCol,
                                     normMetricValsCol, metricsNames):

    # Plot the biases versus sensitivity of each regional metric.
    #    More specifically, plot the maximum magnitude value of each row of the sensitivity matrix.
    df = pd.DataFrame({
    #df = pd.DataFrame({'Max abs normlzd sensitivity': np.max(np.abs(normlzdSensMatrixPoly), axis=1), # max |row elements|
    #df = pd.DataFrame({'Max abs normlzd sensitivity': np.sum(normlzdWeightedSensMatrixPoly, axis=1), # sum of row elements
    #df = pd.DataFrame({'Max abs normlzd sensitivity': np.linalg.norm(normlzdWeightedSensMatrixPoly, axis=1), # rms of row elements
    #df = pd.DataFrame({'Max abs normlzd sensitivity': np.linalg.norm(normlzdSensMatrixPoly, axis=1), # rms of row elements
    #df = pd.DataFrame({'Max abs normlzd sensitivity':
    #                    -defaultBiasesCol[:,0]/np.abs(normMetricValsCol[:,0])*np.linalg.norm(normlzdWeightedSensMatrixPoly, axis=1), # sum of row elements
                       'Max abs normlzd lin+ sensitivity': np.linalg.norm(normlzdLinplusSensMatrixPoly, axis=1), # sum of row elements
                       'Default biases': np.abs(-defaultBiasesCol[:,0])/np.abs(normMetricValsCol[:,0]),
    #                   'revised tuning': (-defaultBiasesApproxElastic-defaultBiasesCol)[:,0]/np.abs(normMetricValsCol[:,0])
                      }, index=metricsNames )
    #biasesVsSensMagScatterplot = px.scatter(df, x='Max abs normlzd sensitivity', y=df.columns[1:2],
    #biasesVsSensMagScatterplot = px.scatter(df, x='Max abs normlzd sensitivity', y='default tuning',
    biasesVsSensMagScatterplot = px.scatter(df, x=['Max abs normlzd lin+ sensitivity'], y='Default biases',
                                 text=metricsNames,
                                 title = """Regional biases vs. magnitude of sensitivity.""")
    biasesVsSensMagScatterplot.update_yaxes(title="Regional biases")
    biasesVsSensMagScatterplot.update_xaxes(title="Magnitude of sensitivity of regional metrics to parameter changes")
    biasesVsSensMagScatterplot.update_layout(showlegend=False)
    biasesVsSensMagScatterplot.update_layout(hovermode="x")
    biasesVsSensMagScatterplot.update_layout( width=700, height=500  )

    return biasesVsSensMagScatterplot

def createBiasesVsSensArrowFig(normlzdWeightedSensMatrixPoly, defaultBiasesCol,
                               defaultBiasesApproxNonlin,
                               normMetricValsCol, metricsNames):

    # Compute length of arrows between default and tuned biases
    #metricsNamesPadded = ",,".join(metricsNames).split(",")
    #metricsNamesPadded = ",,".join(metricsNamesPadded).split(",")
    #metricsNamesPadded = np.append(metricsNamesPadded, ["", "", ""], axis=0)
    xArrow = np.linalg.norm(normlzdWeightedSensMatrixPoly, axis=1)
    yArrow = -defaultBiasesCol[:,0]/np.abs(normMetricValsCol[:,0])
    #uArrow = np.zeros_like(xArrow)
    #vArrow = (-defaultBiasesApproxElasticNonlin)[:,0]/np.abs(normMetricValsCol[:,0])
    #arrowFig = create_quiver(xArrow, yArrow, uArrow, vArrow,
    #                         scale=1,text=metricsNamesPadded)
    #arrowFig.update_yaxes(title="Regional biases")
    #arrowFig.update_traces(mode='lines+text')  # make labels appear in plot, not just hovermode


    # Plot biases vs. sensitivity, but with arrows indicating the degree of bias reduction
    df = pd.DataFrame({'Max abs normlzd sensitivity': np.linalg.norm(normlzdWeightedSensMatrixPoly, axis=1), # sum of row elements

                       'default tuning': -defaultBiasesCol[:,0]/np.abs(normMetricValsCol[:,0]),
                       'revised tuning': (-defaultBiasesApproxNonlin-defaultBiasesCol)[:,0]/np.abs(normMetricValsCol[:,0])
                      }, index=metricsNames )
    biasesVsSensArrowFig = px.scatter(df, x='Max abs normlzd sensitivity', y=df.columns[1:2],
                                 text=metricsNames,
                                 title = """Regional biases with default and nonlin tuning versus sensitivity, with arrows.""" )
    biasesVsSensArrowFig.update_traces(textposition="middle right")
    for i, item in enumerate(metricsNames):
        biasesVsSensArrowFig.add_annotation(
        x=  xArrow[i],  # ith arrow's head
        y= (-defaultBiasesApproxNonlin-defaultBiasesCol)[i,0]/np.abs(normMetricValsCol[i,0]),  # ith arrow's length
        #y= (-defaultBiasesApproxNonlin2x-defaultBiasesCol)[i,0]/np.abs(normMetricValsCol[i,0]),  # ith arrow's length
        ax= xArrow[i],  # ith arrow's tail
        ay=  yArrow[i],  # ith arrow's tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        text='',  # if you want only the arrow
        showarrow=True,
        arrowhead=3,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='black'
        )
    biasesVsSensArrowFig.update_yaxes(title="Regional biases")
    biasesVsSensArrowFig.update_xaxes(title="Sensitivity of regional metrics to parameter changes")
    biasesVsSensArrowFig.update_layout(hovermode="x")
    biasesVsSensArrowFig.update_traces(cliponaxis=False)
    biasesVsSensArrowFig.update_yaxes(automargin=True)

    return biasesVsSensArrowFig

def createMaxSensMetricsFig(normlzdSensMatrixPoly, metricsNames):

    # Plot the sensitivity of each regional metric.
    #    More specifically, plot the maximum magnitude value of each row of the sensitivity matrix.
    df = pd.DataFrame(np.max(np.abs(normlzdSensMatrixPoly), axis=1), # max of absolute val of each row
                  index=metricsNames,
                  columns=['Max abs normlzd sensitivity'])
    maxSensMetricsFig = px.line(df, x=df.index, y=df.columns,
              title = """Maximum normalized sensitivity of each metric with respect to parameters.<br>
                       (Low sensitivity means that the metric is unbudgeable by these parameters.)""" )
    maxSensMetricsFig.update_yaxes(title="Max |sens row|")
    maxSensMetricsFig.update_xaxes(title="Regional metric")
    maxSensMetricsFig.update_layout(hovermode="x")
    maxSensMetricsFig.update_traces(mode='lines+markers')


    return maxSensMetricsFig




def calcMatrixVectorAngles( matrix, row ):
    '''Calculate cos(angle) between one row of a matrix and all rows of the same matrix.
       Returns a column vector, with length equal to the number of rows in the matrix.'''
    
    import sklearn
    
    normed_matrix = sklearn.preprocessing.normalize( matrix, axis=1, norm='l2' )
    
    cosAngles = normed_matrix @ normed_matrix[row, :].T
    
    return cosAngles

def calcMatrixAngles( matrix ):
    '''Calculate cos(angle) among all rows of the same matrix.'''
    
    import sklearn
    
    normed_matrix = sklearn.preprocessing.normalize( matrix, axis=1, norm='l2' )
    
    cosAnglesMatrix = normed_matrix @ normed_matrix.T
    
    return cosAnglesMatrix

def createPcaBiplot(normlzdSensMatrix, defaultBiasesCol, normMetricValsCol, metricsNames, paramsNames):

    import numpy as np
    from pca import pca
    import pdb

    # reduce the data towards 2 PCs
    model = pca(n_components=2, detect_outliers='ht2')

    # Augmented array with LHS and RHS
    augMatrix = np.concatenate((normlzdSensMatrix, -defaultBiasesCol / np.abs(normMetricValsCol) ), axis=1)

    paramsList = list(paramsNames)
    paramsList.append('dbias')
    augParamsNames = np.asarray(paramsList)

    # Fit transform
    results = model.fit_transform(augMatrix, row_labels=metricsNames, col_labels=augParamsNames)
    #results = model.fit_transform(normlzdSensMatrix, row_labels=metricsNames, col_labels=paramsNames)

    PC_test = model.transform(augMatrix)
    #PC_test = model.transform(normlzdSensMatrix)
    outliers, outliers_params = model.compute_outliers(PC=PC_test)
    print("PCA outliers = ", outliers)

    # Plot explained variance
    #fig, ax = model.plot()

    # Scatter first 2 PCs
    #fig, ax = model.scatter()

    # Make biplot with the number of features
    fig, ax = model.biplot(n_feat=paramsNames.size+1)
    #fig, ax = model.biplot(n_feat=paramsNames.size)

    #pdb.set_trace()

    return

def oldCode():



    # Calculate the fraction of the default-sim bias that remains after tuning.
    # This is unweighted and hence is not necessarily less than one.
    # defaultBiasesApprox = J*delta_p = ( fwd - def )
    # numerator = ( fwd - def ) + ( def - obs ) = ( fwd - obs )
#    Bias = ( defaultBiasesApprox + defaultBiasesCol )
    # defaultBiasesCol = delta_b = ( default - obs ) = denominator
#    BiasMagRatio = np.linalg.norm(Bias/np.abs(normMetricValsCol))**2 / \
#                   np.linalg.norm(defaultBiasesCol/np.abs(normMetricValsCol))**2

   # Calculate the global-model bias relative to the default-sim bias.
    # This is unweighted and hence is not necessarily less than one.
    # defaultBiasesApprox = J*delta_p = ( fwd - def )
    # numerator = ( linSoln - def ) + ( def - obs ) = ( linSoln - obs )
    #linSolnBias = ( linSolnBiasesCol + defaultBiasesCol )
    # defaultBiasesCol = delta_b = ( default - obs ) = denominator
    #linSolnBiasMagRatio = np.linalg.norm(linSolnBias/np.abs(normMetricValsCol))**2 / \
    #                      np.linalg.norm(defaultBiasesCol/np.abs(normMetricValsCol))**2

    # weightedBiasLin = metricsWeights * ( lin - obs ) = numerator
    #weightedBiasLinSoln = metricsWeights * ( linSolnBiasesCol + defaultBiasesCol ) / np.abs(normMetricValsCol)
    #weightedBiasLinSolnMagRatio = np.linalg.norm(weightedBiasLinSoln)**2 / np.linalg.norm(normlzdMDeltaB)**2


        # Plot each column of right-singular vector matrix, V.
#    rightSingVectorNums = (np.arange(paramsNames.shape[0])+1).astype(str)
#    df = pd.DataFrame(np.transpose(vhNormlzd),
#                  index=paramsNames,
#                  columns=rightSingVectorNums)
#    vhNormlzdColsFig = px.line(df, x=df.index, y=df.columns,
#              title = """Columns of normalized, unweighted right-singular vector matrix, V.<br>
#                        Each column (line) is a vector of parameter values associated with a singular value.<br>""" )
#    vhNormlzdColsFig.update_yaxes(title="Right-singular vector")
#    vhNormlzdColsFig.update_xaxes(title="Parameter")
#    vhNormlzdColsFig.layout.legend.title = "Singular vector"
#    vhNormlzdColsFig.update_layout(hovermode="x")
#    for idx, val in np.ndenumerate(sNormlzd):
#        vhNormlzdColsFig.data[idx[0]].name = "{}".format(idx[0]+1) + ", " + "{:.2e}".format(val)

    # Plot each column of normalized, unweighted left-singular vector matrix, U.
#    df = pd.DataFrame(uNormlzd,
#                  index=metricsNames,
#                  columns=rightSingVectorNums)
#    uNormlzdColsFig = px.line(df, x=df.index, y=df.columns,
#              title = """Columns of normalized, unweighted left-singular vector matrix, U.<br>
#                       Each column (line) is a vector of metric values associated with a singular value.<br>""" )
#    uNormlzdColsFig.update_yaxes(title="Left-singular vector")
#    uNormlzdColsFig.update_xaxes(title="Parameter")
#    uNormlzdColsFig.layout.legend.title = "Singular vector"
#    uNormlzdColsFig.update_layout(hovermode="x")
#    for idx, val in np.ndenumerate(sNormlzd):
#        uNormlzdColsFig.data[idx[0]].name = "{}".format(idx[0]+1) + ", " + "{:.2e}".format(val)

    # Plot each column of normalized, weighted left-singular vector matrix, U.
#    df = pd.DataFrame(uNormlzdWeighted,
#                  index=metricsNames,
#                  columns=rightSingVectorNums)
#    uNormlzdWeightedColsFig = px.line(df, x=df.index, y=df.columns,
#              title = """Columns of normalized, weighted left-singular vector matrix, U.<br>
#                       Each column (line) is a vector of metric values associated with a singular value.<br>""" )
#    uNormlzdWeightedColsFig.update_yaxes(title="Left-singular vector")
#    uNormlzdWeightedColsFig.update_xaxes(title="Parameter")
#    uNormlzdWeightedColsFig.layout.legend.title = "Singular vector"
#    uNormlzdWeightedColsFig.update_layout(hovermode="x")
#    for idx, val in np.ndenumerate(sNormlzdWeighted):
#        uNormlzdWeightedColsFig.data[idx[0]].name = "{}".format(idx[0]+1) + ", " + "{:.2e}".format(val)

    # Plot each column of left-singular vector matrix, U, multiplied by biases.
    # Plot each column of left-singular vector matrix, U, multiplied by biases.
#    df = pd.DataFrame(uNormlzd*defaultBiasesCol/np.abs(normMetricValsCol),
#
#                   index=metricsNames,
#                  columns=rightSingVectorNums)
#    uNormlzdBiasColsFig = px.line(df, x=df.index, y=df.columns,
#              title = """Columns of normalized, unweighted left-singular vector matrix, U, dotted with delta_b (defaultBiasesCol).<br>
#                       Each column (line) is a vector of metric values associated with a singular value.<br>""" )
#    uNormlzdBiasColsFig.update_yaxes(title="uNormlzd dot delta_b")
#    uNormlzdBiasColsFig.update_xaxes(title="Parameter")
#    uNormlzdBiasColsFig.layout.legend.title = "Singular vector"
#    uNormlzdBiasColsFig.update_layout(hovermode="x")
#    for idx, val in np.ndenumerate(sNormlzd):
#        uNormlzdBiasColsFig.data[idx[0]].name = "{}".format(idx[0]+1) + ", " + "{:.2e}".format(val)
    #pdb.set_trace()

    # Plot the residual*sensitivity vs. bias*sensitivity
    # The goal is to separate out which regional are amenable to tuning
    normlzdBias = -defaultBiasesCol[:,0]/np.abs(normMetricValsCol[:,0])
    normlzdResid = (-defaultBiasesApproxElastic-defaultBiasesCol)[:,0]/np.abs(normMetricValsCol[:,0])
    df = pd.DataFrame({'bias times sensitivity': normlzdBias*np.sum(normlzdSensMatrixPoly, axis=1), # sum of row elements
                       'residual times sensitivity': normlzdResid*np.sum(normlzdSensMatrixPoly, axis=1) # sum of row elements
                      }, index=metricsNames )
    residVsBiasScatter = px.scatter(df, x='bias times sensitivity', y=df.columns[1:],
                                 text=metricsNames, title = """Residual times sensitivity versus bias times sensitivity.""" )
    residVsBiasOneOneLine = px.line(df, x="bias times sensitivity", y="bias times sensitivity")
    residVsBiasFig = go.Figure(data=residVsBiasScatter.data
                                    + residVsBiasOneOneLine.data)
    residVsBiasFig.update_yaxes(title="Residual times sensitivity")
    residVsBiasFig.update_xaxes(title="Bias times sensitivity")
    residVsBiasFig.update_layout(hovermode="x")

    # Plot the relative biases versus sensitivity of each regional metric.
    #    More specifically, plot the maximum magnitude value of each row of the sensitivity matrix.
    #pdb.set_trace()
    relBiasNumerator = np.abs(-defaultBiasesApproxElastic-defaultBiasesCol)[:,0]/np.abs(normMetricValsCol[:,0])
    relBiasDenom = np.maximum(0.02, np.abs(-defaultBiasesCol[:,0]/np.abs(normMetricValsCol[:,0])) )
    df = pd.DataFrame({'Max abs normlzd sensitivity': np.max(np.abs(normlzdSensMatrixPoly), axis=1), # max |row elements|
                       'relative bias': relBiasNumerator / relBiasDenom
                      }, index=metricsNames )
    relBiasesVsSensFig = px.scatter(df, x='Max abs normlzd sensitivity', y=df.columns[1:],
                                 text=metricsNames, title = """Ratio of abs(approx_bias)/abs(default_bias) versus sensitivity.""" )
    relBiasesVsSensFig.update_yaxes(title="Relative biases")
    relBiasesVsSensFig.update_xaxes(title="Max abs normlzd sensitivity")
    relBiasesVsSensFig.update_layout(hovermode="x")

    # Plot the relative biases versus sensitivity of each regional metric.
    #    More specifically, plot the maximum magnitude value of each row of the sensitivity matrix.
    absBiasTuned = np.abs(-defaultBiasesApproxElastic-defaultBiasesCol)[:,0]/np.abs(normMetricValsCol[:,0])
    absBiasDefault = np.abs(-defaultBiasesCol[:,0]/np.abs(normMetricValsCol[:,0]))
    df = pd.DataFrame({'Max abs normlzd sensitivity': np.max(np.abs(normlzdSensMatrixPoly), axis=1), # max |row elements|
                       'bias difference': absBiasDefault - absBiasTuned
                      }, index=metricsNames )
    diffBiasesVsSensFig = px.scatter(df, x='Max abs normlzd sensitivity', y=df.columns[1:],
                                     text=metricsNames,
                                     title = """abs(default_bias) - abs(approx_bias) versus sensitivity.""" )
    diffBiasesVsSensFig.update_yaxes(title="Bias difference")
    diffBiasesVsSensFig.update_xaxes(title="Max abs normlzd sensitivity")
    diffBiasesVsSensFig.update_layout(hovermode="x")

    # Plot the parameter values recommended by SVD.
    # Multiply in the user-designated scale factors before plotting.
    paramsFig = go.Figure()
    paramsFig.add_trace(go.Scatter(x=paramsNames, y=paramsLowValsPCBound[:,0]*paramsScales,
                                   name=r'$paramsSolnPC - \sigma$',
                                   line=dict(color='white', width=0), mode='lines', showlegend=False))
    paramsFig.add_trace(go.Scatter(x=paramsNames, y=paramsHiValsPCBound[:,0]*paramsScales, fill='tonexty',
                               name='Default Parameter Values +- sigma', mode='none',
                                   fillcolor='rgba(253,253,150,1.0)'))
    paramsFig.add_trace(go.Scatter(x=paramsNames, y=defaultParamValsOrigRow[0,:]*paramsScales,
                                   name='Default Parameter Values', line=dict(color='black', width=6) ))
    paramsFig.add_trace(go.Scatter(x=paramsNames, y=paramsSolnLin[:,0]*paramsScales,
                                   name='Linear regression, |dp|=' + '{:.2e}'.format(np.linalg.norm(dnormlzdParamsSolnLin)) ))
    paramsFig.add_trace(go.Scatter(x=paramsNames, y=paramsSolnNonlin[:,0]*paramsScales,
                                   name='paramsSolnNonlin, |dpNonlin|='
                                   + '{:.2e}'.format(np.linalg.norm(dnormlzdParamsSolnNonlin)) ))
    paramsFig.add_trace(go.Scatter(x=paramsNames, y=paramsSolnElastic[:,0]*paramsScales,
                                    name='Lasso regression, |dpLasso|='
                                   + '{:.2e}'.format(np.linalg.norm(dnormlzdParamsSolnElastic)) ,
                                   line=dict(color='red', width=2)  ))
    #paramsFig.add_trace(go.Scatter(x=paramsNames, y=paramsSolnPCBound[:,0]*paramsScales,
    #                                name='paramsSolnPCBound, |dpBound|='
    #                               + '{:.2e}'.format(0.0) ))
    paramsFig.update_yaxes(title="User-scaled parameter value")
    paramsFig.update_xaxes(title="Parameter Name")
    paramsFig.update_layout(hovermode="x")
    paramsFig.update_layout( width=1000, height=500  )

#    # Plot the biases of the default simulation and the SVD approximation of that
#    biasesMatrix = np.dstack((-defaultBiasesCol,
#                          #defaultBiasesApprox,
#                          #defaultBiasesApproxPC,
#                          #defaultBiasesApproxElastic,
#                          defaultBiasesApproxElasticNonlin,
#                          defaultBiasesApproxNonlin,
#                          linSolnBiasesCol
#                         )).squeeze()
#    fracBiasesMatrix = np.diagflat(np.reciprocal(np.abs(normMetricValsCol))) @ biasesMatrix
#    df = pd.DataFrame(fracBiasesMatrix,
#                    index=metricsNames,
#                  columns= ['fracDefBias',
#                            'fracDefBiasesApprox',
#                            'fracDefBiasesApproxPC',
#                            'fracDefBiasesApproxElasticNonlin',
#                            'fracDefBiasesApproxNonlin',
#                            'fracLinSolnBiasesCol'
#                           ])
#    biasesFig = px.line(df, x=df.index, y=df.columns,
#              title = """Fractional biases of default simulation and approximations thereof.<br>
#                    Plotted quantities have the structure -(def-obs), -(def-fwd), -(def-lin)""")
#    biasesFig.update_yaxes(title="-(Def-Sim) / abs(obs metric value)")
#    biasesFig.update_xaxes(title="Regional metric")
#    biasesFig.layout.legend.title = "Default or which approximation"
#    biasesFig.update_layout(hovermode="x")
#    biasesFig.data[1].name = "fracDefBiasesApprox, " \
#                         + "{:.2f}".format(weightedBiasMagRatio) \
#                        + ", {:.2f}".format(BiasMagRatio)
#    biasesFig.data[2].name = "fracDefBiasesApproxPC, " \
#                         + "{:.2f}".format(weightedBiasPCMagRatio) \
#                         + ", {:.2f}".format(BiasPCMagRatio)
#    biasesFig.data[3].name = "fracDefBiasesApproxElastic, " \
#                         + "{:.2f}".format(weightedBiasElasticMagRatio) \
#                         + ", {:.2f}".format(BiasElasticMagRatio)
#    biasesFig.data[4].name = "fracDefBiasesApproxNonlin, " \
#                         + "{:.2f}".format(-99) \
#                         + ", {:.2f}".format(-99)
#    biasesFig.data[5].name = "fracLinSolnBiasesCol, " \
#                          + "{:.2f}".format(weightedBiasLinSolnMagRatio) \
#                          + ", {:.2f}".format(linSolnBiasMagRatio)
#

    df = pd.DataFrame(-1*normlzdSensParamsMatrixOrdered,
                      index=metricsNamesOrdered,
                      columns=paramsNames)
    biasContrOrderFig = px.bar(df, x=df.index, y=df.columns,
              title = """Linear contributions to actual removal of regional biases""")
    biasContrOrderFig.update_yaxes(title="-(Def-Sim) / abs(obs metric value)")
    biasContrOrderFig.update_xaxes(title="Regional metric")
    biasContrOrderFig.update_layout(hovermode="x")
    biasContrOrderFig.update_layout(showlegend=True)
    #biasContrOrderFig.update_traces(mode='markers', line_color='black')  # Plot default biases as black dots
    biasContrOrderFig.update_yaxes(visible=True,zeroline=True,zerolinewidth=1,zerolinecolor='gray') # Plot x axis
    biasContrOrderFig.update_layout( width=800, height=500  )
    # Now plot an arrow for each region that points from default-run bias to new bias after tuning
    xArrow = np.arange(len(metricsNamesOrdered)) # x-coordinate of arrows
    yArrow = -defaultBiasesCol[metricsSensOrdered,0]/np.abs(normMetricValsCol[metricsSensOrdered,0])
    gap = 0.1  # horizontal spacing between arrows
    #Plot arrows showing the tuner's nonlinear predicted bias removal
    for i, item in enumerate(metricsNamesOrdered):
         biasContrOrderFig.add_annotation(
         x=  xArrow[i] - gap,  # ith arrow's head
         # ith arrow's head:
        y= (-defaultBiasesApproxNonlin-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]),
         #y= (-defaultBiasesApproxNonlinNoCurv-defaultBiasesCol)[metricsSensOrdered[i],0]/np.abs(normMetricValsCol[metricsSensOrdered[i],0]),
        ax= xArrow[i] - gap,  # ith arrow's tail
        ay=  yArrow[i],  # ith arrow's tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        text='',  # blank because we want only the arrow
        showarrow=True,
        arrowhead=3,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='blue'
        )
     # Add a hand-made legend
    biasContrOrderFig.add_annotation(text='tuner prediction of bias removal',
                                   font=dict(color='blue'),
                                   align='left', xref='paper', yref='paper', x=0.05, y=0.9, showarrow=False)
    biasContrOrderFig.add_annotation(text='realized E3SM bias removal',
                                   font=dict(color='red'), #'rgba(255,0,0,0.0)'),
                                   align='left', xref='paper', yref='paper', x=0.05, y=0.8, showarrow=False)




    return

