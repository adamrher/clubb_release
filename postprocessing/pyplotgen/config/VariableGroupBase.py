"""
:author: Nicolas Strike
:date: Mid 2019
"""
from netCDF4 import Dataset

import numpy as np

from src.Panel import Panel
from src.VariableGroup import VariableGroup


class VariableGroupBase(VariableGroup):
    """
    This is a panel group used for testing the functionality of pyplotgen.
    It contains a set of common panels being used for representing the majority
    of panels.
    """

    def __init__(self, case, clubb_datasets=None, les_dataset=None, coamps_dataset=None, r408_dataset=None,
                 hoc_dataset=None, cam_datasets=None,
                 e3sm_datasets=None, sam_datasets=None, wrf_datasets=None):
        """

        :param clubb_datasets:
        :param case:
        :param les_dataset:
        """
        self.name = "base variables"

        corr_w_chi_i_lines = [
            {'var_names': ['corr_w_chi_1'], 'legend_label': 'PDF comp. 1'},
            {'var_names': ['corr_w_chi_2'], 'legend_label': 'PDF comp. 2'},
        ]

        corr_chi_eta_i_lines = [
            {'var_names': ['corr_chi_eta_1'], 'legend_label': 'PDF comp. 1'},
            {'var_names': ['corr_chi_eta_2'], 'legend_label': 'PDF comp. 2'},
        ]

        self.variable_definitions = [
            {'var_names':
                {
                    'clubb': ['thlm'],
                    'sam': [self.getThlmSamCalc, 'THETAL', 'THETA'],
                    'coamps': ['thlm'],
                    'r408': ['thlm'],
                    'hoc': ['thlm'],
                    'e3sm': ['thlm'],
                    'cam': ['thlm'],
                    'wrf': ['thlm'],
                },
                # 'sam_calc': self.getThlmSamCalc,
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['rtm'],
                    'sam': [self.getRtmSamCalc],
                    'coamps': ['qtm', 'rtm'],
                    'r408': ['rtm'],
                    'hoc': ['rtm'],
                    'e3sm': ['rtm'],
                    'cam': ['rtm'],
                    'wrf': ['rtm'],
                },
                # 'sam_calc': self.getRtmSamCalc,
                'sci_scale': -3,
            },
            {'var_names':
                {
                    'clubb': ['wpthlp'],
                    'sam': [self.getWpthlpSamCalc, 'WPTHLP'],
                    'coamps': ['wpthlp'],
                    'r408': ['wpthlp'],
                    'hoc': ['wpthlp'],
                    'e3sm': ['wpthlp'],
                    'cam': ['wpthlp'], # WPTHLP_CLUBB / (1 .* 1004)
                    'wrf': ['wpthlp'],
                },
                # 'sam_calc': self.getWpthlpSamCalc,
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['wprtp'],
                    'sam': [self.getWprtpSamCalc, 'WPRTP'],
                    'coamps': ['wpqtp', 'wprtp'],
                    'r408': ['wprtp'],
                    'hoc': ['wprtp'],
                    'e3sm': ['wprtp'],
                    'cam': ['WPRTP_clubb', 'wprtp'],
                    'wrf': ['wprtp'],
                },
                # 'sam_calc': self.getWprtpSamCalc,
                'sci_scale': -4,
            },
            {'var_names':
                {
                    'clubb': ['cloud_frac'],
                    'sam': ['CLD_FRAC_CLUBB', 'CLD'],
                    'coamps': ['cf'],
                    'r408': ['cloud_frac', 'cf'],
                    'hoc': ['cloud_frac', 'cf'],
                    'e3sm': ['cloud_frac'],
                    'cam': ['CLOUD', 'cloud_frac'],
                    'wrf': ['cloud_frac'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['rcm'],
                    'sam': ['QCL'],
                    'coamps': ['qcm', 'rcm'],
                    'r408': ['rcm'],
                    'hoc': ['rcm'],
                    'e3sm': ['rcm'],
                    'cam': ['CLDLIQ', 'rcm'],
                    'wrf': ['rcm'],
                },
                'sam_conv_factor': 1 / 1000,
                'sci_scale': -5,
            },
            {'var_names':
                {
                    'clubb': ['wp2', 'W2'],
                    'sam': [self.get_wp2_sam_calc, 'W2', 'WP2'],
                    'coamps': ['wp2', 'W2'],
                    'r408': ['wp2'],
                    'hoc': ['wp2'],
                    'e3sm': ['wp2'],
                    'cam': ['WP2_CLUBB', 'wp2'],
                    'wrf': ['wp2'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['wp3'],
                    'sam': [self.get_wp3_sam_calc, 'wp3', 'W3', 'WP3'],
                    'coamps': ['wp3', 'W3', 'WP3'],
                    'r408': ['wp3'],
                    'hoc': ['wp3'],
                    'e3sm': ['wp3'],
                    'cam': ['WP3_CLUBB', 'wp3'],
                    'wrf': ['wp3'],
                },
                'sci_scale': 0,
                'axis_title': "wp3",
            },
            {'var_names':
                {
                    'clubb': ['thlp2'],
                    'sam': [self.get_thlp2_sam_calc, 'THLP2', 'TL2'],
                    'coamps': ['thlp2'],
                    'r408': ['thlp2'],
                    'hoc': ['thlp2'],
                    'e3sm': ['thlp2'],
                    'cam': ['THLP2_CLUBB', 'thlp2'],
                    'wrf': ['thlp2'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['rtp2'],
                    'sam': [self.getRtp2SamCalc, 'RTP2'],
                    'coamps': ['qtp2'],
                    'r408': ['rtp2'],
                    'hoc': ['rtp2'],
                    'e3sm': ['rtp2'],
                    'cam': ['RTP2_CLUBB', 'rtp2'],
                    'wrf': ['rtp2'],
                },
                # 'sam_calc': self.getRtp2SamCalc,
                'sci_scale': -7,
            },
            {'var_names':
                {
                    'clubb': ['rtpthlp'],
                    'sam': ['RTPTHLP_SGS', 'RTPTHLP', 'TQ'],
                    'coamps': ['qtpthlp', 'rtpthlp'],
                    'r408': ['rtpthlp'],
                    'hoc': ['rtpthlp'],
                    'e3sm': ['rtpthlp'],
                    'cam': ['rtpthlp'],
                    'wrf': ['rtpthlp'],
                },
                'sci_scale': -4,
            },
            {'var_names':
                {
                    'clubb': ['rtp3'],
                    'sam': [self.getRtp3SamCalc, 'RTP3'],
                    'coamps': ['qtp3', 'rtp3'],
                    'r408': ['rtp3'],
                    'hoc': ['rtp3'],
                    'e3sm': ['rtp3'],
                    'cam': ['rtp3'],
                    'wrf': ['rtp3'],
                },
                # 'sam_calc': self.getRtp3SamCalc,
                'sci_scale': -9,
            },
            {'var_names':
                {
                    'clubb': ['thlp3'],
                    'sam': ['THLP3'],
                    'coamps': ['thlp3'],
                    'r408': ['thlp3'],
                    'hoc': ['thlp3'],
                    'e3sm': ['thlp3'],
                    'cam': ['thlp3'],
                    'wrf': ['thlp3'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['Skw_zt'],
                    'sam': [self.getSkwZtLesCalc,'Skw_zt'],
                    'coamps': [self.getSkwZtLesCalc, 'Skw_zt'],
                    'r408': ['Skw_zt'],
                    'hoc': ['Skw_zt'],
                    'e3sm': ['Skw_zt'],
                    'cam': ['Skw_zt'],
                    'wrf': ['Skw_zt'],
                },
                # 'sam_calc': self.getSkwZtLesCalc,
                # 'coamps_calc': self.getSkwZtLesCalc,
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['Skrt_zt'],
                    'sam': [self.getSkrtZtLesCalc,'Skrt_zt'],
                    'coamps': [self.getSkrtZtLesCalc, 'Skrt_zt'],
                    'r408': ['Skrt_zt'],
                    'hoc': ['Skrt_zt'],
                    'e3sm': ['Skrt_zt'],
                    'cam': ['Skrt_zt'],
                    'wrf': ['Skrt_zt'],
                },
                # 'sam_calc': self.getSkrtZtLesCalc,
                # 'coamps_calc': self.getSkrtZtLesCalc,
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['Skthl_zt'],
                    'sam': [self.getSkthlZtLesCalc,'Skthl_zt'],
                    'coamps': [self.getSkthlZtLesCalc, 'Skthl_zt'],
                    'r408': ['Skthl_zt'],
                    'hoc': ['Skthl_zt'],
                    'e3sm': ['Skthl_zt'],
                    'cam': ['Skthl_zt'],
                    'wrf': ['Skthl_zt'],
                },
                # 'sam_calc': self.getSkthlZtLesCalc, 'coamps_calc': self.getSkthlZtLesCalc,
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['wm', 'wlsm'],
                    'sam': ['WOBS', 'WM'],
                    'coamps': ['wlsm', 'wm'],
                    'r408': ['wm'],
                    'hoc': ['wm'],
                    'e3sm': ['wm'],
                    'cam': ['wm'], # -OMEGA /(9.81.*1)
                    'wrf': ['wm', 'wlsm'],
                },
                'sci_scale': -4,
            },
            {'var_names':
                {
                    'clubb': ['um'],
                    'sam': ['U'],
                    'coamps': ['um'],
                    'r408': ['um'],
                    'hoc': ['um'],
                    'e3sm': ['um'],
                    'cam': ['U','um'],
                    'wrf': ['um'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['vm'],
                    'sam': ['V'],
                    'coamps': ['vm'],
                    'r408': ['vm'],
                    'hoc': ['vm'],
                    'e3sm': ['vm'],
                    'cam': ['V', 'vm'],
                    'wrf': ['vm'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['upwp'],
                    'sam': [self.get_upwp_sam_calc, 'UW'],
                    'coamps': [self.getUwCoampsData, 'upwp'],
                    'r408': ['upwp'],
                    'hoc': ['upwp'],
                    'e3sm': ['upwp'],
                    'cam': ['UPWP_CLUBB', 'upwp'],
                    'wrf': ['upwp'],
                },
                # 'coamps_calc': self.getUwCoampsData,
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['vpwp'],
                    'sam': [self.get_vpwp_sam_calc, 'VW'],
                    'coamps': [self.getVwCoampsData, 'vpwp'],
                    'r408': ['vpwp'],
                    'hoc': ['vpwp'],
                    'e3sm': ['vpwp'],
                    'cam': ['VPWP_CLUBB', 'vpwp'],
                    'wrf': ['vpwp'],
                },
                # 'coamps_calc': self.getVwCoampsData,
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['up2'],
                    'sam': [self.get_up2_sam_calc, 'U2'],
                    'coamps': ['up2'],
                    'r408': ['up2'],
                    'hoc': ['up2'],
                    'e3sm': ['up2'],
                    'cam': ['UU', 'up2'],
                    'wrf': ['up2'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['vp2'],
                    'sam': [self.get_vp2_sam_calc, 'V2'],
                    'coamps': ['vp2'],
                    'r408': ['vp2'],
                    'hoc': ['vp2'],
                    'e3sm': ['vp2'],
                    'cam': ['VV', 'vp2'],
                    'wrf': ['vp2'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['rcp2'],
                    'sam': ['QC2'],
                    'coamps': ['qcp2', 'rcp2', 'rlp2'],
                    'r408': ['rcp2'],
                    'hoc': ['rcp2'],
                    'e3sm': ['rcp2'],
                    'cam': ['rcp2'],
                    'wrf': ['rcp2'],
                },
                'sam_conv_factor': 1 / 10 ** 6,
                'sci_scale': -8,
            },
            {'var_names':
                {
                    'clubb': ['lwp'],
                    'sam': ['CWP'],
                    'coamps': ['lwp'],
                    'r408': ['lwp'],
                    'hoc': ['lwp'],
                    'e3sm': ['lwp'],
                    'cam': ['TGCLDLWP', 'lwp'],
                    'wrf': ['lwp'],
                },
                'type': Panel.TYPE_TIMESERIES,
                'sam_conv_factor': 1 / 1000,
            },
            {'var_names':
                {
                    'clubb': ['wp2_vert_avg'],
                    'sam': ['W2_VERT_AVG'],
                    'coamps': ['wp2_vert_avg'],
                    'r408': ['wp2_vert_avg'],
                    'hoc': ['wp2_vert_avg'],
                    'e3sm': ['wp2_vert_avg'],
                    'cam': ['wp2_vert_avg'],
                    'wrf': ['wp2_vert_avg'],
                },
                'type': Panel.TYPE_TIMESERIES,
            },
            {'var_names':
                {
                    'clubb': ['tau_zm'],
                    'sam': ['tau_zm'],
                    'coamps': ['tau_zm'],
                    'r408': ['tau_zm'],
                    'hoc': ['tau_zm'],
                    'e3sm': ['tau_zm'],
                    'cam': ['tau_zm'],
                    'wrf': ['tau_zm'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['Lscale'],
                    'sam': ['Lscale'],
                    'coamps': ['Lscale'],
                    'r408': ['Lscale'],
                    'hoc': ['Lscale'],
                    'e3sm': ['Lscale'],
                    'cam': ['Lscale'],
                    'wrf': ['Lscale'],
                },
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['wpthvp'],
                    'sam': [self.getWpthvpSamCalc,'WPTHVP'],
                    'coamps': ['wpthvp'],
                    'r408': ['wpthvp'],
                    'hoc': ['wpthvp'],
                    'e3sm': ['wpthvp'],
                    'cam': ['WPTHVP_CLUBB', 'wpthvp'],
                    'wrf': ['wpthvp'],
                },
                # 'sam_calc': self.getWpthvpSamCalc,
            },
            {'var_names':
                {
                    'clubb': ['radht'],
                    'sam': ['RADQR'],
                    'coamps': ['radht'],
                    'r408': ['radht'],
                    'hoc': ['radht'],
                    'e3sm': ['radht'],
                    'cam': ['radht'],
                    'wrf': ['radht'],
                },
                'sam_conv_factor': 1 / 86400,
            },
            {'var_names':
                {
                    'clubb': ['rtpthvp'],
                    'sam': ['RTPTHVP'],
                    'coamps': ['qtpthvp', 'rtpthvp'],
                    'r408': ['rtpthvp'],
                    'hoc': ['rtpthvp'],
                    'e3sm': ['rtpthvp'],
                    'cam': ['rtpthvp'],
                    'wrf': ['rtpthvp'],
                },
                'sci_scale': -5,
            },
            {'var_names':
                {
                    'clubb': ['corr_w_chi_i'],
                    'sam': ['corr_w_chi_i'],
                    'coamps': ['corr_w_chi_i'],
                    'r408': ['corr_w_chi_i'],
                    'hoc': ['corr_w_chi_i'],
                    'e3sm': ['corr_w_chi_i'],
                    'cam': ['corr_w_chi_i'],
                    'wrf': ['corr_w_chi_i'],
                },
                'lines': corr_w_chi_i_lines,
                'title': "Correlation of w and chi",
                'axis_title': "corr_w_chi_i [-]",
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['corr_chi_eta_i'],
                    'sam': ['corr_chi_eta_i'],
                    'coamps': ['corr_chi_eta_i'],
                    'r408': ['corr_chi_eta_i'],
                    'hoc': ['corr_chi_eta_i'],
                    'e3sm': ['corr_chi_eta_i'],
                    'cam': ['corr_chi_eta_i'],
                    'wrf': ['corr_chi_eta_i'],
                },
                'lines': corr_chi_eta_i_lines,
                'title': "Correlation of chi and eta",
                'axis_title': "corr_chi_eta_i [-]",
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': ['thlpthvp'],
                    'sam': ['thlpthvp', 'THLPTHVP'],
                    'coamps': ['thlpthvp'],
                    'r408': ['thlpthvp'],
                    'hoc': ['thlpthvp'],
                    'e3sm': ['thlpthvp'],
                    'cam': ['thlpthvp'],
                    'wrf': ['thlpthvp'],
                },
            },
            # TODO SAM output for these variables
            # TODO validate coamps output
            # TODO Fix output for these vars in some cases
            {'var_names':
                {
                    'clubb': [self.get_rc_coef_zm_X_wprcp_clubb_line, 'rc_coef_zm * wprcp'],
                    'sam': [self.get_rc_coef_zm_X_wprcp_sam_calc, 'rc_coef_zm * wprcp'],
                    'coamps': [self.get_rc_coef_zm_X_wprcp_coamps_calc, 'rc_coef_zm * wprcp'],
                    'r408': ['rc_coef_zm * wprcp'],
                    'hoc': ['rc_coef_zm * wprcp'],
                    'e3sm': ['rc_coef_zm * wprcp'],
                    'cam': ['rc_coef_zm * wprcp'],
                    'wrf': ['rc_coef_zm * wprcp'],
                },
                'clubb_calc': self.get_rc_coef_zm_X_wprcp_clubb_line,
                'sam_calc': self.get_rc_coef_zm_X_wprcp_sam_calc,
                'coamps_calc': self.get_rc_coef_zm_X_wprcp_coamps_calc,
                'title': 'Contribution of Cloud Water Flux to wpthvp',
                'axis_title': 'rc_coef_zm * wprcp [K m/s]',
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': [self.get_rc_coef_zm_X_thlprcp_clubb_calc, 'rc_coef_zm * thlprcp'],
                    'sam': [self.get_rc_coef_zm_X_thlprcp_sam_calc,'rc_coef_zm * thlprcp'],
                    'coamps': [self.get_rc_coef_zm_X_thlprcp_coamps_calc, 'rc_coef_zm * thlprcp'],
                    'r408': ['rc_coef_zm * thlprcp'],
                    'hoc': ['rc_coef_zm * thlprcp'],
                    'e3sm': ['rc_coef_zm * thlprcp'],
                    'cam': ['rc_coef_zm * thlprcp'],
                    'wrf': ['rc_coef_zm * thlprcp'],
                },
                'sam_calc': self.get_rc_coef_zm_X_thlprcp_sam_calc,
                'coamps_calc': self.get_rc_coef_zm_X_thlprcp_coamps_calc,
                'clubb_calc': self.get_rc_coef_zm_X_thlprcp_clubb_calc,
                'title': 'Contribution of Cloud Water Flux to thlpthvp',
                'axis_title': 'rc_coef_zm * thlprcp [K^2]',
                'sci_scale': 0,
            },
            {'var_names':
                {
                    'clubb': [self.get_rc_coef_zm_X_rtprcp_clubb_calc, 'rc_coef_zm * rtprcp'],
                    'sam': [self.get_rc_coef_zm_X_rtprcp_sam_calc,'rc_coef_zm * rtprcp'],
                    'coamps': [self.get_rc_coef_zm_X_rtprcp_coamps_calc, 'rc_coef_zm * rtprcp'],
                    'r408': ['rc_coef_zm * rtprcp'],
                    'hoc': ['rc_coef_zm * rtprcp'],
                    'e3sm': ['rc_coef_zm * rtprcp'],
                    'cam': ['rc_coef_zm * rtprcp'],
                    'wrf': ['rc_coef_zm * rtprcp'],
                },
                'sam_calc': self.get_rc_coef_zm_X_rtprcp_sam_calc,
                'coamps_calc': self.get_rc_coef_zm_X_rtprcp_coamps_calc,
                'clubb_calc': self.get_rc_coef_zm_X_rtprcp_clubb_calc,
                'title': 'Contribution of Cloud Water Flux to rtpthvp',
                'axis_title': 'rc_coef_zm * rtprcp [kg/kg K]',
                'sci_scale': -4
            },
            {'var_names':
                {
                    'clubb': [self.get_rc_coef_X_wp2rcp_clubb_calc, 'rc_coef_zm * wp2rcp'],
                    'sam': [self.get_rc_coef_X_wp2rcp_sam_calc,'rc_coef_zm * wp2rcp'],
                    'coamps': [self.get_rc_coef_X_wp2rcp_coamps_calc, 'rc_coef_zm * wp2rcp'],
                    'r408': ['rc_coef_zm * wp2rcp'],
                    'hoc': ['rc_coef_zm * wp2rcp'],
                    'e3sm': ['rc_coef_zm * wp2rcp'],
                    'cam': ['rc_coef_zm * wp2rcp'],
                    'wrf': ['rc_coef_zm * wp2rcp'],
                },
                'sam_calc': self.get_rc_coef_X_wp2rcp_sam_calc,
                'coamps_calc': self.get_rc_coef_X_wp2rcp_coamps_calc,
                'clubb_calc': self.get_rc_coef_X_wp2rcp_clubb_calc,
                'title': 'Cloud water contribution to wp2thvp',
                'axis_title': 'rc_coef * wp2rcp [m^2/s^2 K]',
                'sci_scale': 0
            },

            # TODO corr chi 2's,
        ]

        # Call ctor of parent class
        super().__init__(case, clubb_datasets=clubb_datasets, sam_datasets=sam_datasets, les_dataset=les_dataset,
                         coamps_dataset=coamps_dataset, r408_dataset=r408_dataset, cam_datasets=cam_datasets,
                         hoc_dataset=hoc_dataset, e3sm_datasets=e3sm_datasets, wrf_datasets=wrf_datasets)

    def getThlmSamCalc(self, dataset_override=None):
        """
        Calculates thlm values from sam output using
        the following equation
        (THETAL + 2500.4.*(THETA/TABS).*(QI/1000))
        :return: requested variable dependent_data in the form of a list.
                Returned dependent_data is already cropped to the appropriate min,max indices
        """
        # z,z, dataset = self.getVarForCalculations('z', self.les_dataset)
        dataset = self.les_dataset
        if dataset_override is not None:
            dataset = dataset_override
        thetal, indep, dataset = self.getVarForCalculations('THETAL', dataset)
        theta, indep, dataset = self.getVarForCalculations('THETA', dataset)
        tabs, indep, dataset = self.getVarForCalculations('TABS', dataset)
        qi, indep, dataset = self.getVarForCalculations('QI', dataset)

        thlm = thetal + (2500.4 * (theta / tabs) * (qi / 1000))
        return thlm, indep

    def getRtmSamCalc(self, dataset_override=None):
        """
        Calculates rtm values from sam output using
        the following equation
        (QT-QI) / 1000
        :return: requested variable dependent_data in the form of a list.
        Returned dependent_data is already cropped to the appropriate min,max indices
        """
        dataset = self.les_dataset
        if dataset_override is not None:
            dataset = dataset_override
        # z,z, dataset = self.getVarForCalculations('z', self.les_dataset)
        qt, indep, dataset = self.getVarForCalculations('QT', dataset)
        qi, indep, dataset = self.getVarForCalculations('QI', dataset)

        rtm = (qt - qi) / 1000
        return rtm, indep

    def getSkwZtLesCalc(self, dataset_override=None):
        """
        Calculates Skw_zt values from sam output using
        the following equation
        WP3 / (WP2 + 1.6e-3)**1.5
        :return: requested variable dependent_data in the form of a list.
                Returned dependent_data is already cropped to the appropriate min,max indices
        """
        dataset = None
        if self.les_dataset is not None:
            dataset = self.les_dataset
        if self.coamps_dataset is not None:
            dataset = self.coamps_dataset['sm']
        if dataset_override is not None:
            dataset = dataset_override

        wp3, indep, dataset = self.getVarForCalculations(['WP3', 'W3', 'wp3'], dataset)
        wp2, indep, dataset = self.getVarForCalculations(['WP2', 'W2', 'wp2'], dataset)

        skw_zt = wp3 / (wp2 + 1.6e-3) ** 1.5

        return skw_zt, indep

    def getSkrtZtLesCalc(self, dataset_override=None):
        """
        Calculates Skrt_zt values from sam output using
        the following equation
         sam eqn 
            RTP3 / (RTP2 + 4e-16)**1.5
         coamps eqn 
            qtp3 / (qtp2 + 4e-16)**1.5
            rtp3 / (rtp2 + 4e-16)**1.5
        :return: requested variable dependent_data in the form of a list.
                Returned dependent_data is already cropped to the appropriate min,max indices
        """
        dataset = None
        if self.les_dataset is not None:
            dataset = self.les_dataset

        if self.coamps_dataset is not None:
            dataset = self.coamps_dataset['sm']
        if dataset_override is not None:
            dataset = dataset_override
        rtp3, indep, dataset = self.getVarForCalculations(['RTP3', 'qtp3', 'rtp3'], dataset)
        rtp2, indep, dataset = self.getVarForCalculations(['RTP2', 'qtp2', 'rtp2', 'rlp2'], dataset)

        skrt_zt = rtp3 / (rtp2 + 4e-16) ** 1.5

        return skrt_zt, indep

    def getSkthlZtLesCalc(self, dataset_override=None):
        """
        Calculates Skthl_zt values from sam output using
        the following equation
        sam THLP3 / (THLP2 + 4e-4)**1.5
        coamps eqn thlp3 / (thlp2 + 4e-4)**1.5
        :return: requested variable dependent_data in the form of a list.
                Returned dependent_data is already cropped to the appropriate min,max indices
        """
        dataset = None
        if self.les_dataset is not None:
            dataset = self.les_dataset

        if self.coamps_dataset is not None:
            dataset = self.coamps_dataset['sm']

        if dataset_override is not None:
            dataset = dataset_override

            # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        thlp3, indep, dataset = self.getVarForCalculations(['THLP3', 'thlp3'], dataset)
        thlp2, indep, dataset = self.getVarForCalculations(['THLP2', 'thlp2'], dataset)

        skthl_zt = thlp3 / (thlp2 + 4e-4)**1.5
        return skthl_zt, indep

    def getWpthlpSamCalc(self, dataset_override=None):
        """
        This gets called if WPTHLP isn't outputted in an nc file as a backup way of gathering the dependent_data
        for plotting.
        WPTHLP = (TLFLUX) / (RHO * 1004) + WPTHLP_SGS
        :return:
        """
        dataset = None
        if self.les_dataset is not None:
            dataset = self.les_dataset
        if dataset_override is not None:
            dataset = dataset_override
        tlflux, indep, dataset = self.getVarForCalculations(['TLFLUX'], dataset)
        rho, indep, dataset = self.getVarForCalculations(['RHO'], dataset)
        wpthlp_sgs, indep, dataset = self.getVarForCalculations(['WPTHLP_SGS'], dataset)

        wpthlp = (tlflux / (rho * 1004)) + wpthlp_sgs

        return wpthlp, indep

    def getWprtpSamCalc(self, dataset_override=None):
        """
        This gets called if WPRTP isn't outputted in an nc file as a backup way of gathering the dependent_data
        for plotting.
        WPRTP = (QTFLUX) / (RHO * 2.5104e+6) + WPRTP_SGS
        WPRTP = (QTFLUX) / (RHO * 2.5104e+6)
        :return:
        """
        dataset = None
        if self.les_dataset is not None:
            dataset = self.les_dataset
        if dataset_override is not None:
            dataset = dataset_override
        qtflux, indep, dataset = self.getVarForCalculations(['QTFLUX'], dataset)
        rho, indep, dataset = self.getVarForCalculations(['RHO'], dataset)
        wprtp_sgs, indep, dataset = self.getVarForCalculations(['WPRTP_SGS'], dataset)

        wprtp = qtflux / (rho * 2.5104e+6) + wprtp_sgs
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], self.les_dataset)
        return wprtp, indep

    def getWpthvpSamCalc(self, dataset_override=None):
        """
        This gets called if WPTHVP isn't outputted in an nc file as a backup way of gathering the dependent_data
        for plotting.
        WPTHVP =  (TVFLUX) / ( RHO * 1004)
        :return:
        """
        dataset = None
        if self.les_dataset is not None:
            dataset = self.les_dataset
        if dataset_override is not None:
            dataset = dataset_override
        tvflux, indep, dataset = self.getVarForCalculations(['TVFLUX'], dataset)
        rho, indep, dataset = self.getVarForCalculations(['RHO'], dataset)
        wpthvp = tvflux / (rho * 1004)
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], self.les_dataset)
        return wpthvp, indep

    def getRtp2SamCalc(self, dataset_override=None):
        """
        This gets called if RTP2 isn't outputted in an nc file as a backup way of gathering the dependent_data
        for plotting.
                (QT2 / 1e+6) + RTP2_SGS
        THLP2 = QT2 / 1e+6
        :return:
        """
        dataset = None
        if self.les_dataset is not None:
            dataset = self.les_dataset
        if dataset_override is not None:
            dataset = dataset_override
        QT2, indep, dataset = self.getVarForCalculations(['QT2'], dataset)
        RTP2_SGS, indep, dataset = self.getVarForCalculations(['RTP2_SGS'], dataset)
        rtp2 = (QT2 / 1e+6) + RTP2_SGS
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], self.les_dataset)
        return rtp2, indep

    def getRtp3SamCalc(self, dataset_override=None):
        """
        Caclulates Rtp3 output
        rc_coef_zm .* rtprcp

        :return:
        """
        rtp3 = None
        z = None
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.les_dataset
        if isinstance(dataset, Dataset):
            dataset = {'temp': dataset}
        for dataset in dataset.values():
            if 'rc_coef_zm' in dataset.variables.keys() and 'rtprcp' in dataset.variables.keys():
                rc_coef_zm, indep, dataset = self.getVarForCalculations('rc_coef_zm', dataset)
                rtprcp, indep, dataset = self.getVarForCalculations('rtprcp', dataset)
                rtp3 = rc_coef_zm * (rtprcp)

            elif 'QCFLUX' in dataset.variables.keys():
                QCFLUX, indep, dataset = self.getVarForCalculations('QCFLUX', dataset)
                RHO, indep, dataset = self.getVarForCalculations('RHO', dataset)
                PRES, indep, dataset = self.getVarForCalculations('PRES', dataset)
                THETAV, indep, dataset = self.getVarForCalculations('THETAV', dataset)
                rtp3 = ((QCFLUX) / (RHO * 2.5104e+6)) * (
                        2.5e6 / (1004.67 * ((PRES / 1000) ** (287.04 / 1004.67))) - 1.61 * THETAV)
            # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        return rtp3, indep

    def get_rc_coef_zm_X_wprcp_clubb_line(self, dataset_override=None):
        """
        Calculates the Contribution of Cloud Water Flux
        to wpthvp using the equation
        rc_coef_zm .* wprcp
        :return: Line representing rc_coef_zm .* wprcp
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.clubb_datasets['zm']
        rc_coef_zm, indep, dataset = self.getVarForCalculations('rc_coef_zm', dataset)
        wprcp, indep, dataset = self.getVarForCalculations('wprcp', dataset)
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        output = rc_coef_zm * wprcp
        return output, indep

    def get_rc_coef_zm_X_wprcp_sam_calc(self, dataset_override=None):
        """
        Calculates the Contribution of Cloud Water Flux
        to wpthvp for SAM using the equation
        sam eqn
        WPRCP                          * (2.5e6 / (1004.67*((PRES / 1000)**(287.04/1004.67))) - 1.61*THETAV)
        ((QCFLUX) / (RHO * 2.5104e+6)) * (2.5e6 / (1004.67*((PRES / 1000)**(287.04/1004.67))) - 1.61*THETAV)

        :return:
        """

        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.les_dataset
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        WPRCP, indep, dataset = self.getVarForCalculations('WPRCP', dataset)
        QCFLUX, indep, dataset = self.getVarForCalculations('QCFLUX', dataset)
        RHO, indep, dataset = self.getVarForCalculations('RHO', dataset)
        PRES, indep, dataset = self.getVarForCalculations('PRES', dataset)
        THETAV, indep, dataset = self.getVarForCalculations('THETAV', dataset)


        # Check if WPRCP contains non-zero values
        wprcp_is_zeroes = (np.nanmin(WPRCP) == 0.0 and np.nanmax(WPRCP) == 0.0)
        if wprcp_is_zeroes:
            output = ((QCFLUX) / (RHO * 2.5104e+6)) * (2.5e6 / (1004.67 * ((PRES / 1000) ** (287.04 / 1004.67))) - 1.61 * THETAV)
        else:
            output = WPRCP * (2.5e6 / (1004.67 * ((PRES / 1000) ** (287.04 / 1004.67))) - 1.61 * THETAV)

        return output, indep

    # rc_coef_zm. * thlprcp
    def get_rc_coef_zm_X_thlprcp_clubb_calc(self, dataset_override=None):
        """
        Calculates the Contribution of Cloud Water Flux
        to thlprcp using the equation
        rc_coef_zm * thlprcp
        :return: Line representing rc_coef_zm .* thlprcp
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.clubb_datasets['zm']
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        rc_coef_zm, indep, dataset = self.getVarForCalculations('rc_coef_zm', dataset)
        thlprcp, indep, dataset = self.getVarForCalculations('thlprcp', dataset)

        output = rc_coef_zm * thlprcp
        return output, indep

    def get_rc_coef_zm_X_rtprcp_clubb_calc(self, dataset_override=None):
        """
        Calculates the Contribution of Cloud Water Flux
        to rtprcp using the equation
        rc_coef_zm * rtprcp
        :return: Line representing rc_coef_zm .* rtprcp
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.clubb_datasets['zm']
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        rc_coef_zm, indep, dataset = self.getVarForCalculations('rc_coef_zm', dataset)
        rtprcp, indep, dataset = self.getVarForCalculations('rtprcp', dataset)

        output = rc_coef_zm * rtprcp
        return output, indep

    def getUwCoampsData(self, dataset_override=None):
        """
        coamps eqn upwp = wpup + wpup_sgs

         :return: requested variable dependent_data in the form of a list. Returned dependent_data is already
         cropped to the appropriate min,max indices
        """
        if dataset_override is not None:
            dataset = dataset_override['sw']
        else:
            dataset = self.coamps_dataset['sw']
        wpup, indep, dataset = self.getVarForCalculations('wpup', dataset)
        wpup_sgs, indep, dataset = self.getVarForCalculations('wpup_sgs', dataset)

        upwp = wpup + wpup_sgs
        return upwp, indep

    def getVwCoampsData(self, dataset_override=None):
        """
        coamps eqn vpwp = wpvp + wpvp_sgs

         :return: requested variable dependent_data in the form of a list. Returned dependent_data is already
         cropped to the appropriate min,max indices
        """
        if dataset_override is not None:
            dataset = dataset_override['sw']
        else:
            dataset = self.coamps_dataset['sw']
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        wpvp, indep, dataset = self.getVarForCalculations('wpvp', dataset)
        wpvp_sgs, indep, dataset = self.getVarForCalculations('wpvp_sgs', dataset)

        vpwp = wpvp + wpvp_sgs
        return vpwp, indep

    def get_rc_coef_zm_X_wprcp_coamps_calc(self, dataset_override=None):
        """
        coamps eqn's
        thlpqcp * (2.5e6 / (1004.67 * ex0)                             - 1.61 * thvm)
        wpqcp   * (2.5e6 / (1004.67 * ex0)                             - 1.61 * thvm)
        wprlp   * (2.5e6 / (1004.67 * (( p /1.0e5)**(287.04/1004.67))) - 1.61 * thvm)
        wprlp   * (2.5e6 / (1004.67 * (( p /1.0e5)**(287.04/1004.67))) - 1.61 * thvm)

        :param dataset_override:
        :return:
        """
        dataset = self.coamps_dataset['sw']
        if dataset_override is not None:
            dataset = dataset_override['sw']

        wprlp, indep, dataset = self.getVarForCalculations(['thlpqcp', 'wpqcp', 'wprlp'], dataset)
        ex0, indep, dataset = self.getVarForCalculations(['ex0'], dataset)
        p, indep, dataset = self.getVarForCalculations('p', dataset)
        thvm, indep, dataset = self.getVarForCalculations('thvm', dataset)
        output1 = wprlp * (2.5e6 / (1004.67 * ex0) - 1.61 * thvm)
        output2 = wprlp * (2.5e6 / (1004.67 * ((p / 1.0e5) ** (287.04 / 1004.67))) - 1.61 * thvm)
        output = self.pickNonZeroOutput(output1, output2)
        return output, indep

    def get_rc_coef_zm_X_thlprcp_sam_calc(self, dataset_override=None):
        """
        sam eqn
        THLPRCP .* (2.5e6 / (1004.67*((PRES / 1000)**(287.04/1004.67))) - 1.61*THETAV)        :param dataset_override:
        :return:
        """
        dataset = self.sam_datasets
        if dataset_override is not None:
            dataset = dataset_override
        THLPRCP, indep, dataset = self.getVarForCalculations(['THLPRCP'], dataset)
        PRES, indep, dataset = self.getVarForCalculations('PRES', dataset)
        THETAV, indep, dataset = self.getVarForCalculations('THETAV', dataset)

        output = THLPRCP * (2.5e6 / (1004.67 * ((PRES / 1000) ** (287.04 / 1004.67))) - 1.61 * THETAV)
        return output, indep

    def get_rc_coef_zm_X_thlprcp_coamps_calc(self, dataset_override=None):
        """
        coamps eqn
        thlpqcp * (2.5e6 / (1004.67 * ex0)                             - 1.61*thvm)
        thlprlp * (2.5e6 / (1004.67 * (( p /1.0e5)**(287.04/1004.67))) - 1.61*thvm)

        :param dataset_override:
        :return:
        """
        dataset = self.coamps_dataset['sw']
        if dataset_override is not None:
            dataset = dataset_override
        thlpqcp, indep, dataset = self.getVarForCalculations(['thlpqcp'], dataset)
        ex0, indep, dataset = self.getVarForCalculations('ex0', dataset)
        thvm, indep, dataset = self.getVarForCalculations('thvm', dataset)

        thlprlp, indep, dataset = self.getVarForCalculations(['thlprlp'], dataset)
        p, indep, dataset = self.getVarForCalculations('p', dataset)

        output1 = thlpqcp * (2.5e6 / (1004.67 * ex0) - 1.61 * thvm)
        output2 = thlprlp * (2.5e6 / (1004.67 * (( p /1.0e5)**(287.04/1004.67))) - 1.61*thvm)
        output = self.pickNonZeroOutput(output1, output2)

        return output, indep

    def get_rc_coef_zm_X_rtprcp_coamps_calc(self, dataset_override=None):
        """
        coamp eqn
        qtpqcp * (2.5e6 / (1004.67*ex0)                           - 1.61*thvm)
        qtpqcp * (2.5e6 / (1004.67*ex0)                           - 1.61*thvm)
        rtprlp * (2.5e6 / (1004.67*((p/1.0e5)**(287.04/1004.67))) - 1.61*thvm)
        :param dataset_override:
        :return:
        """
        dataset = self.coamps_dataset['sm']
        if dataset_override is not None:
            dataset = dataset_override['sm']
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        qtpqcp, indep, dataset = self.getVarForCalculations(['qtpqcp', 'rtprcp'], dataset)
        ex0, indep, dataset = self.getVarForCalculations('ex0', dataset)
        thvm, indep, dataset = self.getVarForCalculations('thvm', dataset)

        rtprlp, indep, dataset = self.getVarForCalculations('rtprlp', dataset)
        p, indep, dataset = self.getVarForCalculations('p', dataset)

        output1 = qtpqcp * (2.5e6 / (1004.67 * ex0) - 1.61 * thvm)
        output2 = rtprlp * (2.5e6 / (1004.67*((p/1.0e5)**(287.04/1004.67))) - 1.61*thvm)
        output = self.pickNonZeroOutput(output1, output2)

        return output, indep

    def get_rc_coef_zm_X_rtprcp_sam_calc(self, dataset_override=None):
        """
        sam eqn
        RTPRCP * (2.5e6 / (1004.67*((PRES / 1000)**(287.04/1004.67))) - 1.61*THETAV)m)
        :param dataset_override:
        :return:
        """
        dataset = self.sam_datasets
        if dataset_override is not None:
            dataset = dataset_override
        # z,z, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], dataset)
        RTPRCP, indep, dataset = self.getVarForCalculations('RTPRCP', dataset)
        PRES, indep, dataset = self.getVarForCalculations('PRES', dataset)
        THETAV, indep, dataset = self.getVarForCalculations('THETAV', dataset)

        output = RTPRCP * (2.5e6 / (1004.67 * ((PRES / 1000) ** (287.04 / 1004.67))) - 1.61 * THETAV)
        return output, indep

    def get_rc_coef_X_wp2rcp_sam_calc(self, dataset_override=None):
        """
        WP2RCP * (2.5e6 / (1004.67*((PRES / 1000)^(287.04/1004.67))) - 1.61*THETAV)
        :param dataset_override:
        :return:
        """
        dataset = self.sam_datasets
        if dataset_override is not None:
            dataset = dataset_override['sam']
        WP2RCP, indep, dataset = self.getVarForCalculations('WP2RCP', dataset)
        PRES, indep, dataset = self.getVarForCalculations('PRES', dataset)
        THETAV, indep, dataset = self.getVarForCalculations('THETAV', dataset)

        output = WP2RCP * (2.5e6 / (1004.67 * ((PRES / 1000) ** (287.04 / 1004.67))) - 1.61 * THETAV)
        return output, indep

    def get_rc_coef_X_wp2rcp_clubb_calc(self, dataset_override=None):
        """

        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.clubb_datasets['zm']
        rc_coef, indep, dataset = self.getVarForCalculations('rc_coef', dataset)
        wp2rcp, indep, dataset = self.getVarForCalculations('wp2rcp', dataset)

        output = rc_coef * wp2rcp
        return output, indep

    def get_rc_coef_X_wp2rcp_coamps_calc(self, dataset_override=None):
        """
        wp2qcp * (2.5e6 / (1004.67 * ex0)                             - 1.61 * thvm)
        wp2rlp * (2.5e6 / (1004.67 * (( p /1.0e5)**(287.04/1004.67))) - 1.61 * thvm)
        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.clubb_datasets['zm']
        wp2qcp, indep, dataset = self.getVarForCalculations('wp2qcp', dataset)
        ex0, indep, dataset = self.getVarForCalculations('ex0', dataset)
        thvm, indep, dataset = self.getVarForCalculations('thvm', dataset)

        wp2rlp, indep, dataset = self.getVarForCalculations('wp2rlp', dataset)
        p, indep, dataset = self.getVarForCalculations('p', dataset)

        output1 = wp2qcp * (2.5e6 / (1004.67 * ex0) - 1.61 * thvm)
        output2 = wp2rlp * (2.5e6 / (1004.67 * (( p /1.0e5)**(287.04/1004.67))) - 1.61 * thvm)

        output = self.pickNonZeroOutput(output1, output2)

        return output, indep


    def get_wp2_sam_calc(self, dataset_override=None):
        """
        WP2_SGS + W2
        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.sam_datasets
        WP2_SGS, z, dataset = self.getVarForCalculations('WP2_SGS', dataset)
        W2, z, dataset = self.getVarForCalculations('W2', dataset)

        output = WP2_SGS + W2

        return output, z

    def get_wp3_sam_calc(self, dataset_override=None):
        """
        WP3_SGS + W3
        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.sam_datasets
        WP3_SGS, z, dataset = self.getVarForCalculations('WP3_SGS', dataset)
        W3, z, dataset = self.getVarForCalculations('W3', dataset)

        output = WP3_SGS + W3

        return output, z

    def get_thlp2_sam_calc(self, dataset_override=None):
        """
        TL2 + THLP2_SGS
        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.sam_datasets
        TL2, z, dataset = self.getVarForCalculations('TL2', dataset)
        THLP2_SGS, z, dataset = self.getVarForCalculations('THLP2_SGS', dataset)

        output = TL2 + THLP2_SGS

        return output, z

    def get_upwp_sam_calc(self, dataset_override=None):
        """
        UW + UPWP_SGS
        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.sam_datasets
        UW, z, dataset = self.getVarForCalculations('UW', dataset)
        UPWP_SGS, z, dataset = self.getVarForCalculations('UPWP_SGS', dataset)

        output = UW + UPWP_SGS

        return output, z

    def get_vpwp_sam_calc(self, dataset_override=None):
        """
        VW + VPWP_SGS
        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.sam_datasets
        VW, z, dataset = self.getVarForCalculations('VW', dataset)
        VPWP_SGS, z, dataset = self.getVarForCalculations('VPWP_SGS', dataset)

        output = VW + VPWP_SGS

        return output, z

    def get_up2_sam_calc(self, dataset_override=None):
        """
        UP2_SGS + U2
        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.sam_datasets
        U2, z, dataset = self.getVarForCalculations('U2', dataset)
        UP2_SGS, z, dataset = self.getVarForCalculations('UP2_SGS', dataset)

        output = UP2_SGS + U2

        return output, z

    def get_vp2_sam_calc(self, dataset_override=None):
        """
        VP2_SGS + V2
        :param dataset_override:
        :return:
        """
        if dataset_override is not None:
            dataset = dataset_override
        else:
            dataset = self.sam_datasets
        V2, z, dataset = self.getVarForCalculations('V2', dataset)
        VP2_SGS, z, dataset = self.getVarForCalculations('VP2_SGS', dataset)

        output = VP2_SGS + V2

        return output, z