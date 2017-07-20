import logging

from calibtool.study_sites.PrevalenceCalibSite import PrevalenceCalibSite
from calibtool.study_sites.site_setup_functions import config_setup_fn, summary_report_fn, site_input_eir_fn

logger = logging.getLogger(__name__)


class NamawalaCalibSite(PrevalenceCalibSite):

    reference_dict = {

        # Digitized by K.McCarthy from data in:
        #   - TODO: Namawala original source reference and/or 2006 Swiss TPH supplement?
        # for K.McCarthy et al. Malaria Journal 2015, 14:6

        "Average Population by Age Bin": [
            150, 150, 626, 1252, 626, 2142,
            1074, 1074, 605, 605, 489
        ],
        "Age Bin": [
            0.5, 1, 2, 4, 5, 10,
            15, 20, 30, 40, 50
        ],
        "PfPR by Age Bin": [
            0.55, 0.85, 0.9, 0.88, 0.85, 0.82,
            0.75, 0.65, 0.45, 0.42, 0.4
        ]
    }

    def get_setup_functions(self):
        setup_fns = super(NamawalaCalibSite, self).get_setup_functions()
        setup_fns.append(config_setup_fn(duration=365 * 70 + 1))  # 60 years (with leap years)
        setup_fns.append(summary_report_fn(start=0, interval=365.0, age_bins=[0.5, 1, 2, 4, 5, 10, 15, 20, 30, 40, 50]))
        setup_fns.append(site_input_eir_fn(self.name, birth_cohort=True))
        setup_fns.append(lambda cb: cb.update_params({'Demographics_Filenames': [
                                                          'Calibration\\birth_cohort_demographics.compiled.json']}))

        return setup_fns

    def __init__(self):
        super(NamawalaCalibSite, self).__init__('Namawala')
