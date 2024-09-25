"""
:author: Nicolas Strike
:date: Mid 2019
"""
from src.Panel import Panel
from src.VariableGroup import VariableGroup


class VariableGroupIceMP(VariableGroup):
    """

    """

    def __init__(self, case, clubb_datasets=None, sam_benchmark_dataset=None, sam_datasets=None,
                 coamps_benchmark_dataset=None, wrf_benchmark_dataset=None, 
                 r408_dataset=None, hoc_dataset=None, cam_datasets=None,
                 e3sm_datasets=None, wrf_datasets=None, priority_vars=False, background_rcm=False,
                 background_rcm_folder=None):
        """

        :param clubb_datasets:
        :param case:
        :param sam_benchmark_dataset:
        """
        self.name = "ice mp variables"
        self.variable_definitions = [
            {'var_names':
                {
                    'clubb': ['rim'],
                    'sam': ['QI', 'QCI'],
                    'coamps': ['rim', 'qim'],
                    'r408': ['rim'],
                    'hoc': ['rim'],
                    'e3sm': ['rim'],
                    'cam': ['CLDICE', 'rim'],
                    'wrf': ['rim'],
                },
                'sam_conv_factor': 1 / 1000,
            },
            {'var_names':
                {
                    'clubb': ['Nim'],
                    'sam': [self.getNimSamLine, 'Nim'],
                    'coamps': ['Nim', 'nim'],
                    'r408': ['Nim'],
                    'hoc': ['Nim'],
                    'e3sm': ['Nim'],
                    'cam': ['AWNI', 'Nim'],
                    'wrf': ['Nim'],
                },
                # 'sam_calc': self.getNimSamLine,
            },
            {'var_names':
                {
                    'clubb': ['rsm'],
                    'sam': ['QS', 'QPI'],
                    'coamps': ['rsm', 'qsm'],
                    'r408': ['rsm'],
                    'hoc': ['rsm'],
                    'e3sm': ['rsm'],
                    'cam': ['AQSNOW', 'rsm'],
                    'wrf': ['rsm'],
                },
                'sam_conv_factor': 1 / 1000,
            },
            {'var_names':
                {
                    'clubb': ['Nsm'],
                    'sam': [self.getNsmSamLine, 'Nsm'],
                    'coamps': ['Nsm'],
                    'r408': ['Nsm'],
                    'hoc': ['Nsm'],
                    'e3sm': ['Nsm'],
                    'cam': ['ANSNOW', 'Nsm'],
                    'wrf': ['Nsm'],
                },
                # 'sam_calc': self.getNsmSamLine,
            },
            {'var_names':
                {
                    'clubb': ['iwp'],
                    'sam': ['IWP'],
                    'coamps': ['iwp'],
                    'r408': ['iwp'],
                    'hoc': ['iwp'],
                    'e3sm': ['iwp'],
                    'cam': ['TGCLDIWP', 'iwp'],
                    'wrf': ['iwp'],
                },
                'type': Panel.TYPE_TIMESERIES, 'sam_conv_factor': 1 / 1000,
            },
            {'var_names':
                {
                    'clubb': ['swp'],
                    'sam': ['SWP'],
                    'coamps': ['swp'],
                    'r408': ['swp'],
                    'hoc': ['swp'],
                    'e3sm': ['swp'],
                    'cam': ['swp'],
                    'wrf': ['swp'],
                },
                'type': Panel.TYPE_TIMESERIES, 'sam_conv_factor': 1 / 1000,
            },
            {'var_names':
                {
                    'clubb': ['ice_supersat_frac'],
                    'sam': ['ice_supersat_frac'],
                    'coamps': ['ice_supersat_frac'],
                    'r408': ['ice_supersat_frac'],
                    'hoc': ['ice_supersat_frac'],
                    'e3sm': ['ice_supersat_frac'],
                    'cam': ['ice_supersat_frac'],
                    'wrf': ['ice_supersat_frac'],
                },
            },
            {'var_names':
                {
                    'clubb': ['Ngm'],
                    'sam': ['NG'],
                    'coamps': ['Ngm'],
                    'r408': ['Ngm'],
                    'hoc': ['Ngm'],
                    'e3sm': ['Ngm'],
                    'cam': ['Ngm'],
                    'wrf': ['Ngm'],
                },
                'sam_conv_factor': 10 ** 6,
                'axis_title': "Ngm [num/kg]"
            },
            {'var_names':
                {
                    'clubb': ['rgm'],
                    'sam': ['QG'],
                    'coamps': ['rgm', 'qgm'],
                    'r408': ['rgm'],
                    'hoc': ['rgm'],
                    'e3sm': ['rgm'],
                    'cam': ['rgm'],
                    'wrf': ['rgm'],
                },
                'sam_conv_factor': 1 / 1000,
            },
        ]

        # Call ctor of parent class
        super().__init__(case, clubb_datasets=clubb_datasets, sam_benchmark_dataset=sam_benchmark_dataset, coamps_benchmark_dataset=coamps_benchmark_dataset,
                         wrf_benchmark_dataset=wrf_benchmark_dataset, 
                         r408_dataset=r408_dataset, hoc_dataset=hoc_dataset, e3sm_datasets=e3sm_datasets,
                         cam_datasets=cam_datasets, sam_datasets=sam_datasets, wrf_datasets=wrf_datasets,
                         priority_vars=priority_vars, background_rcm=background_rcm,
                         background_rcm_folder=background_rcm_folder)

    def getNimSamLine(self, dataset_override=None):
        """
        This is a "calculate function". Calculate functions are intended to be written by the user in the event that
        they need a variable that is not output by their atmospheric model. The general format for these functions
        is:
            1. Get the proper dataset. This is either passed in as dataset_override, or some benchmark dataset
            2. Get the equations needed variables from the dataset using ``self.getVarForCalculations()``
            3. Calculate the new variable
            4. (optional) If there are multiple valid equations, pick the one that worked using
               ``self.pickNonZeroOutput()``
            5. Return the data as (dependent,independent)

        For more information on calculate functions, see the "Creating a new calculated function (for calculated
        variables)" section of the README.md

        Caclulates Nim from sam -> clubb using the equation
        ``(NI * 1e+6) ./ RHO``

        :param dataset_override: If passed, this netcdf dataset will be used to gather the data needed to calculate the
          given variable. if not passed, this function should attempt to find the best source for the data, e.g.
          the benchmark data for the given model
        :return: tuple of numeric lists of the form (dependent_data, independent_data) for the given variable being caluclated.
          Lists will be filled with NaN's if the variable could not be calculated.
        """
        dataset = self.sam_benchmark_dataset
        if dataset_override is not None:
            dataset = dataset_override
        ni, indep, dataset = self.getVarForCalculations('NI', dataset)
        rho, indep, dataset = self.getVarForCalculations('RHO', dataset)
        # indep, indep, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], self.sam_benchmark_dataset)

        nim = (ni * (10 ** 6) / rho)
        return nim, indep

    def getNsmSamLine(self, dataset_override=None):
        """
        Caclulates Nim from sam -> clubb using the equation
        (NS * 1e+6) ./ RHO
        :return:
        """
        dataset = self.sam_benchmark_dataset
        if dataset_override is not None:
            dataset = dataset_override
        ns, indep, dataset = self.getVarForCalculations('NS', dataset)
        rho, indep, dataset = self.getVarForCalculations('RHO', dataset)
        # indep, indep, dataset = self.getVarForCalculations(['z', 'lev', 'altitude'], self.sam_benchmark_dataset)

        nsm = (ns * (10 ** 6) / rho)
        return nsm, indep
