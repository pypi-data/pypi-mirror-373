"""
This module implements the TwoIndependentControlGroupTests class, which provides methods
for conducting statistical tests on two independent control groups.
"""

from dataclasses import dataclass
from typing import Optional
import math
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es, texts


@dataclass
class TwoIndependentControlGroupResults:
    """
    This class holds the results of the two independent control group tests.
    """

    inferential: Optional[res.InferentialStatistics] = None
    glass_delta: Optional[es.GlassDelta] = None
    glass_delta_unbiased: Optional[es.GlassDeltaUnbiased] = None
    experimental_group: Optional[res.Group] = None
    control_group: Optional[res.Group] = None


class TwoIndependentControlGroupTests(interfaces.AbstractTest):
    """
    This class provides methods for conducting statistical tests on two independent control groups.

    Methods:
        - from_score: Not implemented.
        - from_parameters: Creates test results from the given parameters.
        - from_data: Creates test results from the given data.

    """

    @utils.not_implemented(
        interfaces.MethodType.FROM_SCORE, "TwoIndependentControlGroup"
    )
    @staticmethod
    def from_score() -> None:
        """
        A static method to create results from a score.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
                        NotImplementedError: This method is not implemented for TwoIndependentControlGroup.
        """
        pass

    @staticmethod
    def from_parameters(
        sample_mean_experimental: float,
        sample_mean_control: float,
        sample_sd_experimental: float,
        sample_sd_control: float,
        sample_size_experimental: int,
        sample_size_control: int,
        population_mean_diff: float = 0,
        confidence_level: float = 0.95,
    ) -> TwoIndependentControlGroupResults:
        """
        Creates test results from the given parameters.

        Args:
            sample_mean_experimental (float): The mean of the experimental group.
            sample_mean_control (float): The mean of the control group.
            sample_sd_experimental (float): The standard deviation of the experimental group.
            sample_sd_control (float): The standard deviation of the control group.
            sample_size_experimental (int): The sample size of the experimental group.
            sample_size_control (int): The sample size of the control group.
            population_mean_diff (float, optional): The population mean difference. Defaults to 0.
            confidence_level (float, optional): The confidence level for the tests. Defaults to 0.95.

        Returns:
            TwoIndependentControlGroupResults: The results of the tests.
        """
        sample_size = sample_size_experimental + sample_size_control
        df = sample_size - 2
        sample_mean_difference = sample_mean_experimental - sample_mean_control
        standardizer_glass_delta = np.sqrt(
            (
                (((sample_size_experimental - 1) * sample_sd_experimental**2))
                + ((sample_size_control - 1) * sample_sd_control**2)
            )
            / (sample_size - 2)
        )
        standard_error = standardizer_glass_delta * np.sqrt(
            (sample_size_experimental + sample_size_control)
            / (sample_size_experimental * sample_size_control)
        )
        t_score = (sample_mean_difference - population_mean_diff) / standard_error
        t_score_glass = (sample_mean_difference - population_mean_diff) / (
            sample_sd_control / np.sqrt(sample_size_control)
        )
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        glass_delta = (
            sample_mean_difference - population_mean_diff
        ) / sample_sd_control
        df2 = sample_size_control - 1
        correction = math.exp(
            math.lgamma(df2 / 2)
            - math.log(math.sqrt(df2 / 2))
            - math.lgamma((df2 - 1) / 2)
        )
        unbiased_glass_delta = glass_delta * correction
        standardizer_unbiased_glass_delta = standardizer_glass_delta / correction
        ci_lower_glass_delta_pivotal, ci_upper_glass_delta_pivotal = utils.pivotal_ci_t(
            t_score_glass, df2, sample_size_control, confidence_level
        )
        (
            ci_lower_glass_delta_central,
            ci_upper_glass_delta_central,
            standard_error_glass_delta,
        ) = utils.ci_from_cohens_paired(
            glass_delta, sample_size_control, confidence_level
        )
        (
            ci_lower_glass_delta_unbiased_central,
            ci_upper_glass_delta_unbiased_central,
            standard_error_glass_delta_unbiased,
        ) = utils.ci_from_cohens_paired(
            unbiased_glass_delta, sample_size_control, confidence_level
        )

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            score=round(t_score, 4),
            p_value=round(p_value, 4),
        )
        inferential.degrees_of_freedom = round(df, 4)
        inferential.standard_error = round(standard_error, 4)
        inferential.means_difference = round(sample_mean_difference, 4)

        glass_delta_es: es.GlassDelta = es.GlassDelta(
            value=round(glass_delta, 4),
            ci_lower=round(ci_lower_glass_delta_central, 4),
            ci_upper=round(ci_upper_glass_delta_central, 4),
            standard_error=round(standard_error_glass_delta, 4),
        )
        glass_delta_es.standardizer = round(standardizer_glass_delta, 4)
        glass_delta_es.update_pivotal_ci(
            round(ci_lower_glass_delta_pivotal, 4),
            round(ci_upper_glass_delta_pivotal, 4),
        )

        glass_delta_unbiased: es.GlassDeltaUnbiased = es.GlassDeltaUnbiased(
            value=round(unbiased_glass_delta, 4),
            ci_lower=round(ci_lower_glass_delta_unbiased_central, 4),
            ci_upper=round(ci_upper_glass_delta_unbiased_central, 4),
            standard_error=round(standard_error_glass_delta_unbiased, 4),
        )
        glass_delta_unbiased.standardizer = round(standardizer_unbiased_glass_delta, 4)
        glass_delta_unbiased.update_pivotal_ci(
            round(ci_lower_glass_delta_pivotal * correction, 4),
            round(ci_upper_glass_delta_pivotal * correction, 4),
        )

        results = TwoIndependentControlGroupResults()
        results.inferential = inferential
        results.glass_delta = glass_delta_es
        results.glass_delta_unbiased = glass_delta_unbiased

        return results

    @staticmethod
    def from_data(
        columns: list[list], population_mean_diff: float, confidence_level: float = 0.95
    ) -> TwoIndependentControlGroupResults:
        """
        Creates test results from the given data.

        Args:
            columns (list[list]): The data columns for the control and experimental groups.
            population_mean_diff (float): The population mean difference.
            confidence_level (float): The confidence level for the tests. Defaults to 0.95.

        Returns:
            TwoIndependentControlGroupResults: The results of the tests.

        Raises:
            ValueError: If columns length is not 2.
        """
        if len(columns) != 2:
            raise ValueError(texts.Errors.columns_must_be_two)

        column_1 = columns[0]
        column_2 = columns[1]

        sample_mean_control = np.mean(column_1)
        sample_mean_experimental = np.mean(column_2)
        sample_sd_control = np.std(column_1, ddof=1)
        sample_sd_experimental = np.std(column_2, ddof=1)
        sample_size_control = len(column_1)
        sample_size_experimental = len(column_2)
        sample_size = sample_size_control + sample_size_experimental
        df = sample_size - 2
        sample_mean_difference = sample_mean_experimental - sample_mean_control
        standardizer_glass_delta = np.sqrt(
            (
                (((sample_size_experimental - 1) * sample_sd_experimental**2))
                + ((sample_size_control - 1) * sample_sd_control**2)
            )
            / (sample_size - 2)
        )
        standard_error = standardizer_glass_delta * np.sqrt(
            (sample_size_experimental + sample_size_control)
            / (sample_size_experimental * sample_size_control)
        )
        t_score = (sample_mean_difference - population_mean_diff) / standard_error
        t_score_glass = (sample_mean_difference - population_mean_diff) / (
            sample_sd_control / np.sqrt(sample_size_control)
        )
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        glass_delta = (
            sample_mean_difference - population_mean_diff
        ) / sample_sd_control
        df2 = sample_size_control - 1
        correction = math.exp(
            math.lgamma(df2 / 2)
            - math.log(math.sqrt(df2 / 2))
            - math.lgamma((df2 - 1) / 2)
        )
        unbiased_glass_delta = glass_delta * correction
        standardizer_unbiased_glass_delta = standardizer_glass_delta / correction
        ci_lower_glass_delta_pivotal, ci_upper_glass_delta_pivotal = utils.pivotal_ci_t(
            t_score_glass, df2, sample_size_control, confidence_level
        )
        (
            ci_lower_glass_delta_central,
            ci_upper_glass_delta_central,
            standard_error_glass_delta,
        ) = utils.ci_from_cohens_paired(
            float(glass_delta), sample_size_control, confidence_level
        )
        (
            ci_lower_glass_delta_unbiased_central,
            ci_upper_glass_delta_unbiased_central,
            standard_error_glass_delta_unbiased,
        ) = utils.ci_from_cohens_paired(
            float(unbiased_glass_delta), sample_size_control, confidence_level
        )

        experimental_group: res.Group = res.Group(
            mean=float(sample_mean_experimental),
            standard_deviation=float(sample_sd_experimental),
        )
        experimental_group.sample_size = sample_size_experimental
        experimental_group.mean_diff = float(round(sample_mean_difference, 4))

        control_group: res.Group = res.Group(
            mean=float(sample_mean_control),
            standard_deviation=float(sample_sd_control),
        )
        control_group.sample_size = sample_size_control
        control_group.mean_diff = float(round(sample_mean_difference, 4))

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            score=round(t_score, 4), p_value=round(p_value, 4)
        )
        inferential.degrees_of_freedom = round(df, 4)
        inferential.standard_error = round(standard_error, 4)

        glass_delta_es: es.GlassDelta = es.GlassDelta(
            value=round(float(glass_delta), 4),
            standard_error=round(standard_error_glass_delta, 4),
            ci_lower=round(ci_lower_glass_delta_central, 4),
            ci_upper=round(ci_upper_glass_delta_central, 4),
        )
        glass_delta_es.standardizer = round(standardizer_glass_delta, 4)
        glass_delta_es.update_pivotal_ci(
            round(ci_lower_glass_delta_pivotal, 4),
            round(ci_upper_glass_delta_pivotal, 4),
        )

        glass_delta_unbiased_es: es.GlassDeltaUnbiased = es.GlassDeltaUnbiased(
            value=round(float(unbiased_glass_delta), 4),
            standard_error=round(standard_error_glass_delta_unbiased, 4),
            ci_lower=round(ci_lower_glass_delta_unbiased_central, 4),
            ci_upper=round(ci_upper_glass_delta_unbiased_central, 4),
        )
        glass_delta_unbiased_es.standardizer = round(
            standardizer_unbiased_glass_delta, 4
        )
        glass_delta_unbiased_es.update_pivotal_ci(
            round(ci_lower_glass_delta_pivotal * correction, 4),
            round(ci_upper_glass_delta_pivotal * correction, 4),
        )

        results = TwoIndependentControlGroupResults()
        results.experimental_group = experimental_group
        results.control_group = control_group
        results.inferential = inferential
        results.glass_delta = glass_delta_es
        results.glass_delta_unbiased = glass_delta_unbiased_es

        return results
