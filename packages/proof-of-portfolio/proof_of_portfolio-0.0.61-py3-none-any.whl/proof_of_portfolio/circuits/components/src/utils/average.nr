use crate::utils::{constants::ARRAY_SIZE, weighting_distribution::weighting_distribution};


pub fn average(daily_returns: [i64; ARRAY_SIZE], actual_len: u32, use_weighting: bool) -> i64 {
    let mut result = 0;
    if actual_len > 0 {
        if use_weighting {
            let weights = weighting_distribution(actual_len);
            let mut weighted_sum: i64 = 0;
            let mut sum_of_weights: i64 = 0;

            for i in 0..ARRAY_SIZE {
                if (i as u32) < actual_len {
                    weighted_sum += daily_returns[i] * weights[i];
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
                    sum += daily_returns[i];
                }
            }
            result = sum / (actual_len as i64);
        }
    }
    result
}

#[test]
fn test_average_positive_numbers() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;
    returns[2] = 300;

    let result = average(returns, 3, false);
    assert(result == 200);
}

#[test]
fn test_average_negative_numbers() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = -100;
    returns[1] = -200;
    returns[2] = -300;

    let result = average(returns, 3, false);
    assert(result == -200);
}

#[test]
fn test_average_mixed_numbers() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = -200;
    returns[2] = 300;
    returns[3] = -400;

    let result = average(returns, 4, false);
    assert(result == -50);
}

#[test]
fn test_average_single_number() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 500;

    let result = average(returns, 1, false);
    assert(result == 500);
}

#[test]
fn test_average_zeros() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..10 {
        returns[i] = 0;
    }

    let result = average(returns, 10, false);
    assert(result == 0);
}
