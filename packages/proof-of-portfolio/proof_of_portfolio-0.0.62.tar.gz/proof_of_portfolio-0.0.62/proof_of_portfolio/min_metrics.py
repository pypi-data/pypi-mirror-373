import math
import numpy as np
from scipy.stats import ttest_1samp
from typing import Union


class MinMetrics:
    """
    Minimal metrics implementation that matches the proprietary trading network
    validator metrics calculations exactly. Used for comparing ZK circuit outputs
    against Python calculations on the same input data.
    """

    # Constants from ValiConfig
    WEIGHTED_AVERAGE_DECAY_RATE = 0.075
    WEIGHTED_AVERAGE_DECAY_MIN = 0.15
    WEIGHTED_AVERAGE_DECAY_MAX = 1.0
    ANNUAL_RISK_FREE_PERCENTAGE = 4.19
    ANNUAL_RISK_FREE_DECIMAL = ANNUAL_RISK_FREE_PERCENTAGE / 100
    DAYS_IN_YEAR_CRYPTO = 365
    DAYS_IN_YEAR_FOREX = 252

    # Metric-specific constants
    SHARPE_STDDEV_MINIMUM = 0.01
    STATISTICAL_CONFIDENCE_MINIMUM_N = 60
    SHARPE_NOCONFIDENCE_VALUE = -100
    OMEGA_LOSS_MINIMUM = 0.01
    OMEGA_NOCONFIDENCE_VALUE = 0.0
    SORTINO_DOWNSIDE_MINIMUM = 0.01
    SORTINO_NOCONFIDENCE_VALUE = -100
    CALMAR_RATIO_CAP = 10
    CALMAR_NOCONFIDENCE_VALUE = -100
    STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE = -100

    @staticmethod
    def log_risk_free_rate(days_in_year: int) -> float:
        if days_in_year is None or days_in_year <= 0:
            return np.inf
        return math.log(1 + MinMetrics.ANNUAL_RISK_FREE_DECIMAL) / days_in_year

    @staticmethod
    def weighting_distribution(
        log_returns: Union[list[float], np.ndarray],
    ) -> np.ndarray:
        """
        Returns the weighting distribution that decays from max_weight to min_weight
        using the configured decay rate
        """
        max_weight = MinMetrics.WEIGHTED_AVERAGE_DECAY_MAX
        min_weight = MinMetrics.WEIGHTED_AVERAGE_DECAY_MIN
        decay_rate = MinMetrics.WEIGHTED_AVERAGE_DECAY_RATE

        if len(log_returns) < 1:
            return np.ones(0)

        weighting_distribution_days = np.arange(0, len(log_returns))

        # Calculate decay from max to min
        weight_range = max_weight - min_weight
        decay_values = min_weight + (
            weight_range * np.exp(-decay_rate * weighting_distribution_days)
        )

        return decay_values[::-1][-len(log_returns) :]

    @staticmethod
    def average(
        log_returns: Union[list[float], np.ndarray],
        weighting=False,
        indices: Union[list[int], None] = None,
    ) -> float:
        """
        Returns the mean of the log returns
        """
        if len(log_returns) == 0:
            return 0.0

        weighting_distribution = MinMetrics.weighting_distribution(log_returns)

        if indices is not None and len(indices) != 0:
            indices = [i for i in indices if i in range(len(log_returns))]
            log_returns = [log_returns[i] for i in indices]
            weighting_distribution = [weighting_distribution[i] for i in indices]

        if weighting:
            avg_value = np.average(log_returns, weights=weighting_distribution)
        else:
            avg_value = np.mean(log_returns)

        return float(avg_value)

    @staticmethod
    def variance(
        log_returns: list[float],
        ddof: int = 1,
        weighting=False,
        indices: Union[list[int], None] = None,
    ) -> float:
        """
        Returns the variance of the log returns
        """
        if len(log_returns) == 0:
            return 0.0

        window = len(indices) if indices is not None else len(log_returns)
        if window < ddof + 1:
            return np.inf

        return MinMetrics.average(
            (
                np.array(log_returns)
                - MinMetrics.average(log_returns, weighting=weighting, indices=indices)
            )
            ** 2,
            weighting=weighting,
            indices=indices,
        )

    @staticmethod
    def ann_excess_return(
        log_returns: list[float],
        weighting=False,
        days_in_year: int = DAYS_IN_YEAR_CRYPTO,
    ) -> float:
        """
        Calculates annualized excess return using mean daily log returns and mean daily 1yr risk free rate.
        """
        annual_risk_free_rate = MinMetrics.ANNUAL_RISK_FREE_DECIMAL

        if len(log_returns) == 0:
            return 0.0

        # Annualize the mean daily excess returns
        annualized_excess_return = (
            MinMetrics.average(log_returns, weighting=weighting) * days_in_year
        ) - annual_risk_free_rate
        return annualized_excess_return

    @staticmethod
    def ann_volatility(
        log_returns: list[float],
        ddof: int = 1,
        weighting=False,
        indices: list[int] = None,
        days_in_year: int = DAYS_IN_YEAR_CRYPTO,
    ) -> float:
        """
        Calculates annualized volatility ASSUMING DAILY OBSERVATIONS
        """
        if indices is None:
            indices = list(range(len(log_returns)))

        # Annualize volatility of the daily log returns assuming sample variance
        window = len(indices)
        if window < ddof + 1:
            return np.inf

        annualized_volatility = np.sqrt(
            MinMetrics.variance(
                log_returns, ddof=ddof, weighting=weighting, indices=indices
            )
            * days_in_year
        )

        return float(annualized_volatility)

    @staticmethod
    def ann_downside_volatility(
        log_returns: list[float],
        target: int = None,
        weighting=False,
        days_in_year: int = DAYS_IN_YEAR_CRYPTO,
    ) -> float:
        """
        Calculates annualized downside volatility
        """
        if target is None:
            target = MinMetrics.log_risk_free_rate(days_in_year=days_in_year)

        indices = [i for i, log_return in enumerate(log_returns) if log_return < target]
        return MinMetrics.ann_volatility(
            log_returns, weighting=weighting, indices=indices, days_in_year=days_in_year
        )

    @staticmethod
    def daily_max_drawdown(log_returns: list[float]) -> float:
        """
        Calculates the daily maximum drawdown
        """
        if len(log_returns) == 0:
            return 0.0

        # More efficient implementation using cumulative sum of log returns
        cumulative_log_returns = np.cumsum(log_returns)

        # Maximum cumulative log return at each point
        running_max_log = np.maximum.accumulate(cumulative_log_returns)

        # Drawdown = 1 - exp(current - peak)
        # This gives us the percentage decline from the peak
        drawdowns = 1 - np.exp(cumulative_log_returns - running_max_log)

        # Find the maximum drawdown
        max_drawdown = np.max(drawdowns)

        return max_drawdown

    @staticmethod
    def sharpe(
        log_returns: list[float],
        bypass_confidence: bool = False,
        weighting: bool = False,
        days_in_year: int = DAYS_IN_YEAR_CRYPTO,
        **kwargs,
    ) -> float:
        """
        Calculates the Sharpe ratio
        """
        # Need a large enough sample size
        if len(log_returns) < MinMetrics.STATISTICAL_CONFIDENCE_MINIMUM_N:
            if not bypass_confidence:
                return MinMetrics.SHARPE_NOCONFIDENCE_VALUE

        # Hyperparameter
        min_std_dev = MinMetrics.SHARPE_STDDEV_MINIMUM

        excess_return = MinMetrics.ann_excess_return(
            log_returns, weighting=weighting, days_in_year=days_in_year
        )
        volatility = MinMetrics.ann_volatility(
            log_returns, weighting=weighting, days_in_year=days_in_year
        )

        return float(excess_return / max(volatility, min_std_dev))

    @staticmethod
    def omega(
        log_returns: list[float],
        bypass_confidence: bool = False,
        weighting: bool = False,
        **kwargs,
    ) -> float:
        """
        Calculates the Omega ratio
        """
        # Need a large enough sample size
        if len(log_returns) < MinMetrics.STATISTICAL_CONFIDENCE_MINIMUM_N:
            if not bypass_confidence:
                return MinMetrics.OMEGA_NOCONFIDENCE_VALUE

        if weighting:
            weighing_array = MinMetrics.weighting_distribution(log_returns)

            positive_indices = []
            negative_indices = []
            product_sum_positive = product_sum_negative = 0
            sum_of_weights_positive = sum_of_weights_negative = (
                MinMetrics.OMEGA_LOSS_MINIMUM
            )

            for c, log_return in enumerate(log_returns):
                if log_return > 0:
                    positive_indices.append(c)
                else:
                    negative_indices.append(c)

            log_return_arr = np.array(log_returns)

            if len(positive_indices) > 0:
                positive_indices_arr = np.array(positive_indices)
                sum_of_weights_positive = max(
                    np.sum(weighing_array[positive_indices_arr]),
                    MinMetrics.OMEGA_LOSS_MINIMUM,
                )

                product_sum_positive = np.sum(
                    np.multiply(
                        log_return_arr[positive_indices_arr],
                        weighing_array[positive_indices_arr],
                    )
                )

            if len(negative_indices) > 0:
                negative_indices_arr = np.array(negative_indices)
                sum_of_weights_negative = max(
                    np.sum(weighing_array[negative_indices_arr]),
                    MinMetrics.OMEGA_LOSS_MINIMUM,
                )
                product_sum_negative = np.sum(
                    np.multiply(
                        log_return_arr[negative_indices_arr],
                        weighing_array[negative_indices_arr],
                    )
                )

            positive_sum = product_sum_positive * sum_of_weights_negative
            negative_sum = product_sum_negative * sum_of_weights_positive

        else:
            positive_sum = 0
            negative_sum = 0

            for log_return in log_returns:
                if log_return > 0:
                    positive_sum += log_return
                else:
                    negative_sum += log_return

        numerator = positive_sum
        denominator = max(abs(negative_sum), MinMetrics.OMEGA_LOSS_MINIMUM)

        return float(numerator / denominator)

    @staticmethod
    def statistical_confidence(
        log_returns: list[float], bypass_confidence: bool = False, **kwargs
    ) -> float:
        """
        Calculates statistical confidence using t-test
        """
        # Impose a minimum sample size on the miner
        if len(log_returns) < MinMetrics.STATISTICAL_CONFIDENCE_MINIMUM_N:
            if not bypass_confidence or len(log_returns) < 2:
                return MinMetrics.STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE

        # Also now check for zero variance condition
        zero_variance_condition = bool(np.isclose(np.var(log_returns), 0))
        if zero_variance_condition:
            return MinMetrics.STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE

        res = ttest_1samp(log_returns, 0, alternative="greater")
        return float(res.statistic)

    @staticmethod
    def sortino(
        log_returns: list[float],
        bypass_confidence: bool = False,
        weighting: bool = False,
        days_in_year: int = DAYS_IN_YEAR_CRYPTO,
        **kwargs,
    ) -> float:
        """
        Calculates the Sortino ratio
        """
        # Need a large enough sample size
        if len(log_returns) < MinMetrics.STATISTICAL_CONFIDENCE_MINIMUM_N:
            if not bypass_confidence:
                return MinMetrics.SORTINO_NOCONFIDENCE_VALUE

        # Hyperparameter
        min_downside = MinMetrics.SORTINO_DOWNSIDE_MINIMUM

        # Sortino ratio is calculated as the mean of the returns divided by the standard deviation of the negative returns
        excess_return = MinMetrics.ann_excess_return(
            log_returns, weighting=weighting, days_in_year=days_in_year
        )
        downside_volatility = MinMetrics.ann_downside_volatility(
            log_returns, weighting=weighting, days_in_year=days_in_year
        )

        return float(excess_return / max(downside_volatility, min_downside))

    @staticmethod
    def calmar(
        log_returns: list[float],
        bypass_confidence: bool = False,
        weighting: bool = False,
        days_in_year: int = DAYS_IN_YEAR_CRYPTO,
        **kwargs,
    ) -> float:
        if len(log_returns) < MinMetrics.STATISTICAL_CONFIDENCE_MINIMUM_N:
            if not bypass_confidence:
                return MinMetrics.CALMAR_NOCONFIDENCE_VALUE

        base_return_percentage = (
            MinMetrics.average(log_returns, weighting=weighting) * days_in_year * 100
        )
        max_drawdown = MinMetrics.daily_max_drawdown(log_returns)

        if max_drawdown <= 0 or max_drawdown > 1:
            drawdown_normalization_factor = 0
        else:
            drawdown_percentage = max((1 - max_drawdown) * 100, 0.01)
            if drawdown_percentage >= 10:
                drawdown_normalization_factor = 0
            else:
                drawdown_normalization_factor = 1.0 / drawdown_percentage

        raw_calmar = float(base_return_percentage * drawdown_normalization_factor)
        return min(raw_calmar, MinMetrics.CALMAR_RATIO_CAP)
