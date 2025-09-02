"""
This module provides functionality for calculating the Common Language Effect Size (CLES) for one sample t-tests.

Classes:
    OneSampleCLESResults: A class containing results from CLES calculations
    OneSampleTTest: A class containing static methods for calculating the Common Language Effect Size (CLES) and other related statistics.

Methods:
    pivotal_ci_t: Calculate the pivotal confidence intervals for a t-score.
    calculate_central_ci_from_cohens_d_one_sample_t_test: Calculate the central confidence intervals for Cohen's d in a one-sample t-test.
    CI_NCP_one_Sample: Calculate the Non-Central Parameter (NCP) confidence intervals for a one-sample t-test.
    density: Calculate the density function for a given value.
    area_under_function: Calculate the area under a given function using numerical integration.
    WinsorizedVariance: Calculate the Winsorized variance of a sample.
    WinsorizedCorrelation: Calculate the Winsorized correlation between two samples.
"""

import math
from typing import Optional
from dataclasses import dataclass
import numpy as np
import numpy.typing as npt
from scipy.stats import norm, nct, t, trim_mean


@dataclass
class OneSampleCLESResults:
    """Class for storing one-sample CLES test results"""

    # Common Language Effect Sizes
    cles_d: Optional[npt.NDArray[np.float16]] = (
        None  # McGraw & Wong Common Language Effect Size
    )
    cles_g: Optional[npt.NDArray[np.float16]] = (
        None  # McGraw & Wong Unbiased Common Language Effect Size
    )

    # Test Statistics
    t_score: Optional[npt.NDArray[np.float16]] = None
    df: Optional[npt.NDArray[np.float16]] = None
    p_value: Optional[npt.NDArray[np.float16]] = None

    # Central CI's
    lower_central_ci_cld: Optional[npt.NDArray[np.float16]] = None
    upper_central_ci_cld: Optional[npt.NDArray[np.float16]] = None
    lower_central_ci_clg: Optional[npt.NDArray[np.float16]] = None
    upper_central_ci_clg: Optional[npt.NDArray[np.float16]] = None

    # Non-Central CI's
    lower_ncp_ci_cld: Optional[npt.NDArray[np.float16]] = None
    upper_ncp_ci_cld: Optional[npt.NDArray[np.float16]] = None
    lower_ncp_ci_clg: Optional[npt.NDArray[np.float16]] = None
    upper_ncp_ci_clg: Optional[npt.NDArray[np.float16]] = None

    # Pivotal CI's
    lower_pivotal_ci_cld: Optional[npt.NDArray[np.float16]] = None
    upper_pivotal_ci_cld: Optional[npt.NDArray[np.float16]] = None
    lower_pivotal_ci_clg: Optional[npt.NDArray[np.float16]] = None
    upper_pivotal_ci_clg: Optional[npt.NDArray[np.float16]] = None

    # Robust Statistics
    robust_effect_size_akp: Optional[npt.NDArray[np.float16]] = None
    lower_ci_robust_akp: Optional[npt.NDArray[np.float16]] = None
    upper_ci_robust_akp: Optional[npt.NDArray[np.float16]] = None
    trimmed_mean: Optional[npt.NDArray[np.float16] | float] = None
    winsorized_sd: Optional[npt.NDArray[np.float16]] = None
    yuens_t: Optional[npt.NDArray[np.float16]] = None
    robust_df: Optional[npt.NDArray[np.float16]] = None
    robust_p_value: Optional[npt.NDArray[np.float16]] = None
    mean_difference: Optional[npt.NDArray[np.float16]] = None
    standard_error: Optional[npt.NDArray[np.float16]] = None
    statistical_line_robust_akp: Optional[str] = None
    statistical_line_cld: Optional[str] = None
    statistical_line_clg: Optional[str] = None


