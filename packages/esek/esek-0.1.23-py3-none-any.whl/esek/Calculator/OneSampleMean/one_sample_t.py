"""
This module contains functions and classes for performing one-sample t-tests and
calculating various statistics such as Cohen's d, Hedges' g, t-score, p-value,
confidence intervals, and standard errors.

The module includes the following functions:
- pivotal_ci_t: Calculate the Pivotal confidence intervals for a one-sample t-test.
- calculate_central_ci_one_sample_t_test: Calculate the central confidence intervals
for the effect size in a one-sample t-test.
- CI_NCP_one_Sample: Calculate the Non-Central Parameter (NCP) confidence intervals
for a one-sample t-test.

The module also includes the following class:
- One_Sample_ttest: A class containing static methods for performing one-sample
t-tests from t-score and parameters.
"""

import math
from typing import Optional
from dataclasses import dataclass
import numpy as np
from scipy import stats
from ...utils import interfaces, res, es, utils



@dataclass
class OneSampleTResults:
    """
    A class to store results from one-sample t-tests.
    """

    cohens_d: Optional[es.CohenD] = None
    hedges_g: Optional[es.HedgesG] = None
    t_score: Optional[float] = None
    degrees_of_freedom: Optional[int | float] = None
    p_value: Optional[float] = None
    standard_error: Optional[float | int] = None
    sample_mean: Optional[float | int] = None
    population_mean: Optional[float | int] = None
    means_difference: Optional[float | int] = None
    sample_size: Optional[float | int] = None
    sample_sd: Optional[float | int] = None


