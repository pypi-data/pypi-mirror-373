class ConfidenceInterval:
    """
    A class to store confidence interval values.
    """

    def __init__(self, lower: float, upper: float) -> None:
        self.lower: float = float(lower)
        self.upper: float = float(upper)
        self.ci: tuple[float, float] = (self.lower, self.upper)


class ApproximatedStandardError:
    """
    A class to store approximated standard error values.
    """

    def __init__(
        self,
        true_se: float,
        morris: float,
        hedges: float,
        hedges_olkin: float,
        mle: float,
        large_n: float,
        hunter_and_schmidt: float,
    ) -> None:
        self.true_se: float = true_se
        self.morris: float = morris
        self.hedges: float = hedges
        self.hedges_olkin: float = hedges_olkin
        self.mle: float = mle
        self.large_n: float = large_n
        self.hunter_and_schmidt: float = hunter_and_schmidt


class EffectSize:
    """
    A class to store effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        self.effect_size_name: str = "Effect Size"
        self.value: float = value
        self.ci: ConfidenceInterval = ConfidenceInterval(ci_lower, ci_upper)
        self.standard_error: float = standard_error
        self.statistical_line: str = ""

        self.standardizer: float | None = None
        self.non_central_ci: ConfidenceInterval | None = None
        self.pivotal_ci: ConfidenceInterval | None = None
        self.approximated_standard_error: ApproximatedStandardError | None = None
        self.mag: ConfidenceInterval | None = None
        self.lambda_prime: ConfidenceInterval | None = None
        self.morris: ConfidenceInterval | None = None
        self.t_prime: ConfidenceInterval | None = None

    def update_statistical_line(self) -> None:
        """
        Update the statistical line with the current values.
        """
        self.statistical_line = (
            f"{self.effect_size_name}: {self.value} (CI: {self.ci.lower}, {self.ci.upper}) "
            f"SE: {self.standard_error}"
        )

        if self.non_central_ci is not None:
            self.statistical_line += f" Non-Central CI: {self.non_central_ci.lower}, {self.non_central_ci.upper}"

        if self.pivotal_ci is not None:
            self.statistical_line += (
                f" Pivotal CI: {self.pivotal_ci.lower}, {self.pivotal_ci.upper}"
            )

    def update_non_central_ci(
        self, non_central_ci_lower: float, non_central_ci_upper: float
    ) -> None:
        """
        Update the non-central confidence interval.
        """
        self.non_central_ci = ConfidenceInterval(
            non_central_ci_lower, non_central_ci_upper
        )
        self.update_statistical_line()

    def update_pivotal_ci(
        self, pivotal_ci_lower: float, pivotal_ci_upper: float
    ) -> None:
        """
        Update the pivotal confidence interval.
        """
        self.pivotal_ci = ConfidenceInterval(pivotal_ci_lower, pivotal_ci_upper)
        self.update_statistical_line()

    def update_mag_ci(self, mag_ci_lower: float, mag_ci_upper: float) -> None:
        """
        Update the mag confidence interval.
        """
        self.mag = ConfidenceInterval(mag_ci_lower, mag_ci_upper)
        self.update_statistical_line()

    def update_lambda_prime_ci(
        self, lambda_prime_ci_lower: float, lambda_prime_ci_upper: float
    ) -> None:
        """
        Update the lambda prime confidence interval.
        """
        self.lambda_prime = ConfidenceInterval(
            lambda_prime_ci_lower, lambda_prime_ci_upper
        )
        self.update_statistical_line()

    def update_morris_ci(self, morris_ci_lower: float, morris_ci_upper: float) -> None:
        """
        Update the morris prime confidence interval.
        """
        self.morris = ConfidenceInterval(morris_ci_lower, morris_ci_upper)
        self.update_statistical_line()

    def update_t_prime_ci(
        self, t_prime_ci_lower: float, t_prime_ci_upper: float
    ) -> None:
        """
        Update the t prime prime confidence interval.
        """
        self.t_prime = ConfidenceInterval(t_prime_ci_lower, t_prime_ci_upper)
        self.update_statistical_line()


class InferentialStatistics:
    """
    A class to store inferential statistics.
    """

    def __init__(
        self,
        p_value: float,
        score: float,
    ) -> None:
        self.p_value: float = p_value
        self.score: float = score
        self.standard_error: float | None = None
        self.degrees_of_freedom: float | None = None
        self.means_difference: float | None = None


class DescriptiveStatistics:
    """
    A class to store descriptive statistics.
    """

    def __init__(
        self,
        mean: float,
        standard_deviation: float,
    ) -> None:
        self.mean: float = mean
        self.sd: float = standard_deviation


class Sample(DescriptiveStatistics):
    """
    A class to store descriptive statistics for a sample.
    """

    def __init__(
        self,
        mean: float,
        standard_deviation: float,
        size: int,
    ) -> None:
        super().__init__(mean, standard_deviation)
        self.size: int = size
        self.diff_mean: float | None = None
        self.diff_sd: float | None = None
        self.population_sd_diff: float | None = None


class Group(DescriptiveStatistics):
    """
    A class to store descriptive statistics for a group.
    """

    def __init__(
        self,
        mean: float,
        standard_deviation: float,
        median: float | None = None,
        median_absolute_deviation: float | None = None,
    ) -> None:
        super().__init__(mean, standard_deviation)
        self.median: float | None = median
        self.median_absolute_deviation: float | None = median_absolute_deviation
        self.diff_median: float | None = None
        self.sample_size: int | None = None
        self.u_statistic: float | None = None
        self.w_statistic: float | None = None
        self.mean_rank: float | None = None
        self.population_sd: float | None = None
        self.mean_diff: float | None = None
        self.sd_diff: float | None = None


class WilcoxonSignedRank(DescriptiveStatistics):
    """
    A class to store descriptive statistics from the Wilcoxon Signed-Rank test.
    """

    def __init__(
        self,
        times_group1_larger: float,
        times_group2_larger: float,
        ties: float,
        num_of_pairs: float,
        num_of_non_tied_pairs: float,
    ) -> None:
        self.times_group1_larger: float = times_group1_larger
        self.times_group2_larger: float = times_group2_larger
        self.ties: float = ties
        self.num_of_pairs: float = num_of_pairs
        self.num_of_non_tied_pairs: float = num_of_non_tied_pairs
