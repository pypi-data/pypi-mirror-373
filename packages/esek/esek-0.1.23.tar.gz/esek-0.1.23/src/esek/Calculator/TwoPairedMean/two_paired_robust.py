"""
This module implements robust statistical tests for two paired samples.
It includes methods for calculating robust effect sizes, confidence intervals,
and inferential statistics using Yuen's t-test and winsorized Pearson correlation.
It also provides a data class to store the results of these tests.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es


@dataclass
class TwoPairedRobustResults:
    """
    A data class to store the results of two paired robust tests.
        It includes samples, inferential statistics, robust effect sizes,
    """

    sample1: Optional[res.Sample] = None
    sample2: Optional[res.Sample] = None
    inferential: Optional[res.InferentialStatistics] = None
    robust_akp: Optional[es.RobustAKP] = None
    robust_explanatory: Optional[es.RobustExplanatory] = None
    yuen_robust_t: Optional[float] = None
    winsorized_pearson_correlation: Optional[float] = None
    winsorized_pearson_correlation_p_value: Optional[float] = None


class TwoPairedRobustTests(interfaces.AbstractTest):
    """
    A class to perform robust statistical tests for two paired samples.
    It includes methods for calculating robust effect sizes, confidence intervals,
    and inferential statistics using Yuen's t-test and winsorized Pearson correlation.

        Methods:
                - from_score: Not implemented.
                - from_parameters: Not implemented.
                - from_data: Calculates robust statistics from two paired samples.
    """

    @staticmethod
    def from_score() -> TwoPairedRobustResults:
        """
        A static method to create results from a score.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
                NotImplementedError: This method is not implemented for TwoPairedRobustResults.

        """
        raise NotImplementedError(
            "from_score method is not implemented for TwoPairedRobust."
        )

    @staticmethod
    def from_parameters() -> TwoPairedRobustResults:
        """
        A static method to create results from parameters.
            This method is not implemented and will raise a NotImplementedError.
        Raises:
                    NotImplementedError: This method is not implemented for TwoPairedRobustResults.
        """
        raise NotImplementedError(
            "from_parameters method is not implemented for TwoPairedRobust."
        )

    @staticmethod
    def from_data(
        columns: list[list[float]],
        reps: int,
        confidence_level: float,
        trimming_level: float = 0.2,
        population_difference: float = 0.2,
    ) -> TwoPairedRobustResults:
        """
        A method to calculate robust statistics from two paired samples.
        """

        column_1 = columns[0]
        column_2 = columns[1]

        difference = np.array(column_1) - np.array(column_2)
        sample_size = len(column_1)

        lower_bound = stats.norm.ppf(trimming_level)
        upper_bound = stats.norm.ppf(1 - trimming_level)

        area = utils.area_under_function(
            utils.density,
            float(lower_bound),
            float(upper_bound),
        )

        tail_correction = 2 * (lower_bound**2) * trimming_level

        correction = np.sqrt(area + tail_correction)

        trimmed_mean_1 = stats.trim_mean(column_1, trimming_level)
        trimmed_mean_2 = stats.trim_mean(column_2, trimming_level)
        winsorized_standard_deviation_1 = np.sqrt(utils.winsorized_variance(column_1))
        winsorized_standard_deviation_2 = np.sqrt(utils.winsorized_variance(column_2))
        winsorized = utils.winsorized_correlation(column_1, column_2, trimming_level)
        winsorized_correlation = winsorized["cor"]
        winsorized_correlation_p_value = winsorized["p.value"]

        standardizer = np.sqrt(utils.winsorized_variance(difference, trimming_level))
        trimmed_mean = stats.trim_mean(difference, trimming_level)
        akp_effect_size = (
            correction * (trimmed_mean - population_difference) / standardizer
        )

        bootstrap_samples_difference = []
        for _ in range(reps):
            difference_bootstrap = np.random.choice(
                difference, len(difference), replace=True
            )
            bootstrap_samples_difference.append(difference_bootstrap)

        trimmed_means_of_bootstrap = stats.trim_mean(
            bootstrap_samples_difference, trimming_level, axis=1
        )
        standardizer_of_bootstrap = np.sqrt(
            [
                utils.winsorized_variance(array, trimming_level)
                for array in bootstrap_samples_difference
            ]
        )
        akp_effect_size_bootstrap = (
            correction
            * (trimmed_means_of_bootstrap - population_difference)
            / standardizer_of_bootstrap
        )
        lower_ci_akp_boot = np.percentile(
            akp_effect_size_bootstrap,
            ((1 - confidence_level) - ((1 - confidence_level) / 2)) * 100,
        )
        upper_ci_akp_boot = np.percentile(
            akp_effect_size_bootstrap,
            ((confidence_level) + ((1 - confidence_level) / 2)) * 100,
        )

        sort_values = [float(item) for item in np.concatenate((column_1, column_2))]
        variance_between_trimmed_means = (
            np.std(np.array([trimmed_mean_1, trimmed_mean_2]), ddof=1)
        ) ** 2
        winsorized_variance_value = utils.winsorized_variance(
            sort_values, trimming_level
        )
        explained_variance = variance_between_trimmed_means / (
            winsorized_variance_value / correction**2
        )
        explanatory_power_effect_size = min(float(np.sqrt(explained_variance)), 1)

        bootstrap_samples_x = []
        bootstrap_samples_y = []
        for _ in range(reps):
            sample_1_bootstrap = np.random.choice(column_1, len(column_1), replace=True)
            sample_2_bootstrap = np.random.choice(column_2, len(column_2), replace=True)
            bootstrap_samples_x.append(sample_1_bootstrap)
            bootstrap_samples_y.append(sample_2_bootstrap)

        concatenated_samples = [
            np.concatenate((x, y))
            for x, y in zip(bootstrap_samples_x, bootstrap_samples_y)
        ]
        trimmed_means_of_bootstrap_sample_1 = np.array(
            (stats.trim_mean(bootstrap_samples_x, trimming_level, axis=1))
        )
        trimmed_means_of_bootstrap_sample_2 = np.array(
            (stats.trim_mean(bootstrap_samples_y, trimming_level, axis=1))
        )
        variance_between_trimmed_means_bootstrap = [
            (np.std(np.array([x, y]), ddof=1)) ** 2
            for x, y in zip(
                trimmed_means_of_bootstrap_sample_1, trimmed_means_of_bootstrap_sample_2
            )
        ]
        winsorized_variances_bootstrap = [
            utils.winsorized_variance(arr, trimming_level)
            for arr in concatenated_samples
        ]
        explained_variance_bootstrapping = np.array(
            variance_between_trimmed_means_bootstrap
            / (winsorized_variances_bootstrap / correction**2)
        )
        explanatory_power_effect_size_bootstrap = [
            array**0.5 for array in explained_variance_bootstrapping
        ]
        lower_ci_e_pow_boot = np.percentile(
            explanatory_power_effect_size_bootstrap,
            ((1 - confidence_level) - ((1 - confidence_level) / 2)) * 100,
        )
        upper_ci_e_pow_boot = np.percentile(
            explanatory_power_effect_size_bootstrap,
            ((confidence_level) + ((1 - confidence_level) / 2)) * 100,
        )

        q1 = (len(column_1) - 1) * winsorized_standard_deviation_1**2
        q2 = (len(column_2) - 1) * winsorized_standard_deviation_2**2
        q3 = (len(column_1) - 1) * winsorized["cov"]
        non_winsorized_sample_size = len(column_1) - 2 * np.floor(
            trimming_level * len(column_1)
        )
        df = non_winsorized_sample_size - 1
        yuen_standard_error = np.sqrt(
            (q1 + q2 - 2 * q3)
            / (non_winsorized_sample_size * (non_winsorized_sample_size - 1))
        )
        difference_trimmed_means = trimmed_mean_1 - trimmed_mean_2
        yuen_statistic = difference_trimmed_means / yuen_standard_error
        yuen_p_value = 2 * (1 - stats.t.cdf(np.abs(yuen_statistic), df))

        sample1 = res.Sample(
            mean=round(trimmed_mean_1, 4),
            standard_deviation=round(winsorized_standard_deviation_1, 4),
            size=round(sample_size, 4),
        )
        sample2 = res.Sample(
            mean=round(trimmed_mean_2, 4),
            standard_deviation=round(winsorized_standard_deviation_2, 4),
            size=round(sample_size, 4),
        )

        inferential = res.InferentialStatistics(
            p_value=float(np.around(yuen_p_value, 4)),
            score=round(yuen_statistic, 4),
        )
        inferential.standard_error = round(yuen_standard_error, 4)
        inferential.degrees_of_freedom = round(df, 4)
        inferential.means_difference = round(difference_trimmed_means, 4)

        robust_akp = es.RobustAKP(
            value=round(akp_effect_size, 4),
            ci_lower=float(round(lower_ci_akp_boot, 4)),
            ci_upper=float(round(upper_ci_akp_boot, 4)),
            standard_error=round(yuen_standard_error, 4),
        )
        robust_explanatory = es.RobustExplanatory(
            value=round(explanatory_power_effect_size, 4),
            ci_lower=float(round(lower_ci_e_pow_boot, 4)),
            ci_upper=round(min(float(upper_ci_e_pow_boot), 1.0), 4),
            standard_error=round(yuen_standard_error, 4),
        )

        results = TwoPairedRobustResults()
        results.sample1 = sample1
        results.sample2 = sample2
        results.inferential = inferential
        results.robust_akp = robust_akp
        results.robust_explanatory = robust_explanatory
        results.yuen_robust_t = round(yuen_statistic, 4)
        results.winsorized_pearson_correlation = round(winsorized_correlation, 4)
        results.winsorized_pearson_correlation_p_value = round(
            winsorized_correlation_p_value, 4
        )

        return results
