# -*- coding: utf-8 -*-

# Run this app with `python3 sens_matrix_dashboard.py` and
# view the plots at http://127.0.0.1:8050/ in your web browser.
# (To open a web browser on a larson-group computer,
# login to malan with `ssh -X` and then type `firefox &`.)

def main():

    import dash
    from dash import dcc
    #import dash_core_components as dcc
    from dash import html
    #import dash_html_components as html
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd

    import numpy as np
    import pdb
    import sklearn
    import plotly.figure_factory as ff
    from plotly.subplots import make_subplots
    #from plotly.figure_factory import create_quiver
    from itertools import chain

    from test_analyzeSensMatrix import write_test_netcdf_files
    from set_up_dashboard_inputs import setUpInputs, setUpPreliminaries, \
                                        setupDefaultMetricValsCol
    from  create_figs import createFigs

    #print("New run --------------------------------------")

    # The user should input all tuning data into file set_up_dashboard_inputs.py
    metricsNames, metricsWeights, metricsNorms, \
    obsMetricValsDict, \
    paramsNames, paramsScales, \
    transformedParamsNames, \
    prescribedParamsNames, prescribedParamsScales, \
    prescribedTransformedParamsNames, \
    prescribedParamValsRow, \
    prescribedSensNcFilenames, prescribedSensNcFilenamesExt, \
    sensNcFilenames, sensNcFilenamesExt, \
    defaultNcFilename, linSolnNcFilename, \
    reglrCoef \
    = \
        setUpInputs()

    #pdb.set_trace()

    # Number of metrics
    numMetrics = len(metricsNames)

    obsMetricValsCol, normMetricValsCol, \
    defaultBiasesCol, \
    defaultParamValsOrigRow,\
    magParamValsRow, \
    dnormlzdPrescribedParams, \
    magPrescribedParamValsRow, \
    = setUpPreliminaries(metricsNames, metricsNorms,
                           obsMetricValsDict,
                           paramsNames, transformedParamsNames,
                           prescribedParamsNames, prescribedParamValsRow,
                           prescribedTransformedParamsNames,
                           sensNcFilenames,
                           defaultNcFilename
                          )

    #print("Orig defaultBiasesCol=", defaultBiasesCol)
    #print("metricsNames=", metricsNames)
    #print("obsMetricValsCol=", obsMetricValsCol)

    # Construct numMetrics x numParams matrix of second derivatives, d2metrics/dparams2.
    # The derivatives are normalized by observed metric values and max param values.
    normlzdCurvMatrix, normlzdSensMatrixPoly, normlzdConstMatrix, \
    normlzdOrdDparamsMin, normlzdOrdDparamsMax = \
        constructNormlzdCurvMatrix(metricsNames, paramsNames, transformedParamsNames, \
                                   metricsWeights, obsMetricValsCol, normMetricValsCol, magParamValsRow, \
                                   sensNcFilenames, sensNcFilenamesExt, defaultNcFilename)

    #print("normlzdSensMatrixPoly=", normlzdSensMatrixPoly)
    #print("normlzdCurvMatrix=", normlzdCurvMatrix)

    # In order to weight certain metrics, multiply each row of normlzdSensMatrixPoly
    # by metricsWeights
    normlzdWeightedSensMatrixPoly = np.diag(np.transpose(metricsWeights)[0]) @ normlzdSensMatrixPoly

    # For prescribed parameters, construct numMetrics x numParams matrix of second derivatives, d2metrics/dparams2.
    # The derivatives are normalized by observed metric values and max param values.
    normlzdPrescribedCurvMatrix, normlzdPrescribedSensMatrixPoly, normlzdPrescribedConstMatrix, \
    normlzdPrescribedOrdDparamsMin, normlzdPrescribedOrdDparamsMax = \
        constructNormlzdCurvMatrix(metricsNames, prescribedParamsNames, prescribedTransformedParamsNames, \
                                   metricsWeights, obsMetricValsCol, normMetricValsCol, magPrescribedParamValsRow, \
                                   prescribedSensNcFilenames, prescribedSensNcFilenamesExt, defaultNcFilename)

    #print("normlzdPrecribedSensMatrixPoly=", normlzdPrescribedSensMatrixPoly)
    #print("normlzdPrecribedCurvMatrix=", normlzdPrescribedCurvMatrix)

    # This is the prescribed correction to the metrics that appears on the left-hand side of the Taylor equation.
    #   It is not a bias from the obs.  It is a correction to the simulated default metric values
    #   based on prescribed param values.
    normlzdPrescribedBiasesCol = \
         fwdFnc( dnormlzdPrescribedParams, normlzdPrescribedSensMatrixPoly, normlzdPrescribedCurvMatrix, numMetrics )

    #print("normlzdPrecribedBiasesCol=", normlzdPrescribedBiasesCol)

    prescribedBiasesCol = normlzdPrescribedBiasesCol * np.abs(normMetricValsCol)

    #print("precribedBiasesCol=", prescribedBiasesCol)

    # defaultBiasesCol + prescribedBiasesCol = -fwdFnc_tuned_params  (see objFnc).
    # This lumps the prescribed-parameter adjustment into defaultBiasesCol
    defaultBiasesCol = defaultBiasesCol + prescribedBiasesCol

    #print("Orig+Prescribed defaultBiasesCol=", defaultBiasesCol)

    #pdb.set_trace()

    print("Optimizing parameter values . . . ")

    defaultBiasesApproxNonlin, \
    dnormlzdParamsSolnNonlin, paramsSolnNonlin, \
    dnormlzdParamsSolnLin, paramsSolnLin, \
    defaultBiasesApproxNonlin2x, \
    defaultBiasesApproxNonlinNoCurv, defaultBiasesApproxNonlin2xCurv = \
        solveUsingNonlin(metricsNames, paramsNames, transformedParamsNames,
                         metricsWeights, normMetricValsCol, magParamValsRow,
                         sensNcFilenames, sensNcFilenamesExt, defaultNcFilename,
                         defaultParamValsOrigRow,
                         normlzdSensMatrixPoly, defaultBiasesCol,
                         #normlzdSensMatrixPoly, defaultBiasesCol-prescribedBiasesCol,
                         normlzdCurvMatrix,
                         reglrCoef,
                         beVerbose=False)

    print("Tuned parameter values (paramsSolnNonlin)")
    for idx in range(0,len(paramsNames)): print("{:33s} {:7.7g}".format( paramsNames[idx], paramsSolnNonlin[idx][0] ) )

    normlzdLinplusSensMatrixPoly = normlzdSemiLinMatrixFnc(
                                        dnormlzdParamsSolnNonlin, normlzdSensMatrixPoly, 
                                        normlzdCurvMatrix, numMetrics)
    normlzdWeightedLinplusSensMatrixPoly = np.diag(np.transpose(metricsWeights)[0]) @ normlzdLinplusSensMatrixPoly



    # Find best-fit params by use of the Elastic Net algorithm
    defaultBiasesApproxElastic, defaultBiasesApproxElasticNonlin, \
    dnormlzdParamsSolnElastic, paramsSolnElastic = \
        findParamsUsingElastic(normlzdSensMatrixPoly, normlzdWeightedSensMatrixPoly,
                     defaultBiasesCol, normMetricValsCol, metricsWeights,
                     magParamValsRow, defaultParamValsOrigRow,
                     normlzdCurvMatrix,
                     beVerbose=False)

    defaultBiasesApproxElasticCheck = ( normlzdWeightedSensMatrixPoly @ dnormlzdParamsSolnElastic ) \
                            * np.reciprocal(metricsWeights) * np.abs(normMetricValsCol)

    #print("defaultBiasesApproxElastic = ", defaultBiasesApproxElastic)
    #print("defaultBiasesApproxElasticCheck = ", defaultBiasesApproxElasticCheck)

    #pdb.set_trace()

    # Estimate non-linearity of the global model to perturbations in parameter values.
    # To do so, calculate radius of curvature of the three points from the default simulation
    #   and the two sensitivity simulations.
    #calcNormlzdRadiusCurv(metricsNames, paramsNames, transformedParamsNames, paramsScales,
    #                      metricsWeights, obsMetricValsCol,
    #                      sensNcFilenames, sensNcFilenamesExt, defaultNcFilename)


    ## Find outliers by use of the ransac algorithm
    #outlier_mask, defaultBiasesApproxRansac, normlzdWeightedDefaultBiasesApproxRansac, \
    #dnormlzdParamsSolnRansac, paramsSolnRansac = \
    #    findOutliers(normlzdSensMatrix, normlzdWeightedSensMatrix, \
    #                 defaultBiasesCol, normMetricValsCol, magParamValsRow, defaultParamValsOrigRow)
    #print( "ransac_outliers = ", metricsNames[outlier_mask] )
    #print( "ransac_inliers = ", metricsNames[~outlier_mask] )
    ##pdb.set_trace()


    # Check whether the minimizer actually reduces chisqd
    # Initial value of chisqd, which assumes parameter perturbations are zero
    normlzdDefaultBiasesCol = defaultBiasesCol/np.abs(normMetricValsCol)
    normlzdWeightedDefaultBiasesCol = metricsWeights * normlzdDefaultBiasesCol
    chisqdZero = objFnc(np.zeros_like(defaultParamValsOrigRow), \
                        normlzdSensMatrixPoly, normlzdDefaultBiasesCol, metricsWeights, \
                        normlzdCurvMatrix, reglrCoef, numMetrics)
    # Optimized value of chisqd, which uses optimal values of parameter perturbations
    chisqdMin = objFnc(dnormlzdParamsSolnNonlin.T, \
                        normlzdSensMatrixPoly, normlzdDefaultBiasesCol, metricsWeights, \
                        normlzdCurvMatrix, reglrCoef, numMetrics)

    #print("chisqdZero =", chisqdZero)
    #print("chisqdMin =", chisqdMin)
    print("chisqdMinRatio =", chisqdMin/chisqdZero)

    chisqdUnweightedZero = objFnc(np.zeros_like(defaultParamValsOrigRow), \
                        normlzdSensMatrixPoly, normlzdDefaultBiasesCol, np.ones_like(metricsWeights), \
                        normlzdCurvMatrix, reglrCoef, numMetrics)
    # Optimized value of chisqd, which uses optimal values of parameter perturbations
    chisqdUnweightedMin = objFnc(dnormlzdParamsSolnNonlin.T, \
                        normlzdSensMatrixPoly, normlzdDefaultBiasesCol, np.ones_like(metricsWeights), \
                        normlzdCurvMatrix, reglrCoef, numMetrics)

    #print("chisqdUnweightedZero =", chisqdUnweightedZero)
    #print("chisqdUnweightedMin =", chisqdUnweightedMin)
    print("chisqdUnweightedMinRatio =", chisqdUnweightedMin/chisqdUnweightedZero)

    # Set up a column vector of metric values from the global simulation based on optimized
    #     parameter values.
    linSolnMetricValsCol = setupDefaultMetricValsCol(metricsNames, linSolnNcFilename)

    # Store biases in default simulation, ( global_model - obs )
    linSolnBiasesCol = np.subtract(linSolnMetricValsCol, obsMetricValsCol)
    #linSolnBiasesCol = linSolnBiasesCol + prescribedBiasesCol

    # Check whether the minimizer actually reduces chisqd
    # Initial value of chisqd, which assumes parameter perturbations are zero
    normlzdLinSolnBiasesCol = linSolnBiasesCol/np.abs(normMetricValsCol)
    chisqdLinSolnMin = objFnc(np.zeros_like(defaultParamValsOrigRow), \
                        normlzdSensMatrixPoly, normlzdLinSolnBiasesCol, metricsWeights, \
                        normlzdCurvMatrix, reglrCoef, numMetrics)

    #print("chisqdZero =", chisqdZero)
    #print("chisqdMin =", chisqdMin)
    print("chisqdLinSolnMinRatio =", chisqdLinSolnMin/chisqdZero)

    chisqdUnweightedLinSolnMin = objFnc(np.zeros_like(defaultParamValsOrigRow), \
                        normlzdSensMatrixPoly, normlzdLinSolnBiasesCol, np.ones_like(metricsWeights), \
                        normlzdCurvMatrix, reglrCoef, numMetrics)

    #print("chisqdUnweightedZero =", chisqdUnweightedZero)
    #print("chisqdUnweightedMin =", chisqdUnweightedMin)
    print("chisqdUnweightedLinSolnMinRatio =", chisqdUnweightedLinSolnMin/chisqdUnweightedZero)
    print("-----------------------------------------------------")

    ##############################################
    #
    #    Create plots
    #
    ##############################################


    #print("Creating plots . . .")
    paramsLowValsPCBound, paramsHiValsPCBound, \
    threeDotFig = \
        createFigs(metricsNames, 
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
               sensNcFilenames, sensNcFilenamesExt, defaultNcFilename)


    return