def pivotal_ci_t(t_score, df, sample_size, confidence_level):
    """
    Calculate the pivotal confidence intervals for a t-score.

    Parameters
    ----------
    t_Score : float
        The t-score value.
    df : int
        Degrees of freedom.
    sample_size : int
        The size of the sample.
    confidence_level : float
        The confidence level as a decimal (e.g., 0.95 for 95%).

    Returns
    -------
    tuple
        A tuple containing:
        - lower_ci (float): Lower bound of the pivotal confidence interval.
        - upper_ci (float): Upper bound of the pivotal confidence interval.
    """
    is_negative = False
    if t_score < 0:
        is_negative = True
        t_score = abs(t_score)
    upper_limit = 1 - (1 - confidence_level) / 2
    lower_limit = (1 - confidence_level) / 2

    lower_criterion = [-t_score, t_score / 2, t_score]
    upper_criterion = [t_score, 2 * t_score, 3 * t_score]

    while nct.cdf(t_score, df, lower_criterion[0]) < upper_limit:
        lower_criterion = [
            lower_criterion[0] - t_score,
            lower_criterion[0],
            lower_criterion[2],
        ]

    while nct.cdf(t_score, df, upper_criterion[0]) < lower_limit:
        if nct.cdf(t_score, df) < lower_limit:
            lower_ci = [0, nct.cdf(t_score, df)]
            upper_criterion = [
                upper_criterion[0] / 4,
                upper_criterion[0],
                upper_criterion[2],
            ]

    while nct.cdf(t_score, df, upper_criterion[2]) > lower_limit:
        upper_criterion = [
            upper_criterion[0],
            upper_criterion[2],
            upper_criterion[2] + t_score,
        ]

    lower_ci = 0.0
    diff_lower = 1
    while diff_lower > 0.00001:
        if nct.cdf(t_score, df, lower_criterion[1]) < upper_limit:
            lower_criterion = [
                lower_criterion[0],
                (lower_criterion[0] + lower_criterion[1]) / 2,
                lower_criterion[1],
            ]
        else:
            lower_criterion = [
                lower_criterion[1],
                (lower_criterion[1] + lower_criterion[2]) / 2,
                lower_criterion[2],
            ]
        diff_lower = abs(nct.cdf(t_score, df, lower_criterion[1]) - upper_limit)
        lower_ci = lower_criterion[1] / (np.sqrt(sample_size))

    upper_ci = 0.0
    diff_upper = 1
    while diff_upper > 0.00001:
        if nct.cdf(t_score, df, upper_criterion[1]) < lower_limit:
            upper_criterion = [
                upper_criterion[0],
                (upper_criterion[0] + upper_criterion[1]) / 2,
                upper_criterion[1],
            ]
        else:
            upper_criterion = [
                upper_criterion[1],
                (upper_criterion[1] + upper_criterion[2]) / 2,
                upper_criterion[2],
            ]
        diff_upper = abs(nct.cdf(t_score, df, upper_criterion[1]) - lower_limit)
        upper_ci = upper_criterion[1] / (np.sqrt(sample_size))
    if is_negative:
        return -upper_ci, -lower_ci
    else:
        return lower_ci, upper_ci


def calculate_central_ci_from_cohens_d_one_sample_t_test(
    cohens_d, sample_size, confidence_level
):
    """
    Calculate the central confidence intervals for Cohen's d in a one-sample t-test.

    Parameters
    ----------
    cohens_d : float
        The calculated Cohen's d effect size.
    sample_size : int
        The size of the sample.
    confidence_level : float
        The confidence level as a decimal (e.g., 0.95 for 95%).

    Returns
    -------
    tuple
        A tuple containing:
        - ci_lower (float): Lower bound of the central confidence interval.
        - ci_upper (float): Upper bound of the central confidence interval.
        - standard_error_es (float): Standard error of the effect size.
    """
    df = sample_size - 1
    correction_factor = math.exp(
        math.lgamma(df / 2) - math.log(math.sqrt(df / 2)) - math.lgamma((df - 1) / 2)
    )
    standard_error_es = np.sqrt(
        (df / (df - 2)) * (1 / sample_size) * (1 + cohens_d**2 * sample_size)
        - (cohens_d**2 / correction_factor**2)
    )
    z_critical_value = norm.ppf(confidence_level + ((1 - confidence_level) / 2))
    ci_lower, ci_upper = (
        cohens_d - standard_error_es * z_critical_value,
        cohens_d + standard_error_es * z_critical_value,
    )
    return ci_lower, ci_upper, standard_error_es


def ci_ncp_one_sample(effect_size, sample_size, confidence_level):
    """
    Calculate the Non-Central Parameter (NCP) confidence intervals for a one-sample t-test.

    Parameters
    ----------
    Effect_Size : float
        The calculated effect size (Cohen's d).
    sample_size : int
        The size of the sample.
    confidence_level : float
        The confidence level as a decimal (e.g., 0.95 for 95%).

    Returns
    -------
    tuple
        A tuple containing:
        - CI_NCP_low (float): Lower bound of the NCP confidence interval.
        - CI_NCP_High (float): Upper bound of the NCP confidence interval.
    """
    NCP_value = effect_size * math.sqrt(sample_size)
    CI_NCP_low = (
        (
            nct.ppf(
                1 / 2 - confidence_level / 2,
                (sample_size - 1),
                loc=0,
                scale=1,
                nc=NCP_value,
            )
        )
        / NCP_value
        * effect_size
    )
    CI_NCP_High = (
        (
            nct.ppf(
                1 / 2 + confidence_level / 2,
                (sample_size - 1),
                loc=0,
                scale=1,
                nc=NCP_value,
            )
        )
        / NCP_value
        * effect_size
    )
    return CI_NCP_low, CI_NCP_High


