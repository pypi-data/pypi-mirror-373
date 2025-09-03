global ARRAY_SIZE: u32 = 120;
global SORTINO_NOCONFIDENCE_VALUE: i64 = -100;
global SORTINO_DOWNSIDE_MINIMUM: i64 = 100000;
global STATISTICAL_CONFIDENCE_MINIMUM_N: u32 = 60;
global DAYS_IN_YEAR: u64 = 365;
global DAILY_LOG_RISK_FREE_RATE: i64 = 1124;

global SCALE: i64 = 10_000_000;

unconstrained fn compute_sqrt(n: u64) -> u64 {
    if n <= 1 {
        n
    } else if n <= 3 {
        1
    } else if n <= 8 {
        2
    } else if n <= 15 {
        3
    } else {
        let mut x = if n < 100 {
            n / 3
        } else if n < 10000 {
            n / 10
        } else {
            n / 100
        };

        if x == 0 {
            x = 1;
        }

        let mut prev = 0;
        for _ in 0..100 {
            if x != prev {
                if x > 0 {
                    prev = x;
                    x = (x + n / x) / 2;
                }
            }
        }

        x
    }
}

pub fn sqrt(n: u64) -> u64 {
    let sqrt_result = unsafe { compute_sqrt(n) };
    assert(sqrt_result * sqrt_result <= n);
    assert((sqrt_result + 1) * (sqrt_result + 1) > n);
    sqrt_result
}

fn exp_decay_scaled(neg_x_scaled: i64) -> i64 {
    let scale: i64 = 100000;
    let x_pow_2 = neg_x_scaled * neg_x_scaled;
    let x_pow_3 = x_pow_2 * neg_x_scaled;

    let term1 = neg_x_scaled;
    let term2 = x_pow_2 / (2 * scale);
    let term3 = x_pow_3 / (6 * scale * scale);
    let term4 = (x_pow_3 * neg_x_scaled) / (24 * scale * scale * scale);

    scale + term1 + term2 + term3 + term4
}

pub fn weighting_distribution(actual_len: u32) -> [i64; ARRAY_SIZE] {
    let mut weights = [0; ARRAY_SIZE];
    let max_weight: i64 = 100000;
    let min_weight: i64 = 40000;
    let decay_rate: i64 = 8000;
    let weight_range = max_weight - min_weight;
    let scale: i64 = 100000;

    for i in 0..ARRAY_SIZE {
        if (i as u32) < actual_len {
            let neg_x_scaled = -decay_rate * (i as i64);
            let exp_val_scaled = exp_decay_scaled(neg_x_scaled);

            let weighted_val = (weight_range * exp_val_scaled) / scale;
            weights[actual_len - 1 - i] = min_weight + weighted_val;
        }
    }

    weights
}

pub fn average(log_returns: [i64; ARRAY_SIZE], actual_len: u32, use_weighting: bool) -> i64 {
    let mut result = 0;
    if actual_len > 0 {
        if use_weighting {
            let weights = weighting_distribution(actual_len);
            let mut weighted_sum: i64 = 0;
            let mut sum_of_weights: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    weighted_sum += log_returns[i] * weights[i];
                    sum_of_weights += weights[i];
                }
            }
            if sum_of_weights != 0 {
                result = weighted_sum / sum_of_weights;
            }
        } else {
            let mut sum: i64 = 0;
            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    sum += log_returns[i];
                }
            }
            result = sum / (actual_len as i64);
        }
    }
    result
}

pub fn annualized_excess_return(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    risk_free_rate: i64,
    use_weighting: bool,
) -> i64 {
    let result = if actual_len == 0 {
        0
    } else {
        let avg_daily_return = average(log_returns, actual_len, use_weighting);
        let annualized_return = avg_daily_return * 365;
        annualized_return - risk_free_rate
    };
    result
}

pub fn annualized_downside_volatility(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    use_weighting: bool,
) -> i64 {
    let mut downside_variance_sum: u64 = 0;
    let mut negative_count: u32 = 0;

    if use_weighting {
        let weights = weighting_distribution(actual_len);
        let mut weighted_sum: i64 = 0;
        let mut sum_of_weights: i64 = 0;

        for i in 0..ARRAY_SIZE {
            if (i as u32) < actual_len {
                if log_returns[i] < DAILY_LOG_RISK_FREE_RATE {
                    weighted_sum += log_returns[i] * weights[i];
                    sum_of_weights += weights[i];
                }
            }
        }

        if sum_of_weights > 0 {
            let weighted_mean = weighted_sum / sum_of_weights;
            let mut weighted_sum_sq_diff: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    if log_returns[i] < DAILY_LOG_RISK_FREE_RATE {
                        let diff = log_returns[i] - weighted_mean;
                        let sq_diff = (diff / 1000) * (diff / 1000);
                        weighted_sum_sq_diff += sq_diff * weights[i];
                    }
                }
            }

            let downside_variance = weighted_sum_sq_diff / sum_of_weights;
            let annualized_variance = downside_variance * (DAYS_IN_YEAR as i64);
            sqrt(annualized_variance as u64) as i64 * 1000
        } else {
            SCALE
        }
    } else {
        let mut downside_returns_sum: i64 = 0;

        for i in 0..ARRAY_SIZE {
            if (i as u32) < actual_len {
                if log_returns[i] < DAILY_LOG_RISK_FREE_RATE {
                    downside_returns_sum += log_returns[i];
                    negative_count = negative_count + 1;
                }
            }
        }

        if negative_count > 1 {
            let downside_mean = downside_returns_sum / (negative_count as i64);

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    if log_returns[i] < DAILY_LOG_RISK_FREE_RATE {
                        let diff = log_returns[i] - downside_mean;
                        downside_variance_sum += ((diff * diff) as u64);
                    }
                }
            }

            let downside_variance = downside_variance_sum / ((negative_count - 1) as u64);
            let downside_volatility = sqrt(downside_variance * DAYS_IN_YEAR) as i64;
            downside_volatility
        } else {
            SCALE
        }
    }
}

pub fn sortino(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    risk_free_rate: i64,
    use_weighting: bool,
) -> i64 {
    if actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        SORTINO_NOCONFIDENCE_VALUE
    } else {
        let excess_return =
            annualized_excess_return(log_returns, actual_len, risk_free_rate, use_weighting);
        let downside_volatility =
            annualized_downside_volatility(log_returns, actual_len, use_weighting);

        let effective_downside_volatility = if downside_volatility < SORTINO_DOWNSIDE_MINIMUM {
            SORTINO_DOWNSIDE_MINIMUM
        } else {
            downside_volatility
        };

        (excess_return * SCALE) / effective_downside_volatility
    }
}

pub fn main(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    risk_free_rate: i64,
    use_weighting: bool,
    bypass_confidence: bool,
) -> pub i64 {
    let result = if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        SORTINO_NOCONFIDENCE_VALUE
    } else {
        sortino(log_returns, actual_len, risk_free_rate, use_weighting)
    };
    result
}