# Calculate semi-linear matrix, sensMatrix + curvMatrix*dp, for use in forward solution
def normlzdSemiLinMatrixFnc(dnormlzdParams, normlzdSensMatrix, normlzdCurvMatrix, numMetrics):
    import numpy as np

    normlzdSemiLinMatrix = \
        normlzdSensMatrix \
        + 0.5 * normlzdCurvMatrix * ( np.ones((numMetrics,1)) @ dnormlzdParams.T )

    return normlzdSemiLinMatrix

# Calculate forward nonlinear solution, normalized but not weighted
def fwdFnc(dnormlzdParams, normlzdSensMatrix, normlzdCurvMatrix, numMetrics):
    import numpy as np

    normlzdDefaultBiasesApproxNonlin = \
        normlzdSemiLinMatrixFnc(dnormlzdParams, normlzdSensMatrix, normlzdCurvMatrix, numMetrics) @ dnormlzdParams

            #normlzdSensMatrix @ dnormlzdParams \
            #+ 0.5 * normlzdCurvMatrix @ (dnormlzdParams * dnormlzdParams) 

    return normlzdDefaultBiasesApproxNonlin

# Define objective function that is to be minimized.
def objFnc(dnormlzdParams, normlzdSensMatrix, normlzdDefaultBiasesCol, metricsWeights,
           normlzdCurvMatrix, reglrCoef, numMetrics):

    import numpy as np
    import pdb

    dnormlzdParams = np.atleast_2d(dnormlzdParams).T # convert from 1d row array to 2d column array
    chisqd = np.linalg.norm( (-normlzdDefaultBiasesCol \
                              - fwdFnc(dnormlzdParams, normlzdSensMatrix, normlzdCurvMatrix, numMetrics) \
                             ) * metricsWeights \
                                , ord=2 \
                           )**1  \
                + reglrCoef * np.linalg.norm( dnormlzdParams, ord=1 )

    return chisqd

