use crate::utils::{average::average, constants::{ARRAY_SIZE, DAYS_IN_YEAR}};

pub fn ann_excess_return(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    RISK_FREE_RATE: i64,
    use_weighting: bool,
) -> i64 {
    let avg = average(log_returns, actual_len, use_weighting);
    let annualized = avg * DAYS_IN_YEAR;
    annualized - RISK_FREE_RATE
}

#[test]
fn test_ann_excess_return_positive() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;
    returns[2] = 150;

    let result = ann_excess_return(returns, 3, 10000, false);
    assert(result > 0);
}

#[test]
fn test_ann_excess_return_negative() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = -100;
    returns[1] = -200;
    returns[2] = -150;

    let result = ann_excess_return(returns, 3, 10000, false);
    assert(result < 0);
}

#[test]
fn test_ann_excess_return_equal_to_risk_free() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 100;
    returns[2] = 100;

    let result = ann_excess_return(returns, 3, 36500, false);
    assert(result == 0);
}

#[test]
fn test_ann_excess_return_zero_risk_free() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 100;
    returns[1] = 200;

    let result = ann_excess_return(returns, 2, 0, false);
    assert(result == 54750);
}
