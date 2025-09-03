use crate::utils::{
    ann_excess_return::ann_excess_return,
    constants::{ARRAY_SIZE, SCALE, STATISTICAL_CONFIDENCE_MINIMUM_N},
};
use super::drawdown::daily_max_drawdown;

pub fn calmar(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    RISK_FREE_RATE: i64,
    use_weighting: bool,
) -> i64 {
    if actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        -100
    } else {
        let ann_excess_return =
            ann_excess_return(log_returns, actual_len, RISK_FREE_RATE, use_weighting);
        let max_drawdown = daily_max_drawdown(log_returns, actual_len);

        if max_drawdown == 0 {
            SCALE
        } else {
            (ann_excess_return * SCALE) / max_drawdown
        }
    }
}

#[test]
fn test_calmar_normal_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 2000;
    returns[3] = -1000;
    returns[4] = 500;
    for i in 5..40 {
        returns[i] = if i % 2 == 0 { 200 } else { -150 };
    }

    let result = calmar(returns, 40, 100, false);
    assert(result != 0);
}

#[test]
fn test_calmar_insufficient_data() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;

    let result = calmar(returns, 2, 100, false);
    assert(result == 0);
}

#[test]
fn test_calmar_exactly_30_days() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..30 {
        returns[i] = 100;
    }

    let result = calmar(returns, 30, 50, false);
    assert(result != 0);
}

#[test]
fn test_calmar_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..50 {
        returns[i] = -100;
    }

    let result = calmar(returns, 50, 0, false);
    assert(result != 0);
}