def solveUsingNonlin(metricsNames, paramsNames, transformedParamsNames,
                     metricsWeights, normMetricValsCol, magParamValsRow,
                     sensNcFilenames, sensNcFilenamesExt, defaultNcFilename,
                     defaultParamValsOrigRow,
                     normlzdSensMatrix, defaultBiasesCol,
                     normlzdCurvMatrix,
                     reglrCoef,
                     beVerbose):

    import numpy as np
    import pdb
    from scipy.optimize import minimize
    from scipy.optimize import Bounds

    numMetrics = len(metricsNames)

    #pdb.set_trace()

    # Don't let parameter values go negative
    lowerBoundsCol =  -defaultParamValsOrigRow[0]/magParamValsRow[0]

    # Perform nonlinear optimization
    normlzdDefaultBiasesCol = defaultBiasesCol/np.abs(normMetricValsCol)
    #dnormlzdParamsSolnNonlin = minimize(objFnc,x0=np.ones_like(np.transpose(defaultParamValsOrigRow)), \
    dnormlzdParamsSolnNonlin = minimize(objFnc,x0=np.zeros_like(np.transpose(defaultParamValsOrigRow[0])), \
    #dnormlzdParamsSolnNonlin = minimize(objFnc,dnormlzdParamsSoln, \
                               args=(normlzdSensMatrix, normlzdDefaultBiasesCol, metricsWeights,
                               normlzdCurvMatrix, reglrCoef, numMetrics),\
                               method='Powell', tol=1e-12,
                               bounds=Bounds(lb=lowerBoundsCol) )
    dnormlzdParamsSolnNonlin = np.atleast_2d(dnormlzdParamsSolnNonlin.x).T


    dparamsSolnNonlin = dnormlzdParamsSolnNonlin * np.transpose(magParamValsRow)
    paramsSolnNonlin = np.transpose(defaultParamValsOrigRow) + dparamsSolnNonlin
    if beVerbose:
        print("paramsSoln.T=", paramsSoln.T)
        print("paramsSolnNonlin.T=", paramsSolnNonlin.T)
        print("normlzdSensMatrix@dnPS.x.T=", normlzdSensMatrix @ dnormlzdParamsSolnNonlin)
        print("normlzdDefaultBiasesCol.T=", normlzdDefaultBiasesCol.T)
        print("normlzdSensMatrix=", normlzdSensMatrix)

    normlzdWeightedDefaultBiasesApproxNonlin = \
             fwdFnc(dnormlzdParamsSolnNonlin, normlzdSensMatrix, normlzdCurvMatrix, numMetrics) \
             * metricsWeights

    scale = 2
    normlzdWeightedDefaultBiasesApproxNonlin2x = \
             fwdFnc(scale*dnormlzdParamsSolnNonlin, normlzdSensMatrix, 1*normlzdCurvMatrix, numMetrics) \
             * metricsWeights

    # defaultBiasesApprox = (forward model soln - default soln)
    defaultBiasesApproxNonlin = normlzdWeightedDefaultBiasesApproxNonlin \
                                * np.reciprocal(metricsWeights) * np.abs(normMetricValsCol)

    defaultBiasesApproxNonlin2x = normlzdWeightedDefaultBiasesApproxNonlin2x \
                                * np.reciprocal(metricsWeights) * np.abs(normMetricValsCol)

    # To provide error bars, calculate solution with no nonlinear term and double the nonlinear term
    defaultBiasesApproxNonlinNoCurv = \
             fwdFnc(dnormlzdParamsSolnNonlin, normlzdSensMatrix, 0*normlzdCurvMatrix, numMetrics) \
             * np.abs(normMetricValsCol)

    defaultBiasesApproxNonlin2xCurv = \
             fwdFnc(dnormlzdParamsSolnNonlin, normlzdSensMatrix, 2*normlzdCurvMatrix, numMetrics) \
             * np.abs(normMetricValsCol)



    dnormlzdParamsSolnLin = minimize(objFnc,x0=np.zeros_like(np.transpose(defaultParamValsOrigRow[0])), \
                               args=(normlzdSensMatrix, normlzdDefaultBiasesCol, metricsWeights,
                               0*normlzdCurvMatrix, reglrCoef, numMetrics),\
                               method='Powell')
    dnormlzdParamsSolnLin = np.atleast_2d(dnormlzdParamsSolnLin.x).T
    dparamsSolnLin = dnormlzdParamsSolnLin * np.transpose(magParamValsRow)
    paramsSolnLin = np.transpose(defaultParamValsOrigRow) + dparamsSolnLin


    return (defaultBiasesApproxNonlin, \
            dnormlzdParamsSolnNonlin, paramsSolnNonlin, \
            dnormlzdParamsSolnLin, paramsSolnLin, \
            defaultBiasesApproxNonlin2x, \
            defaultBiasesApproxNonlinNoCurv, defaultBiasesApproxNonlin2xCurv \
           )

