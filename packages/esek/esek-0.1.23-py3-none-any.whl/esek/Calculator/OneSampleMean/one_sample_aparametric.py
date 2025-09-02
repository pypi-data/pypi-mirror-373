"""
This module provides functionality for calculating the Aparametric effect size using the sign test for one sample.

Classes:
    AparametricOneSample: A class containing static methods for calculating the Aparametric effect size.

Methods:
    ApermetricEffectSizeOneSample: Calculate the Aparametric effect size using the sign test for one sample.
"""

import math
from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy.stats import norm, rankdata, median_abs_deviation


# Create results class
@dataclass
class OneSampleAparametricResults:
    """
    A class to store results from one-sample aparametric statistical tests.

    This class contains attributes to store various statistical measures including:
    - General summary statistics (sample size, means, medians etc.)
    - Wilcoxon test statistics (ignoring ties)
    - Rank biserial correlations
    - Confidence intervals
    - Statistical lines in formatted output
    - Pratt test statistics (considering ties)
    """

    sample: Optional[int | float] = None
    sample_median: Optional[int | float] = None
    median_of_the_difference: Optional[int | float] = None
    median_of_absolute_deviation: Optional[int | float] = None
    sample_mean: Optional[int | float] = None
    sample_standard_deviation: Optional[int | float] = None
    number_of_pairs: Optional[int | float] = None
    number_of_pairs_with_a_sign: Optional[int | float] = None
    number_of_times_sample_is_larger: Optional[int | float] = None
    number_of_times_sample_is_smaller: Optional[int | float] = None
    number_of_ties: Optional[int | float] = None

    # Wilcoxon Statistics (Wilcoxon Method that Ignores ties)
    wilcoxon_method: str = ""
    _______________: str = ""
    sum_of_the_positive_ranks_without_ties: Optional[int | float] = None
    sum_of_the_negative_ranks_without_ties: Optional[int | float] = None

    # Wilcoxon Sign Rank Test Statistics (Wilcoxon)
    wilcoxon_mean_w_without_ties: Optional[int | float] = None
    wilcoxon_standard_deviation: Optional[int | float] = None
    wilcoxon_z: Optional[int | float] = None
    wilcoxon_z_with_normal_approximation_continuity_correction: Optional[
        int | float
    ] = None
    wilcoxon_p_value: Optional[int | float] = None
    wilcoxon_p_value_with_normal_approximation_continuity_correction: Optional[
        int | float
    ] = None

    # Rank Biserial Correlation
    matched_pairs_rank_biserial_correlation_ignoring_ties: Optional[int | float] = None
    z_based_rank_biserial_correlation_wilcoxon_method: Optional[int | float] = None
    z_based_corrected_rank_biserial_correlation_wilcoxon_method: Optional[
        int | float
    ] = None

    # Confidence Intervals
    standard_error_of_the_matched_pairs_rank_biserial_correlation_wilcoxon_method: (
        Optional[int | float]
    ) = (None)
    lower_ci_matched_pairs_rank_biserial_wilcoxon: Optional[int | float] = None
    upper_ci_matched_pairs_rank_biserial_wilcoxon: Optional[int | float] = None
    lower_ci_z_based_rank_biserial_wilcoxon: Optional[int | float] = None
    upper_ci_z_based_rank_biserial_wilcoxon: Optional[int | float] = None
    lower_ci_z_based_corrected_rank_biserial_wilcoxon: Optional[int | float] = None
    upper_ci_z_based_corrected_rank_biserial_wilcoxon: Optional[int | float] = None

    # Statistical Lines Wilcoxon Method
    statistical_line_wilcoxon: Optional[int | float] = None
    statistical_line_wilcoxon_corrected: Optional[int | float] = None
    statistical_line_wilcoxon_matched_pairs: Optional[int | float] = None

    pratt_method: str = ""
    sum_of_the_positive_ranks_with_ties: Optional[int | float] = None
    sum_of_the_negative_ranks_with_ties: Optional[int | float] = None

    pratt_meanw_considering_ties: Optional[int | float] = None
    pratt_standard_deviation: Optional[int | float] = None
    pratt_z: Optional[int | float] = None
    pratt_z_with_normal_approximation_continuity_correction: Optional[int | float] = (
        None
    )
    pratt_p_value: Optional[int | float] = None
    pratt_p_value_with_normal_approximation_continuity_correction: Optional[
        int | float
    ] = None

    # Rank Biserial Correlation
    matched_pairs_rank_biserial_correlation_considering_ties: Optional[int | float] = (
        None
    )
    z_based_rank_biserial_correlation_pratt_method: Optional[int | float] = None
    z_based_corrected_rank_biserial_correlation_pratt_method: Optional[int | float] = (
        None
    )

    # Confidence Intervals
    standard_error_of_the_matched_pairs_rank_biserial_correlation_pratt_method: (
        Optional[int | float]
    ) = (None)
    lower_ci_matched_pairs_rank_biserial_pratt: Optional[int | float] = None
    upper_ci_matched_pairs_rank_biserial_pratt: Optional[int | float] = None
    lower_ci_z_based_rank_biserial_pratt: Optional[int | float] = None
    upper_ci_z_based_rank_biserial_pratt: Optional[int | float] = None
    lower_ci_z_based_corrected_rank_biserial_pratt: Optional[int | float] = None
    upper_ci_z_based_corrected_rank_biserial_pratt: Optional[int | float] = None

    # Statistical Lines
    statistical_line_pratt: Optional[int | float] = None
    statistical_line_pratt_corrected: Optional[int | float] = None
    statistical_line_pratt_matched_pairs: Optional[int | float] = None


