use crate::utils::{constants::{ARRAY_SIZE, SCALE}, sqrt::sqrt, variance::variance};

pub fn ann_volatility(
    daily_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    use_weighting: bool,
) -> i64 {
    let result = if actual_len < 2 {
        SCALE
    } else {
        let daily_variance = variance(daily_returns, actual_len, 1, use_weighting);
        let annualized_variance = daily_variance * 365;
        sqrt(annualized_variance as u64) as i64 * 1000
    };
    result
}
#[test]
fn test_ann_volatility_zero_variance() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 100;
    }

    let result = ann_volatility(returns, 5, false);
    assert(result == 0);
}

#[test]
fn test_ann_volatility_positive_variance() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;
    returns[2] = 300;
    returns[3] = 400;
    returns[4] = 500;

    let result = ann_volatility(returns, 5, false);
    assert(result > 0);
}

#[test]
fn test_ann_volatility_ddof_zero() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;
    returns[2] = 300;

    let result_ddof_0 = ann_volatility(returns, 3, false);
    let result_ddof_1 = ann_volatility(returns, 3, false);
    assert(result_ddof_0 != result_ddof_1);
}

#[test]
fn test_ann_volatility_single_value() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 500;

    let result = ann_volatility(returns, 1, false);
    assert(result == 0);
}
