"""
This module implements statistical methods for comparing the means of two independent samples using the two-sample t-test.
It provides classes and methods to compute inferential statistics, effect sizes (Cohen's d, Hedges' g, and population Cohen's d),
and the ratio of means, along with their confidence intervals and standard errors.

Classes:
    - TwoIndependentTResults: Container for results of two-sample t-tests, including sample statistics, inferential statistics, and effect sizes.
    - TwoIndependentTTests: Implements static methods for performing two-sample t-tests from summary statistics, t-scores, or raw data.

Dependencies:
    - numpy, scipy.stats, math
    - Internal modules: interfaces, res, utils, es

Note:
    All effect sizes and statistics are returned with confidence intervals and standard errors.
    The module assumes equal variances between groups for pooled standard deviation calculations.
Two Independent T-tests for comparing means of two independent samples.

"""

from dataclasses import dataclass
import math
from typing import Optional
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es, texts


@dataclass
class TwoIndependentTResults:
    """
    Container for results of two-sample t-tests.
    """

    sample1: Optional[res.Sample] = None
    sample2: Optional[res.Sample] = None
    inferential: Optional[res.InferentialStatistics] = None
    cohens_d: Optional[es.CohenD] = None
    hedges_g: Optional[es.HedgesG] = None
    cohens_d_pop: Optional[es.CohensDPop] = None
    ratio_of_means: Optional[es.RatioOfMeans] = None


