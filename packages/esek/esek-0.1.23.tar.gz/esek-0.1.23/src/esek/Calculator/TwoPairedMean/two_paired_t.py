"""
This module implements the Two Paired T-test for comparing two related samples.
It provides methods to calculate the test statistics, confidence intervals,
and effect sizes such as Cohen's d, Hedges' g, and their variants.
"""

import math
from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es


@dataclass
class TwoPairedTResults:
    """
    A class to store the results of a Two Paired T-test.
    """

    cohens_d: Optional[es.CohenD] = None
    hedge_g: Optional[es.HedgesG] = None
    cohens_dav: Optional[es.CohensDav] = None
    hedge_gav: Optional[es.HedgesGav] = None
    cohens_drm: Optional[es.CohensDrm] = None
    hedge_grm: Optional[es.HedgesGrm] = None
    ratio_of_means: Optional[es.RatioOfMeans] = None
    inferential: Optional[res.InferentialStatistics] = None
    sample1: Optional[res.Sample] = None
    sample2: Optional[res.Sample] = None


class TwoPairedTTests(interfaces.AbstractTest):
    """
    A class to perform Two Paired T-tests and calculate effect sizes.
    This class provides methods to calculate Cohen's d, Hedges' g, and their variants
    based on the t-score, sample size, and confidence level.
    It also provides methods to calculate confidence intervals and standard errors
    for the effect sizes.
    It can be used to analyze paired samples and compute the necessary statistics
    for hypothesis testing in a two-sample context.

    Attributes:
        None
    Methods:
        from_score -> TwoPairedTResults:
            Calculates effect sizes and confidence intervals from a t-score.
        from_parameters -> TwoPairedTResults:
            Calculates effect sizes and confidence intervals from sample parameters.
        from_data -> TwoPairedTResults:
            Calculates effect sizes and confidence intervals from data columns.
        calculate_central_ci -> tuple:
            Calculates central confidence intervals and standard errors for effect sizes.
        calculate_se_pooled -> tuple:
            Calculates pooled standard errors and confidence intervals for effect sizes.
        pivotal_ci_t -> tuple:
            Calculates pivotal confidence intervals for effect sizes based on t-distribution.
        ci_t_prime -> tuple:
            Calculates t-prime confidence intervals for effect sizes.
        ci_adjusted_lambda_prime -> tuple:
            Calculates adjusted lambda prime confidence intervals for effect sizes.
        ci_mag -> tuple:
            Calculates magnitude confidence intervals for effect sizes.
        ci_morris -> tuple:
            Calculates Morris confidence intervals for effect sizes.

    """

    @staticmethod
    def from_score(
        t_score: float, sample_size: int, confidence_level: float
    ) -> TwoPairedTResults:
        """
        Calculates effect sizes and confidence intervals from a t-score.
        """

        df = int(sample_size - 1)
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)

        cohens_dz_value = t_score / np.sqrt(sample_size)
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gz_value = correction * cohens_dz_value

        (
            ci_lower_cohens_dz_central,
            ci_upper_cohens_dz_central,
            standard_error_cohens_dz_true,
            standard_error_cohens_dz_morris,
            standard_error_cohens_dz_hedges,
            standard_error_cohens_dz_hedges_olkin,
            standard_error_cohens_dz_mle,
            standard_error_cohens_dz_largen,
            standard_error_cohens_dz_small_n,
        ) = utils.central_ci_paired(cohens_dz_value, sample_size, confidence_level)
        (
            ci_lower_hedges_gz_central,
            ci_upper_hedges_gz_central,
            standard_error_hedges_gz_true,
            standard_error_hedges_gz_morris,
            standard_error_hedges_gz_hedges,
            standard_error_hedges_gz_hedges_olkin,
            standard_error_hedges_gz_mle,
            standard_error_hedges_gz_largen,
            standard_error_hedges_gz_small_n,
        ) = utils.central_ci_paired(hedges_gz_value, sample_size, confidence_level)

        ci_lower_cohens_dz_pivotal, ci_upper_cohens_dz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_gz_pivotal, ci_upper_hedges_gz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )

        cohens_dz = es.CohenD(
            value=cohens_dz_value,
            ci_lower=ci_lower_cohens_dz_central,
            ci_upper=ci_upper_cohens_dz_central,
            standard_error=standard_error_cohens_dz_true,
        )

        hedges_gz = es.HedgesG(
            value=hedges_gz_value,
            ci_lower=ci_lower_hedges_gz_central,
            ci_upper=ci_upper_hedges_gz_central,
            standard_error=standard_error_hedges_gz_true,
        )

        cohens_dz.standardizer = (2 * cohens_dz.value) / t_score
        hedges_gz.standardizer = cohens_dz.standardizer / correction

        cohens_dz.update_pivotal_ci(
            round(ci_lower_cohens_dz_pivotal, 4), round(ci_upper_cohens_dz_pivotal, 4)
        )
        hedges_gz.update_pivotal_ci(
            round(ci_lower_hedges_gz_pivotal * correction, 4),
            round(ci_upper_hedges_gz_pivotal * correction, 4),
        )

        inferential = res.InferentialStatistics(
            score=round(t_score, 4),
            p_value=round(p_value, 4),
        )
        inferential.degrees_of_freedom = round(df, 4)

        results = TwoPairedTResults()
        results.cohens_d = cohens_dz
        results.hedge_g = hedges_gz
        results.inferential = inferential

        return results

    @staticmethod
    def from_parameters(
        sample_mean_1: float,
        sample_mean_2: float,
        sample_sd_1: float,
        sample_sd_2: float,
        sample_size: int,
        correlation: float,
        confidence_level: float,
        population_mean_diff: float = 0,
    ) -> TwoPairedTResults:
        """
        Calculates effect sizes and confidence intervals from sample parameters.
        """

        df = int(sample_size - 1)
        standardizer_dz = np.sqrt(
            sample_sd_1**2
            + sample_sd_2**2
            - 2 * correlation * sample_sd_1 * sample_sd_2
        )
        standardizer_dav = np.sqrt((sample_sd_1**2 + sample_sd_2**2) / 2)
        standardizer_drm = np.sqrt(
            sample_sd_1**2
            + sample_sd_2**2
            - 2 * correlation * sample_sd_1 * sample_sd_2
        ) / np.sqrt(2 * (1 - correlation))
        standard_error = np.sqrt(
            ((sample_sd_1**2 / sample_size) + (sample_sd_2**2 / sample_size))
            - (
                2
                * correlation
                * (sample_sd_1 / np.sqrt(sample_size))
                * (sample_sd_2 / np.sqrt(sample_size))
            )
        )
        t_score = (
            (sample_mean_1 - sample_mean_2) - population_mean_diff
        ) / standard_error
        t_score_av = ((sample_mean_1 - sample_mean_2) - population_mean_diff) / (
            (np.sqrt((sample_sd_1**2 + sample_sd_2**2) / 2)) / np.sqrt(sample_size)
        )

        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        cohens_dz_value = (
            (sample_mean_1 - sample_mean_2) - population_mean_diff
        ) / standardizer_dz
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gz_value = cohens_dz_value * correction
        cohens_dav_value = (
            (sample_mean_1 - sample_mean_2) - population_mean_diff
        ) / standardizer_dav
        hedges_gav_value = cohens_dav_value * correction
        cohens_drm_value = (
            sample_mean_1 - sample_mean_2 - population_mean_diff
        ) / standardizer_drm
        hedges_grm_value = cohens_drm_value * correction

        (
            ci_lower_cohens_dz_central,
            ci_upper_cohens_dz_central,
            standard_error_cohens_dz_true,
            standard_error_cohens_dz_morris,
            standard_error_cohens_dz_hedges,
            standard_error_cohens_dz_hedges_olkin,
            standard_error_cohens_dz_MLE,
            standard_error_cohens_dz_Largen,
            standard_error_cohens_dz_Small_n,
        ) = utils.central_ci_paired(cohens_dz_value, sample_size, confidence_level)
        (
            ci_lower_hedges_gz_central,
            ci_upper_hedges_gz_central,
            standard_error_hedges_gz_true,
            standard_error_hedges_gz_morris,
            standard_error_hedges_gz_hedges,
            standard_error_hedges_gz_hedges_olkin,
            standard_error_hedges_gz_MLE,
            standard_error_hedges_gz_Largen,
            standard_error_hedges_gz_Small_n,
        ) = utils.central_ci_paired(hedges_gz_value, sample_size, confidence_level)
        (
            ci_lower_cohens_dav_central,
            ci_upper_cohens_dav_central,
            standard_error_cohens_dav_true,
            standard_error_cohens_dav_morris,
            standard_error_cohens_dav_hedges,
            standard_error_cohens_dav_hedges_olkin,
            standard_error_cohens_dav_MLE,
            standard_error_cohens_dav_Largen,
            standard_error_cohens_dav_Small_n,
        ) = utils.central_ci_paired(cohens_dav_value, sample_size, confidence_level)
        (
            ci_lower_hedges_gav_central,
            ci_upper_hedges_gav_central,
            standard_error_hedges_gav_true,
            standard_error_hedges_gav_morris,
            standard_error_hedges_gav_hedges,
            standard_error_hedges_gav_hedges_olkin,
            standard_error_hedges_gav_MLE,
            standard_error_hedges_gav_Largen,
            standard_error_hedges_gav_Small_n,
        ) = utils.central_ci_paired(hedges_gav_value, sample_size, confidence_level)
        (
            ci_lower_cohens_drm_central,
            ci_upper_cohens_drm_central,
            standard_error_cohens_drm_true,
            standard_error_cohens_drm_morris,
            standard_error_cohens_drm_hedges,
            standard_error_cohens_drm_hedges_olkin,
            standard_error_cohens_drm_MLE,
            standard_error_cohens_drm_Largen,
            standard_error_cohens_drm_Small_n,
        ) = utils.central_ci_paired(cohens_drm_value, sample_size, confidence_level)
        (
            ci_lower_hedges_grm_central,
            ci_upper_hedges_grm_central,
            standard_error_hedges_grm_true,
            standard_error_hedges_grm_morris,
            standard_error_hedges_grm_hedges,
            standard_error_hedges_grm_hedges_olkin,
            standard_error_hedges_grm_MLE,
            standard_error_hedges_grm_Largen,
            standard_error_hedges_grm_Small_n,
        ) = utils.central_ci_paired(hedges_gz_value, sample_size, confidence_level)
        (
            ci_lower_cohens_dz_central_pooled,
            ci_upper_cohens_dz_central_pooled,
            standard_error_cohens_dz_true_pooled,
            standard_error_cohens_dz_morris_pooled,
            standard_error_cohens_dz_hedges_pooled,
            standard_error_cohens_dz_hedges_olkin_pooled,
            standard_error_cohens_dz_MLE_pooled,
            standard_error_cohens_dz_Largen_pooled,
            standard_error_cohens_dz_Small_n_pooled,
        ) = utils.calculate_se_pooled(
            cohens_dz_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_hedges_gz_central_pooled,
            ci_upper_hedges_gz_central_pooled,
            standard_error_hedges_gz_true_pooled,
            standard_error_hedges_gz_morris_pooled,
            standard_error_hedges_gz_hedges_pooled,
            standard_error_hedges_gz_hedges_olkin_pooled,
            standard_error_hedges_gz_MLE_pooled,
            standard_error_hedges_gz_Largen_pooled,
            standard_error_hedges_gz_Small_n_pooled,
        ) = utils.calculate_se_pooled(
            hedges_gz_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_cohens_dav_central_pooled,
            ci_upper_cohens_dav_central_pooled,
            standard_error_cohens_dav_true_pooled,
            standard_error_cohens_dav_morris_pooled,
            standard_error_cohens_dav_hedges_pooled,
            standard_error_cohens_dav_hedges_olkin_pooled,
            standard_error_cohens_dav_MLE_pooled,
            standard_error_cohens_dav_Largen_pooled,
            standard_error_cohens_dav_Small_n_pooled,
        ) = utils.calculate_se_pooled(
            cohens_dav_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_hedges_gav_central_pooled,
            ci_upper_hedges_gav_central_pooled,
            standard_error_hedges_gav_true_pooled,
            standard_error_hedges_gav_morris_pooled,
            standard_error_hedges_gav_hedges_pooled,
            standard_error_hedges_gav_hedges_olkin_pooled,
            standard_error_hedges_gav_MLE_pooled,
            standard_error_hedges_gav_Largen_pooled,
            standard_error_hedges_gav_Small_n_pooled,
        ) = utils.calculate_se_pooled(
            hedges_gav_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_cohens_drm_central_pooled,
            ci_upper_cohens_drm_central_pooled,
            standard_error_cohens_drm_true_pooled,
            standard_error_cohens_drm_morris_pooled,
            standard_error_cohens_drm_hedges_pooled,
            standard_error_cohens_drm_hedges_olkin_pooled,
            standard_error_cohens_drm_MLE_pooled,
            standard_error_cohens_drm_Largen_pooled,
            standard_error_cohens_drm_Small_n_pooled,
        ) = utils.calculate_se_pooled(
            cohens_drm_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_hedges_grm_central_pooled,
            ci_upper_hedges_grm_central_pooled,
            standard_error_hedges_grm_true_pooled,
            standard_error_hedges_grm_morris_pooled,
            standard_error_hedges_grm_hedges_pooled,
            standard_error_hedges_grm_hedges_olkin_pooled,
            standard_error_hedges_grm_MLE_pooled,
            standard_error_hedges_grm_Largen_pooled,
            standard_error_hedges_grm_Small_n_pooled,
        ) = utils.calculate_se_pooled(
            hedges_gz_value, sample_size, correlation, confidence_level
        )
        ci_lower_cohens_dz_pivotal, ci_upper_cohens_dz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_cohens_dav_pivotal, ci_upper_cohens_dav_pivotal = utils.pivotal_ci_t(
            t_score_av, df, sample_size, confidence_level
        )
        ci_lower_cohens_drm_pivotal, ci_upper_cohens_drm_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )

        lower_ci_tprime_dav, upper_ci_tprime_dav = utils.ci_t_prime(
            cohens_dav_value,
            sample_sd_1,
            sample_sd_2,
            sample_size,
            correlation,
            confidence_level,
        )
        lower_ci_tprime_gav, upper_ci_tprime_gav = (
            lower_ci_tprime_dav * correction,
            upper_ci_tprime_dav * correction,
        )
        lower_ci_lambda_prime_dav, upper_ci_lambda_prime_dav = (
            utils.ci_adjusted_lambda_prime(
                cohens_dav_value,
                sample_sd_1,
                sample_sd_2,
                sample_size,
                correlation,
                confidence_level,
            )
        )
        lower_ci_lambda_prime_gav, upper_ci_lambda_prime_gav = (
            lower_ci_lambda_prime_dav * correction,
            upper_ci_lambda_prime_dav * correction,
        )
        lower_ci_mag_dav, upper_ci_mag_dav = utils.ci_mag(
            cohens_dav_value,
            sample_sd_1,
            sample_sd_2,
            sample_size,
            correlation,
            confidence_level,
        )
        lower_ci_mag_gav, upper_ci_mag_gav = (
            lower_ci_mag_dav * correction,
            upper_ci_mag_dav * correction,
        )
        lower_ci_morris_dav, upper_ci_morris_dav = utils.ci_morris(
            cohens_dav_value, sample_size, correlation, confidence_level
        )
        lower_ci_morris_gav, upper_ci_morris_gav = (
            lower_ci_morris_dav * correction,
            upper_ci_morris_dav * correction,
        )

        ratio_of_means = sample_mean_1 / sample_mean_2
        variance_of_means_ratio = (
            sample_sd_1**2 / (sample_mean_1**2)
            + sample_sd_2**2 / (sample_mean_2**2)
            - 2
            * correlation
            * np.sqrt(sample_sd_1**2 * sample_sd_2**2)
            / (sample_mean_1 * sample_mean_2)
        ) / sample_size
        standard_error_of_means_ratio = np.sqrt(variance_of_means_ratio)
        degrees_of_freedom_means_ratio = sample_size - 1
        t_critical_value = stats.t.ppf(
            confidence_level + ((1 - confidence_level) / 2),
            degrees_of_freedom_means_ratio,
        )
        lower_ci_means_ratio = math.exp(
            np.log(ratio_of_means) - t_critical_value * np.sqrt(variance_of_means_ratio)
        )
        upper_ci_means_ratio = math.exp(
            np.log(ratio_of_means) + t_critical_value * np.sqrt(variance_of_means_ratio)
        )

        cohens_dz = es.CohenD(
            value=cohens_dz_value,
            ci_lower=ci_lower_cohens_dz_central,
            ci_upper=ci_upper_cohens_dz_central,
            standard_error=standard_error_cohens_dz_true,
        )
        hedges_gz = es.HedgesG(
            value=hedges_gz_value,
            ci_lower=ci_lower_hedges_gz_central,
            ci_upper=ci_upper_hedges_gz_central,
            standard_error=standard_error_hedges_gz_true,
        )
        cohens_dav = es.CohensDav(
            value=cohens_dav_value,
            ci_lower=ci_lower_cohens_dav_central,
            ci_upper=ci_upper_cohens_dav_central,
            standard_error=standard_error_cohens_dav_true,
        )
        hedges_gav = es.HedgesGav(
            value=hedges_gav_value,
            ci_lower=ci_lower_hedges_gav_central,
            ci_upper=ci_upper_hedges_gav_central,
            standard_error=standard_error_hedges_gav_true,
        )
        cohens_drm = es.CohensDrm(
            value=cohens_drm_value,
            ci_lower=ci_lower_cohens_drm_central,
            ci_upper=ci_upper_cohens_drm_central,
            standard_error=standard_error_cohens_drm_true,
        )
        hedges_grm = es.HedgesGrm(
            value=hedges_grm_value,
            ci_lower=ci_lower_hedges_grm_central,
            ci_upper=ci_upper_hedges_grm_central,
            standard_error=standard_error_hedges_grm_true,
        )
        cohens_dz.standardizer = (2 * cohens_dz.value) / t_score
        if cohens_dz.standardizer:
            hedges_gz.standardizer = cohens_dz.standardizer / correction
        cohens_dav.standardizer = (2 * cohens_dav.value) / t_score_av
        if cohens_dav.standardizer:
            hedges_gav.standardizer = cohens_dav.standardizer / correction
        cohens_drm.standardizer = (2 * cohens_drm.value) / t_score
        if cohens_drm.standardizer:
            hedges_grm.standardizer = cohens_drm.standardizer / correction
        cohens_dz.update_pivotal_ci(
            round(ci_lower_cohens_dz_pivotal, 4), round(ci_upper_cohens_dz_pivotal, 4)
        )
        hedges_gz.update_pivotal_ci(
            round(ci_lower_cohens_dz_pivotal * correction, 4),
            round(ci_upper_cohens_dz_pivotal * correction, 4),
        )
        cohens_dav.update_pivotal_ci(
            round(ci_lower_cohens_dav_pivotal, 4), round(ci_upper_cohens_dav_pivotal, 4)
        )
        hedges_gav.update_pivotal_ci(
            round(ci_lower_cohens_dav_pivotal * correction, 4),
            round(ci_upper_cohens_dav_pivotal * correction, 4),
        )
        cohens_drm.update_pivotal_ci(
            round(ci_lower_cohens_drm_pivotal, 4), round(ci_upper_cohens_drm_pivotal, 4)
        )
        hedges_grm.update_pivotal_ci(
            round(ci_lower_cohens_drm_pivotal * correction, 4),
            round(ci_upper_cohens_drm_pivotal * correction, 4),
        )

        cohens_dav.update_mag_ci(round(lower_ci_mag_dav, 4), round(upper_ci_mag_dav, 4))
        hedges_gav.update_mag_ci(round(lower_ci_mag_gav, 4), round(upper_ci_mag_gav, 4))
        cohens_dav.update_morris_ci(
            round(lower_ci_morris_dav, 4), round(upper_ci_morris_dav, 4)
        )
        hedges_gav.update_morris_ci(
            round(lower_ci_morris_gav, 4), round(upper_ci_morris_gav, 4)
        )
        cohens_dav.update_t_prime_ci(
            round(lower_ci_tprime_dav, 4), round(upper_ci_tprime_dav, 4)
        )
        hedges_gav.update_t_prime_ci(
            round(lower_ci_tprime_gav, 4), round(upper_ci_tprime_gav, 4)
        )
        cohens_dav.update_lambda_prime_ci(
            round(lower_ci_lambda_prime_dav, 4), round(upper_ci_lambda_prime_dav, 4)
        )
        hedges_gav.update_lambda_prime_ci(
            round(lower_ci_lambda_prime_gav, 4), round(upper_ci_lambda_prime_gav, 4)
        )
        ratio_of_means_effect_size = es.RatioOfMeans(
            value=round(ratio_of_means, 4),
            standard_error=round(standard_error_of_means_ratio, 4),
            ci_lower=round(lower_ci_means_ratio, 4),
            ci_upper=round(upper_ci_means_ratio, 4),
        )
        sample1 = res.Sample(
            mean=round(sample_mean_1, 4),
            standard_deviation=int(sample_sd_1),
            size=sample_size,
        )
        sample2 = res.Sample(
            mean=round(sample_mean_2, 4),
            standard_deviation=int(sample_sd_2),
            size=sample_size,
        )

        sample1.diff_mean = round(sample_mean_1 - sample_mean_2, 4)
        sample2.diff_mean = round(sample_mean_2 - sample_mean_1, 4)

        inferential = res.InferentialStatistics(
            score=round(t_score, 4),
            p_value=round(p_value, 4),
        )
        inferential.degrees_of_freedom = round(df, 4)
        inferential.standard_error = round(standard_error, 4)

        results = TwoPairedTResults()
        results.cohens_d = cohens_dz
        results.hedge_g = hedges_gz
        results.cohens_dav = cohens_dav
        results.hedge_gav = hedges_gav
        results.cohens_drm = cohens_drm
        results.hedge_grm = hedges_grm
        results.sample1 = sample1
        results.sample2 = sample2
        results.inferential = inferential
        results.ratio_of_means = ratio_of_means_effect_size

        return results

    @staticmethod
    def from_data(
        columns: list, population_mean_diff: float, confidence_level: float
    ) -> TwoPairedTResults:
        """
        Calculates effect sizes and confidence intervals from data columns.
        """
        column_1 = columns[0]
        column_2 = columns[1]
        sample_mean_1 = np.mean(column_1)
        sample_mean_2 = np.mean(column_2)
        sample_sd_1 = np.std(column_1, ddof=1)
        sample_sd_2 = np.std(column_2, ddof=1)
        sample_size = len(column_1)
        correlation_matrix = np.corrcoef(column_1, column_2)
        correlation = correlation_matrix[0, 1]

        df = int(sample_size - 1)
        standardizer_dz = np.sqrt(
            sample_sd_1**2
            + sample_sd_2**2
            - 2 * correlation * sample_sd_1 * sample_sd_2
        )
        standardizer_dav = np.sqrt((sample_sd_1**2 + sample_sd_2**2) / 2)
        standardizer_drm = np.sqrt(
            sample_sd_1**2
            + sample_sd_2**2
            - 2 * correlation * sample_sd_1 * sample_sd_2
        ) / np.sqrt(2 * (1 - correlation))
        standard_error = np.sqrt(
            ((sample_sd_1**2 / sample_size) + (sample_sd_2**2 / sample_size))
            - (
                2
                * correlation
                * (sample_sd_1 / np.sqrt(sample_size))
                * (sample_sd_2 / np.sqrt(sample_size))
            )
        )
        t_score = (
            (sample_mean_1 - sample_mean_2) - population_mean_diff
        ) / standard_error
        t_score_av = ((sample_mean_1 - sample_mean_2) - population_mean_diff) / (
            (np.sqrt((sample_sd_1**2 + sample_sd_2**2) / 2)) / np.sqrt(sample_size)
        )
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        cohens_dz_value = (
            (sample_mean_1 - sample_mean_2) - population_mean_diff
        ) / standardizer_dz
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gz_value = cohens_dz_value * correction
        cohens_dav_value = (
            (sample_mean_1 - sample_mean_2) - population_mean_diff
        ) / standardizer_dav
        hedges_gav_value = cohens_dav_value * correction
        cohens_drm_value = (
            sample_mean_1 - sample_mean_2 - population_mean_diff
        ) / standardizer_drm
        hedges_grm_value = cohens_drm_value * correction

        (
            ci_lower_cohens_dz_central,
            ci_upper_cohens_dz_central,
            standard_error_cohens_dz_true,
            standard_error_cohens_dz_morris,
            standard_error_cohens_dz_hedges,
            standard_error_cohens_dz_hedges_olkin,
            standard_error_cohens_dz_mle,
            standard_error_cohens_dz_largen,
            standard_error_cohens_dz_small_n,
        ) = utils.central_ci_paired(cohens_dz_value, sample_size, confidence_level)
        (
            ci_lower_hedges_gz_central,
            ci_upper_hedges_gz_central,
            standard_error_hedges_gz_true,
            standard_error_hedges_gz_morris,
            standard_error_hedges_gz_hedges,
            standard_error_hedges_gz_hedges_olkin,
            standard_error_hedges_gz_mle,
            standard_error_hedges_gz_largen,
            standard_error_hedges_gz_small_n,
        ) = utils.central_ci_paired(hedges_gz_value, sample_size, confidence_level)
        (
            ci_lower_cohens_dav_central,
            ci_upper_cohens_dav_central,
            standard_error_cohens_dav_true,
            standard_error_cohens_dav_morris,
            standard_error_cohens_dav_hedges,
            standard_error_cohens_dav_hedges_olkin,
            standard_error_cohens_dav_mle,
            standard_error_cohens_dav_largen,
            standard_error_cohens_dav_small_n,
        ) = utils.central_ci_paired(cohens_dav_value, sample_size, confidence_level)
        (
            ci_lower_hedges_gav_central,
            ci_upper_hedges_gav_central,
            standard_error_hedges_gav_true,
            standard_error_hedges_gav_morris,
            standard_error_hedges_gav_hedges,
            standard_error_hedges_gav_hedges_olkin,
            standard_error_hedges_gav_mle,
            standard_error_hedges_gav_largen,
            standard_error_hedges_gav_small_n,
        ) = utils.central_ci_paired(hedges_gav_value, sample_size, confidence_level)
        (
            ci_lower_cohens_drm_central,
            ci_upper_cohens_drm_central,
            standard_error_cohens_drm_true,
            standard_error_cohens_drm_morris,
            standard_error_cohens_drm_hedges,
            standard_error_cohens_drm_hedges_olkin,
            standard_error_cohens_drm_mle,
            standard_error_cohens_drm_largen,
            standard_error_cohens_drm_small_n,
        ) = utils.central_ci_paired(cohens_drm_value, sample_size, confidence_level)
        (
            ci_lower_hedges_grm_central,
            ci_upper_hedges_grm_central,
            standard_error_hedges_grm_true,
            standard_error_hedges_grm_morris,
            standard_error_hedges_grm_hedges,
            standard_error_hedges_grm_hedges_olkin,
            standard_error_hedges_grm_mle,
            standard_error_hedges_grm_largen,
            standard_error_hedges_grm_small_n,
        ) = utils.central_ci_paired(hedges_gz_value, sample_size, confidence_level)
        ci_lower_cohens_dz_pivotal, ci_upper_cohens_dz_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_cohens_dav_pivotal, ci_upper_cohens_dav_pivotal = utils.pivotal_ci_t(
            t_score_av, df, sample_size, confidence_level
        )
        ci_lower_cohens_drm_pivotal, ci_upper_cohens_drm_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        (
            ci_lower_cohens_dz_central_pooled,
            ci_upper_cohens_dz_central_pooled,
            standard_error_cohens_dz_true_pooled,
            standard_error_cohens_dz_morris_pooled,
            standard_error_cohens_dz_hedges_pooled,
            standard_error_cohens_dz_hedges_olkin_pooled,
            standard_error_cohens_dz_mle_pooled,
            standard_error_cohens_dz_largen_pooled,
            standard_error_cohens_dz_small_n_pooled,
        ) = utils.calculate_se_pooled(
            cohens_dz_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_hedges_gz_central_pooled,
            ci_upper_hedges_gz_central_pooled,
            standard_error_hedges_gz_true_pooled,
            standard_error_hedges_gz_morris_pooled,
            standard_error_hedges_gz_hedges_pooled,
            standard_error_hedges_gz_hedges_olkin_pooled,
            standard_error_hedges_gz_mle_pooled,
            standard_error_hedges_gz_largen_pooled,
            standard_error_hedges_gz_small_n_pooled,
        ) = utils.calculate_se_pooled(
            hedges_gz_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_cohens_dav_central_pooled,
            ci_upper_cohens_dav_central_pooled,
            standard_error_cohens_dav_true_pooled,
            standard_error_cohens_dav_morris_pooled,
            standard_error_cohens_dav_hedges_pooled,
            standard_error_cohens_dav_hedges_olkin_pooled,
            standard_error_cohens_dav_mle_pooled,
            standard_error_cohens_dav_largen_pooled,
            standard_error_cohens_dav_small_n_pooled,
        ) = utils.calculate_se_pooled(
            cohens_dav_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_hedges_gav_central_pooled,
            ci_upper_hedges_gav_central_pooled,
            standard_error_hedges_gav_true_pooled,
            standard_error_hedges_gav_morris_pooled,
            standard_error_hedges_gav_hedges_pooled,
            standard_error_hedges_gav_hedges_olkin_pooled,
            standard_error_hedges_gav_mle_pooled,
            standard_error_hedges_gav_largen_pooled,
            standard_error_hedges_gav_small_n_pooled,
        ) = utils.calculate_se_pooled(
            hedges_gav_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_cohens_drm_central_pooled,
            ci_upper_cohens_drm_central_pooled,
            standard_error_cohens_drm_true_pooled,
            standard_error_cohens_drm_morris_pooled,
            standard_error_cohens_drm_hedges_pooled,
            standard_error_cohens_drm_hedges_olkin_pooled,
            standard_error_cohens_drm_mle_pooled,
            standard_error_cohens_drm_largen_pooled,
            standard_error_cohens_drm_small_n_pooled,
        ) = utils.calculate_se_pooled(
            cohens_drm_value, sample_size, correlation, confidence_level
        )
        (
            ci_lower_hedges_grm_central_pooled,
            ci_upper_hedges_grm_central_pooled,
            standard_error_hedges_grm_true_pooled,
            standard_error_hedges_grm_morris_pooled,
            standard_error_hedges_grm_hedges_pooled,
            standard_error_hedges_grm_hedges_olkin_pooled,
            standard_error_hedges_grm_mle_pooled,
            standard_error_hedges_grm_largen_pooled,
            standard_error_hedges_grm_small_n_pooled,
        ) = utils.calculate_se_pooled(
            hedges_gz_value, sample_size, correlation, confidence_level
        )

        lower_ci_tprime_dav, upper_ci_tprime_dav = utils.ci_t_prime(
            cohens_dav_value,
            float(sample_sd_1),
            float(sample_sd_2),
            sample_size,
            float(correlation),
            confidence_level,
        )
        lower_ci_tprime_gav, upper_ci_tprime_gav = (
            lower_ci_tprime_dav * correction,
            upper_ci_tprime_dav * correction,
        )
        lower_ci_lambda_prime_dav, upper_ci_lambda_prime_dav = (
            utils.ci_adjusted_lambda_prime(
                cohens_dav_value,
                float(sample_sd_1),
                float(sample_sd_2),
                sample_size,
                float(correlation),
                confidence_level,
            )
        )
        lower_ci_lambda_prime_gav, upper_ci_lambda_prime_gav = (
            lower_ci_lambda_prime_dav * correction,
            upper_ci_lambda_prime_dav * correction,
        )
        lower_ci_mag_dav, upper_ci_mag_dav = utils.ci_mag(
            cohens_dav_value,
            float(sample_sd_1),
            float(sample_sd_2),
            sample_size,
            correlation,
            confidence_level,
        )
        lower_ci_mag_gav, upper_ci_mag_gav = (
            lower_ci_mag_dav * correction,
            upper_ci_mag_dav * correction,
        )
        lower_ci_morris_dav, upper_ci_morris_dav = utils.ci_morris(
            cohens_dav_value, sample_size, correlation, confidence_level
        )
        lower_ci_morris_gav, upper_ci_morris_gav = (
            lower_ci_morris_dav * correction,
            upper_ci_morris_dav * correction,
        )

        ratio_of_means = sample_mean_1 / sample_mean_2
        variance_of_means_ratio = (
            sample_sd_1**2 / (sample_mean_1**2)
            + sample_sd_2**2 / (sample_mean_2**2)
            - 2
            * correlation
            * np.sqrt(sample_sd_1**2 * sample_sd_2**2)
            / (sample_mean_1 * sample_mean_2)
        ) / sample_size
        standard_error_of_means_ratio = np.sqrt(variance_of_means_ratio)
        degrees_of_freedom_means_ratio = sample_size - 1
        t_critical_value = stats.t.ppf(
            confidence_level + ((1 - confidence_level) / 2),
            degrees_of_freedom_means_ratio,
        )
        lower_ci_means_ratio = math.exp(
            np.log(ratio_of_means) - t_critical_value * np.sqrt(variance_of_means_ratio)
        )
        upper_ci_means_ratio = math.exp(
            np.log(ratio_of_means) + t_critical_value * np.sqrt(variance_of_means_ratio)
        )

        cohens_dz = es.CohenD(
            value=cohens_dz_value,
            ci_lower=ci_lower_cohens_dz_central,
            ci_upper=ci_upper_cohens_dz_central,
            standard_error=standard_error_cohens_dz_true,
        )
        hedges_gz = es.HedgesG(
            value=hedges_gz_value,
            ci_lower=ci_lower_hedges_gz_central,
            ci_upper=ci_upper_hedges_gz_central,
            standard_error=standard_error_hedges_gz_true,
        )
        cohens_dav = es.CohensDav(
            value=cohens_dav_value,
            ci_lower=ci_lower_cohens_dav_central,
            ci_upper=ci_upper_cohens_dav_central,
            standard_error=standard_error_cohens_dav_true,
        )
        hedges_gav = es.HedgesGav(
            value=hedges_gav_value,
            ci_lower=ci_lower_hedges_gav_central,
            ci_upper=ci_upper_hedges_gav_central,
            standard_error=standard_error_hedges_gav_true,
        )
        cohens_drm = es.CohensDrm(
            value=cohens_drm_value,
            ci_lower=ci_lower_cohens_drm_central,
            ci_upper=ci_upper_cohens_drm_central,
            standard_error=standard_error_cohens_drm_true,
        )
        hedges_grm = es.HedgesGrm(
            value=hedges_grm_value,
            ci_lower=ci_lower_hedges_grm_central,
            ci_upper=ci_upper_hedges_grm_central,
            standard_error=standard_error_hedges_grm_true,
        )
        cohens_dz.standardizer = standardizer_dz
        if cohens_dz.standardizer:
            hedges_gz.standardizer = cohens_dz.standardizer / correction
        cohens_dav.standardizer = standardizer_dav
        if cohens_dav.standardizer:
            hedges_gav.standardizer = cohens_dav.standardizer / correction
        cohens_drm.standardizer = standardizer_drm
        if cohens_drm.standardizer:
            hedges_grm.standardizer = cohens_drm.standardizer / correction
        cohens_dz.update_pivotal_ci(
            round(ci_lower_cohens_dz_pivotal, 4), round(ci_upper_cohens_dz_pivotal, 4)
        )
        hedges_gz.update_pivotal_ci(
            round(ci_lower_cohens_dz_pivotal * correction, 4),
            round(ci_upper_cohens_dz_pivotal * correction, 4),
        )
        cohens_dav.update_pivotal_ci(
            round(ci_lower_cohens_dav_pivotal, 4), round(ci_upper_cohens_dav_pivotal, 4)
        )
        hedges_gav.update_pivotal_ci(
            round(ci_lower_cohens_dav_pivotal * correction, 4),
            round(ci_upper_cohens_dav_pivotal * correction, 4),
        )
        cohens_drm.update_pivotal_ci(
            round(ci_lower_cohens_drm_pivotal, 4), round(ci_upper_cohens_drm_pivotal, 4)
        )
        hedges_grm.update_pivotal_ci(
            round(ci_lower_cohens_drm_pivotal * correction, 4),
            round(ci_upper_cohens_drm_pivotal * correction, 4),
        )
        cohens_dav.update_mag_ci(round(lower_ci_mag_dav, 4), round(upper_ci_mag_dav, 4))
        hedges_gav.update_mag_ci(round(lower_ci_mag_gav, 4), round(upper_ci_mag_gav, 4))
        cohens_dav.update_morris_ci(
            round(lower_ci_morris_dav, 4), round(upper_ci_morris_dav, 4)
        )
        hedges_gav.update_morris_ci(
            round(lower_ci_morris_gav, 4), round(upper_ci_morris_gav, 4)
        )
        cohens_dav.update_t_prime_ci(
            round(lower_ci_tprime_dav, 4), round(upper_ci_tprime_dav, 4)
        )
        hedges_gav.update_t_prime_ci(
            round(lower_ci_tprime_gav, 4), round(upper_ci_tprime_gav, 4)
        )
        cohens_dav.update_lambda_prime_ci(
            round(lower_ci_lambda_prime_dav, 4), round(upper_ci_lambda_prime_dav, 4)
        )
        hedges_gav.update_lambda_prime_ci(
            round(lower_ci_lambda_prime_gav, 4), round(upper_ci_lambda_prime_gav, 4)
        )
        ratio_of_means_effect_size = es.RatioOfMeans(
            value=round(ratio_of_means, 4),
            standard_error=round(standard_error_of_means_ratio, 4),
            ci_lower=round(lower_ci_means_ratio, 4),
            ci_upper=round(upper_ci_means_ratio, 4),
        )

        sample1 = res.Sample(
            mean=round(sample_mean_1, 4),
            standard_deviation=int(sample_sd_1),
            size=sample_size,
        )
        sample2 = res.Sample(
            mean=round(sample_mean_2, 4),
            standard_deviation=int(sample_sd_2),
            size=sample_size,
        )
        sample1.diff_mean = round(sample_mean_1 - sample_mean_2, 4)
        sample2.diff_mean = round(sample_mean_2 - sample_mean_1, 4)

        inferential = res.InferentialStatistics(
            score=round(t_score, 4),
            p_value=round(p_value, 4),
        )
        inferential.degrees_of_freedom = round(df, 4)
        inferential.standard_error = round(standard_error, 4)

        results = TwoPairedTResults()
        results.cohens_d = cohens_dz
        results.hedge_g = hedges_gz
        results.cohens_dav = cohens_dav
        results.hedge_gav = hedges_gav
        results.cohens_drm = cohens_drm
        results.hedge_grm = hedges_grm
        results.ratio_of_means = ratio_of_means_effect_size
        results.inferential = inferential
        results.sample1 = sample1
        results.sample2 = sample2

        return results
