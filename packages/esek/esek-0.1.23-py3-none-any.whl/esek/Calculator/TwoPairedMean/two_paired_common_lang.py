"""
A module for calculating common language effect sizes for two paired means.
This module provides functionality to compute various effect sizes such as CLES, Hedges' g,
and Cliff's delta, as well as their confidence intervals and other related statistics.
It includes methods for calculating effect sizes from scores, parameters, and data,
and provides a results class to encapsulate the output of these calculations.
This module is part of the Esek library, which is designed for statistical analysis and effect size
calculations.
"""

from dataclasses import dataclass
import math
from typing import Optional
import numpy as np
from scipy import stats
from ...utils import interfaces, utils, es


@dataclass
class TwoPairedCommonLangResults:
    """
    A class to hold the results of common language effect size calculations for two paired means.
        This class contains various effect size results such as CLES, Hedges' g, probability
    """

    cles_cohen: Optional[es.CLES] = None
    cles_hedges: Optional[es.CLES] = None
    probability_of_superiority: Optional[es.ProbabilityOfSuperiority] = None
    vargha_delaney: Optional[es.VarghaDelaney] = None
    cliff_delta: Optional[es.CliffsDelta] = None
    non_param_u1: Optional[es.NonParametricU1] = None
    non_param_u3: Optional[es.NonParametricU3] = None
    kraemer_andrew_gamma: Optional[es.KraemerAndrewGamma] = None
    wilcox_musaka_q: Optional[es.WilcoxMusakaQ] = None