def density(x):
    """
    Calculate the density function for a given value.

    Parameters
    ----------
    x : float
        The input value.

    Returns
    -------
    float
        The density value.
    """
    x = np.array(x)
    return x**2 * norm.pdf(x)


def area_under_function(
    f, a, b, *args, function_a=None, function_b=None, limit=10, eps=1e-5
):
    """
    Calculate the area under a given function using numerical integration.

    Parameters
    ----------
    f : function
        The function to integrate.
    a : float
        The lower bound of the integration.
    b : float
        The upper bound of the integration.
    *args : tuple
        Additional arguments to pass to the function.
    function_a : float, optional
        The function value at the lower bound.
    function_b : float, optional
        The function value at the upper bound.
    limit : int, optional
        The maximum number of recursive calls (default is 10).
    eps : float, optional
        The tolerance for stopping the recursion (default is 1e-5).

    Returns
    -------
    float
        The area under the function.
    """
    if function_a is None:
        function_a = f(a, *args)
    if function_b is None:
        function_b = f(b, *args)
    midpoint = (a + b) / 2
    f_midpoint = f(midpoint, *args)
    area_trapezoidal = ((function_a + function_b) * (b - a)) / 2
    area_simpson = ((function_a + 4 * f_midpoint + function_b) * (b - a)) / 6
    if abs(area_trapezoidal - area_simpson) < eps or limit == 0:
        return area_simpson
    return area_under_function(
        f,
        a,
        midpoint,
        *args,
        function_a=function_a,
        function_b=f_midpoint,
        limit=limit - 1,
        eps=eps,
    ) + area_under_function(
        f,
        midpoint,
        b,
        *args,
        function_a=f_midpoint,
        function_b=function_b,
        limit=limit - 1,
        eps=eps,
    )


def WinsorizedVariance(x, trimming_level=0.2):
    """
    Calculate the Winsorized variance of a sample.

    Parameters
    ----------
    x : array-like
        The input sample.
    trimming_level : float, optional
        The trimming level (default is 0.2).

    Returns
    -------
    float
        The Winsorized variance.
    """
    y = np.sort(x)
    n = len(x)
    ibot = int(np.floor(trimming_level * n)) + 1
    itop = n - ibot + 1
    xbot = y[ibot - 1]
    xtop = y[itop - 1]
    y = np.where(y <= xbot, xbot, y)
    y = np.where(y >= xtop, xtop, y)
    winvar = np.std(y, ddof=1) ** 2
    return winvar


def WinsorizedCorrelation(x, y, trimming_level=0.2):
    """
    Calculate the Winsorized correlation between two samples.

    Parameters
    ----------
    x : array-like
        The first input sample.
    y : array-like
        The second input sample.
    trimming_level : float, optional
        The trimming level (default is 0.2).

    Returns
    -------
    dict
        A dictionary containing the Winsorized correlation, covariance, p-value, sample size, and test statistic.
    """
    sample_size = len(x)
    x_sorted = np.sort(x)
    y_sorted = np.sort(y)
    trimming_size = int(np.floor(trimming_level * sample_size)) + 1
    x_lower = x_sorted[trimming_size - 1]
    x_upper = x_sorted[sample_size - trimming_size]
    y_lower = y_sorted[trimming_size - 1]
    y_upper = y_sorted[sample_size - trimming_size]
    x_winzsorized = np.clip(x, x_lower, x_upper)
    y_winzsorized = np.clip(y, y_lower, y_upper)
    winsorized_correlation = np.corrcoef(x_winzsorized, y_winzsorized)[0, 1]
    winsorized_covariance = np.cov(x_winzsorized, y_winzsorized)[0, 1]
    test_statistic = winsorized_correlation * np.sqrt(
        (sample_size - 2) / (1 - winsorized_correlation**2)
    )
    Number_of_trimmed_values = int(np.floor(trimming_level * sample_size))
    p_value = 2 * (
        1
        - t.cdf(np.abs(test_statistic), sample_size - 2 * Number_of_trimmed_values - 2)
    )
    return {
        "cor": winsorized_correlation,
        "cov": winsorized_covariance,
        "p.value": p_value,
        "n": sample_size,
        "test_statistic": test_statistic,
    }


