"""
TwoPairedAparametric module for performing two paired aparametric tests.
This module implements the TwoPairedAparametricTests class, which provides methods
for calculating various statistics related to two paired aparametric tests, such as
Wilcoxon signed-rank tests and rank biserial correlations.
It includes methods for computing results from data, score, and parameters, as well as
calculating confidence intervals for the results.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es


@dataclass
class TwoPairedAparametricResults:
    """
    A class to store results from two paired aparametric tests.
    """

    group1: Optional[res.Group] = None
    group2: Optional[res.Group] = None
    wilcoxon_sign_rank: Optional[res.WilcoxonSignedRank] = None
    matched_pairs_biserial_wilcoxon: Optional[es.Biserial] = None
    z_based_biserial_wilcoxon: Optional[es.Biserial] = None
    corrected_z_based_biserial_wilcoxon: Optional[es.Biserial] = None
    matched_pairs_biserial_pratt: Optional[es.Biserial] = None
    z_based_biserial_pratt: Optional[es.Biserial] = None
    corrected_z_based_biserial_pratt: Optional[es.Biserial] = None


class TwoPairedAparametricTests(interfaces.AbstractTest):
    """
    A class to perform two paired aparametric tests, such as Wilcoxon signed-rank tests
    and rank biserial correlations.
    This class provides methods to compute results from data, score, and parameters,
    as well as to calculate confidence intervals for the results.
    Methods:
        from_score: Not implemented, raises NotImplementedError.
        from_parameters: Not implemented, raises NotImplementedError.
        from_data: Computes results from provided data columns, population difference,
            and confidence level.
        compute_confidence_interval: Computes the lower and upper confidence intervals
            for a given correlation
    """

    @staticmethod
    def from_score() -> TwoPairedAparametricResults:
        """
        A static method to create results from a score.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
            NotImplementedError: This method is not implemented for TwoPairedAparametric.
        """
        raise NotImplementedError(
            "from_score method is not implemented for TwoPairedAparametric."
        )

    @staticmethod
    def from_parameters() -> TwoPairedAparametricResults:
        """
        A static method to create results from parameters.
        This method is not implemented and will raise a NotImplementedError.
        Raises:
            NotImplementedError: This method is not implemented for TwoPairedAparametric.
        """
        raise NotImplementedError(
            "from_score method is not implemented for TwoPairedAparametric."
        )

    @staticmethod
    def from_data(
        columns: list, population_difference: float, confidence_level: float
    ) -> TwoPairedAparametricResults:
        """
        Computes results from two paired aparametric tests using provided data columns,
        population difference, and confidence level.

        Args:
            columns (list): A list containing two numpy arrays representing the paired data.
            population_difference (float): The expected difference between the two populations.
            confidence_level (float): The confidence level for the confidence intervals.

        Returns:
            TwoPairedAparametricResults: An instance containing the results of the tests,
            including group statistics, Wilcoxon signed-rank results, and rank biserial correlations.
        """
        column_1 = columns[0]
        column_2 = columns[1]

        sample_median_1 = np.median(column_1)
        sample_median_2 = np.median(column_2)
        sample_mean_1 = np.mean(column_1)
        sample_mean_2 = np.mean(column_2)
        sample_standard_deviation_1 = np.std(column_1, ddof=1)
        sample_standard_deviation_2 = np.std(column_2, ddof=1)
        difference = (np.array(column_1) - np.array(column_2)) - population_difference
        positive_n = difference[difference > 0].shape[0]
        negative_n = difference[difference < 0].shape[0]
        zero_n = difference[difference == 0].shape[0]
        sample_size = len(difference)
        median_difference = np.median(difference)
        median_absolute_deviation = stats.median_abs_deviation(difference)

        difference_no_ties = difference[difference != 0]
        ranked_no_ties = stats.rankdata(abs(difference_no_ties))
        positive_sum_ranks_no_ties = ranked_no_ties[difference_no_ties > 0].sum()
        negative_sum_ranks_no_ties = ranked_no_ties[difference_no_ties < 0].sum()

        ranked_with_ties = stats.rankdata(abs(difference))
        positive_sum_ranks_with_ties = ranked_with_ties[difference > 0].sum()
        negative_sum_ranks_with_ties = ranked_with_ties[difference < 0].sum()

        meanw_not_considering_ties = (
            positive_sum_ranks_no_ties + negative_sum_ranks_no_ties
        ) / 2
        sign_no_ties = np.where(
            difference_no_ties == 0, 0, (np.where(difference_no_ties < 0, -1, 1))
        )
        ranked_signs_no_ties = sign_no_ties * ranked_no_ties
        ranked_signs_no_ties = np.where(
            difference_no_ties == 0, 0, ranked_signs_no_ties
        )
        unadjusted_variance_wilcoxon = (
            len(difference_no_ties)
            * (len(difference_no_ties) + 1)
            * (2 * (len(difference_no_ties)) + 1)
        ) / 24
        var_adj_T = (ranked_signs_no_ties * ranked_signs_no_ties).sum()
        adjusted_variance_wilcoxon = (1 / 4) * var_adj_T

        z_numerator_wilcoxon = positive_sum_ranks_no_ties - meanw_not_considering_ties
        z_numerator_wilcoxon = np.where(
            z_numerator_wilcoxon < 0, z_numerator_wilcoxon + 0.5, z_numerator_wilcoxon
        )

        z_adjusted_wilcoxon = (z_numerator_wilcoxon) / np.sqrt(
            adjusted_variance_wilcoxon
        )
        z_adjusted_normal_approximation_wilcoxon = (
            z_numerator_wilcoxon - 0.5
        ) / np.sqrt(adjusted_variance_wilcoxon)
        z_unadjusted_wilcoxon = (z_numerator_wilcoxon) / np.sqrt(
            unadjusted_variance_wilcoxon
        )
        z_unadjusted_normal_approximation_wilcoxon = (
            z_numerator_wilcoxon - 0.5
        ) / np.sqrt(unadjusted_variance_wilcoxon)
        p_value_adjusted_wilcoxon = min(
            float(stats.norm.sf((abs(z_adjusted_wilcoxon))) * 2), 0.99999
        )
        p_value_adjusted_Normal_approximation_wilcoxon = min(
            float(stats.norm.sf((abs(z_adjusted_normal_approximation_wilcoxon))) * 2),
            0.99999,
        )
        p_value_unadjusted_wilcoxon = min(
            float(stats.norm.sf((abs(z_unadjusted_wilcoxon))) * 2), 0.99999
        )
        p_value_unadjusted_normal_approximation_wilcoxon = min(
            float(stats.norm.sf((abs(z_unadjusted_normal_approximation_wilcoxon))) * 2),
            0.99999,
        )

        meanw_considering_ties = (
            positive_sum_ranks_with_ties + negative_sum_ranks_with_ties
        ) / 2
        sign_with_ties = np.where(difference == 0, 0, (np.where(difference < 0, -1, 1)))
        ranked_signs_with_ties = sign_with_ties * ranked_with_ties
        ranked_signs_with_ties = np.where(difference == 0, 0, ranked_signs_with_ties)
        var_adj_t_with_ties = (ranked_signs_with_ties * ranked_signs_with_ties).sum()
        adjusted_variance_pratt = (1 / 4) * var_adj_t_with_ties

        z_numerator_pratt = positive_sum_ranks_with_ties - meanw_considering_ties
        z_numerator_pratt = np.where(
            z_numerator_pratt < 0, z_numerator_pratt + 0.5, z_numerator_pratt
        )

        z_adjusted_pratt = (z_numerator_pratt) / np.sqrt(adjusted_variance_pratt)

        z_adjusted_normal_approximation_pratt = (z_numerator_pratt - 0.5) / np.sqrt(
            adjusted_variance_pratt
        )
        p_value_adjusted_pratt = min(
            float(stats.norm.sf((abs(z_adjusted_pratt))) * 2), 0.99999
        )
        p_value_adjusted_normal_approximation_pratt = min(
            float(stats.norm.sf((abs(z_adjusted_normal_approximation_pratt))) * 2),
            0.99999,
        )

        matched_pairs_rank_biserial_corelation_ignoring_ties = (
            positive_sum_ranks_no_ties - negative_sum_ranks_no_ties
        ) / np.sum(ranked_no_ties)
        matched_pairs_rank_biserial_corelation_considering_ties = (
            positive_sum_ranks_with_ties - negative_sum_ranks_with_ties
        ) / np.sum(ranked_with_ties)

        z_based_rank_biserial_correlation_no_ties = z_adjusted_wilcoxon / np.sqrt(
            len(ranked_no_ties)
        )
        z_based_rank_biserial_correlation_corrected_no_ties = (
            z_adjusted_normal_approximation_wilcoxon / np.sqrt(len(ranked_no_ties))
        )
        z_based_rank_biserial_correlation_with_ties = z_adjusted_pratt / np.sqrt(
            sample_size
        )
        z_based_rank_biserial_correlation_corrected_with_ties = (
            z_adjusted_normal_approximation_pratt / np.sqrt(sample_size)
        )

        standard_error_match_pairs_rank_biserial_corelation_no_ties = np.sqrt(
            (
                (
                    2 * (len(ranked_no_ties)) ** 3
                    + 3 * (len(ranked_no_ties)) ** 2
                    + (len(ranked_no_ties))
                )
                / 6
            )
            / (((len(ranked_no_ties)) ** 2 + (len(ranked_no_ties))) / 2)
        )
        standard_error_match_pairs_rank_biserial_corelation_with_ties = np.sqrt(
            ((2 * sample_size**3 + 3 * sample_size**2 + sample_size) / 6)
            / ((sample_size**2 + sample_size) / 2)
        )
        z_critical_value = float(
            stats.norm.ppf((1 - confidence_level) + ((confidence_level) / 2))
        )

        lower_ci_matched_pairs_wilcoxon, upper_ci_matched_pairs_wilcoxon = (
            utils.compute_fisher_confidence_interval(
                matched_pairs_rank_biserial_corelation_ignoring_ties,
                standard_error_match_pairs_rank_biserial_corelation_no_ties,
                z_critical_value,
            )
        )

        lower_ci_z_based_wilcoxon, upper_ci_z_based_wilcoxon = (
            utils.compute_fisher_confidence_interval(
                z_based_rank_biserial_correlation_no_ties,
                standard_error_match_pairs_rank_biserial_corelation_no_ties,
                z_critical_value,
            )
        )

        lower_ci_z_based_corrected_wilcoxon, upper_ci_z_based_corrected_wilcoxon = (
            utils.compute_fisher_confidence_interval(
                z_based_rank_biserial_correlation_corrected_no_ties,
                standard_error_match_pairs_rank_biserial_corelation_no_ties,
                z_critical_value,
            )
        )

        lower_ci_matched_pairs_pratt, upper_ci_matched_pairs_pratt = (
            utils.compute_fisher_confidence_interval(
                matched_pairs_rank_biserial_corelation_considering_ties,
                standard_error_match_pairs_rank_biserial_corelation_with_ties,
                z_critical_value,
            )
        )

        lower_ci_z_based_pratt, upper_ci_z_based_pratt = (
            utils.compute_fisher_confidence_interval(
                z_based_rank_biserial_correlation_with_ties,
                standard_error_match_pairs_rank_biserial_corelation_with_ties,
                z_critical_value,
            )
        )

        lower_ci_z_based_corrected_pratt, upper_ci_z_based_corrected_pratt = (
            utils.compute_fisher_confidence_interval(
                z_based_rank_biserial_correlation_corrected_with_ties,
                standard_error_match_pairs_rank_biserial_corelation_with_ties,
                z_critical_value,
            )
        )

        group1 = res.Group(
            mean=round(sample_mean_1, 4),
            median=round(sample_median_1, 4),
            standard_deviation=round(float(sample_standard_deviation_1), 4),
            median_absolute_deviation=float(median_absolute_deviation),
        )
        group2 = res.Group(
            mean=round(sample_mean_2, 4),
            median=round(sample_median_2, 4),
            standard_deviation=round(float(sample_standard_deviation_2), 4),
            median_absolute_deviation=float(median_absolute_deviation),
        )

        group1.diff_median = float(median_difference)
        group2.diff_median = float(median_difference)

        wilcoxon_sign_rank = res.WilcoxonSignedRank(
            times_group1_larger=positive_n,
            times_group2_larger=round(negative_n, 4),
            ties=zero_n,
            num_of_pairs=sample_size,
            num_of_non_tied_pairs=len(ranked_no_ties),
        )

        matched_pairs_biserial_wilcoxon = es.Biserial(
            name="Matched Pairs Rank Biserial (Wilcoxon Method)",
            value=round(matched_pairs_rank_biserial_corelation_ignoring_ties, 5),
            standard_error=round(
                standard_error_match_pairs_rank_biserial_corelation_no_ties, 4
            ),
            ci_lower=round(lower_ci_matched_pairs_wilcoxon, 5),
            ci_upper=round(upper_ci_matched_pairs_wilcoxon, 5),
        )
        z_based_biserial_wilcoxon = es.Biserial(
            name="Z-based Rank Biserial Correlation (Wilcoxon Method)",
            value=round(z_based_rank_biserial_correlation_no_ties, 5),
            standard_error=round(
                standard_error_match_pairs_rank_biserial_corelation_no_ties, 4
            ),
            ci_lower=round(lower_ci_z_based_wilcoxon, 5),
            ci_upper=round(upper_ci_z_based_wilcoxon, 5),
        )
        corrected_z_based_biserial_wilcoxon = es.Biserial(
            name="Corrected Z-based Rank Biserial Correlation (Wilcoxon Method)",
            value=round(z_based_rank_biserial_correlation_corrected_no_ties, 5),
            standard_error=round(
                standard_error_match_pairs_rank_biserial_corelation_no_ties, 4
            ),
            ci_lower=round(lower_ci_z_based_corrected_wilcoxon, 5),
            ci_upper=round(upper_ci_z_based_corrected_wilcoxon, 5),
        )

        matched_pairs_biserial_pratt = es.Biserial(
            name="Matched Pairs Rank Biserial (Pratt Method)",
            value=round(matched_pairs_rank_biserial_corelation_considering_ties, 5),
            standard_error=np.sqrt(adjusted_variance_pratt),
            ci_lower=round(lower_ci_matched_pairs_pratt, 5),
            ci_upper=round(upper_ci_matched_pairs_pratt, 5),
        )
        z_based_biserial_pratt = es.Biserial(
            name="Z-based Rank Biserial Correlation (Pratt Method)",
            value=round(z_based_rank_biserial_correlation_with_ties, 5),
            standard_error=np.sqrt(adjusted_variance_pratt),
            ci_lower=round(lower_ci_z_based_pratt, 5),
            ci_upper=round(upper_ci_z_based_pratt, 5),
        )
        corrected_z_based_biserial_pratt = es.Biserial(
            name="Corrected Z-based Rank Biserial Correlation (Pratt Method)",
            value=round(z_based_rank_biserial_correlation_corrected_with_ties, 5),
            standard_error=np.sqrt(adjusted_variance_pratt),
            ci_lower=round(lower_ci_z_based_corrected_pratt, 5),
            ci_upper=round(upper_ci_z_based_corrected_pratt, 5),
        )

        pratt_biserial = [
            matched_pairs_biserial_pratt,
            z_based_biserial_pratt,
            corrected_z_based_biserial_pratt,
        ]

        for biserial in pratt_biserial:
            biserial.p_value = p_value_adjusted_pratt
            biserial.z_score = z_adjusted_pratt

        wilcoxon_biserial = [
            matched_pairs_biserial_wilcoxon,
            z_based_biserial_wilcoxon,
            corrected_z_based_biserial_wilcoxon,
        ]

        for biserial in wilcoxon_biserial:
            biserial.p_value = p_value_adjusted_wilcoxon
            biserial.z_score = z_adjusted_wilcoxon

        results = TwoPairedAparametricResults()
        results.group1 = group1
        results.group2 = group2
        results.wilcoxon_sign_rank = wilcoxon_sign_rank
        results.matched_pairs_biserial_wilcoxon = matched_pairs_biserial_wilcoxon
        results.z_based_biserial_wilcoxon = z_based_biserial_wilcoxon
        results.corrected_z_based_biserial_wilcoxon = (
            corrected_z_based_biserial_wilcoxon
        )
        results.matched_pairs_biserial_pratt = matched_pairs_biserial_pratt
        results.z_based_biserial_pratt = z_based_biserial_pratt
        results.corrected_z_based_biserial_pratt = corrected_z_based_biserial_pratt

        return results
