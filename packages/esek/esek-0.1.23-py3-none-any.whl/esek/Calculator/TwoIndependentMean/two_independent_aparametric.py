"""
TwoIndependentAparametric module provides functionality for performing two independent aparametric tests.
It includes methods for calculating statistics such as U-statistic, mean ranks, and rank-biserial correlation.
The results are encapsulated in a dataclass for easy access and manipulation.
"""

from dataclasses import dataclass
from typing import Optional
from collections import Counter
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es, texts


@dataclass
class TwoIndependentAparametricResults:
    """
    A class to store results from two independent aparametric tests.
    """

    group1: Optional[res.Group] = None
    group2: Optional[res.Group] = None
    exact_inferential: Optional[res.InferentialStatistics] = None
    inferential: Optional[res.InferentialStatistics] = None
    corrected_inferential: Optional[res.InferentialStatistics] = None
    rank_biserial_correlation: Optional[es.Biserial] = None
    z_based_rank_biserial_correlation: Optional[es.Biserial] = None
    z_based_rank_biserial_correlation_corrected: Optional[es.Biserial] = None


class TwoIndependentAparametricTests(interfaces.AbstractTest):
    """
    A class to perform two independent aparametric tests.
    This class implements methods to calculate various statistics and effect sizes.

    It is designed to be used with two independent samples, calculating U-statistic, mean ranks,
    and rank-biserial correlation, among other statistics.

    Attributes:
        None

    Methods:
        from_score: Not implemented.
        from_parameters: Not implemented.
        from_data: Creates results from data columns.
        compute_confidence_interval: Computes confidence intervals for a given correlation.
    """

    @staticmethod
    def from_score() -> TwoIndependentAparametricResults:
        """
        A static method to create results from a score.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
            NotImplementedError: This method is not implemented for TwoIndependentAparametric.
        """
        raise NotImplementedError(
            "from_score method is not implemented for TwoIndependentAparametric."
        )

    @staticmethod
    def from_parameters() -> TwoIndependentAparametricResults:
        """
        A static method to create results from parameters.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
            NotImplementedError: This method is not implemented for TwoIndependentAparametric.
        """
        raise NotImplementedError(
            "from_parameters method is not implemented for TwoIndependentAparametric."
        )

    @staticmethod
    def from_data(
        columns: list, confidence_level: float = 0.95
    ) -> TwoIndependentAparametricResults:
        """
        Create results from data columns.

        Args:
            columns (list): A list containing two numpy arrays or lists representing the two independent samples.
            confidence_level (float): The confidence level for the confidence intervals, default is 0.95.
        Returns:
            TwoIndependentAparametricResults: An instance containing the results of the two independent aparametric tests.
        Raises:
            ValueError: If the length of columns is not 2.
        """
        if len(columns) != 2:
            raise ValueError(texts.Errors.columns_must_be_two)

        column_1 = columns[0]
        column_2 = columns[1]
        sample_median_1 = np.median(column_1)
        sample_median_2 = np.median(column_2)
        sample_mean_1 = np.mean(column_1)
        sample_mean_2 = np.mean(column_2)
        sample_size_1 = len(column_1)
        sample_size_2 = len(column_2)
        sample_size = sample_size_1 + sample_size_2

        merged_samples = np.append(column_1, column_2)
        ranks = stats.rankdata(merged_samples, method="average")
        sum_ranks_1 = np.sum(ranks[:sample_size_1])
        sum_ranks_2 = np.sum(ranks[sample_size_1:])
        mean_ranks_1 = np.mean(ranks[:sample_size_1])
        mean_ranks_2 = np.mean(ranks[sample_size_1:])

        freq = Counter(merged_samples)
        frequencies = list(freq.values())
        ties_correction = [(f**3 - f) for f in frequencies]
        multiplicity_factor = sum(ties_correction)

        mean_w_1 = (sample_size_1 * (sample_size + 1)) / 2
        mean_w_2 = (sample_size_2 * (sample_size + 1)) / 2
        u_statistic_1 = sum_ranks_1 - (sample_size_1 * (sample_size_1 + 1)) / 2
        u_statistic_2 = sum_ranks_2 - (sample_size_2 * (sample_size_2 + 1)) / 2
        variance = (
            (sample_size_1 * sample_size_2 * (sample_size_1 + sample_size_2 + 1)) / 12
        ) - ((sample_size_1 * sample_size_2 * (multiplicity_factor))) / (
            12 * sample_size * (sample_size - 1)
        )

        z_score = abs(sum_ranks_1 - mean_w_1) / np.sqrt(variance)
        z_score_corrected = (abs(sum_ranks_1 - mean_w_1) - 0.5) / np.sqrt(variance)

        p_value = min(float(stats.norm.sf((abs(z_score))) * 2), 0.99999)
        p_value_corrected = min(
            float(stats.norm.sf((abs(z_score_corrected))) * 2), 0.99999
        )

        rank_biserial_correlation = (u_statistic_1 - u_statistic_2) / (
            u_statistic_1 + u_statistic_2
        )
        rosenthal_rank_biserial_correlation_z = z_score / np.sqrt(sample_size)
        rosenthal_rank_biserial_correlation_z_corrected = z_score_corrected / np.sqrt(
            sample_size
        )

        exact_p_value = stats.mannwhitneyu(column_1, column_2, method="exact")[1]

        standard_error_rbc = np.sqrt(
            (sample_size_1 + sample_size_2 + 1) / (3 * sample_size_1 + sample_size_2)
        )
        z_critical_value = float(
            stats.norm.ppf((1 - confidence_level) + ((confidence_level) / 2))
        )

        lower_ci_rank_biserial_correlation, upper_ci_rank_biserial_correlation = (
            utils.compute_fisher_confidence_interval(
                rank_biserial_correlation, standard_error_rbc, (z_critical_value)
            )
        )

        lower_ci_z_based, upper_ci_z_based = utils.compute_fisher_confidence_interval(
            rosenthal_rank_biserial_correlation_z, standard_error_rbc, z_critical_value
        )

        lower_ci_z_based_corrected, upper_ci_z_based_corrected = (
            utils.compute_fisher_confidence_interval(
                rosenthal_rank_biserial_correlation_z_corrected,
                standard_error_rbc,
                z_critical_value,
            )
        )

        group1 = res.Group(
            mean=round(mean_w_1, 4),
            median=round(sample_median_1, 4),
            standard_deviation=round(np.sqrt(variance), 4),
        )
        group2 = res.Group(
            mean=round(mean_w_2, 4),
            median=round(sample_median_2, 4),
            standard_deviation=round(np.sqrt(variance), 4),
        )
        group1.sample_size = sample_size_1
        group1.u_statistic = round(u_statistic_1, 4)
        group1.w_statistic = round(sum_ranks_1, 4)
        group1.mean_rank = float(round(mean_ranks_1, 4))

        group2.sample_size = sample_size_2
        group2.u_statistic = round(u_statistic_2, 4)
        group2.w_statistic = round(sum_ranks_2, 4)
        group2.mean_rank = float(round(mean_ranks_2, 4))

        inferential = res.InferentialStatistics(
            score=round(z_score, 4),
            p_value=round(p_value, 6),
        )
        corrected_inferential = res.InferentialStatistics(
            score=round(z_score_corrected, 4),
            p_value=round(p_value_corrected, 6),
        )
        exact_inferential = res.InferentialStatistics(
            score=round(z_score, 4),
            p_value=round(exact_p_value, 6),
        )

        rank_biserial_correlation_result = es.Biserial(
            name="Rank Biserial Correlation",
            value=round(rank_biserial_correlation, 4),
            ci_lower=lower_ci_rank_biserial_correlation,
            ci_upper=upper_ci_rank_biserial_correlation,
            standard_error=standard_error_rbc,
        )
        z_based_rank_biserial_correlation_result = es.Biserial(
            name="Z Based Rank Biserial Correlation",
            value=round(rosenthal_rank_biserial_correlation_z, 4),
            ci_lower=lower_ci_z_based,
            ci_upper=upper_ci_z_based,
            standard_error=standard_error_rbc,
        )
        z_based_rank_biserial_correlation_corrected_result = es.Biserial(
            name="Z Based Rank Biserial Correlation (Corrected)",
            value=round(rosenthal_rank_biserial_correlation_z_corrected, 6),
            ci_lower=lower_ci_z_based_corrected,
            ci_upper=upper_ci_z_based_corrected,
            standard_error=standard_error_rbc,
        )

        results = TwoIndependentAparametricResults()
        results.group1 = group1
        results.group2 = group2
        results.inferential = inferential
        results.corrected_inferential = corrected_inferential
        results.exact_inferential = exact_inferential
        results.rank_biserial_correlation = rank_biserial_correlation_result
        results.z_based_rank_biserial_correlation = (
            z_based_rank_biserial_correlation_result
        )
        results.z_based_rank_biserial_correlation_corrected = (
            z_based_rank_biserial_correlation_corrected_result
        )

        return results
