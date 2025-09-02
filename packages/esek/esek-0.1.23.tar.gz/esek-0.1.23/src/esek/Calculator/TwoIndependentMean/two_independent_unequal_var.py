"""
Two Independent Means with Unequal Variances Calculator
"""

from dataclasses import dataclass
from typing import Optional
import math
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es, texts


@dataclass
class TwoIndependentUnequalVarResults:
    """
    Results for the Two Independent Means with Unequal Variances test.
    """

    inferential: Optional[res.InferentialStatistics] = None
    aoki_epsilon: Optional[es.AokiEpsilon] = None
    aoki_epsilon_unbiased: Optional[es.AokiEpsilonUnbiased] = None
    sample1: Optional[res.Sample] = None
    sample2: Optional[res.Sample] = None


class TwoIndependentUnequalVarTests(interfaces.AbstractTest):
    """
    Two Independent Means with Unequal Variances test.
    This test evaluates the difference between two independent means when the variances are unequal.
    It calculates Welch's t-test, degrees of freedom, p-value, and Aoki's Epsilon effect sizes.
    This class provides methods to compute the test from parameters, data, or a score.

        Attributes:
                None

        Methods:
                from_score: Computes the test from a score (not implemented).
                from_parameters: Computes the test from sample means, standard deviations, sizes, and population mean difference.
                from_data: Computes the test from two independent samples.
    """

    @utils.not_implemented(
        interfaces.MethodType.FROM_SCORE, "TwoIndependentUnequalVarTests"
    )
    @staticmethod
    def from_score() -> None:
        """
        A static method to create results from a score.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
                NotImplementedError: This method is not implemented for TwoIndependentUnequalVar.
        """
        pass

    @staticmethod
    def from_parameters(
        sample_mean_1: float,
        sample_mean_2: float,
        sample_sd_1: float,
        sample_sd_2: float,
        sample_size_1: int,
        sample_size_2: int,
        population_mean_diff: float = 0,
        confidence_level: float = 0.95,
    ) -> TwoIndependentUnequalVarResults:
        """
        Computes the test from parameters.

        Arguments:
            sample_mean_1 (float): The mean of the first sample.
            sample_mean_2 (float): The mean of the second sample.
            sample_sd_1 (float): The standard deviation of the first sample.
            sample_sd_2 (float): The standard deviation of the second sample.
            sample_size_1 (int): The size of the first sample.
            sample_size_2 (int): The size of the second sample.
            population_mean_diff (float): The hypothesized difference in population means. Default is 0.
            confidence_level (float): The confidence level for the confidence intervals. Default is 0.95.

        Returns:
            TwoIndependentUnequalVarResults: The results of the test.
        """
        sample_size = sample_size_1 + sample_size_2
        mean_difference = sample_mean_1 - sample_mean_2
        variance_1 = sample_sd_1**2
        variance_2 = sample_sd_2**2
        standard_error_welch_t = np.sqrt(
            variance_1 / sample_size_1 + (variance_2 / sample_size_2)
        )
        welchs_t = (
            sample_mean_1 - sample_mean_2 - population_mean_diff
        ) / standard_error_welch_t
        df = (variance_1 / sample_size_1 + variance_2 / sample_size_2) ** 2 / (
            (variance_1 / sample_size_1) ** 2 / (sample_size_1 - 1)
            + (variance_2 / sample_size_2) ** 2 / (sample_size_2 - 1)
        )
        p_value = min(float(stats.t.sf((abs(welchs_t)), df) * 2), 0.99999)

        harmonic_n = sample_size_1 * sample_size_2 / (sample_size_1 + sample_size_2)
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        epsilon = welchs_t / np.sqrt(harmonic_n)
        epsilon_unbiased = epsilon * correction
        standard_error_epsilon_biased = (
            df / (df - 2) * (1 / harmonic_n + epsilon_unbiased**2)
            - epsilon_unbiased**2 / correction**2
        )
        standard_error_epsilon_unbiased = standard_error_epsilon_biased * correction**2
        standardizer_biased = np.sqrt(
            (variance_1 * sample_size_2 + variance_2 * sample_size_1)
            / (sample_size_1 + sample_size_2)
        )
        standardizer_unbiased = standardizer_biased / correction

        lower_ncp, upper_ncp = utils.pivotal_ci_t(
            welchs_t, df, sample_size, confidence_level
        )

        epsilon_biased_lower_ci = (lower_ncp * (np.sqrt(sample_size))) / np.sqrt(
            harmonic_n
        )
        epsilon_biased_upper_ci = (upper_ncp * (np.sqrt(sample_size))) / np.sqrt(
            harmonic_n
        )
        epsilon_unbiased_lower_ci = (
            (lower_ncp * (np.sqrt(sample_size))) / np.sqrt(harmonic_n) * correction
        )
        epsilon_unbiased_upper_ci = (
            (upper_ncp * (np.sqrt(sample_size))) / np.sqrt(harmonic_n) * correction
        )

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            score=round(welchs_t, 4),
            p_value=round(p_value, 4),
        )
        inferential.degrees_of_freedom = round(df, 4)
        inferential.standard_error = round(standard_error_welch_t, 4)
        inferential.means_difference = round(mean_difference, 4)

        aoki_epsilon: es.AokiEpsilon = es.AokiEpsilon(
            value=round(epsilon, 4),
            standard_error=round(standard_error_epsilon_biased, 4),
            ci_lower=round(epsilon_biased_lower_ci, 4),
            ci_upper=round(epsilon_biased_upper_ci, 4),
        )
        aoki_epsilon.standardizer = round(standardizer_biased, 4)

        aoki_epsilon_unbiased: es.AokiEpsilonUnbiased = es.AokiEpsilonUnbiased(
            value=round(epsilon_unbiased, 4),
            standard_error=round(standard_error_epsilon_unbiased, 4),
            ci_lower=round(epsilon_unbiased_lower_ci, 4),
            ci_upper=round(epsilon_unbiased_upper_ci, 4),
        )
        aoki_epsilon_unbiased.standardizer = round(standardizer_unbiased, 4)

        results = TwoIndependentUnequalVarResults()
        results.inferential = inferential
        results.aoki_epsilon = aoki_epsilon
        results.aoki_epsilon_unbiased = aoki_epsilon_unbiased

        return results

    @staticmethod
    def from_data(
        columns: list[list], population_mean_diff: float, confidence_level: float = 0.95
    ) -> TwoIndependentUnequalVarResults:
        """
        Computes the test from data.

        Arguments:
            columns (list[list]): A list of two columns of data.
            population_mean_diff (float): The hypothesized difference in population means. Default is 0.
            confidence_level (float): The confidence level for the confidence intervals. Default is 0.95.

        Returns:
            TwoIndependentUnequalVarResults: The results of the test.
        """
        if len(columns) != 2:
            raise ValueError(texts.Errors.columns_must_be_two)

        column_1 = columns[0]
        column_2 = columns[1]

        sample_mean_1 = np.mean(column_1)
        sample_mean_2 = np.mean(column_2)
        sample_sd_1 = np.std(column_1, ddof=1)
        sample_sd_2 = np.std(column_2, ddof=1)
        sample_size = len(column_1)
        sample_size_1 = len(column_1)
        sample_size_2 = len(column_2)

        sample_size = sample_size_1 + sample_size_2
        mean_difference = sample_mean_1 - sample_mean_2
        variance_1 = sample_sd_1**2
        variance_2 = sample_sd_2**2

        standard_error_welch_t = np.sqrt(
            variance_1 / sample_size_1 + (variance_2 / sample_size_2)
        )
        welchs_t = (
            sample_mean_1 - sample_mean_2 - population_mean_diff
        ) / standard_error_welch_t
        df = (variance_1 / sample_size_1 + variance_2 / sample_size_2) ** 2 / (
            (variance_1 / sample_size_1) ** 2 / (sample_size_1 - 1)
            + (variance_2 / sample_size_2) ** 2 / (sample_size_2 - 1)
        )
        p_value = min(float(stats.t.sf((abs(welchs_t)), df) * 2), 0.99999)

        harmonic_n = sample_size_1 * sample_size_2 / (sample_size_1 + sample_size_2)
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )

        epsilon = welchs_t / np.sqrt(harmonic_n)
        epsilon_unbiased = epsilon * correction

        standard_error_epsilon_biased = (
            df / (df - 2) * (1 / harmonic_n + epsilon_unbiased**2)
            - epsilon_unbiased**2 / correction**2
        )
        standard_error_epsilon_unbiased = standard_error_epsilon_biased * correction**2

        standardizer_biased = np.sqrt(
            (variance_1 * sample_size_2 + variance_2 * sample_size_1)
            / (sample_size_1 + sample_size_2)
        )
        standardizer_unbiased = standardizer_biased / correction

        lower_ncp, upper_ncp = utils.pivotal_ci_t(
            welchs_t, float(df), sample_size, confidence_level
        )

        epsilon_biased_lower_ci = (lower_ncp * (np.sqrt(sample_size))) / np.sqrt(
            harmonic_n
        )
        epsilon_biased_upper_ci = (upper_ncp * (np.sqrt(sample_size))) / np.sqrt(
            harmonic_n
        )
        epsilon_unbiased_lower_ci = (
            (lower_ncp * (np.sqrt(sample_size))) / np.sqrt(harmonic_n) * correction
        )
        epsilon_unbiased_upper_ci = (
            (upper_ncp * (np.sqrt(sample_size))) / np.sqrt(harmonic_n) * correction
        )

        sample1: res.Sample = res.Sample(
            mean=float(sample_mean_1),
            standard_deviation=float(sample_sd_1),
            size=sample_size_1,
        )

        sample2: res.Sample = res.Sample(
            mean=float(sample_mean_2),
            standard_deviation=float(sample_sd_2),
            size=sample_size_2,
        )

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            score=round(welchs_t, 4),
            p_value=round(p_value, 4),
        )
        inferential.degrees_of_freedom = round(float(df), 4)
        inferential.means_difference = round(float(mean_difference), 4)

        aoki_epsilon: es.AokiEpsilon = es.AokiEpsilon(
            value=round(epsilon, 4),
            standard_error=round(standard_error_epsilon_biased, 4),
            ci_lower=round(epsilon_biased_lower_ci, 4),
            ci_upper=round(epsilon_biased_upper_ci, 4),
        )
        aoki_epsilon.standardizer = round(standardizer_biased, 4)

        aoki_epsilon_unbiased: es.AokiEpsilonUnbiased = es.AokiEpsilonUnbiased(
            value=round(epsilon_unbiased, 4),
            standard_error=round(standard_error_epsilon_unbiased, 4),
            ci_lower=round(epsilon_unbiased_lower_ci, 4),
            ci_upper=round(epsilon_unbiased_upper_ci, 4),
        )
        aoki_epsilon_unbiased.standardizer = round(standardizer_unbiased, 4)

        results = TwoIndependentUnequalVarResults()
        results.inferential = inferential
        results.sample1 = sample1
        results.sample2 = sample2
        results.aoki_epsilon = aoki_epsilon
        results.aoki_epsilon_unbiased = aoki_epsilon_unbiased

        return results
