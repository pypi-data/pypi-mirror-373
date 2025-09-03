global ARRAY_SIZE: u32 = 120;
global OMEGA_NOCONFIDENCE_VALUE: i64 = -100;
global OMEGA_SCALE_FACTOR: i64 = 10000000;
global STATISTICAL_CONFIDENCE_MINIMUM_N: u32 = 60;

global SCALE: i64 = 10_000_000;

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

pub fn omega(log_returns: [i64; ARRAY_SIZE], actual_len: u32, use_weighting: bool) -> i64 {
    if actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        OMEGA_NOCONFIDENCE_VALUE
    } else {
        if use_weighting {
            let weights = weighting_distribution(actual_len);
            let mut weighted_positive_sum: i64 = 0;
            let mut weighted_negative_sum: i64 = 0;
            let weight_scale: i64 = 100000;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    let weight = weights[i] as i64;
                    let log_return = log_returns[i] as i64;
                    if log_return > 0 {
                        weighted_positive_sum += log_return * weight;
                    } else if log_return < 0 {
                        weighted_negative_sum += log_return * weight;
                    }
                }
            }

            let descaled_positive_sum = weighted_positive_sum / weight_scale;
            let descaled_negative_sum = weighted_negative_sum / weight_scale;
            let abs_weighted_negative_sum = -descaled_negative_sum;
            if abs_weighted_negative_sum > 0 {
                ((descaled_positive_sum * (OMEGA_SCALE_FACTOR as i64)) / abs_weighted_negative_sum)
                     as i64
                } else {
                    OMEGA_SCALE_FACTOR
                }
            } else {
                let mut positive_sum: u64 = 0;
                let mut negative_sum: u64 = 0;

                for i in 0..ARRAY_SIZE {
                    if (i as u32) < actual_len {
                        if log_returns[i] > 0 {
                            positive_sum = positive_sum + (log_returns[i] as u64);
                        } else if log_returns[i] < 0 {
                            negative_sum = negative_sum + ((-log_returns[i]) as u64);
                        }
                    }
                }

                if negative_sum > 0 {
                    ((positive_sum * (OMEGA_SCALE_FACTOR as u64)) / negative_sum) as i64
                } else {
                    OMEGA_SCALE_FACTOR
                }
            }
        }
    }

pub fn main(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    use_weighting: bool,
    bypass_confidence: bool,
) -> pub i64 {
    let result = if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        OMEGA_NOCONFIDENCE_VALUE
    } else {
        omega(log_returns, actual_len, use_weighting)
    };
    result
}