class TwoIndependentTTests(interfaces.AbstractTest):
    """
    Implements statistical methods for conducting two-sample independent t-tests,
    including calculation of inferential statistics and effect sizes.
    This class provides static methods to compute results for two independent samples
    using three approaches: from_score, from_parameters, from_data
    For each approach, the following statistics and effect sizes are computed:
        - Inferential statistics: t-score, p-value, degrees of freedom, standard error.
        - Effect sizes: Cohen's d, Hedges' g, and population Cohen's d, with central and pivotal confidence intervals.
        - Ratio of means (from_parameters only), including confidence intervals and standard error.

    The class supports calculation of confidence intervals for effect sizes using both central and pivotal methods,
    and applies bias correction for Hedges' g.

    Args:
        None (all methods are static).

    Methods:
        - from_score: Calculates results from a given t-score and sample sizes.
        - from_parameters: Calculates results from sample means, standard deviations, and sizes.
        - from_data: Calculates results directly from raw data columns.

    Raises:
        ValueError: If input data is invalid (e.g., incorrect number of columns in from_data).
    Returns:
        TwoIndependentTResults: An object containing all computed statistics and effect sizes.
    Usage:
        Use the static methods to obtain results for two independent samples, depending on available data.
    """

    @staticmethod
    def from_score(
        t_score: float,
        sample_size_1: int,
        sample_size_2: int,
        confidence_level: float = 0.95,
    ) -> TwoIndependentTResults:
        """
        Computes inferential statistics and effect sizes for a two-sample independent t-test from a given t-score and sample sizes.
        Parameters
        ----------
        t_score : float
            The t-statistic value from the independent t-test.
        sample_size_1 : int
            Sample size of the first group.
        sample_size_2 : int
            Sample size of the second group.
        confidence_level : float, optional
            Confidence level for confidence intervals (default is 0.95).

        Returns
        -------
        TwoIndependentTResults
            An object containing inferential statistics (p-value, t-score, degrees of freedom)
            and effect size estimates (Cohen's d, Hedges' g, population Cohen's d) with their
            confidence intervals and standard errors.

        Notes
        -----
        - Calculates p-value, Cohen's d, Hedges' g, and population Cohen's d.
        - Computes central and pivotal confidence intervals for effect sizes.
        - Standard errors for effect sizes are included.
        - Uses correction factors for Hedges' g and population Cohen's d.
        """
        sample_size = sample_size_1 + sample_size_2
        df = sample_size - 2
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        cohens_ds = t_score * (np.sqrt(1 / sample_size_1 + 1 / sample_size_2))
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gs = cohens_ds * correction
        cohens_d_pop = cohens_ds / np.sqrt((df / sample_size))
        ci_lower_cohens_ds_pivotal, ci_upper_cohens_ds_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        (
            ci_lower_cohens_ds_central,
            ci_upper_cohens_ds_central,
            standard_error_cohens_ds_true,
            standard_error_cohens_ds_morris,
            standard_error_cohens_ds_hedges,
            standard_error_cohens_ds_hedges_olkin,
            standard_error_cohens_ds_mle,
            standard_error_cohens_ds_largen,
            standard_error_cohens_ds_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            cohens_ds, sample_size_1, sample_size_2, confidence_level
        )
        (
            ci_lower_hedges_gs_central,
            ci_upper_hedges_gs_central,
            standard_error_hedges_gs_true,
            standard_error_hedges_gs_morris,
            standard_error_hedges_gs_hedges,
            standard_error_hedges_gs_hedges_olkin,
            standard_error_hedges_gs_mle,
            standard_error_hedges_gs_largen,
            standard_error_hedges_gs_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            hedges_gs, sample_size_1, sample_size_2, confidence_level
        )
        (
            ci_lower_cohens_d_pop_central,
            ci_upper_cohens_d_pop_central,
            standard_error_cohens_d_pop_true,
            standard_error_cohens_d_pop_morris,
            standard_error_cohens_d_pop_hedges,
            standard_error_cohens_d_pop_hedges_olkin,
            standard_error_cohens_d_pop_mle,
            standard_error_cohens_d_pop_largen,
            standard_error_cohens_d_pop_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            cohens_d_pop, sample_size_1, sample_size_2, confidence_level
        )

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            p_value=round(p_value, 4), score=round(t_score, 4)
        )
        inferential.degrees_of_freedom = round(df, 4)

        cohens_d_es: es.CohenD = es.CohenD(
            value=round(cohens_ds, 4),
            ci_lower=round(ci_lower_cohens_ds_central, 4),
            ci_upper=round(ci_upper_cohens_ds_central, 4),
            standard_error=round(standard_error_cohens_ds_true, 4),
        )

        cohens_d_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal, 4), round(ci_upper_cohens_ds_pivotal, 4)
        )

        hedges_g_es: es.HedgesG = es.HedgesG(
            value=round(hedges_gs, 4),
            ci_lower=round(ci_lower_hedges_gs_central, 4),
            ci_upper=round(ci_upper_hedges_gs_central, 4),
            standard_error=round(standard_error_hedges_gs_true, 4),
        )

        hedges_g_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal * correction, 4),
            round(ci_upper_cohens_ds_pivotal * correction, 4),
        )

        cohens_d_pop_es: es.CohensDPop = es.CohensDPop(
            value=round(cohens_d_pop, 4),
            ci_lower=round(ci_lower_cohens_d_pop_central, 4),
            ci_upper=round(ci_upper_cohens_d_pop_central, 4),
            standard_error=round(standard_error_cohens_d_pop_true, 4),
        )

        cohens_d_pop_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal / np.sqrt(df / sample_size), 4),
            round(ci_upper_cohens_ds_pivotal / np.sqrt(df / sample_size), 4),
        )

        results = TwoIndependentTResults()

        results.inferential = inferential
        results.cohens_d = cohens_d_es
        results.hedges_g = hedges_g_es
        results.cohens_d_pop = cohens_d_pop_es

        return results

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
    ) -> TwoIndependentTResults:
        """
        Calculates inferential statistics and effect sizes for a two-sample independent t-test
        using sample means, standard deviations, and sample sizes.

        Parameters
        ----------
        sample_mean_1 : float
            Mean of sample 1.
        sample_mean_2 : float
            Mean of sample 2.
        sample_sd_1 : float
            Standard deviation of sample 1.
        sample_sd_2 : float
            Standard deviation of sample 2.
        sample_size_1 : int
            Size (number of observations) of sample 1.
        sample_size_2 : int
            Size (number of observations) of sample 2.
        population_mean_diff : float, optional
            Hypothesized difference in population means (default is 0).
        confidence_level : float, optional
            Confidence level for confidence intervals (default is 0.95).

        Returns
        -------
        TwoIndependentTResults
            Object containing descriptive statistics, inferential statistics, and effect sizes
            (Cohen's d, Hedges' g, population Cohen's d, and ratio of means) with confidence intervals.
        """
        sample_size = sample_size_1 + sample_size_2
        df = sample_size - 2
        sample_mean_difference = sample_mean_1 - sample_mean_2
        standardizer_ds = np.sqrt(
            (
                (((sample_size_1 - 1) * sample_sd_1**2))
                + ((sample_size_2 - 1) * sample_sd_2**2)
            )
            / (sample_size - 2)
        )
        standardizer_dpop = np.sqrt(
            (
                (((sample_size_1 - 1) * sample_sd_1**2))
                + ((sample_size_2 - 1) * sample_sd_2**2)
            )
            / (sample_size)
        )
        standard_error = standardizer_ds * np.sqrt(
            (sample_size_1 + sample_size_2) / (sample_size_1 * sample_size_2)
        )
        t_score = (sample_mean_difference - population_mean_diff) / standard_error
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        cohens_ds = t_score * (np.sqrt(1 / sample_size_1 + 1 / sample_size_2))
        cohens_dpop = cohens_ds / np.sqrt((df / sample_size))
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gs = cohens_ds * correction
        standardizer_hedges_gs = standardizer_ds / correction
        ci_lower_cohens_ds_pivotal, ci_upper_cohens_ds_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        (
            ci_lower_cohens_ds_central,
            ci_upper_cohens_ds_central,
            standard_error_cohens_ds_true,
            standard_error_cohens_ds_morris,
            standard_error_cohens_ds_hedges,
            standard_error_cohens_ds_hedges_olkin,
            standard_error_cohens_ds_mle,
            standard_error_cohens_ds_largen,
            standard_error_cohens_ds_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            cohens_ds, sample_size_1, sample_size_2, confidence_level
        )
        (
            ci_lower_hedges_gs_central,
            ci_upper_hedges_gs_central,
            standard_error_hedges_gs_true,
            standard_error_hedges_gs_morris,
            standard_error_hedges_gs_hedges,
            standard_error_hedges_gs_hedges_olkin,
            standard_error_hedges_gs_mle,
            standard_error_hedges_gs_largen,
            standard_error_hedges_gs_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            hedges_gs, sample_size_1, sample_size_2, confidence_level
        )
        (
            ci_lower_cohens_dpop_central,
            ci_upper_cohens_dpop_central,
            standard_error_cohens_dpop_true,
            standard_error_cohens_dpop_morris,
            standard_error_cohens_dpop_hedges,
            standard_error_cohens_dpop_hedges_olkin,
            standard_error_cohens_dpop_mle,
            standard_error_cohens_dpop_largen,
            standard_error_cohens_dpop_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            cohens_dpop, sample_size_1, sample_size_2, confidence_level
        )

        ratio_of_means = sample_mean_1 / sample_mean_2
        variance_of_means_ratio = sample_sd_1**2 / (
            sample_size_1 * sample_mean_1**2
        ) + sample_sd_2**2 / (sample_size_2 * sample_mean_2**2)
        standard_error_of_means_ratio = np.sqrt(variance_of_means_ratio)
        degrees_of_freedom_means_ratio = variance_of_means_ratio**2 / (
            sample_sd_1**4 / (sample_mean_1**4 * (sample_size_1**3 - sample_size_1**2))
            + sample_sd_2**4
            / (sample_mean_2**4 * (sample_size_2**3 - sample_size_2**2))
        )
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

        sample1: res.Sample = res.Sample(
            mean=round(sample_mean_1, 4),
            size=round(sample_size_1, 4),
            standard_deviation=round(sample_sd_1, 4),
        )

        sample2: res.Sample = res.Sample(
            mean=round(sample_mean_2, 4),
            size=round(sample_size_2, 4),
            standard_deviation=round(sample_sd_2, 4),
        )

        sample1.diff_mean = round(sample_mean_difference, 4)
        sample2.diff_mean = round(sample_mean_difference, 4)

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            p_value=round(p_value, 4), score=round(t_score, 4)
        )
        inferential.degrees_of_freedom = round(df, 4)
        inferential.standard_error = round(standard_error, 4)

        cohens_d_es: es.CohenD = es.CohenD(
            value=round(cohens_ds, 4),
            ci_lower=round(ci_lower_cohens_ds_central, 4),
            ci_upper=round(ci_upper_cohens_ds_central, 4),
            standard_error=round(standard_error_cohens_ds_true, 4),
        )
        cohens_d_es.standardizer = round(standardizer_ds, 4)
        cohens_d_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal, 4), round(ci_upper_cohens_ds_pivotal, 4)
        )

        hedges_g_es: es.HedgesG = es.HedgesG(
            value=round(hedges_gs, 4),
            ci_lower=round(ci_lower_hedges_gs_central, 4),
            ci_upper=round(ci_upper_hedges_gs_central, 4),
            standard_error=round(standard_error_hedges_gs_true, 4),
        )
        hedges_g_es.standardizer = round(standardizer_hedges_gs, 4)
        hedges_g_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal * correction, 4),
            round(ci_upper_cohens_ds_pivotal * correction, 4),
        )

        cohens_d_pop_es: es.CohensDPop = es.CohensDPop(
            value=round(cohens_dpop, 4),
            ci_lower=round(ci_lower_cohens_dpop_central, 4),
            ci_upper=round(ci_upper_cohens_dpop_central, 4),
            standard_error=round(standard_error_cohens_dpop_true, 4),
        )
        cohens_d_pop_es.standardizer = round(standardizer_dpop, 4)
        cohens_d_pop_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal / np.sqrt(df / sample_size), 4),
            round(ci_upper_cohens_ds_pivotal / np.sqrt(df / sample_size), 4),
        )

        ratio_of_means_es: es.RatioOfMeans = es.RatioOfMeans(
            value=round(ratio_of_means, 4),
            ci_lower=round(lower_ci_means_ratio, 4),
            ci_upper=round(upper_ci_means_ratio, 4),
            standard_error=round(standard_error_of_means_ratio, 4),
        )

        results = TwoIndependentTResults()
        results.sample1 = sample1
        results.sample2 = sample2
        results.inferential = inferential
        results.cohens_d = cohens_d_es
        results.hedges_g = hedges_g_es
        results.cohens_d_pop = cohens_d_pop_es
        results.ratio_of_means = ratio_of_means_es

        return results

    @staticmethod
    def from_data(
        columns: list[list],
        population_mean_diff: float = 0,
        confidence_level: float = 0.95,
    ) -> TwoIndependentTResults:
        """
        Calculates statistics for a two-sample independent t-test from raw data.
        Parameters
        ----------
        columns : list[list]
            A list containing two lists, each representing the sample data for one group.
        population_mean_diff : float, optional
            The hypothesized difference in population means (default is 0).
        confidence_level : float, optional
            The confidence level for confidence intervals (default is 0.95).
        Returns
        -------
        TwoIndependentTResults
            An object containing descriptive statistics for both samples, inferential statistics (t-score, p-value, degrees of freedom, standard error), and effect size estimates (Cohen's d, Hedges' g, population Cohen's d) with their confidence intervals and standardizers.
        Raises
        ------
        ValueError
            If the input does not contain exactly two columns of data.
        Notes
        -----
        This method computes the independent samples t-test using the provided data, including effect sizes and their confidence intervals.
        It assumes equal variances between groups.
        """
        if len(columns) != 2:
            raise ValueError(texts.Errors.columns_must_be_two)
        column_1 = columns[0]
        column_2 = columns[1]

        sample_mean_1 = np.mean(column_1)
        sample_mean_2 = np.mean(column_2)
        sample_sd_1 = np.std(column_1, ddof=1)
        sample_sd_2 = np.std(column_2, ddof=1)
        sample_size_1 = len(column_1)
        sample_size_2 = len(column_2)
        sample_size = sample_size_1 + sample_size_2
        df = sample_size - 2
        sample_mean_difference = sample_mean_1 - sample_mean_2
        standardizer_ds = np.sqrt(
            (
                (((sample_size_1 - 1) * sample_sd_1**2))
                + ((sample_size_2 - 1) * sample_sd_2**2)
            )
            / (sample_size - 2)
        )
        standardizer_dpop = np.sqrt(
            (
                (((sample_size_1 - 1) * sample_sd_1**2))
                + ((sample_size_2 - 1) * sample_sd_2**2)
            )
            / (sample_size)
        )
        standard_error = standardizer_ds * np.sqrt(
            (sample_size_1 + sample_size_2) / (sample_size_1 * sample_size_2)
        )
        t_score = (sample_mean_difference - population_mean_diff) / standard_error
        p_value = min(float(stats.t.sf((abs(t_score)), df) * 2), 0.99999)
        cohens_ds = t_score * (np.sqrt(1 / sample_size_1 + 1 / sample_size_2))
        cohens_dpop = cohens_ds / np.sqrt((df / sample_size))
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_gs = cohens_ds * correction
        standardizer_hedges_gs = standardizer_ds / correction
        ci_lower_cohens_ds_pivotal, ci_upper_cohens_ds_pivotal = utils.pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        (
            ci_lower_cohens_ds_central,
            ci_upper_cohens_ds_central,
            standard_error_cohens_ds_true,
            standard_error_cohens_ds_morris,
            standard_error_cohens_ds_hedges,
            standard_error_cohens_ds_hedges_olkin,
            standard_error_cohens_ds_mle,
            standard_error_cohens_ds_largen,
            standard_error_cohens_ds_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            cohens_ds, sample_size_1, sample_size_2, confidence_level
        )
        (
            ci_lower_hedges_gs_central,
            ci_upper_hedges_gs_central,
            standard_error_hedges_gs_true,
            standard_error_hedges_gs_morris,
            standard_error_hedges_gs_hedges,
            standard_error_hedges_gs_hedges_olkin,
            standard_error_hedges_gs_mle,
            standard_error_hedges_gs_largen,
            standard_error_hedges_gs_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            hedges_gs, sample_size_1, sample_size_2, confidence_level
        )
        (
            ci_lower_cohens_dpop_central,
            ci_upper_cohens_dpop_central,
            standard_error_cohens_dpop_true,
            standard_error_cohens_dpop_morris,
            standard_error_cohens_dpop_hedges,
            standard_error_cohens_dpop_hedges_olkin,
            standard_error_cohens_dpop_mle,
            standard_error_cohens_dpop_largen,
            standard_error_cohens_dpop_small_n,
        ) = utils.ci_from_cohens_d_t_test(
            cohens_dpop, sample_size_1, sample_size_2, confidence_level
        )

        sample1: res.Sample = res.Sample(
            mean=round(float(sample_mean_1), 4),
            size=round(sample_size_1, 4),
            standard_deviation=round(float(sample_sd_1), 4),
        )

        sample2: res.Sample = res.Sample(
            mean=round(float(sample_mean_2), 4),
            size=round(sample_size_2, 4),
            standard_deviation=round(float(sample_sd_2), 4),
        )

        sample1.diff_mean = round(float(sample_mean_difference), 4)
        sample2.diff_mean = round(float(sample_mean_difference), 4)
        sample1.population_sd_diff = round(population_mean_diff, 4)
        sample2.population_sd_diff = round(population_mean_diff, 4)

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            p_value=round(p_value, 4), score=round(t_score, 4)
        )
        inferential.degrees_of_freedom = round(df, 4)
        inferential.standard_error = round(standard_error, 4)

        cohens_d_es: es.CohenD = es.CohenD(
            value=round(cohens_ds, 4),
            ci_lower=round(ci_lower_cohens_ds_central, 4),
            ci_upper=round(ci_upper_cohens_ds_central, 4),
            standard_error=round(standard_error_cohens_ds_true, 4),
        )
        cohens_d_es.standardizer = round(standardizer_ds, 4)
        cohens_d_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal, 4), round(ci_upper_cohens_ds_pivotal, 4)
        )

        hedges_g_es: es.HedgesG = es.HedgesG(
            value=round(hedges_gs, 4),
            ci_lower=round(ci_lower_hedges_gs_central, 4),
            ci_upper=round(ci_upper_hedges_gs_central, 4),
            standard_error=round(standard_error_hedges_gs_true, 4),
        )
        hedges_g_es.standardizer = round(standardizer_hedges_gs, 4)
        hedges_g_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal * correction, 4),
            round(ci_upper_cohens_ds_pivotal * correction, 4),
        )

        cohens_d_pop_es: es.CohensDPop = es.CohensDPop(
            value=round(cohens_dpop, 4),
            ci_lower=round(ci_lower_cohens_dpop_central, 4),
            ci_upper=round(ci_upper_cohens_dpop_central, 4),
            standard_error=round(standard_error_cohens_dpop_true, 4),
        )
        cohens_d_pop_es.standardizer = round(standardizer_dpop, 4)
        cohens_d_pop_es.update_pivotal_ci(
            round(ci_lower_cohens_ds_pivotal / np.sqrt(df / sample_size), 4),
            round(ci_upper_cohens_ds_pivotal / np.sqrt(df / sample_size), 4),
        )

        results = TwoIndependentTResults()
        results.sample1 = sample1
        results.sample2 = sample2
        results.inferential = inferential
        results.cohens_d = cohens_d_es
        results.hedges_g = hedges_g_es
        results.cohens_d_pop = cohens_d_pop_es

        return results
