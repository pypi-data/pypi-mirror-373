"""
This module contains functions for performing one-sample Z-tests and calculating
various statistics such as Cohen's d, Z-score, p-value, confidence intervals, and
standard errors.

The module includes the following functions:
- calculate_central_ci_from_cohens_d_one_sample: Calculate the confidence intervals
and standard error for Cohen's d effect size in a one-sample Z-test.
- One_Sample_ZTests: A class containing static methods for performing one-sample
Z-tests from Z-score, parameters, and data.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import stats
from ...utils import interfaces, es


def calculate_central_ci_from_cohens_d_one_sample(
    cohens_d, sample_size, confidence_level
):
    """
    Calculate the confidence intervals and standard error for Cohen's d effect size in a
    one-sample Z-test.

    This function calculates the confidence intervals of the effect size (Cohen's d) for a
    one-sample Z-test or two dependent samples test using the Hedges and Olkin (1985)
    formula to estimate the standard error.

    Parameters
    ----------
    cohens_d : float
        The calculated Cohen's d effect size
    sample_size : int
        The size of the sample
    confidence_level : float
        The confidence level as a decimal (e.g., 0.95 for 95%)

    Returns
    -------
    tuple
        A tuple containing:
        - ci_lower (float): Lower bound of the confidence interval
        - ci_upper (float): Upper bound of the confidence interval
        - standard_error_es (float): Standard error of the effect size

    Notes
    -----
    Since the effect size in the population and its standard deviation are unknown,
    we estimate it based on the sample using the Hedges and Olkin (1985) formula
    to estimate the standard deviation of the effect size.
    """
    standard_error_es = np.sqrt((1 / sample_size) + ((cohens_d**2 / (2 * sample_size))))
    z_critical_value = stats.norm.ppf(confidence_level + ((1 - confidence_level) / 2))
    ci_lower, ci_upper = (
        cohens_d - standard_error_es * z_critical_value,
        cohens_d + standard_error_es * z_critical_value,
    )
    return ci_lower, ci_upper, standard_error_es


@dataclass
class OneSampleZResults:
    """
    A class to store results from one-sample Z statistical tests.

    This class contains attributes to store various statistical measures including:
    - Effect size (Cohen's d)
    - Z-score and p-value
    - Standard error of the mean
    - Confidence intervals for Cohen's d
    - Standard error of the effect size
    """

    cohens_d: Optional[es.CohenD] = None
    z_score: Optional[float] = None
    p_value: Optional[float] = None
    standard_error_of_the_mean: Optional[float] = None
    sample_mean: Optional[float] = None
    population_mean: Optional[float] = None
    population_sd: Optional[float] = None
    sample_sd: Optional[float] = None
    difference_between_means: Optional[float] = None
    sample_size: Optional[float] = None


class OneSampleZTests(interfaces.AbstractTest):
    """
    A class for performing one-sample Z-tests.
    This class provides methods to calculate Z-test results from a Z-score,
    from sample parameters, and from sample data.
    """

    @staticmethod
    def from_score(
        z_score: float, sample_size: float, confidence_level: float = 0.95
    ) -> OneSampleZResults:
        """
        Calculate the one-sample Z-test results from a given Z-score.
        """

        p_value = min(float(stats.norm.sf((abs(z_score))) * 2), 0.99999)
        cohens_d = z_score / np.sqrt(sample_size)
        ci_lower, ci_upper, standard_error_es = (
            calculate_central_ci_from_cohens_d_one_sample(
                cohens_d, sample_size, confidence_level
            )
        )

        cohens_d = es.CohenD(
            value=round(cohens_d, 4),
            ci_lower=round(ci_lower, 4),
            ci_upper=round(ci_upper, 4),
            standard_error=round(standard_error_es, 4),
        )

        results = OneSampleZResults()
        results.z_score = z_score
        results.p_value = p_value
        results.cohens_d = cohens_d

        return results

    @staticmethod
    def from_parameters(
        sample_mean: float,
        sample_size: int,
        population_mean: int,
        population_sd,
        confidence_level=0.95,
    ) -> OneSampleZResults:
        """
        Calculate the one-sample Z-test results from given population and sample parameters.
        """

        mean_standard_error = population_sd / np.sqrt(sample_size)
        z_score = (population_mean - sample_mean) / mean_standard_error
        cohens_d = (population_mean - sample_mean) / population_sd
        p_value = min(float(stats.norm.sf((abs(z_score))) * 2), 0.99999)
        ci_lower, ci_upper, standard_error_es = (
            calculate_central_ci_from_cohens_d_one_sample(
                cohens_d, sample_size, confidence_level
            )
        )

        cohens_d = es.CohenD(
            value=round(cohens_d, 4),
            ci_lower=round(ci_lower, 4),
            ci_upper=round(ci_upper, 4),
            standard_error=round(standard_error_es, 4),
        )

        # Create results object
        results = OneSampleZResults()
        results.z_score = z_score
        results.p_value = p_value
        results.cohens_d = cohens_d
        results.standard_error_of_the_mean = round(mean_standard_error, 4)
        results.sample_mean = sample_mean
        results.population_mean = population_mean
        results.population_sd = population_sd
        return results

    @staticmethod
    def from_data(
        column: list,
        population_mean: float,
        population_sd: float,
        confidence_level: float = 0.95,
    ) -> OneSampleZResults:
        """
        Calculate the one-sample Z-test results from given sample data.
        """

        sample_mean = np.mean(column)
        sample_sd = np.std(column, ddof=1)
        diff_mean = population_mean - sample_mean
        sample_size = len(column)
        standard_error = population_sd / (np.sqrt(sample_size))
        z_score = diff_mean / standard_error
        cohens_d = (
            diff_mean
        ) / population_sd  # This is the effect size for one sample z-test Cohen's d
        p_value = min(float(stats.norm.sf((abs(z_score))) * 2), 0.99999)
        ci_lower, ci_upper, standard_error_es = (
            calculate_central_ci_from_cohens_d_one_sample(
                cohens_d, sample_size, confidence_level
            )
        )

        cohens_d = es.CohenD(
            value=float(cohens_d),
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            standard_error=standard_error_es,
        )

        results = OneSampleZResults()
        results.z_score = z_score
        results.p_value = p_value
        results.cohens_d = cohens_d
        results.sample_size = sample_size
        results.population_mean = population_mean
        results.sample_mean = float(sample_mean)
        results.sample_sd = float(sample_sd)
        results.standard_error_of_the_mean = standard_error
        results.difference_between_means = float(diff_mean)

        return results
