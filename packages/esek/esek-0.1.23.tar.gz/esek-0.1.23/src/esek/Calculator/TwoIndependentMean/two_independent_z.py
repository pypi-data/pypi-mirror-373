"""
Two Independent Z Tests for Two Independent Means
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import stats
from ...utils import interfaces, res, utils, es, texts


@dataclass
class TwoIndependentZResults:
    """
    Results for Two Independent Z Tests.
    """

    inferential: Optional[res.InferentialStatistics] = None
    cohens_d: Optional[es.CohenD] = None
    sample1: Optional[res.Sample] = None
    sample2: Optional[res.Sample] = None


class TwoIndependentZTests(interfaces.AbstractTest):
    """
    Two Independent Z Tests for Two Independent Means.
    This class provides methods to calculate Z scores, Cohen's d, and confidence intervals
    for two independent samples.

    Attributes
    ----------
    None

    Methods
    -------
    from_score() - Create an instance from a Z score.
    from_parameters() - Create an instance from sample parameters.
    from_data() - Create an instance from raw data.
    """

    @staticmethod
    def from_score(
        z_score: float,
        sample_size_1: int,
        sample_size_2: int,
        confidence_level: float = 0.95,
    ) -> TwoIndependentZResults:
        """
        Create an instance from a Z score.

        Args
        ----
        z_score: float
                The Z score to use.
        sample_size_1: int
                The sample size of the first group.
        sample_size_2: int
                The sample size of the second group.
        confidence_level: float
                The confidence level for the confidence interval (default is 0.95).

        Returns
        -------
        TwoIndependentZResults
            The results of the two independent Z test.
        """
        total_sample_size = sample_size_1
        mean_sample_size = (sample_size_1 + sample_size_2) / 2
        cohens_d = ((2 * z_score) / np.sqrt(total_sample_size)) * np.sqrt(
            mean_sample_size / ((2 * sample_size_1 * sample_size_2) / total_sample_size)
        )
        p_value = min(float(stats.norm.sf((abs(z_score))) * 2), 0.99999)
        ci_lower, ci_upper, standard_error_es = utils.ci_from_cohens_d_two_samples(
            cohens_d, sample_size_1, sample_size_2, confidence_level
        )

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            score=round(z_score, 4),
            p_value=round(p_value, 4),
        )

        cohens_d_es: es.CohenD = es.CohenD(
            value=round(cohens_d, 4),
            ci_lower=round(ci_lower, 4),
            ci_upper=round(ci_upper, 4),
            standard_error=round(standard_error_es, 4),
        )

        results = TwoIndependentZResults()
        results.inferential = inferential
        results.cohens_d = cohens_d_es

        return results

    @staticmethod
    def from_parameters(
        sample_mean_1: float,
        sample_mean_2: float,
        population_sd_1: float,
        population_sd_2: float,
        sample_size_1: int,
        sample_size_2: int,
        population_diff: float,
        confidence_level: float = 0.95,
    ) -> TwoIndependentZResults:
        """
        Create an instance from a parameters.

        Args
        ----
        sample_mean_1: float
                The mean of the first sample.
        sample_mean_2: float
                The mean of the second sample.
        population_sd_1: float
                The population standard deviation of the first sample.
        population_sd_2: float
                The population standard deviation of the second sample.
        sample_size_1: int
                The sample size of the first group.
        sample_size_2: int
                The sample size of the second group.
        population_diff: float
                The population difference to test.
        confidence_level: float
                The confidence level for the confidence interval (default is 0.95).

        Returns
        -------
        TwoIndependentZResults
            The results of the two independent Z test.
        """
        var1 = population_sd_1**2
        var2 = population_sd_2**2
        standard_error_mean_difference_population = np.sqrt(
            ((var1 / sample_size_1) + (var2 / sample_size_2))
        )
        sd_difference_pop = np.sqrt((var1 + var2) / 2)
        z_score = (
            population_diff - (sample_mean_1 - sample_mean_2)
        ) / standard_error_mean_difference_population
        cohens_d = abs(
            (population_diff - (sample_mean_1 - sample_mean_2)) / sd_difference_pop
        )
        p_value = min(float(stats.norm.sf((abs(z_score))) * 2), 0.99999)
        ci_lower, ci_upper, standard_error_es = utils.ci_from_cohens_d_two_samples(
            cohens_d, sample_size_1, sample_size_2, confidence_level
        )

        sample1: res.Sample = res.Sample(
            mean=round(sample_mean_1, 4),
            size=round(sample_size_1, 4),
            standard_deviation=round(population_sd_1, 4),
        )

        sample1.diff_mean = round(population_diff, 4)
        sample1.diff_sd = round(sd_difference_pop, 4)

        sample2: res.Sample = res.Sample(
            mean=round(sample_mean_2, 4),
            size=round(sample_size_2, 4),
            standard_deviation=round(population_sd_2, 4),
        )

        sample2.diff_mean = round(population_diff, 4)
        sample2.diff_sd = round(sd_difference_pop, 4)

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            score=round(z_score, 4),
            p_value=round(p_value, 4),
        )
        inferential.standard_error = round(standard_error_mean_difference_population, 4)

        cohens_d_es: es.CohenD = es.CohenD(
            value=round(cohens_d, 4),
            ci_lower=round(ci_lower, 4),
            ci_upper=round(ci_upper, 4),
            standard_error=round(standard_error_es, 4),
        )

        results = TwoIndependentZResults()
        results.sample1 = sample1
        results.sample2 = sample2
        results.inferential = inferential
        results.cohens_d = cohens_d_es

        return results

    @staticmethod
    def from_data(
        columns: list[list],
        population_diff: float,
        population_sd_1: float,
        population_sd_2: float,
        confidence_level: float = 0.95,
    ) -> TwoIndependentZResults:
        """
        Create an instance from a parameters.

        Args
        ----
        columns: list[list]
                The data columns to use for the test.
        population_diff: float
                The population difference to test.
        population_sd_1: float
                The population standard deviation of the first sample.
        population_sd_2: float
                The population standard deviation of the second sample..
        confidence_level: float
                The confidence level for the confidence interval (default is 0.95).

        Returns
        -------
        TwoIndependentZResults
            The results of the two independent Z test.

        Raises
        ------
        ValueError
            If the columns list does not contain exactly two columns.
        """
        if len(columns) != 2:
            raise ValueError(texts.Errors.columns_must_be_two)

        column_1 = columns[0]
        column_2 = columns[1]

        sample_mean_1 = np.mean(column_1)
        sample_mean_2 = np.mean(column_2)
        sample_std_1 = np.std(column_1, ddof=1)
        sample_std_2 = np.std(column_2, ddof=1)
        var1 = population_sd_1**2
        var2 = population_sd_2**2
        sample_size_1 = len(column_1)
        sample_size_2 = len(column_2)
        standard_error_mean_difference_population = np.sqrt(
            ((var1 / sample_size_1) + (var2 / sample_size_2))
        )
        sd_difference_pop = np.sqrt((var1 + var2) / 2)
        z_score = (
            population_diff - (sample_mean_1 - sample_mean_2)
        ) / standard_error_mean_difference_population
        cohens_d = abs(
            (population_diff - (sample_mean_1 - sample_mean_2)) / sd_difference_pop
        )
        p_value = min(float(stats.norm.sf((abs(z_score))) * 2), 0.99999)
        ci_lower, ci_upper, standard_error_es = utils.ci_from_cohens_d_two_samples(
            cohens_d, sample_size_1, sample_size_2, confidence_level
        )

        sample1: res.Sample = res.Sample(
            mean=round(float(sample_mean_1), 4),
            size=round(sample_size_1, 4),
            standard_deviation=round(float(sample_std_1), 4),
        )
        sample1.population_sd_diff = round(population_sd_1, 4)
        sample1.diff_sd = round(sd_difference_pop, 4)

        sample2: res.Sample = res.Sample(
            mean=round(float(sample_mean_2), 4),
            size=round(sample_size_2, 4),
            standard_deviation=round(float(sample_std_2), 4),
        )
        sample2.population_sd_diff = round(population_sd_2, 4)
        sample2.diff_sd = round(sd_difference_pop, 4)

        inferential: res.InferentialStatistics = res.InferentialStatistics(
            score=round(z_score, 4),
            p_value=round(p_value, 4),
        )
        inferential.standard_error = round(standard_error_mean_difference_population, 4)

        cohens_d_es: es.CohenD = es.CohenD(
            value=round(cohens_d, 4),
            ci_lower=round(ci_lower, 4),
            ci_upper=round(ci_upper, 4),
            standard_error=round(standard_error_es, 4),
        )

        results = TwoIndependentZResults()
        results.sample1 = sample1
        results.sample2 = sample2
        results.inferential = inferential
        results.cohens_d = cohens_d_es

        return results