class TwoPairedCommonLangTests(interfaces.AbstractTest):
    """
    A class to perform common language effect size calculations for two paired means.
    This class provides methods to calculate effect sizes from t-scores, parameters, and data.
    It includes methods for calculating CLES, Hedges' g, Cliff's delta, and other
    effect sizes, along with their confidence intervals and related statistics.

    This class is part of the Esek library, which is designed for statistical analysis
    and effect size calculations.

    Attributes:
            None

    Methods:
            from_score() ->
                    TwoPairedCommonLangResults:
                    Calculates common language effect sizes from a t-score, sample size, and confidence level
            from_parameters() -> TwoPairedCommonLangResults:
                    Calculates common language effect sizes from sample means, standard deviations,
                    sample size, population mean difference, correlation, and confidence level.
            from_data() -> TwoPairedCommonLangResults:
                    Calculates common language effect sizes from data in two columns.
                    The columns should contain paired samples, and the method computes various effect sizes
                    including CLES, Hedges' g, Cliff's delta, and others, along with their confidence intervals.
                    The method also handles bootstrapping for non-parametric effect sizes.
            pivotal_ci() -> tuple:
                    Calculates pivotal confidence intervals for the effect sizes based on the t-score,
                    degrees of freedom, sample size, and confidence level.
            calculate_central_ci( -> tuple:
                    Calculates central confidence intervals for Cohen's d effect size based on the
                    effect size, sample size, and confidence level.

    """

    @staticmethod
    def from_score(
        t_score: float, sample_size: int, confidence_level: float
    ) -> TwoPairedCommonLangResults:
        """
        Calculates common language effect sizes from a t-score, sample size, and confidence level.
        """

        cohens_dz = t_score / np.sqrt(sample_size)
        cles_dz = stats.norm.cdf(cohens_dz) * 100
        df = sample_size - 1
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gz = correction * cohens_dz
        cles_gz = stats.norm.cdf(hedges_gz) * 100
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)

        (
            ci_lower_cohens_dz_central,
            ci_upper_cohens_dz_central,
            standard_error_cohens_dz,
        ) = utils.ci_from_cohens_paired(cohens_dz, sample_size, confidence_level)
        (
            ci_lower_hedges_gz_central,
            ci_upper_hedges_gz_central,
            standard_error_hedges_gz,
        ) = utils.ci_from_cohens_paired(hedges_gz, sample_size, confidence_level)
        ci_lower_cohens_dz_pivotal, ci_upper_cohens_dz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_gz_pivotal, ci_upper_hedges_gz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )

        cles_cohen = es.CLES(
            method="cohen's dz",
            value=float(np.around(cles_dz, 4)),
            standard_error=standard_error_cohens_dz,
            ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_cohens_dz_central) * 100, 4)
            ),
            ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_cohens_dz_central) * 100, 4)
            ),
        )
        cles_hedges = es.CLES(
            method="hedges' gz",
            value=float(np.around(cles_gz, 4)),
            standard_error=standard_error_hedges_gz,
            ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_hedges_gz_central) * 100, 4)
            ),
            ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_hedges_gz_central) * 100, 4)
            ),
        )

        cles_cohen.update_pivotal_ci(
            pivotal_ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_cohens_dz_pivotal) * 100, 4)
            ),
            pivotal_ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_cohens_dz_pivotal) * 100, 4)
            ),
        )
        cles_hedges.update_pivotal_ci(
            pivotal_ci_lower=float(
                np.around(
                    stats.norm.cdf(ci_lower_hedges_gz_pivotal * correction) * 100, 4
                )
            ),
            pivotal_ci_upper=float(
                np.around(
                    stats.norm.cdf(ci_upper_hedges_gz_pivotal * correction) * 100, 4
                )
            ),
        )

        results = TwoPairedCommonLangResults()
        results.cles_cohen = cles_cohen
        results.cles_hedges = cles_hedges

        return results

    @staticmethod
    def from_parameters(
        sample_mean_1: float,
        sample_mean_2: float,
        sample_sd_1: float,
        sample_sd_2: float,
        sample_size: int,
        population_mean_diff: float,
        correlation: float,
        confidence_level: float,
    ) -> TwoPairedCommonLangResults:
        """
        Calculates common language effect sizes from sample means, standard deviations,
        """
        difference = sample_mean_1 - sample_mean_2
        mean_difference = np.mean(difference - population_mean_diff)

        standardizer_dz = np.sqrt(
            sample_sd_1**2
            + sample_sd_2**2
            - 2 * correlation * sample_sd_1 * sample_sd_2
        )
        cohens_dz = mean_difference / standardizer_dz
        cles_dz = stats.norm.cdf(cohens_dz) * 100
        t_score = cohens_dz * np.sqrt(sample_size)
        df = sample_size - 1
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gz = correction * cohens_dz
        cles_gz = stats.norm.cdf(hedges_gz) * 100
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)

        (
            ci_lower_cohens_dz_central,
            ci_upper_cohens_dz_central,
            standard_error_cohens_dz,
        ) = utils.ci_from_cohens_paired(cohens_dz, sample_size, confidence_level)
        (
            ci_lower_hedges_gz_central,
            ci_upper_hedges_gz_central,
            standard_error_hedges_gz,
        ) = utils.ci_from_cohens_paired(hedges_gz, sample_size, confidence_level)
        ci_lower_cohens_dz_pivotal, ci_upper_cohens_dz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_gz_pivotal, ci_upper_hedges_gz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )

        cles_cohen = es.CLES(
            method="cohen's dz",
            value=float(np.around(cles_dz, 4)),
            standard_error=standard_error_cohens_dz,
            ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_cohens_dz_central) * 100, 4)
            ),
            ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_cohens_dz_central) * 100, 4)
            ),
        )
        cles_hedges = es.CLES(
            method="hedges' gz",
            value=float(np.around(cles_gz, 4)),
            standard_error=standard_error_hedges_gz,
            ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_hedges_gz_central) * 100, 4)
            ),
            ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_hedges_gz_central) * 100, 4)
            ),
        )
        cles_cohen.update_pivotal_ci(
            pivotal_ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_cohens_dz_pivotal) * 100, 4)
            ),
            pivotal_ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_cohens_dz_pivotal) * 100, 4)
            ),
        )
        cles_hedges.update_pivotal_ci(
            pivotal_ci_lower=float(
                np.around(
                    stats.norm.cdf(ci_lower_hedges_gz_pivotal * correction) * 100, 4
                )
            ),
            pivotal_ci_upper=float(
                np.around(
                    stats.norm.cdf(ci_upper_hedges_gz_pivotal * correction) * 100, 4
                )
            ),
        )

        results = TwoPairedCommonLangResults()
        results.cles_cohen = cles_cohen
        results.cles_hedges = cles_hedges

        return results

    @staticmethod
    def from_data(
        column: list, reps: int, confidence_level: float
    ) -> TwoPairedCommonLangResults:
        """
        Calculates common language effect sizes from data in two columns.
        """

        if len(column) != 2:
            raise ValueError("Input must be a list with two columns of data.")

        column_1 = column[0]
        column_2 = column[1]

        sample_1_mean = np.mean(column_1)
        sample_2_mean = np.mean(column_2)
        sample_1_median = np.median(column_1)
        sample_2_median = np.median(column_2)
        sample_1_standard_deviation = np.std(column_1, ddof=1)
        sample_2_standard_deviation = np.std(column_2, ddof=1)
        sample_size_1 = len(column_1)
        sample_size_2 = len(column_2)

        difference = np.array(column_1) - np.array(column_2)
        mean_difference = np.mean(difference)
        standard_deviation_of_the_difference = np.std(difference, ddof=1)
        sample_size = len(difference)

        cohens_dz = mean_difference / standard_deviation_of_the_difference
        cles_dz = stats.norm.cdf(cohens_dz) * 100
        t_score = cohens_dz * np.sqrt(sample_size)
        df = sample_size - 1
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gz = correction * cohens_dz
        cles_gz = stats.norm.cdf(hedges_gz) * 100
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)

        (
            ci_lower_cohens_dz_central,
            ci_upper_cohens_dz_central,
            standard_error_cohens_dz,
        ) = utils.ci_from_cohens_paired(float(cohens_dz), sample_size, confidence_level)
        (
            ci_lower_hedges_gz_central,
            ci_upper_hedges_gz_central,
            standard_error_hedges_gz,
        ) = utils.ci_from_cohens_paired(float(hedges_gz), sample_size, confidence_level)
        ci_lower_cohens_dz_pivotal, ci_upper_cohens_dz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_gz_pivotal, ci_upper_hedges_gz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )

        count_group1_larger = sum(np.where(difference > 0, 1, 0))
        count_group2_larger = sum(np.where(difference < 0, 1, 0))
        count_ties = sum(np.where(difference == 0, 1, 0))
        ps_dep = count_group1_larger / sample_size

        superiority_counts = np.where(
            column_1 > column_2, 1, np.where(column_1 < column_2, 0, 0.5)
        )
        vda_xy = sum(superiority_counts) / sample_size

        cliffs_delta = (
            sum(np.where(column_1 > column_2, 1, 0))
            - sum(np.where(column_2 > column_1, 1, 0))
        ) / sample_size

        ctag_square = stats.norm.ppf(1 - confidence_level) ** 2
        ctag = stats.norm.ppf(1 - confidence_level)
        A = ((count_group1_larger + 1) / (sample_size - count_group1_larger)) ** 2
        B = (
            81 * (count_group1_larger + 1) * (sample_size - count_group1_larger)
            - 9 * sample_size
            - 8
        )
        C = (
            -3
            * ctag
            * np.sqrt(
                9
                * (count_group1_larger + 1)
                * (sample_size - count_group1_larger)
                * (9 * sample_size + 5 - ctag_square)
                + sample_size
                + 1
            )
        )
        D = (
            81 * (count_group1_larger + 1) ** 2
            - 9 * (count_group1_larger + 1) * (2 + ctag_square)
            + 1
        )
        E = 1 + A * ((B + C) / D) ** 3
        A2 = (count_group1_larger / (sample_size - count_group1_larger - 1)) ** 2
        B2 = (
            81 * (count_group1_larger) * (sample_size - count_group1_larger - 1)
            - 9 * sample_size
            - 8
        )
        C2 = (
            3
            * ctag
            * np.sqrt(
                9
                * count_group1_larger
                * (sample_size - count_group1_larger - 1)
                * (9 * sample_size + 5 - ctag_square)
                + sample_size
                + 1
            )
        )
        D2 = (
            81 * count_group1_larger**2
            - (9 * count_group1_larger) * (2 + ctag_square)
            + 1
        )
        E2 = 1 + A2 * ((B2 + C2) / D2) ** 3

        upper_ci_ps_dep_pratt = 1 / E2
        lower_ci_ps_dep_pratt = 1 / E

        if count_group1_larger == 1:
            lower_ci_ps_dep_pratt = 1 - (1 - confidence_level) ** (1 / sample_size)
            upper_ci_ps_dep_pratt = 1 - (confidence_level) ** (1 / sample_size)

        if count_group1_larger == 0:
            lower_ci_ps_dep_pratt = 0
            upper_ci_ps_dep_pratt = stats.beta.ppf(
                1 - confidence_level,
                count_group1_larger + 1,
                sample_size - count_group1_larger,
            )

        if count_group1_larger == sample_size - 1:
            lower_ci_ps_dep_pratt = (confidence_level) ** (1 / sample_size)
            upper_ci_ps_dep_pratt = (1 - confidence_level) ** (1 / sample_size)

        if count_group1_larger == sample_size:
            lower_ci_ps_dep_pratt = (confidence_level * 2) ** (1 / sample_size)
            upper_ci_ps_dep_pratt = 1

        if lower_ci_ps_dep_pratt < 0:
            lower_ci_ps_dep_pratt = 0
        if upper_ci_ps_dep_pratt > 1:
            upper_ci_ps_dep_pratt = 1

        critical_z_value = stats.norm.ppf(0.05 / 2)
        critical_t_value = stats.t.ppf(0.05 / 2, (sample_size - 1))

        feng_standard_error = np.sqrt(
            np.sum((np.sign(difference) - cliffs_delta) ** 2)
            / (sample_size * (sample_size - 1))
        )
        upper_ci_cliff = (
            cliffs_delta
            - cliffs_delta**3
            - critical_t_value
            * feng_standard_error
            * np.sqrt(
                (1 - cliffs_delta**2) ** 2
                + critical_t_value**2 * feng_standard_error**2
            )
        ) / (1 - cliffs_delta**2 + critical_t_value**2 * feng_standard_error**2)
        lower_ci_cliff = (
            cliffs_delta
            - cliffs_delta**3
            + critical_t_value
            * feng_standard_error
            * np.sqrt(
                (1 - cliffs_delta**2) ** 2
                + critical_t_value**2 * feng_standard_error**2
            )
        ) / (1 - cliffs_delta**2 + critical_t_value**2 * feng_standard_error**2)

        number_of_cases_x_larger_than_median_y = sum(
            1 for val in column_1 if val > sample_2_median
        )
        aparametric_cohens_u3_no_ties = (
            number_of_cases_x_larger_than_median_y / sample_size
        )

        if aparametric_cohens_u3_no_ties == 0:
            aparametric_cohens_u3_no_ties = 1 / (sample_size + 1)
        elif aparametric_cohens_u3_no_ties == 1:
            aparametric_cohens_u3_no_ties = sample_size / (sample_size + 1)
        kraemer_andrews_gamma = stats.norm.ppf(aparametric_cohens_u3_no_ties)

        number_of_cases_x_equal_to_median_y = sum(
            1 for val in column_1 if val == sample_2_median
        )
        hentschke_stuttgen_u3 = (
            number_of_cases_x_larger_than_median_y
            + number_of_cases_x_equal_to_median_y * 0.5
        ) / sample_size
        if sample_1_median == sample_2_median:
            hentschke_stuttgen_u3 = 0.5

        number_of_cases_x_larger_than_maximum_y = sum(
            1 for val in column_1 if val > np.max(column_2)
        )
        number_of_cases_x_smaller_than_minimum_y = sum(
            1 for val in column_1 if val < np.min(column_2)
        )
        hentschke_stuttgen_u1 = (
            number_of_cases_x_larger_than_maximum_y
            + number_of_cases_x_smaller_than_minimum_y
        ) / sample_size

        eta = 0

        h1 = max(
            (1.2 * (np.percentile(column_1, 75) - np.percentile(column_1, 25)))
            / (sample_size ** (1 / 5)),
            0.05,
        )
        h2 = max(
            (1.2 * (np.percentile(column_2, 75) - np.percentile(column_2, 25)))
            / (sample_size ** (1 / 5)),
            0.05,
        )

        for value in column_1:
            f_x1 = (
                np.sum(column_1 <= (value + h1)) - np.sum(column_1 < (value - h1))
            ) / (2 * sample_size * h1)
            f_x2 = (
                np.sum(column_2 <= (value + h2)) - np.sum(column_2 < (value - h2))
            ) / (2 * sample_size * h2)
            if f_x1 > f_x2:
                eta += 1

        wilcox_musaka_q_dep = eta / sample_size

        bootstrap_samples_x = []
        for _ in range(reps):
            sample_1_bootstrap = np.random.choice(column_1, len(column_1), replace=True)
            difference_bootstrapping = np.random.choice(
                column_1 - column_2, len(column_1), replace=True
            )
            bootstrap_samples_x.append(sample_1_bootstrap)

        number_of_cases_x_larger_than_median_y_bootstrapping = np.array(
            [(np.sum(sample_x > sample_2_median)) for sample_x in bootstrap_samples_x]
        )
        number_of_cases_x_larger_than_median_y_bootstrapping = (
            number_of_cases_x_larger_than_median_y_bootstrapping / sample_size
        )
        number_of_cases_x_larger_than_median_y_bootstrapping = np.where(
            number_of_cases_x_larger_than_median_y_bootstrapping == 0,
            1 / (sample_size + 1),
            number_of_cases_x_larger_than_median_y_bootstrapping,
        )
        number_of_cases_x_larger_than_median_y_bootstrapping = np.where(
            number_of_cases_x_larger_than_median_y_bootstrapping == 1,
            sample_size / (sample_size + 1),
            number_of_cases_x_larger_than_median_y_bootstrapping,
        )
        kraemer_andrews_gamma_bootstrapping = stats.norm.ppf(
            number_of_cases_x_larger_than_median_y_bootstrapping
        )
        lower_ci_kraemer_andrews_gamma_boot = np.percentile(
            kraemer_andrews_gamma_bootstrapping,
            ((1 - confidence_level) - ((1 - confidence_level) / 2)) * 100,
        )
        upper_ci_kraemer_andrews_gamma_boot = np.percentile(
            kraemer_andrews_gamma_bootstrapping,
            ((confidence_level) + ((1 - confidence_level) / 2)) * 100,
        )

        hentschke_stuttgen_u3_boot = []
        for sample_x in bootstrap_samples_x:
            hentschke_stuttgen_u3_boot.append(
                (
                    np.sum(sample_x > sample_2_median)
                    + np.sum(sample_x == sample_2_median) * 0.5
                )
                / sample_size
            )
            if np.median(sample_x) == sample_2_median:
                hentschke_stuttgen_u3_boot.append(0.5)
        lower_ci_hentschke_stuttgen_u3 = np.percentile(
            hentschke_stuttgen_u3_boot,
            ((1 - confidence_level) - ((1 - confidence_level) / 2)) * 100,
        )
        upper_ci_hentschke_stuttgen_u3 = np.percentile(
            hentschke_stuttgen_u3_boot,
            ((confidence_level) + ((1 - confidence_level) / 2)) * 100,
        )

        number_of_cases_x_larger_than_max_y_bootstrapping = np.array(
            [(np.sum(sample_x > np.max(column_2))) for sample_x in bootstrap_samples_x]
        )
        number_of_cases_x_smaller_than_min_y_bootstrapping = np.array(
            [(np.sum(sample_x < np.min(column_2))) for sample_x in bootstrap_samples_x]
        )
        hentschke_stuttgen_u1_boot = (
            number_of_cases_x_larger_than_max_y_bootstrapping
            + number_of_cases_x_smaller_than_min_y_bootstrapping
        ) / sample_size
        lower_ci_hentschke_stuttgen_u1 = np.percentile(
            hentschke_stuttgen_u1_boot,
            ((1 - confidence_level) - ((1 - confidence_level) / 2)) * 100,
        )
        upper_ci_hentschke_stuttgen_u1 = np.percentile(
            hentschke_stuttgen_u1_boot,
            ((confidence_level) + ((1 - confidence_level) / 2)) * 100,
        )

        cles_dz = es.CLES(
            method="cohen's dz",
            value=float(np.around(cles_dz, 4)),
            standard_error=standard_error_cohens_dz,
            ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_cohens_dz_central) * 100, 4)
            ),
            ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_cohens_dz_central) * 100, 4)
            ),
        )
        cles_gz = es.CLES(
            method="hedges' gz",
            value=float(np.around(cles_gz, 4)),
            standard_error=standard_error_hedges_gz,
            ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_hedges_gz_central) * 100, 4)
            ),
            ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_hedges_gz_central) * 100, 4)
            ),
        )
        cles_dz.update_pivotal_ci(
            pivotal_ci_lower=float(
                np.around(stats.norm.cdf(ci_lower_cohens_dz_pivotal) * 100, 4)
            ),
            pivotal_ci_upper=float(
                np.around(stats.norm.cdf(ci_upper_cohens_dz_pivotal) * 100, 4)
            ),
        )
        cles_gz.update_pivotal_ci(
            pivotal_ci_lower=float(
                np.around(
                    stats.norm.cdf(ci_lower_hedges_gz_pivotal * correction) * 100, 4
                )
            ),
            pivotal_ci_upper=float(
                np.around(
                    stats.norm.cdf(ci_upper_hedges_gz_pivotal * correction) * 100, 4
                )
            ),
        )
        probability_of_superiority = es.ProbabilityOfSuperiority(
            value=round(ps_dep, 4),
            standard_error=0.0,
            ci_lower=np.round(
                min(float(lower_ci_ps_dep_pratt), float(upper_ci_ps_dep_pratt)), 4
            ),
            ci_upper=np.round(
                max(float(lower_ci_ps_dep_pratt), float(upper_ci_ps_dep_pratt)), 4
            ),
        )
        vargha_delaney = es.VarghaDelaney(
            value=round(vda_xy, 4),
            standard_error=0.0,
            ci_lower=round((lower_ci_cliff + 1) / 2, 4),
            ci_upper=round((upper_ci_cliff + 1) / 2, 4),
        )
        cliffs_delta_es = es.CliffsDelta(
            value=round(cliffs_delta, 4),
            standard_error=0.0,
            ci_lower=round(lower_ci_cliff, 4),
            ci_upper=round(upper_ci_cliff, 4),
        )
        kraemer_andrews_gamma = es.KraemerAndrewGamma(
            value=float(kraemer_andrews_gamma),
            standard_error=0.0,
            ci_lower=float(round(lower_ci_kraemer_andrews_gamma_boot, 4)),
            ci_upper=float(round(upper_ci_kraemer_andrews_gamma_boot, 4)),
        )
        non_param_u3 = es.NonParametricU3(
            value=round(hentschke_stuttgen_u3, 4),
            standard_error=0.0,
            ci_lower=float(round(lower_ci_hentschke_stuttgen_u3, 4)),
            ci_upper=float(round(upper_ci_hentschke_stuttgen_u3, 4)),
        )
        non_param_u1 = es.NonParametricU1(
            value=round(hentschke_stuttgen_u1, 4),
            standard_error=0.0,
            ci_lower=float(round(lower_ci_hentschke_stuttgen_u1, 4)),
            ci_upper=float(round(upper_ci_hentschke_stuttgen_u1, 4)),
        )
        wilcox_musaka_q_dep = es.WilcoxMusakaQ(
            value=wilcox_musaka_q_dep,
            standard_error=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
        )

        results = TwoPairedCommonLangResults()
        results.cles_cohen = cles_dz
        results.cles_hedges = cles_gz
        results.probability_of_superiority = probability_of_superiority
        results.vargha_delaney = vargha_delaney
        results.cliff_delta = cliffs_delta_es
        results.kraemer_andrew_gamma = kraemer_andrews_gamma
        results.non_param_u3 = non_param_u3
        results.non_param_u1 = non_param_u1
        results.wilcox_musaka_q = wilcox_musaka_q_dep

        return results
