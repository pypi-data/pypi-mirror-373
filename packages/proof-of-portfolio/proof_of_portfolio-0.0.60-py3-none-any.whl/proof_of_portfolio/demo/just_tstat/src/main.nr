global ARRAY_SIZE: u32 = 120;
global STATISTICAL_CONFIDENCE_MINIMUM_N: u32 = 60;
global STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE: i64 = -100;
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
    // Safety: this is constrained for floored int div properly. The computation to get to the result doesn't need to be constrained.
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

pub fn variance(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    ddof: u32,
    use_weighting: bool,
) -> i64 {
    let mut variance = 0;
    let mut proceed = false;
    if use_weighting {
        if actual_len >= 2 {
            proceed = true;
        }
    } else {
        if actual_len > ddof {
            proceed = true;
        }
    }

    if proceed {
        let mean = average(log_returns, actual_len, use_weighting);
        if use_weighting {
            let weights = weighting_distribution(actual_len);
            let mut weighted_sum_sq_diff: i64 = 0;
            let mut sum_of_weights: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let diff = log_returns[i] - mean;
                    let sq_diff = diff * diff;
                    weighted_sum_sq_diff += sq_diff * weights[i];
                    sum_of_weights += weights[i];
                }
            }

            if sum_of_weights != 0 {
                variance = weighted_sum_sq_diff / sum_of_weights;
            }
        } else {
            let mut sum_sq_diff: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let diff = log_returns[i] - mean;
                    let sq_diff = diff * diff;
                    sum_sq_diff += sq_diff;
                }
            }
            variance = sum_sq_diff / ((actual_len - ddof) as i64);
        }
    }
    variance
}

fn compute_t_statistic(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    use_weighting: bool,
) -> i64 {
    let avg = average(log_returns, actual_len, use_weighting);
    let var = variance(log_returns, actual_len, 1, use_weighting);

    if var <= 0 {
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE
    } else {
        let std_dev = sqrt(var as u64) as i64;
        let n_sqrt = sqrt(actual_len as u64) as i64;
        let standard_error = std_dev / n_sqrt;

        if standard_error == 0 {
            // Effectively infinite t-statistic, return a large number
            1000000
        } else {
            (avg * SCALE) / standard_error
        }
    }
}

pub fn statistical_confidence(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    use_weighting: bool,
) -> i64 {
    if actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        if actual_len < 2 {
            STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE
        } else {
            compute_t_statistic(log_returns, actual_len, use_weighting)
        }
    } else {
        compute_t_statistic(log_returns, actual_len, use_weighting)
    }
}

pub fn main(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    use_weighting: bool,
    bypass_confidence: bool,
) -> pub i64 {
    let result = if !bypass_confidence & (actual_len < 2) {
        STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE
    } else {
        statistical_confidence(log_returns, actual_len, use_weighting)
    };
    result
}
