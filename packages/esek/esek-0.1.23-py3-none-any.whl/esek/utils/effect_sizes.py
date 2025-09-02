from .results import EffectSize


class CohenD(EffectSize):
    """
    A class to store Cohen's d effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Cohen's d"
        self.update_statistical_line()


class HedgesG(EffectSize):
    """
    A class to store Hedges' g effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Hedges' g"
        self.update_statistical_line()


class CohensDav(EffectSize):
    """
    A class to store Cohen's dav effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Cohen's dav"
        self.update_statistical_line()


class HedgesGav(EffectSize):
    """
    A class to store Hedge's gav effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Hedge's gav"
        self.update_statistical_line()


class CohensDrm(EffectSize):
    """
    A class to store Cohen's drm effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Cohen's drm"
        self.update_statistical_line()


class HedgesGrm(EffectSize):
    """
    A class to store Hedge's grm effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Hedge's grm"
        self.update_statistical_line()


class CohensDPop(EffectSize):
    """
    A class to store Cohen's d pop effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Cohen's d pop"
        self.update_statistical_line()


class Biserial(EffectSize):
    """
    A class to store Biserial effect size values.
    """

    def __init__(
        self,
        value: float,
        ci_lower: float,
        ci_upper: float,
        standard_error: float,
        name: str,
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = name
        self.z_score: float | None = None
        self.p_value: float | None = None
        self.update_statistical_line()


class RatioOfMeans(EffectSize):
    """
    A class to store Ratio of Means effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Ratio of Means"
        self.update_statistical_line()


class RobustAKP(EffectSize):
    """
    A class to store Robust AKP effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Robust AKP"
        self.update_statistical_line()


class RobustExplanatory(EffectSize):
    """
    A class to store Robust Explanatory effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Robust Explanatory"
        self.update_statistical_line()


class CLES(EffectSize):
    """
    A class to store Common Language Effect Size (CLES) values.
    """

    def __init__(
        self,
        value: float,
        ci_lower: float,
        ci_upper: float,
        standard_error: float,
        method: str,
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = (
            "Common Language Effect Size (CLES)" + f" ({method})"
        )
        self.update_statistical_line()


class ProbabilityOfSuperiority(EffectSize):
    """
    A class to store Probability of Superiority (PS) values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Probability of Superiority (PS)"
        self.update_statistical_line()


class VarghaDelaney(EffectSize):
    """
    A class to store Vargha-Delaney effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Vargha-Delaney"
        self.update_statistical_line()


class CliffsDelta(EffectSize):
    """
    A class to store Cliff's Delta effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Cliff's Delta"
        self.update_statistical_line()


class NonParametricU1(EffectSize):
    """
    A class to store Non-Parametric U1 effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Non-Parametric U1"
        self.update_statistical_line()


class NonParametricU3(EffectSize):
    """
    A class to store Non-Parametric U3 effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Non-Parametric U3"
        self.update_statistical_line()


class KraemerAndrewGamma(EffectSize):
    """
    A class to store Kraemer-Andrew Gamma effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Kraemer-Andrew Gamma"
        self.update_statistical_line()


class WilcoxMusakaQ(EffectSize):
    """
    A class to store Wilcox-Musaka Q effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Wilcox-Musaka Q"
        self.update_statistical_line()


class GlassDelta(EffectSize):
    """
    A class to store Glass's Delta effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Glass's Delta"
        self.update_statistical_line()


class GlassDeltaUnbiased(EffectSize):
    """
    A class to store Glass's Delta Unbiased effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Glass's Delta Unbiased"
        self.update_statistical_line()


class AokiEpsilon(EffectSize):
    """
    A class to store Aoki's Epsilon effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Aoki's Epsilon"
        self.update_statistical_line()


class AokiEpsilonUnbiased(EffectSize):
    """
    A class to store Aoki's Epsilon Unbiased effect size values.
    """

    def __init__(
        self, value: float, ci_lower: float, ci_upper: float, standard_error: float
    ) -> None:
        super().__init__(value, ci_lower, ci_upper, standard_error)
        self.effect_size_name: str = "Aoki's Epsilon Unbiased"
        self.update_statistical_line()
