use crate::utils::constants::{
    ARRAY_SIZE, OMEGA_NOCONFIDENCE_VALUE, OMEGA_SCALE_FACTOR,
    STATISTICAL_CONFIDENCE_MINIMUM_N,
};
use crate::utils::weighting_distribution::weighting_distribution;

pub fn omega(log_returns: [i64; ARRAY_SIZE], actual_len: u32, use_weighting: bool) -> i64 {
    // Check minimum sample size for statistical confidence
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
                ((descaled_positive_sum * (OMEGA_SCALE_FACTOR as i64)) / abs_weighted_negative_sum) as i64
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

#[test]
fn test_omega_all_positive() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 100;
    }

    let result = omega(returns, 5, false);
    assert(result == 10000000);
}

#[test]
fn test_omega_all_negative() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -100;
    }

    let result = omega(returns, 5, false);
    assert(result == 0);
}

#[test]
fn test_omega_mixed_returns() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -300;

    let result = omega(returns, 4, false);
    assert(result == 22500000);
}

#[test]
fn test_omega_zero_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 0;
    }

    let result = omega(returns, 5, false);
    assert(result == 10000000);
}
