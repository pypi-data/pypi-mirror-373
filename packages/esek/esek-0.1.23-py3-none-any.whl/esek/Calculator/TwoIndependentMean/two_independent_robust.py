"""
Two Independent Robust Tests Module
This module provides functionality for conducting two independent robust tests,
including the calculation of various robust statistics and effect sizes.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es, texts


@dataclass
class TwoIndependentRobustResults:
    """
    This class holds the results of two independent robust tests,
    including the samples, inferential statistics, and robust effect sizes.
    """

    sample1: Optional[res.Sample] = None
    sample2: Optional[res.Sample] = None
    inferential: Optional[res.InferentialStatistics] = None
    robust_akp: Optional[es.RobustAKP] = None
    robust_exp: Optional[es.RobustExplanatory] = None


class TwoIndependentRobustTests(interfaces.AbstractTest):
    """
    This class implements two independent robust tests.
    It provides methods to calculate robust effect sizes and inferential statistics.

        It is designed to handle two independent samples and compute various statistics.

        Attributes:
                None

        Methods:
                - from_score: Create an instance from a score (Not implemented).
                - from_parameters: Create an instance from parameters (Not implemented).
                - from_data: Create an instance from data.
    """

    @utils.not_implemented(
        interfaces.MethodType.FROM_SCORE, "TwoIndependentRobustTests"
    )
    @staticmethod
    def from_score() -> None:
        """
        A static method to create results from a score.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
                NotImplementedError: This method is not implemented for TwoIndependentRobustTests.
        """
        pass

    @utils.not_implemented(
        interfaces.MethodType.FROM_PARAMETERS, "TwoIndependentRobustTests"
    )
    @staticmethod
    def from_parameters() -> None:
        """
        A static method to create results from parameters.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
                NotImplementedError: This method is not implemented for TwoIndependentRobustTests
        """
        pass

    @staticmethod
    def from_data(
        columns: list[list],
        reps: int = 10000,
        trimming_level: float = 0.2,
        population_difference: float = 0.2,
        confidence_level: float = 0.95,
    ) -> TwoIndependentRobustResults:
        """
        Create an instance from data.

        Args:
            columns (list[list]): The data columns.
            reps (int): The number of bootstrap repetitions. Default is 10000.
            trimming_level (float): The trimming level for robust statistics. Default is 0.2.
            population_difference (float): The population difference for effect size calculation. Default is 0.2.
            confidence_level (float): The confidence level for interval estimation. Default is 0.95.

        Returns:
            TwoIndependentRobustResults: The results of the robust tests.

        Raises:
            ValueError: If the input data is not valid.
        """

        if len(columns) != 2:
            raise ValueError(texts.Errors.columns_must_be_two)
        column_1 = columns[0]
        column_2 = columns[1]
        sample_size_1 = len(column_1)
        sample_size_2 = len(column_1)
        sample_size = sample_size_1 + sample_size_2
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

        standardizer = np.sqrt(
            (
                (
                    winsorized_standard_deviation_1**2 * (sample_size_1 - 1)
                    + winsorized_standard_deviation_2**2 * (sample_size_2 - 1)
                )
                / (sample_size - 2)
            )
        )
        akp_effect_size = (
            correction
            * ((trimmed_mean_1 - trimmed_mean_2) - population_difference)
            / standardizer
        )

        q = sample_size_1 / sample_size
        kms = (
            (trimmed_mean_1 - trimmed_mean_2)
            / (
                (1 - q) * winsorized_standard_deviation_1**2
                + q * winsorized_standard_deviation_2**2
            )
            / (q * (1 - q))
        )

        bootstrap_samples_x = []
        bootstrap_samples_y = []
        for _ in range(reps):
            sample_1_bootstrap = np.random.choice(column_1, len(column_1), replace=True)
            sample_2_bootstrap = np.random.choice(column_2, len(column_2), replace=True)
            bootstrap_samples_x.append(sample_1_bootstrap)
            bootstrap_samples_y.append(sample_2_bootstrap)

        trimmed_means_of_bootstrap_sample_1 = np.array(
            (stats.trim_mean(bootstrap_samples_x, trimming_level, axis=1))
        )
        trimmed_means_of_bootstrap_sample_2 = np.array(
            (stats.trim_mean(bootstrap_samples_y, trimming_level, axis=1))
        )
        winsorized_variances_of_bootstrap_sample_1 = np.array(
            (
                [
                    utils.winsorized_variance(arr, trimming_level)
                    for arr in bootstrap_samples_x
                ]
            )
        )
        winsorized_variances_of_bootstrap_sample_2 = np.array(
            (
                [
                    utils.winsorized_variance(arr, trimming_level)
                    for arr in bootstrap_samples_y
                ]
            )
        )
        standardizer_of_bootstrap = np.array(
            (
                [
                    (x * (sample_size_1 - 1) + y * (sample_size_2 - 1))
                    / (sample_size - 2)
                    for x, y in zip(
                        winsorized_variances_of_bootstrap_sample_1,
                        winsorized_variances_of_bootstrap_sample_2,
                    )
                ]
            )
        )
        sample_difference_of_bootstrap = np.array(
            (
                [
                    (x - y)
                    for x, y in zip(
                        trimmed_means_of_bootstrap_sample_1,
                        trimmed_means_of_bootstrap_sample_2,
                    )
                ]
            )
        )
        akp_effect_size_bootstrap = [
            correction * (x - population_difference) / np.sqrt(y)
            for x, y in zip(sample_difference_of_bootstrap, standardizer_of_bootstrap)
        ]

        lower_ci_akp_boot = np.percentile(
            akp_effect_size_bootstrap,
            ((1 - confidence_level) - ((1 - confidence_level) / 2)) * 100,
        )
        upper_ci_akp_boot = np.percentile(
            akp_effect_size_bootstrap,
            ((confidence_level) + ((1 - confidence_level) / 2)) * 100,
        )

        sort_values = np.concatenate((column_1, column_2))
        variance_between_trimmed_means = (
            np.std(np.array([trimmed_mean_1, trimmed_mean_2]), ddof=1)
        ) ** 2
        winsorized_variance_value = utils.winsorized_variance(
            sort_values, trimming_level
        )
        explained_variance = variance_between_trimmed_means / (
            winsorized_variance_value / correction**2
        )
        explanatory_power_effect_size = np.sqrt(explained_variance)

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

        h1 = sample_size_1 - 2 * np.floor(trimming_level * sample_size_1)
        h2 = sample_size_2 - 2 * np.floor(trimming_level * sample_size_2)
        difference_trimmed_means = trimmed_mean_1 - trimmed_mean_2
        lower_bound = stats.norm.ppf(trimming_level)
        upper_bound = stats.norm.ppf(1 - trimming_level)
        area = utils.area_under_function(
            utils.density, float(lower_bound), float(upper_bound)
        )
        tail_correction = 2 * (lower_bound**2) * trimming_level
        correction = area + tail_correction

        q1 = (sample_size_1 - 1) * winsorized_standard_deviation_1**2 / (h1 * (h1 - 1))
        q2 = (sample_size_2 - 1) * winsorized_standard_deviation_2**2 / (h2 * (h2 - 1))
        df = (q1 + q2) ** 2 / ((q1**2 / (h1 - 1)) + (q2**2 / (h2 - 1)))
        yuen_standard_error = np.sqrt(q1 + q2)
        yuen_statistic = np.abs(difference_trimmed_means / yuen_standard_error)
        yuen_p_value = 2 * (1 - stats.t.cdf(abs(yuen_statistic), df))

        sample1: res.Sample = res.Sample(
            mean=round(trimmed_mean_1, 4),
            standard_deviation=round(winsorized_standard_deviation_1, 4),
            size=round(sample_size_1),
        )
        sample2: res.Sample = res.Sample(
            mean=round(trimmed_mean_2, 4),
            standard_deviation=round(winsorized_standard_deviation_2, 4),
            size=round(sample_size_2),
        )
        inferential: res.InferentialStatistics = res.InferentialStatistics(
            p_value=float(np.around(yuen_p_value, 4)),
            score=round(yuen_statistic, 4),
        )
        inferential.degrees_of_freedom = round(df, 4)
        inferential.means_difference = round(difference_trimmed_means, 4)
        inferential.standard_error = round(yuen_standard_error, 4)

        robust_akp: es.RobustAKP = es.RobustAKP(
            value=round(float(akp_effect_size), 4),
            ci_lower=float(lower_ci_akp_boot),
            ci_upper=float(upper_ci_akp_boot),
            standard_error=round(yuen_standard_error, 4),
        )

        robust_exp: es.RobustExplanatory = es.RobustExplanatory(
            value=round(min(float(explanatory_power_effect_size), 1.0), 4),
            ci_lower=round(float(lower_ci_e_pow_boot), 4),
            ci_upper=round(min(float(upper_ci_e_pow_boot), 1.0), 4),
            standard_error=round(yuen_standard_error, 4),
        )

        results = TwoIndependentRobustResults()
        results.sample1 = sample1
        results.sample2 = sample2
        results.inferential = inferential
        results.robust_akp = robust_akp
        results.robust_exp = robust_exp

        return results