class OneSampleTTest(interfaces.AbstractTest):
    """
    A class to perform one-sample t-tests and calculate various statistics.
    This class provides methods to calculate T-test results from a t-score,
    from sample parameters, and from sample data.
    """

    @staticmethod
    def from_score(
        t_score: float, sample_size: int, confidence_level=0.95
    ) -> OneSampleTResults:
        """
        Calculate the one-sample t-test results from a given t-score.
        """

        # Calculation
        df = sample_size - 1
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        cohens_d = t_score / np.sqrt(
            df
        )  # This is Cohen's d and it is calculated based on the sample's standard deviation
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_g = correction * cohens_d
        (
            ci_lower_cohens_d_central,
            ci_upper_cohens_d_central,
            standard_error_cohens_d_true,
            standard_error_cohens_d_morris,
            standard_error_cohens_d_hedges,
            standard_error_cohens_d_hedges_olkin,
            standard_error_cohens_d_mle,
            standard_error_cohens_d_large_n,
            standard_error_cohens_d_small_n,
        ) = utils.central_ci_paired(
            cohens_d, sample_size, confidence_level
        )
        (
            ci_lower_hedges_g_central,
            ci_upper_hedges_g_central,
            standard_error_hedges_g_true,
            standard_error_hedges_g_morris,
            standard_error_hedges_g_hedges,
            standard_error_hedges_g_hedges_olkin,
            standard_error_hedges_g_mle,
            standard_error_hedges_g_large_n,
            standard_error_hedges_g_small_n,
        ) = utils.central_ci_paired(
            hedges_g, sample_size, confidence_level
        )
        ci_lower_cohens_d_pivotal, ci_upper_cohens_d_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_g_pivotal, ci_upper_hedges_g_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_cohens_d_ncp, ci_upper_cohens_d_ncp = utils.ci_ncp(
            cohens_d, sample_size, confidence_level
        )
        ci_lower_hedges_g_ncp, ci_upper_hedges_g_ncp = utils.ci_ncp(
            hedges_g, sample_size, confidence_level
        )

        cohens_d = es.CohenD(
            cohens_d,
            ci_lower_cohens_d_central,
            ci_upper_cohens_d_central,
            standard_error_cohens_d_true,
        )

        cohens_d.standardizer = correction
        cohens_d.update_non_central_ci(ci_lower_cohens_d_ncp, ci_upper_cohens_d_ncp)
        cohens_d.update_pivotal_ci(ci_lower_cohens_d_pivotal, ci_upper_cohens_d_pivotal)

        cohens_d_approximated = res.ApproximatedStandardError(
            standard_error_cohens_d_true,
            standard_error_cohens_d_morris,
            standard_error_cohens_d_hedges,
            standard_error_cohens_d_hedges_olkin,
            standard_error_cohens_d_mle,
            standard_error_cohens_d_large_n,
            standard_error_cohens_d_small_n,
        )

        cohens_d.approximated_standard_error = cohens_d_approximated

        hedges_g = es.HedgesG(
            hedges_g,
            ci_lower_hedges_g_central,
            ci_upper_hedges_g_central,
            standard_error_hedges_g_true,
        )

        hedges_g.update_non_central_ci(ci_lower_hedges_g_ncp, ci_upper_hedges_g_ncp)
        hedges_g.update_pivotal_ci(ci_lower_hedges_g_pivotal, ci_upper_hedges_g_pivotal)

        hedges_g_approximated = res.ApproximatedStandardError(
            standard_error_hedges_g_true,
            standard_error_hedges_g_morris,
            standard_error_hedges_g_hedges,
            standard_error_hedges_g_hedges_olkin,
            standard_error_hedges_g_mle,
            standard_error_hedges_g_large_n,
            standard_error_hedges_g_small_n,
        )
        hedges_g.approximated_standard_error = hedges_g_approximated

        results = OneSampleTResults()
        results.t_score = t_score
        results.degrees_of_freedom = df
        results.p_value = p_value
        results.cohens_d = cohens_d
        results.hedges_g = hedges_g

        return results

    @staticmethod
    def from_parameters(
        population_mean: float,
        sample_mean: float,
        sample_sd: float,
        sample_size: int,
        confidence_level: float = 0.95,
    ) -> OneSampleTResults:
        """
        Calculate the one-sample t-test results from given parameters.
        """
        df = sample_size - 1
        standard_error = sample_sd / np.sqrt(
            df
        )  # This is the standrt error of mean's estimate in o ne samaple t-test
        t_score = (
            sample_mean - population_mean
        ) / standard_error  # This is the t score in the test which is used to calculate the p-value
        cohens_d = (
            sample_mean - population_mean
        ) / sample_sd  # This is the effect size for one sample t-test Cohen's d
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_g = cohens_d * correction  # This is the actual corrected effect size
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        (
            ci_lower_cohens_d_central,
            ci_upper_cohens_d_central,
            standard_error_cohens_d_true,
            standard_error_cohens_d_morris,
            standard_error_cohens_d_hedges,
            standard_error_cohens_d_hedges_olkin,
            standard_error_cohens_d_mle,
            standard_error_cohens_d_large_n,
            standard_error_cohens_d_small_n,
        ) = utils.central_ci_paired(
            cohens_d, sample_size, confidence_level
        )
        (
            ci_lower_hedges_g_central,
            ci_upper_hedges_g_central,
            standard_error_hedges_g_true,
            standard_error_hedges_g_morris,
            standard_error_hedges_g_hedges,
            standard_error_hedges_g_hedges_olkin,
            standard_error_hedges_g_mle,
            standard_error_hedges_g_large_n,
            standard_error_hedges_g_small_n,
        ) = utils.central_ci_paired(
            hedges_g, sample_size, confidence_level
        )
        ci_lower_cohens_d_pivotal, ci_upper_cohens_d_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_g_pivotal, ci_upper_hedges_g_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_cohens_d_ncp, ci_upper_cohens_d_ncp = utils.ci_ncp(
            cohens_d, sample_size, confidence_level
        )
        ci_lower_hedges_g_ncp, ci_upper_hedges_g_ncp = utils.ci_ncp(
            hedges_g, sample_size, confidence_level
        )

        cohens_d = es.CohenD(
            cohens_d,
            ci_lower_cohens_d_central,
            ci_upper_cohens_d_central,
            standard_error_cohens_d_true,
        )
        cohens_d.standardizer = correction
        cohens_d.update_non_central_ci(
            float(ci_lower_cohens_d_ncp), float(ci_upper_cohens_d_ncp)
        )
        cohens_d.update_pivotal_ci(ci_lower_cohens_d_pivotal, ci_upper_cohens_d_pivotal)
        cohens_d_approximated = res.ApproximatedStandardError(
            standard_error_cohens_d_true,
            standard_error_cohens_d_morris,
            standard_error_cohens_d_hedges,
            standard_error_cohens_d_hedges_olkin,
            standard_error_cohens_d_mle,
            standard_error_cohens_d_large_n,
            standard_error_cohens_d_small_n,
        )
        cohens_d.approximated_standard_error = cohens_d_approximated

        hedges_g = es.HedgesG(
            hedges_g,
            ci_lower_hedges_g_central,
            ci_upper_hedges_g_central,
            standard_error_hedges_g_true,
        )

        hedges_g.update_non_central_ci(
            float(ci_lower_hedges_g_ncp), float(ci_upper_hedges_g_ncp)
        )
        hedges_g.update_pivotal_ci(ci_lower_hedges_g_pivotal, ci_upper_hedges_g_pivotal)
        hedges_g_approximated = res.ApproximatedStandardError(
            standard_error_hedges_g_true,
            standard_error_hedges_g_morris,
            standard_error_hedges_g_hedges,
            standard_error_hedges_g_hedges_olkin,
            standard_error_hedges_g_mle,
            standard_error_hedges_g_large_n,
            standard_error_hedges_g_small_n,
        )
        hedges_g.approximated_standard_error = hedges_g_approximated

        # Create results object
        results = OneSampleTResults()

        results.t_score = t_score
        results.degrees_of_freedom = df
        results.p_value = p_value
        results.cohens_d = cohens_d
        results.hedges_g = hedges_g

        # Assign values to the results object
        results.sample_size = sample_size
        results.population_mean = population_mean
        results.sample_mean = sample_mean
        results.sample_sd = sample_sd
        results.standard_error = standard_error
        results.means_difference = sample_mean - population_mean

        return results

    @staticmethod
    def from_data() -> OneSampleTResults:
        """
        Calculate the one-sample t-test results from sample data.
        This method is not implemented yet.
        """
        raise NotImplementedError("This method is not implemented yet.")