def constructNormlzdCurvMatrix(metricsNames, paramsNames, transformedParamsNames,
                               metricsWeights, obsMetricValsCol, normMetricValsCol, magParamValsRow,
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
        print("Number of parameters does not equal number of netcdf files.")
        quit()

    # Number of tunable parameters
    numParams = len(paramsNames)

    # Number of metrics
    numMetrics = len(metricsNames)

    # For use in normalizing metrics matrices
    invrsObsMatrix = np.reciprocal(np.abs(normMetricValsCol)) @ np.ones((1,numParams))

    # Set up a column vector of metric values from the default simulation
    defaultMetricValsCol = \
        setupDefaultMetricValsCol(metricsNames, defaultNcFilename)
    defaultMetricValsMatrix = defaultMetricValsCol @ np.ones((1,numParams))
    normlzdDefaultMetricValsMatrix = defaultMetricValsMatrix * invrsObsMatrix

    # Based on the default simulation,
    #    set up a column vector of metrics and a row vector of parameter values.
    defaultParamValsRow, defaultParamValsOrigRow = \
        setupDefaultParamVectors(paramsNames, transformedParamsNames,
                                 numParams,
                                 defaultNcFilename)
    normlzdDefaultParamValsRow = defaultParamValsRow * np.reciprocal(magParamValsRow)

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
    normlzdSens1ParamValsRow = sens1ParamValsRow * np.reciprocal(magParamValsRow)
    normlzdSens1MetricValsMatrix = sens1MetricValsMatrix * invrsObsMatrix

    # Set up sensitivity-simulation matrices from the extended sensitivity simulation
    sens2MetricValsMatrix, sens2ParamValsRow, sens2ParamValsOrigRow = \
        setupSensArrays(metricsNames, paramsNames, transformedParamsNames,
                        numMetrics, numParams,
                        sens2NcFilenames,
                        beVerbose=False)
    normlzdSens2ParamValsRow = sens2ParamValsRow * np.reciprocal(magParamValsRow)
    normlzdSens2MetricValsMatrix = sens2MetricValsMatrix * invrsObsMatrix

    # Initialize matrix to store second derivatives of metrics w.r.t. parameters
    normlzdCurvMatrix = np.zeros_like(sens1MetricValsMatrix)
    normlzdCurvMatrix2 = np.zeros_like(sens1MetricValsMatrix)  # 2nd way of calculating derivs
    normlzdCurvMatrixPoly = np.zeros_like(sens1MetricValsMatrix)  # 3rd way of calculating derivs
    normlzdSensMatrixPoly = np.zeros_like(sens1MetricValsMatrix)  # Approx of linear sensitivity
    normlzdConstMatrixPoly = np.zeros_like(sens1MetricValsMatrix)  # Approx of linear sensitivity
    normlzdOrdDparamsMin = np.zeros_like(sens1MetricValsMatrix)
    normlzdOrdDparamsMax = np.zeros_like(sens1MetricValsMatrix)

    #pdb.set_trace()

    # Compute quadratic coefficients using a polynomial fit to metric and parameters
    for arrayCol in np.arange(numParams):
        for arrayRow in np.arange(numMetrics):

            # Set up three (x,y) points whose 2nd-order derivative we wish to calculate.
            # For the spline code below, the x points need to be ordered from least to greatest.
            if normlzdSens1ParamValsRow[0,arrayCol] < normlzdDefaultParamValsRow[0,arrayCol] < normlzdSens2ParamValsRow[0,arrayCol]:
                normlzdOrdParams = [ normlzdSens1ParamValsRow[0,arrayCol],
                       normlzdDefaultParamValsRow[0,arrayCol],
                       normlzdSens2ParamValsRow[0,arrayCol] ]
                normlzdOrdDparams = normlzdOrdParams - normlzdDefaultParamValsRow[0,arrayCol]
                normlzdOrdMetrics = [ normlzdSens1MetricValsMatrix[arrayRow,arrayCol],
                        normlzdDefaultMetricValsMatrix[arrayRow,arrayCol],
                        normlzdSens2MetricValsMatrix[arrayRow,arrayCol] ]
            elif normlzdSens2ParamValsRow[0,arrayCol] < normlzdDefaultParamValsRow[0,arrayCol] < normlzdSens1ParamValsRow[0,arrayCol]:
                normlzdOrdParams = [ normlzdSens2ParamValsRow[0,arrayCol],
                       normlzdDefaultParamValsRow[0,arrayCol],
                       normlzdSens1ParamValsRow[0,arrayCol] ]
                normlzdOrdDparams = normlzdOrdParams - normlzdDefaultParamValsRow[0,arrayCol]
                normlzdOrdMetrics = [ normlzdSens2MetricValsMatrix[arrayRow,arrayCol],
                        normlzdDefaultMetricValsMatrix[arrayRow,arrayCol],
                        normlzdSens1MetricValsMatrix[arrayRow,arrayCol] ]
            elif normlzdDefaultParamValsRow[0,arrayCol] < normlzdSens1ParamValsRow[0,arrayCol] < normlzdSens2ParamValsRow[0,arrayCol]:
                normlzdOrdParams = [ normlzdDefaultParamValsRow[0,arrayCol],
                       normlzdSens1ParamValsRow[0,arrayCol],
                       normlzdSens2ParamValsRow[0,arrayCol] ]
                normlzdOrdDparams = normlzdOrdParams - normlzdDefaultParamValsRow[0,arrayCol]
                normlzdOrdMetrics = [ normlzdDefaultMetricValsMatrix[arrayRow,arrayCol],
                        normlzdSens1MetricValsMatrix[arrayRow,arrayCol],
                        normlzdSens2MetricValsMatrix[arrayRow,arrayCol] ]
            elif normlzdDefaultParamValsRow[0,arrayCol] < normlzdSens2ParamValsRow[0,arrayCol] < normlzdSens1ParamValsRow[0,arrayCol]:
                normlzdOrdParams = [ normlzdDefaultParamValsRow[0,arrayCol],
                       normlzdSens2ParamValsRow[0,arrayCol],
                       normlzdSens1ParamValsRow[0,arrayCol] ]
                normlzdOrdDparams = normlzdOrdParams - normlzdDefaultParamValsRow[0,arrayCol]
                normlzdOrdMetrics = [ normlzdDefaultMetricValsMatrix[arrayRow,arrayCol],
                        normlzdSens2MetricValsMatrix[arrayRow,arrayCol],
                        normlzdSens1MetricValsMatrix[arrayRow,arrayCol] ]
            elif normlzdSens1ParamValsRow[0,arrayCol] < normlzdSens2ParamValsRow[0,arrayCol] < normlzdDefaultParamValsRow[0,arrayCol]:
                normlzdOrdParams = [ normlzdSens1ParamValsRow[0,arrayCol],
                       normlzdSens2ParamValsRow[0,arrayCol],
                       normlzdDefaultParamValsRow[0,arrayCol] ]
                normlzdOrdDparams = normlzdOrdParams - normlzdDefaultParamValsRow[0,arrayCol]
                normlzdOrdMetrics = [ normlzdSens1MetricValsMatrix[arrayRow,arrayCol],
                        normlzdSens2MetricValsMatrix[arrayRow,arrayCol],
                        normlzdDefaultMetricValsMatrix[arrayRow,arrayCol] ]
            elif normlzdSens2ParamValsRow[0,arrayCol] < normlzdSens1ParamValsRow[0,arrayCol] < normlzdDefaultParamValsRow[0,arrayCol]:
                normlzdOrdParams = [ normlzdSens2ParamValsRow[0,arrayCol],
                       normlzdSens1ParamValsRow[0,arrayCol],
                       normlzdDefaultParamValsRow[0,arrayCol] ]
                normlzdOrdDparams = normlzdOrdParams - normlzdDefaultParamValsRow[0,arrayCol]
                normlzdOrdMetrics = [ normlzdSens2MetricValsMatrix[arrayRow,arrayCol],
                        normlzdSens1MetricValsMatrix[arrayRow,arrayCol],
                        normlzdDefaultMetricValsMatrix[arrayRow,arrayCol] ]
            else:
                print("Sensitivity parameter values are equal to each other or the default value in constructNormlzdCurvMatrix.")
                print("normlzdSens1ParamValsRow=", normlzdSens1ParamValsRow)
                print("normlzdSens2ParamValsRow=", normlzdSens2ParamValsRow)
                print("normlzdDefaultParamValsRow=", normlzdDefaultParamValsRow)
                pdb.set_trace()
                quit()

            normlzdOrdDparamsMin[arrayRow,arrayCol] = np.min(normlzdOrdDparams)
            normlzdOrdDparamsMax[arrayRow,arrayCol]  = np.max(normlzdOrdDparams)

            # Calculate second-order spline based on three given (x,y) points.
            metricValsSpline = UnivariateSpline(normlzdOrdParams,normlzdOrdMetrics,s=0,k=2)
            # Based on spline, find 2nd derivative at arbitrary point (1).
            # I hope that the derivative has the same value at all points,
            #    since it is a parabola.
            normlzdCurvMatrix[arrayRow,arrayCol] = metricValsSpline.derivative(n=2)(1)

            # Check results using a 2nd calculation
            polyCoefs = np.polyfit(normlzdOrdParams, normlzdOrdMetrics, 2)
            normlzdCurvMatrix2[arrayRow,arrayCol] = 2*polyCoefs[0]
            #pdb.set_trace()

            # Check results using a 3rd calculation
            polyCoefs = np.polyfit(normlzdOrdDparams, normlzdOrdMetrics, 2)
            normlzdCurvMatrixPoly[arrayRow][arrayCol] = 2. * polyCoefs[0]
            normlzdSensMatrixPoly[arrayRow,arrayCol] = polyCoefs[1]
            normlzdConstMatrixPoly[arrayRow,arrayCol] = polyCoefs[2]


    return ( normlzdCurvMatrixPoly, normlzdSensMatrixPoly, normlzdConstMatrixPoly, \
             normlzdOrdDparamsMin, normlzdOrdDparamsMax )

#def constructNormlzd2ndOrderTensor(numParams, numMetrics,
#                                   normlzdCurvMatrix, normlzdSensMatrixPoly, normlzdConstMatrix, corrParam):
#    '''Constructs a numParams x numMetrics x numParams tensor of second derivatives, d2metrics/dparams1dparams2.
#    The derivatives are normalized by observed metric values and max param values.'''
#
#    normlzdCurvMatrix, normlzdSensMatrixPoly, normlzdConstMatrix, \
#    normlzdOrdDparamsMin, normlzdOrdDparamsMax = \
#        constructNormlzdCurvMatrix(metricsNames, paramsNames, transformedParamsNames, \
#                                   metricsWeights, obsMetricValsCol, normMetricValsCol, magParamValsRow, \
#                                   sensNcFilenames, sensNcFilenamesExt, defaultNcFilename)
#
#    for i in np.arange(numMetrics):
#        # Construct matrix with M(j,k)=0 if curv opposite for i,j; otherwise, M(j,k)=1.
#        curvParamMatrix = np.outer( normlzdCurvMatrix[i,:], np.ones(numParams) )
#        corrParamMatrix = 0.5 * np.abs( np.sign( curvParamMatrix ) + np.sign( curvParamMatrix.T ) )
#        corrParamMatrix = np.fill_diagonal(corrParamMatrix, 1.0)
#        diagSqrtCurvMatrix = np.diag(np.sqrt(normlzdCurvMatrix[i,:]))
#
#    # d4 = np.einsum('j,jik,k->i', params, offdiagtensor, params)
#
#    return ( normlzd2ndOrderTensor  )


def calcNormlzdRadiusCurv(metricsNames, paramsNames, transformedParamsNames, paramsScales,
                          metricsWeights, obsMetricValsCol,
                          sensNcFilenames, sensNcFilenamesExt, defaultNcFilename):

    """
    Calculate radius of curvature of output from 2 sensitivity simulations plus the default
    simulation.
    """
    import numpy as np
    import sys
    import netCDF4
    import matplotlib.pyplot as plt
    import pdb

    from analyze_sensitivity_matrix import setupDefaultParamVectors, \
                                           setupSensArrays
    from set_up_dashboard_inputs import setupDefaultMetricValsCol

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

    # Set up sensitivity-simulation matrices from the extended sensitivity simulation
    sensMetricValsMatrixExt, sensParamValsRowExt, sensParamValsOrigRowExt = \
        setupSensArrays(metricsNames, paramsNames, transformedParamsNames,
                        numMetrics, numParams,
                        sensNcFilenamesExt,
                        beVerbose=False)

    normlzd_radius_of_curv = np.full_like(sensMetricValsMatrix, 0.0)

    # Calculate differences in parameter values between default, sensitivity,
    #    and extended sensitivity runs.
    delta_params_def_sens = sensParamValsRow - defaultParamValsRow
    delta_params_def_sensExt = sensParamValsRowExt - defaultParamValsRow
    delta_params_sens_sensExt = sensParamValsRowExt - sensParamValsRow

    # Calculate numMetrics x numParams matrix of metric values.
    delta_metrics_def_sens = sensMetricValsMatrix - defaultMetricValsMatrix
    delta_metrics_def_sensExt = sensMetricValsMatrixExt - defaultMetricValsMatrix
    delta_metrics_sens_sensExt = sensMetricValsMatrixExt - sensMetricValsMatrix
    for col in np.arange(numParams):
        for row in np.arange(numMetrics):
            # Distance between points in simulations = sqrt(dparam**2 + dmetric**2)
            length_def_sens = np.linalg.norm([delta_params_def_sens[0][col],
                                              delta_metrics_def_sens[row][col]])
            length_def_sensExt = np.linalg.norm([delta_params_def_sensExt[0][col],
                                                 delta_metrics_def_sensExt[row][col]])
            length_sens_sensExt = np.linalg.norm([delta_params_sens_sensExt[0][col],
                                                  delta_metrics_sens_sensExt[row][col]])
            semi_perim = 0.5 * ( length_def_sens + length_def_sensExt + length_sens_sensExt )
            # area of triangle formed by points.  Use Heron's formula.
            area = np.sqrt( semi_perim *
                           (semi_perim-length_def_sens) *
                           (semi_perim-length_def_sensExt) *
                           (semi_perim-length_sens_sensExt)
                          )
            if (area == 0.0):
                print( '\nIn calcNormlzdRadiusCurv, area == 0.0 for param ', paramsNames[col],
                        'and metric ', metricsNames[row] )

            # Greatest distance between parameter values in the 3 simulations:
            max_params_width = \
            np.max(np.abs([delta_params_def_sens[0][col],
                        delta_params_def_sensExt[0][col],
                        delta_params_sens_sensExt[0][col]]))
            if (max_params_width == 0.0):
                print( '\nIn calcNormlzdRadiusCurv, max_params_width == 0.0 for param ', paramsNames[col],
                        'and metric ', metricsNames[row] )

            # Calculate Menger curvature from triangle area and distance between points:
            normlzd_radius_of_curv[row][col] = 0.25 * length_def_sens*length_def_sensExt*length_sens_sensExt \
                                                / area / max_params_width

    #pdb.set_trace()
    fig, axs = plt.subplots(numMetrics, numParams, figsize=(24,36))
    for col in np.arange(numParams):
        for row in np.arange(numMetrics):

            paramVals = [defaultParamValsRow[0][col], sensParamValsRow[0][col], sensParamValsRowExt[0][col]]
            metricVals = [defaultMetricValsMatrix[row][col], sensMetricValsMatrix[row][col],
                  sensMetricValsMatrixExt[row][col]]

            axs[row, col].plot( paramVals, metricVals, marker=".", ls="" )
            axs[row, col].plot( paramVals, obsMetricValsCol[row][0] * np.ones((3,1)), color="r" )
            axs[row, col].set_xlabel(paramsNames[col])
            axs[row, col].set_ylabel(metricsNames[row])
            #fig.show()

    plt.show()
    plt.savefig('param_metric_scatter.png')
    #pdb.set_trace()

    return

def findOutliers(normlzdSensMatrix, normlzdWeightedSensMatrix, \
                 defaultBiasesCol, normMetricValsCol, magParamValsRow, defaultParamValsOrigRow):

    import numpy as np
    from sklearn import linear_model
    import pdb

#    ransac = linear_model.RANSACRegressor(max_trials=1000,random_state=0,
#                                          base_estimator=linear_model.LinearRegression(), residual_threshold=None)
#    ransac.fit(normlzdSensMatrix, -defaultBiasesCol / np.abs(normMetricValsCol) )
#    defaultBiasesApproxRansac = ransac.predict(normlzdSensMatrix) * np.abs(normMetricValsCol)
#    dnormlzdParamsSolnRansac = np.transpose( ransac.estimator_.coef_ )
#    ransac = linear_model.RANSACRegressor(max_trials=10000,random_state=0,
#             base_estimator=linear_model.ElasticNet(fit_intercept=False, random_state=0, tol=1e-3,
#                                                    l1_ratio=0.0, alpha=5),
#                                          residual_threshold=None)
#    ransac.fit(normlzdSensMatrix, -defaultBiasesCol / np.abs(normMetricValsCol) )
#    defaultBiasesApproxRansac = np.transpose( np.atleast_2d( ransac.predict(normlzdSensMatrix) ) ) \
#                                * np.abs(normMetricValsCol)
#    dnormlzdParamsSolnRansac = np.transpose( np.atleast_2d( ransac.estimator_.coef_ ) )
#    inlier_mask = ransac.inlier_mask_
#    outlier_mask = np.logical_not(inlier_mask)


    ransac = linear_model.HuberRegressor(fit_intercept=False)
    ransac.fit(normlzdSensMatrix, -defaultBiasesCol / np.abs(normMetricValsCol) )
    defaultBiasesApproxRansac = np.transpose( np.atleast_2d( ransac.predict(normlzdSensMatrix) ) ) \
                                * np.abs(normMetricValsCol)
    dnormlzdParamsSolnRansac = np.transpose( np.atleast_2d( ransac.coef_ ) )
#    defaultBiasesApproxRansac = ransac.predict(normlzdSensMatrix) * np.abs(normMetricValsCol)
#    dnormlzdParamsSolnRansac = np.transpose( ransac.coef_ )

    dparamsSolnRansac = dnormlzdParamsSolnRansac * np.transpose(magParamValsRow)
    paramsSolnRansac = np.transpose(defaultParamValsOrigRow) + dparamsSolnRansac

    outlier_mask = ransac.outliers_
    inlier_mask = np.logical_not(outlier_mask)

    print( "paramsSolnRansac = ", paramsSolnRansac )
    print( "dparamsSolnRansac = ", dparamsSolnRansac )

    # If the solution were perfect, this variable would equal
    #     the normalized, weighted right-hand side.
    normlzdWeightedDefaultBiasesApproxRansac = \
            normlzdWeightedSensMatrix @ dnormlzdParamsSolnRansac

    #pdb.set_trace()

    return (outlier_mask, defaultBiasesApproxRansac, normlzdWeightedDefaultBiasesApproxRansac, \
            dnormlzdParamsSolnRansac, paramsSolnRansac)



def findParamsUsingElastic(normlzdSensMatrix, normlzdWeightedSensMatrix, \
                 defaultBiasesCol, normMetricValsCol, metricsWeights, \
                 magParamValsRow, defaultParamValsOrigRow, \
                 normlzdCurvMatrix,
                 beVerbose):

    import numpy as np
    from sklearn.linear_model import ElasticNet, ElasticNetCV
    from sklearn.linear_model import Lasso, LassoCV
    import pdb

    #regr = ElasticNet(fit_intercept=True, random_state=0, tol=1e-10, l1_ratio=0.5, alpha=0.01)
    #regr =Lasso(fit_intercept=True, random_state=0, tol=1e-10, alpha=0.01) # don't fit intercept!;use line below
    regr = Lasso(fit_intercept=False, random_state=0, tol=1e-10, alpha=0.01)
    #regr = LassoCV(fit_intercept=True, random_state=0, eps=1e-5, tol=1e-10, cv=metricsWeights.size)
    #print( "alpha_ = ", regr.alpha_ )
    regr.fit(normlzdWeightedSensMatrix, -metricsWeights * defaultBiasesCol / np.abs(normMetricValsCol) )
    #regr.fit(normlzdSensMatrix, -defaultBiasesCol / np.abs(normMetricValsCol) )

    defaultBiasesApproxElastic = np.transpose( np.atleast_2d(regr.predict(normlzdWeightedSensMatrix)) ) \
                          * np.reciprocal(metricsWeights) * np.abs(normMetricValsCol)
    dnormlzdParamsSolnElastic = np.transpose( np.atleast_2d(regr.coef_) )
    dparamsSolnElastic = dnormlzdParamsSolnElastic * np.transpose(magParamValsRow)
    paramsSolnElastic = np.transpose(defaultParamValsOrigRow) + dparamsSolnElastic

    if beVerbose:
        print( "paramsSolnElastic = ", paramsSolnElastic )
        print( "dparamsSolnElastic = ", dparamsSolnElastic )

    #pdb.set_trace()

    # If the solution were perfect, this variable would equal
    #     the normalized, weighted right-hand side.
    defaultBiasesApproxElasticNonlin = \
            normlzdWeightedSensMatrix @ dnormlzdParamsSolnElastic \
                        * np.reciprocal(metricsWeights) * np.abs(normMetricValsCol) \
            + 0.5 * normlzdCurvMatrix @ (dnormlzdParamsSolnElastic**2) * np.abs(normMetricValsCol)

    #pdb.set_trace()

    return (defaultBiasesApproxElastic, defaultBiasesApproxElasticNonlin, \
            dnormlzdParamsSolnElastic, paramsSolnElastic)







if __name__ == '__main__':
    main()
#        sensMatrixDashboard.run_server(debug=True)