class OneSampleTTest:
    """
    A class containing static methods for calculating the Common Language Effect Size (CLES) and other related statistics.

    This class includes the following static methods:
    - one_sample_from_t_score: Calculate the one-sample t-test results from a given t-score.
    - one_sample_from_params: Calculate the one-sample t-test results from given parameters.
    - one_sample_from_data: Calculate the one-sample t-test results from given sample data.
    - Robust_One_Sample: Calculate the robust one-sample t-test results.
    """

    @staticmethod
    def one_sample_from_t_score(params: dict) -> OneSampleCLESResults:
        """
        Calculate the one-sample t-test results from a given t-score.

        Parameters
        ----------
        params : dict
            A dictionary containing the following keys:
            - "t score" (float): The t-score value.
            - "Sample Size" (int): The size of the sample.
            - "Confidence Level" (float): The confidence level as a percentage (e.g., 95 for 95%).

        Returns
        -------
        OneSampleCLESResults
            An object containing all calculated statistics and results
        """
        # Get params
        t_score = params["t score"]
        sample_size = params["Sample Size"]
        confidence_level_percentages = params["Confidence Level"]

        # Create results object
        results = OneSampleCLESResults()

        # Calculation
        confidence_level = confidence_level_percentages / 100
        df = sample_size - 1
        p_value = min(float(t.sf((abs(t_score)), df) * 2), 0.99999)
        cohens_d = t_score / np.sqrt(
            df
        )  # This is Cohen's d and it is calculated based on the sample's standard deviation
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_g = correction * cohens_d
        cles_d = norm.cdf(cohens_d) * 100
        cles_g = norm.cdf(hedges_g) * 100

        (
            ci_lower_cohens_d_central,
            ci_upper_cohens_d_central,
            standrat_error_cohens_d,
        ) = calculate_central_ci_from_cohens_d_one_sample_t_test(
            cohens_d, sample_size, confidence_level
        )
        (
            ci_lower_hedges_g_central,
            ci_upper_hedges_g_central,
            standrat_error_hedges_g,
        ) = calculate_central_ci_from_cohens_d_one_sample_t_test(
            hedges_g, sample_size, confidence_level
        )
        ci_lower_cohens_d_pivotal, ci_upper_cohens_d_pivotal = pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_g_pivotal, ci_upper_hedges_g_pivotal = pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_cohens_d_ncp, ci_upper_cohens_d_ncp = ci_ncp_one_sample(
            cohens_d, sample_size, confidence_level
        )
        ci_lower_hedges_g_ncp, ci_upper_hedges_g_ncp = ci_ncp_one_sample(
            hedges_g, sample_size, confidence_level
        )

        # Set results
        results.cles_d = np.around(cles_d, 4)
        results.cles_g = np.around(cles_g, 4)
        results.t_score = np.around(t_score, 4)
        results.df = np.around(df, 4)
        results.p_value = np.around(p_value, 4)

        results.lower_central_ci_cld = np.around(
            norm.cdf(ci_lower_cohens_d_central) * 100, 4
        )
        results.upper_central_ci_cld = np.around(
            norm.cdf(ci_upper_cohens_d_central) * 100, 4
        )
        results.lower_central_ci_clg = np.around(
            norm.cdf(ci_lower_hedges_g_central) * 100, 4
        )
        results.upper_central_ci_clg = np.around(
            norm.cdf(ci_upper_hedges_g_central) * 100, 4
        )

        results.lower_ncp_ci_cld = np.around(norm.cdf(ci_lower_cohens_d_ncp) * 100, 4)
        results.upper_ncp_ci_cld = np.around(norm.cdf(ci_upper_cohens_d_ncp) * 100, 4)
        results.lower_ncp_ci_clg = np.around(norm.cdf(ci_lower_hedges_g_ncp) * 100, 4)
        results.upper_ncp_ci_clg = np.around(norm.cdf(ci_upper_hedges_g_ncp) * 100, 4)

        results.lower_pivotal_ci_cld = np.around(
            norm.cdf(ci_lower_cohens_d_pivotal) * 100, 4
        )
        results.upper_pivotal_ci_cld = np.around(
            norm.cdf(ci_upper_cohens_d_pivotal) * 100, 4
        )
        results.lower_pivotal_ci_clg = np.around(
            norm.cdf(ci_lower_hedges_g_pivotal * correction) * 100, 4
        )
        results.upper_pivotal_ci_clg = np.around(
            norm.cdf(ci_upper_hedges_g_pivotal * correction) * 100, 4
        )
        formatted_p_value = (
            "{:.3f}".format(p_value).lstrip("0")
            if p_value >= 0.001
            else "\033[3mp\033[0m < .001"
        )
        results.statistical_line_cld = "\033[3mt\033[0m({}) = {:.3f}, {}{}, CLd = {:.3f}, {}% CI(pivotal) [{:.3f}, {:.3f}]".format(
            df,
            t_score,
            "\033[3mp = \033[0m" if p_value >= 0.001 else "",
            formatted_p_value,
            cles_d,
            confidence_level_percentages,
            np.around(norm.cdf(ci_lower_cohens_d_pivotal) * 100, 3),
            np.around(norm.cdf(ci_upper_cohens_d_pivotal) * 100, 3),
        )
        results.statistical_line_clg = "\033[3mt\033[0m({}) = {:.3f}, {}{}, CLg = {:.3f}, {}% CI(pivotal) [{:.3f}, {:.3f}]".format(
            df,
            t_score,
            "\033[3mp = \033[0m" if p_value >= 0.001 else "",
            formatted_p_value,
            cles_g,
            confidence_level_percentages,
            np.around(norm.cdf(ci_lower_hedges_g_pivotal * correction) * 100, 3),
            np.around(norm.cdf(ci_upper_hedges_g_pivotal * correction) * 100, 3),
        )

        return results

    @staticmethod
    def one_sample_from_params(params: dict) -> OneSampleCLESResults:
        """
        Calculate the one-sample t-test results from given parameters.

        Parameters
        ----------
        params : dict
            A dictionary containing the following keys:
            - "Population Mean" (float): The population mean value.
            - "Mean Sample" (float): The mean of the sample.
            - "Standard Deviation Sample" (float): The standard deviation of the sample.
            - "Sample Size" (int): The size of the sample.
            - "Confidence Level" (float): The confidence level as a percentage (e.g., 95 for 95%).

        Returns
        -------
        OneSampleCLESResults
            An object containing all calculated statistics and results
        """
        # Set params
        population_mean = params["Population Mean"]
        sample_mean = params["Mean Sample"]
        sample_sd = params["Standard Deviation Sample"]
        sample_size = params["Sample Size"]
        confidence_level_percentages = params["Confidence Level"]

        # Create results object
        results = OneSampleCLESResults()

        # Calculation
        confidence_level = confidence_level_percentages / 100
        df = sample_size - 1
        standard_error = sample_sd / np.sqrt(
            df
        )  # This is the standard error of mean's estimate in one sample t-test
        t_score = (
            sample_mean - population_mean
        ) / standard_error  # This is the t score in the test which is used to calculate the p-value
        cohens_d = (
            sample_mean - population_mean
        ) / sample_sd  # This is the effect size for one sample t-test Cohen's d
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_g = cohens_d * correction  # This is the actual corrected effect size
        cles_d = norm.cdf(cohens_d) * 100
        cles_g = norm.cdf(hedges_g) * 100
        p_value = min(float(t.sf((abs(t_score)), df) * 2), 0.99999)
        (
            ci_lower_cohens_d_central,
            ci_upper_cohens_d_central,
            standrat_error_cohens_d,
        ) = calculate_central_ci_from_cohens_d_one_sample_t_test(
            cohens_d, sample_size, confidence_level
        )
        (
            ci_lower_hedges_g_central,
            ci_upper_hedges_g_central,
            standrat_error_hedges_g,
        ) = calculate_central_ci_from_cohens_d_one_sample_t_test(
            hedges_g, sample_size, confidence_level
        )
        ci_lower_cohens_d_pivotal, ci_upper_cohens_d_pivotal = pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_g_pivotal, ci_upper_hedges_g_pivotal = pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_cohens_d_ncp, ci_upper_cohens_d_ncp = ci_ncp_one_sample(
            cohens_d, sample_size, confidence_level
        )
        ci_lower_hedges_g_ncp, ci_upper_hedges_g_ncp = ci_ncp_one_sample(
            hedges_g, sample_size, confidence_level
        )

        # Set results
        results.cles_d = np.around(cles_d, 4)
        results.cles_g = np.around(cles_g, 4)
        results.t_score = np.around(t_score, 4)
        results.df = np.around(df, 4)
        results.p_value = np.around(p_value, 4)

        results.lower_central_ci_cld = np.around(
            norm.cdf(ci_lower_cohens_d_central) * 100, 4
        )
        results.upper_central_ci_cld = np.around(
            norm.cdf(ci_upper_cohens_d_central) * 100, 4
        )
        results.lower_central_ci_clg = np.around(
            norm.cdf(ci_lower_hedges_g_central) * 100, 4
        )
        results.upper_central_ci_clg = np.around(
            norm.cdf(ci_upper_hedges_g_central) * 100, 4
        )

        results.lower_ncp_ci_cld = np.around(norm.cdf(ci_lower_cohens_d_ncp) * 100, 4)
        results.upper_ncp_ci_cld = np.around(norm.cdf(ci_upper_cohens_d_ncp) * 100, 4)
        results.lower_ncp_ci_clg = np.around(norm.cdf(ci_lower_hedges_g_ncp) * 100, 4)
        results.upper_ncp_ci_clg = np.around(norm.cdf(ci_upper_hedges_g_ncp) * 100, 4)

        results.lower_pivotal_ci_cld = np.around(
            norm.cdf(ci_lower_cohens_d_pivotal) * 100, 4
        )
        results.upper_pivotal_ci_cld = np.around(
            norm.cdf(ci_upper_cohens_d_pivotal) * 100, 4
        )
        results.lower_pivotal_ci_clg = np.around(
            norm.cdf(ci_lower_hedges_g_pivotal * correction) * 100, 4
        )
        results.upper_pivotal_ci_clg = np.around(
            norm.cdf(ci_upper_hedges_g_pivotal * correction) * 100, 4
        )
        formatted_p_value = (
            "{:.3f}".format(p_value).lstrip("0")
            if p_value >= 0.001
            else "\033[3mp\033[0m < .001"
        )
        results.statistical_line_cld = "\033[3mt\033[0m({}) = {:.3f}, {} {}, CLd = {:.3f}, {}% CI(pivotal) [{:.3f}, {:.3f}]".format(
            int(df),
            t_score,
            "\033[3mp = \033[0m" if p_value >= 0.001 else "",
            formatted_p_value,
            cles_d,
            confidence_level_percentages,
            np.around(norm.cdf(ci_lower_cohens_d_pivotal) * 100, 3),
            np.around(norm.cdf(ci_upper_cohens_d_pivotal) * 100, 3),
        )
        results.statistical_line_clg = "\033[3mt\033[0m({}) = {:.3f}, {} {}, CLg = {:.3f}, {}% CI(pivotal) [{:.3f}, {:.3f}]".format(
            int(df),
            t_score,
            "\033[3mp = \033[0m" if p_value >= 0.001 else "",
            formatted_p_value,
            cles_g,
            confidence_level_percentages,
            np.around(norm.cdf(ci_lower_hedges_g_pivotal * correction) * 100, 3),
            np.around(norm.cdf(ci_upper_hedges_g_pivotal * correction) * 100, 3),
        )

        return results

    @staticmethod
    def one_sample_from_data(params: dict) -> OneSampleCLESResults:
        """
        Calculate the one-sample t-test results from given sample data.

        Parameters
        ----------
        params : dict
            A dictionary containing the following keys:
            - "column 1" (array-like): The sample data.
            - "Population's Mean" (float): The population mean value.
            - "Confidence Level" (float): The confidence level as a percentage (e.g., 95 for 95%).

        Returns
        -------
        dict
            A dictionary containing the calculated results:
            - "Mcgraw & Wong, Common Language Effect Size (CLd)" (float): The Common Language Effect Size (CLd).
            - "Mcgraw & Wong, Unbiased Common Language Effect Size (CLg)" (float): The Unbiased Common Language Effect Size (CLg).
            - "t-score" (float): The t-score value.
            - "degrees of freedom" (float): The degrees of freedom.
            - "p-value" (float): The p-value.
            - "Lower Central CI's CLd" (float): Lower bound of the central confidence interval for CLd.
            - "Upper Central CI's CLd" (float): Upper bound of the central confidence interval for CLd.
            - "Lower Central CI's CLg" (float): Lower bound of the central confidence interval for CLg.
            - "Upper Central CI's CLg" (float): Upper bound of the central confidence interval for CLg.
            - "Lower Non-Central CI's CLd" (float): Lower bound of the non-central confidence interval for CLd.
            - "Upper Non-Central CI's CLd" (float): Upper bound of the non-central confidence interval for CLd.
            - "Lower Non-Central CI's CLg" (float): Lower bound of the non-central confidence interval for CLg.
            - "Upper Non-Central CI's CLg" (float): Upper bound of the non-central confidence interval for CLg.
            - "Lower Pivotal CI's CLd" (float): Lower bound of the pivotal confidence interval for CLd.
            - "Upper Pivotal CI's CLd" (float): Upper bound of the pivotal confidence interval for CLd.
            - "Lower Pivotal CI's CLg" (float): Lower bound of the pivotal confidence interval for CLg.
            - "Upper Pivotal CI's CLg" (float): Upper bound of the pivotal confidence interval for CLg.
            - "Statistical Line CLd" (str): A formatted string with the statistical results for CLd.
            - "Statistical Line CLg" (str): A formatted string with the statistical results for CLg.
        """
        # Set params
        column_1 = params["column 1"]
        population_mean = params[
            "Population's Mean"
        ]  # Default should be 0 if not mentioned
        confidence_level_percentages = params["Confidence Level"]

        # Calculation
        confidence_level = confidence_level_percentages / 100
        sample_mean = np.mean(column_1)
        sample_sd = np.std(column_1, ddof=1)
        sample_size = len(column_1)
        df = sample_size - 1  # Degrees of freedom one sample t-test
        standard_error = sample_sd / np.sqrt(
            df
        )  # This is the standard error of mean's estimate in one sample t-test
        t_score = (
            sample_mean - population_mean
        ) / standard_error  # This is the t score in the test which is used to calculate the p-value
        cohens_d = (
            sample_mean - population_mean
        ) / sample_sd  # This is the effect size for one sample t-test Cohen's d
        correction = math.exp(
            math.lgamma(df / 2)
            - math.log(math.sqrt(df / 2))
            - math.lgamma((df - 1) / 2)
        )
        hedges_g = cohens_d * correction  # This is the actual corrected effect size
        p_value = min(float(t.sf((abs(t_score)), df) * 2), 0.99999)
        (
            ci_lower_cohens_d_central,
            ci_upper_cohens_d_central,
            standrat_error_cohens_d,
        ) = calculate_central_ci_from_cohens_d_one_sample_t_test(
            cohens_d, sample_size, confidence_level
        )
        (
            ci_lower_hedges_g_central,
            ci_upper_hedges_g_central,
            standrat_error_hedges_g,
        ) = calculate_central_ci_from_cohens_d_one_sample_t_test(
            hedges_g, sample_size, confidence_level
        )
        ci_lower_cohens_d_pivotal, ci_upper_cohens_d_pivotal = pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_hedges_g_pivotal, ci_upper_hedges_g_pivotal = pivotal_ci_t(
            t_score, df, sample_size, confidence_level
        )
        ci_lower_cohens_d_ncp, ci_upper_cohens_d_ncp = ci_ncp_one_sample(
            cohens_d, sample_size, confidence_level
        )
        ci_lower_hedges_g_ncp, ci_upper_hedges_g_ncp = ci_ncp_one_sample(
            hedges_g, sample_size, confidence_level
        )
        cles_d = norm.cdf(cohens_d) * 100
        cles_g = norm.cdf(hedges_g) * 100

        # Non Parametric Common Language Effect Sizes
        # Consider Adding Common language effect size to test the probability of a sample value to be larger than the median in the population...(as in matlab mes package)

        # Create results object
        results = OneSampleCLESResults()

        # Set results
        results.cles_d = np.around(cles_d, 4)
        results.cles_g = np.around(cles_g, 4)
        results.t_score = np.around(t_score, 4)
        results.df = np.around(df, 4)
        results.p_value = np.around(p_value, 4)

        results.lower_central_ci_cld = np.around(
            norm.cdf(ci_lower_cohens_d_central) * 100, 4
        )
        results.upper_central_ci_cld = np.around(
            norm.cdf(ci_upper_cohens_d_central) * 100, 4
        )
        results.lower_central_ci_clg = np.around(
            norm.cdf(ci_lower_hedges_g_central) * 100, 4
        )
        results.upper_central_ci_clg = np.around(
            norm.cdf(ci_upper_hedges_g_central) * 100, 4
        )

        results.lower_ncp_ci_cld = np.around(norm.cdf(ci_lower_cohens_d_ncp) * 100, 4)
        results.upper_ncp_ci_cld = np.around(norm.cdf(ci_upper_cohens_d_ncp) * 100, 4)
        results.lower_ncp_ci_clg = np.around(norm.cdf(ci_lower_hedges_g_ncp) * 100, 4)
        results.upper_ncp_ci_clg = np.around(norm.cdf(ci_upper_hedges_g_ncp) * 100, 4)

        results.lower_pivotal_ci_cld = np.around(
            norm.cdf(ci_lower_cohens_d_pivotal) * 100, 4
        )
        results.upper_pivotal_ci_cld = np.around(
            norm.cdf(ci_upper_cohens_d_pivotal) * 100, 4
        )
        results.lower_pivotal_ci_clg = np.around(
            norm.cdf(ci_lower_hedges_g_pivotal * correction) * 100, 4
        )
        results.upper_pivotal_ci_clg = np.around(
            norm.cdf(ci_upper_hedges_g_pivotal * correction) * 100, 4
        )

        return results

    @staticmethod
    def robust_one_sample(params: dict) -> OneSampleCLESResults:
        """
        Calculate the robust one-sample t-test results.

        Parameters
        ----------
        params : dict
            A dictionary containing the following keys:
            - "column 1" (array-like): The sample data.
            - "Trimming Level" (float): The trimming level.
            - "Population Mean" (float): The population mean value.
            - "Number of Bootstrap Samples" (int): The number of bootstrap samples.
            - "Confidence Level" (float): The confidence level as a percentage (e.g., 95 for 95%).
        Returns
        -------
        OneSampleCLESResults
            An object containing all calculated statistics and results:
            - robust_effect_size_akp (float): The robust effect size (AKP)
            - lower_ci_robust_akp (float): Lower bound of the confidence interval for the robust effect size (AKP)
            - upper_ci_robust_akp (float): Upper bound of the confidence interval for the robust effect size (AKP)
            - trimmed_mean (float): The trimmed mean of the sample
            - winsorized_sd (float): The Winsorized standard deviation of the sample
            - yuens_t (float): The Yuen's T statistic
            - robust_df (float): The degrees of freedom
            - robust_p_value (float): The p-value
            - mean_difference (float): The difference between means
            - standard_error (float): The standard error
        """
        # Set Parameters
        column_1 = params["column 1"]
        trimming_level = params["Trimming Level"]  # The default should be 0.2
        population_mean = params["Population Mean"]  # The default should be 0.2
        reps = params["Number of Bootstrap Samples"]
        confidence_level_percentages = params["Confidence Level"]

        # Calculation
        confidence_level = confidence_level_percentages / 100
        sample_size = len(column_1)
        difference = np.array(column_1) - population_mean
        correction = np.sqrt(
            area_under_function(
                density, norm.ppf(trimming_level), norm.ppf(1 - trimming_level)
            )
            + 2 * (norm.ppf(trimming_level) ** 2) * trimming_level
        )
        trimmed_mean_1 = trim_mean(column_1, trimming_level)
        winsorized_standard_deviation_1 = np.sqrt(WinsorizedVariance(column_1))

        # Algina, Penfield, Kesselman robust effect size (AKP)
        standardizer = np.sqrt(WinsorizedVariance(difference, trimming_level))
        trimmed_mean = trim_mean(difference, trimming_level)
        akp_effect_size = correction * (trimmed_mean - population_mean) / standardizer

        # Confidence Intervals for AKP effect size using Bootstrapping
        bootstrap_difference = []
        for _ in range(reps):
            # Generate bootstrap samples
            difference_bootstrap = np.random.choice(
                difference, len(difference), replace=True
            )
            bootstrap_difference.append(difference_bootstrap)

        trimmed_means_of_bootstrap = trim_mean(
            bootstrap_difference, trimming_level, axis=1
        )
        standardizers_of_bootstrap = np.sqrt(
            [
                WinsorizedVariance(array, trimming_level)
                for array in bootstrap_difference
            ]
        )
        akp_effect_size_bootstrap = (
            correction
            * (trimmed_means_of_bootstrap - population_mean)
            / standardizers_of_bootstrap
        )
        lower_ci_akp_boot = np.percentile(
            akp_effect_size_bootstrap,
            ((1 - confidence_level) - ((1 - confidence_level) / 2)) * 100,
        )
        upper_ci_akp_boot = np.percentile(
            akp_effect_size_bootstrap,
            ((confidence_level) + ((1 - confidence_level) / 2)) * 100,
        )

        # Yuen Test Statistics
        non_winsorized_sample_size = len(column_1) - 2 * np.floor(
            trimming_level * len(column_1)
        )
        df = non_winsorized_sample_size - 1
        yuen_standard_error = winsorized_standard_deviation_1 / (
            (1 - 2 * trimming_level) * np.sqrt(len(column_1))
        )
        difference_trimmed_means = trimmed_mean_1 - population_mean
        yuen_statistic = difference_trimmed_means / yuen_standard_error
        yuen_p_value = 2 * (1 - t.cdf(np.abs(yuen_statistic), df))

        # Set results
        results = OneSampleCLESResults()

        results.robust_effect_size_akp = round(akp_effect_size, 4)
        results.lower_ci_robust_akp = round(lower_ci_akp_boot, 4)
        results.upper_ci_robust_akp = round(upper_ci_akp_boot, 4)

        # Descriptive Statistics
        results.trimmed_mean = round(trimmed_mean_1, 4)
        results.winsorized_sd = round(winsorized_standard_deviation_1, 4)

        # Inferential Statistics
        results.yuens_t = round(yuen_statistic, 4)
        results.robust_df = round(df, 4)
        results.robust_p_value = np.around(yuen_p_value, 4)
        results.mean_difference = round(difference_trimmed_means, 4)
        results.standard_error = round(yuen_standard_error, 4)

        return results

    # Things to consider
    # 1. Consider adding a robust one-sample measures here
    # 2. Consider adding the z value transformed option
    # 3. Consider adding the mes matlab package for one sample CLES