def apermetric_effect_size_one_sample(params: dict) -> OneSampleAparametricResults:
    """
    Calculate the Aparametric effect size using the sign test for one sample.

    Parameters:
    params (dict): A dictionary containing the following keys:
        - "Column 1": A numpy array of sample data.
        - "Population's Value": The population value to compare against.
        - "Confidence Level": The confidence level as a percentage.

    Returns:
    dict: A dictionary containing the results of the Aparametric effect size calculations.
    """
    # region
    # Set Parameters
    column_1 = params["Column 1"]
    population_value = params["Population's Value"]
    confidence_level_percentages = params["Confidence Level"]

    # Calculation
    confidence_level = confidence_level_percentages / 100

    # General Summary Statistics
    sample_median_1 = np.median(column_1)
    sample_mean_1 = np.mean(column_1)
    sample_standard_deviation_1 = float(np.std(column_1, ddof=1))
    difference = column_1 - population_value
    positive_n = difference[difference > 0].shape[
        0
    ]  # How many times sample is greater than population value
    negative_n = difference[difference < 0].shape[
        0
    ]  # How many times sample is lower than population value
    zero_n = difference[difference == 0].shape[0]  # Number of ties
    sample_size = len(difference)
    median_difference = np.median(difference)
    median_absolute_deviation = float(median_abs_deviation(difference))

    # Summary Statistics for the Wilcoxon Sign Rank Test not Considering ties
    difference_no_ties = difference[difference != 0]  # This line removes the ties
    ranked_no_ties = rankdata(abs(difference_no_ties))
    positive_sum_ranks_no_ties = ranked_no_ties[difference_no_ties > 0].sum()
    negative_sum_ranks_no_ties = ranked_no_ties[difference_no_ties < 0].sum()

    # Summary Statistics for the Wilcoxon Sign Rank Considering ties
    ranked_with_ties = rankdata(abs(difference))
    positive_sum_ranks_with_ties = ranked_with_ties[difference > 0].sum()
    negative_sum_ranks_with_ties = ranked_with_ties[difference < 0].sum()

    # Wilcoxon Sign Rank Test Statistics Non Considering Ties (Wilcoxon Method)
    mean_w_not_considering_ties = (
        positive_sum_ranks_no_ties + negative_sum_ranks_no_ties
    ) / 2
    sign_no_ties = np.where(
        difference_no_ties == 0, 0, (np.where(difference_no_ties < 0, -1, 1))
    )
    ranked_signs_no_ties = sign_no_ties * ranked_no_ties
    ranked_signs_no_ties = np.where(difference_no_ties == 0, 0, ranked_signs_no_ties)
    unadjusted_variance_wilcoxon = (
        len(difference_no_ties)
        * (len(difference_no_ties) + 1)
        * (2 * (len(difference_no_ties)) + 1)
    ) / 24
    var_adj_t = (ranked_signs_no_ties * ranked_signs_no_ties).sum()
    adjusted_variance_wilcoxon = (1 / 4) * var_adj_t

    # Calculate The Z score wilcox
    z_numerator_wilcoxon = positive_sum_ranks_no_ties - mean_w_not_considering_ties
    z_numerator_wilcoxon = np.where(
        z_numerator_wilcoxon < 0, z_numerator_wilcoxon + 0.5, z_numerator_wilcoxon
    )

    z_adjusted_wilcoxon = (z_numerator_wilcoxon) / np.sqrt(adjusted_variance_wilcoxon)
    z_adjusted_normal_approximation_wilcoxon = (z_numerator_wilcoxon - 0.5) / np.sqrt(
        adjusted_variance_wilcoxon
    )
    z_unadjusted_wilcoxon = (z_numerator_wilcoxon) / np.sqrt(
        unadjusted_variance_wilcoxon
    )
    z_unadjusted_normal_approximation_wilcoxon = (z_numerator_wilcoxon - 0.5) / np.sqrt(
        unadjusted_variance_wilcoxon
    )
    p_value_adjusted_wilcoxon = min(
        float(norm.sf((abs(z_adjusted_wilcoxon))) * 2), 0.99999
    )
    p_value_adjusted_normal_approximation_wilcoxon = min(
        float(norm.sf((abs(z_adjusted_normal_approximation_wilcoxon))) * 2),
        0.99999,
    )
    p_value_unadjusted_wilcoxon = min(
        float(norm.sf((abs(z_unadjusted_wilcoxon))) * 2), 0.99999
    )
    p_value_unadjusted_normal_approximation_wilcoxon = min(
        float(norm.sf((abs(z_unadjusted_normal_approximation_wilcoxon))) * 2),
        0.99999,
    )

    # Wilcoxon Sign Rank Test Statistics Considering Ties (Pratt Method)
    mean_w_considering_ties = (
        positive_sum_ranks_with_ties + negative_sum_ranks_with_ties
    ) / 2
    sign_with_ties = np.where(difference == 0, 0, (np.where(difference < 0, -1, 1)))
    ranked_signs_with_ties = sign_with_ties * ranked_with_ties
    ranked_signs_with_ties = np.where(difference == 0, 0, ranked_signs_with_ties)
    var_adj_t_with_ties = (ranked_signs_with_ties * ranked_signs_with_ties).sum()
    adjusted_variance_pratt = (1 / 4) * var_adj_t_with_ties

    z_numerator_pratt = positive_sum_ranks_with_ties - mean_w_considering_ties
    z_numerator_pratt = np.where(
        z_numerator_pratt < 0, z_numerator_pratt + 0.5, z_numerator_pratt
    )

    z_adjusted_pratt = (z_numerator_pratt) / np.sqrt(adjusted_variance_pratt)
    z_adjusted_normal_approximation_pratt = (z_numerator_pratt - 0.5) / np.sqrt(
        adjusted_variance_pratt
    )
    p_value_adjusted_pratt = min(float(norm.sf((abs(z_adjusted_pratt))) * 2), 0.99999)
    p_value_adjusted_normal_approximation_pratt = min(
        float(norm.sf((abs(z_adjusted_normal_approximation_pratt))) * 2), 0.99999
    )

    # Matched Pairs Rank Biserial Correlation
    matched_pairs_rank_biserial_correlation_ignoring_ties = min(
        (positive_sum_ranks_no_ties - negative_sum_ranks_no_ties)
        / np.sum(ranked_no_ties),
        0.99999999,
    )  # This is the match paired rank biserial correlation using kerby formula that is not considering ties (Kerby, 2014)
    matched_pairs_rank_biserial_correlation_considering_ties = min(
        (positive_sum_ranks_with_ties - negative_sum_ranks_with_ties)
        / np.sum(ranked_with_ties),
        0.999999999,
    )  # this is the Kerby 2014 Formula - (With ties one can apply either Kerby or King Minium Formulae but not cureton - King's Formula is the most safe)

    # Z-based Rank Biserial Correlation (Note that since the Wilcoxon method is ignoring ties the sample size should actually be the number of the non tied pairs)
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

    # Confidence Intervals
    standard_error_match_pairs_rank_biserial_correlation_no_ties = np.sqrt(
        (
            (
                2 * (len(ranked_no_ties)) ** 3
                + 3 * (len(ranked_no_ties)) ** 2
                + (len(ranked_no_ties))
            )
            / 6
        )
        / (((len(ranked_no_ties)) ** 2 + (len(ranked_no_ties)) / 2))
    )
    standard_error_match_pairs_rank_biserial_correlation_with_ties = np.sqrt(
        ((2 * sample_size**3 + 3 * sample_size**2 + sample_size) / 6)
        / ((sample_size**2 + sample_size) / 2)
    )
    z_critical_value = norm.ppf((1 - confidence_level) + ((confidence_level) / 2))

    lower_ci_matched_pairs_wilcoxon = max(
        math.tanh(
            math.atanh(matched_pairs_rank_biserial_correlation_ignoring_ties)
            - z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_no_ties
        ),
        -1,
    )
    upper_ci_matched_pairs_wilcoxon = min(
        math.tanh(
            math.atanh(matched_pairs_rank_biserial_correlation_ignoring_ties)
            + z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_no_ties
        ),
        1,
    )
    lower_ci_z_based_wilcoxon = max(
        math.tanh(
            math.atanh(z_based_rank_biserial_correlation_no_ties)
            - z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_no_ties
        ),
        -1,
    )
    upper_ci_z_based_wilcoxon = min(
        math.tanh(
            math.atanh(z_based_rank_biserial_correlation_no_ties)
            + z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_no_ties
        ),
        1,
    )
    lower_ci_z_based_corrected_wilcoxon = max(
        math.tanh(
            math.atanh(z_based_rank_biserial_correlation_corrected_no_ties)
            - z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_no_ties
        ),
        -1,
    )
    upper_ci_z_based_corrected_wilcoxon = min(
        math.tanh(
            math.atanh(z_based_rank_biserial_correlation_corrected_no_ties)
            + z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_no_ties
        ),
        1,
    )

    lower_ci_matched_pairs_pratt = max(
        math.tanh(
            math.atanh(matched_pairs_rank_biserial_correlation_considering_ties)
            - z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_with_ties
        ),
        -1,
    )
    upper_ci_matched_pairs_pratt = min(
        math.tanh(
            math.atanh(matched_pairs_rank_biserial_correlation_considering_ties)
            + z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_with_ties
        ),
        1,
    )
    lower_ci_z_based_pratt = max(
        math.tanh(
            math.atanh(z_based_rank_biserial_correlation_with_ties)
            - z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_with_ties
        ),
        -1,
    )
    upper_ci_z_based_pratt = min(
        math.tanh(
            math.atanh(z_based_rank_biserial_correlation_with_ties)
            + z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_with_ties
        ),
        1,
    )
    lower_ci_z_based_corrected_pratt = max(
        math.tanh(
            math.atanh(z_based_rank_biserial_correlation_corrected_with_ties)
            - z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_with_ties
        ),
        -1,
    )
    upper_ci_z_based_corrected_pratt = min(
        math.tanh(
            math.atanh(z_based_rank_biserial_correlation_corrected_with_ties)
            + z_critical_value
            * standard_error_match_pairs_rank_biserial_correlation_with_ties
        ),
        1,
    )
    # endregion

    results = OneSampleAparametricResults()

    # General Summary Statistics
    results.sample = positive_sum_ranks_with_ties
    results.sample_median = round(sample_median_1, 4)
    results.median_of_the_difference = median_difference
    results.median_of_absolute_deviation = median_absolute_deviation
    results.sample_mean = round(sample_mean_1, 4)
    results.sample_standard_deviation = round(sample_standard_deviation_1, 4)
    results.number_of_pairs = sample_size
    results.number_of_pairs_with_a_sign = len(ranked_no_ties)
    results.number_of_times_sample_is_larger = positive_n
    results.number_of_times_sample_is_smaller = negative_n
    results.number_of_ties = zero_n

    # Wilcoxon Statistics (Wilcoxon Method that Ignores ties)
    results.sum_of_the_positive_ranks_without_ties = round(
        positive_sum_ranks_no_ties, 4
    )
    results.sum_of_the_negative_ranks_without_ties = round(
        negative_sum_ranks_no_ties, 4
    )

    # Wilcoxon Sign Rank Test Statistics (Wilcoxon)
    results.wilcoxon_mean_w_without_ties = mean_w_not_considering_ties
    results.wilcoxon_standard_deviation = np.sqrt(adjusted_variance_wilcoxon)
    results.wilcoxon_z = z_adjusted_wilcoxon
    results.wilcoxon_z_with_normal_approximation_continuity_correction = (
        z_adjusted_normal_approximation_wilcoxon
    )
    results.wilcoxon_p_value = p_value_adjusted_wilcoxon
    results.wilcoxon_p_value_with_normal_approximation_continuity_correction = (
        p_value_adjusted_normal_approximation_wilcoxon
    )

    # Rank Biserial Correlation
    results.matched_pairs_rank_biserial_correlation_ignoring_ties = round(
        matched_pairs_rank_biserial_correlation_ignoring_ties, 5
    )
    results.z_based_rank_biserial_correlation_wilcoxon_method = round(
        z_based_rank_biserial_correlation_no_ties, 5
    )
    results.z_based_corrected_rank_biserial_correlation_wilcoxon_method = round(
        z_based_rank_biserial_correlation_corrected_no_ties, 5
    )

    # Confidence Intervals
    results.standard_error_of_the_matched_pairs_rank_biserial_correlation_wilcoxon_method = round(
        standard_error_match_pairs_rank_biserial_correlation_no_ties, 4
    )
    results.lower_ci_matched_pairs_rank_biserial_wilcoxon = round(
        lower_ci_matched_pairs_wilcoxon, 5
    )
    results.upper_ci_matched_pairs_rank_biserial_wilcoxon = round(
        upper_ci_matched_pairs_wilcoxon, 5
    )
    results.lower_ci_z_based_rank_biserial_wilcoxon = round(
        lower_ci_z_based_wilcoxon, 5
    )
    results.upper_ci_z_based_rank_biserial_wilcoxon = round(
        upper_ci_z_based_wilcoxon, 5
    )
    results.lower_ci_z_based_corrected_rank_biserial_wilcoxon = round(
        lower_ci_z_based_corrected_wilcoxon, 5
    )
    results.upper_ci_z_based_corrected_rank_biserial_wilcoxon = round(
        upper_ci_z_based_corrected_wilcoxon, 5
    )

    results.sum_of_the_positive_ranks_with_ties = round(positive_sum_ranks_with_ties, 4)
    results.sum_of_the_negative_ranks_with_ties = round(negative_sum_ranks_with_ties, 4)

    results.pratt_meanw_considering_ties = mean_w_considering_ties
    results.pratt_standard_deviation = np.sqrt(adjusted_variance_pratt)
    results.pratt_z = z_adjusted_pratt
    results.pratt_z_with_normal_approximation_continuity_correction = (
        z_adjusted_normal_approximation_pratt
    )
    results.pratt_p_value = p_value_adjusted_pratt
    results.pratt_p_value_with_normal_approximation_continuity_correction = (
        p_value_adjusted_normal_approximation_pratt
    )

    # Rank Biserial Correlation
    results.matched_pairs_rank_biserial_correlation_considering_ties = round(
        matched_pairs_rank_biserial_correlation_considering_ties, 5
    )
    results.z_based_rank_biserial_correlation_pratt_method = round(
        z_based_rank_biserial_correlation_with_ties, 5
    )
    results.z_based_corrected_rank_biserial_correlation_pratt_method = round(
        z_based_rank_biserial_correlation_corrected_with_ties, 5
    )

    # Confidence Intervals
    results.standard_error_of_the_matched_pairs_rank_biserial_correlation_pratt_method = round(
        standard_error_match_pairs_rank_biserial_correlation_with_ties, 4
    )
    results.lower_ci_matched_pairs_rank_biserial_pratt = round(
        lower_ci_matched_pairs_pratt, 5
    )
    results.upper_ci_matched_pairs_rank_biserial_pratt = round(
        upper_ci_matched_pairs_pratt, 5
    )
    results.lower_ci_z_based_rank_biserial_pratt = round(lower_ci_z_based_pratt, 5)
    results.upper_ci_z_based_rank_biserial_pratt = round(upper_ci_z_based_pratt, 5)
    results.lower_ci_z_based_corrected_rank_biserial_pratt = round(
        lower_ci_z_based_corrected_pratt, 5
    )
    results.upper_ci_z_based_corrected_rank_biserial_pratt = round(
        upper_ci_z_based_corrected_pratt, 5
    )

    return results


# Things to Consider
# 1. Consider adding other CI's for example metsamuuronen method for sommers delta (which in the case of two groups equals the rank biserial correlation)
# 2. Test if the matched pairs version is also equal to Sommers delta and cliffs delta (dependent version)
# 3. For convenience change the confidence levels to percentages and not decimals
