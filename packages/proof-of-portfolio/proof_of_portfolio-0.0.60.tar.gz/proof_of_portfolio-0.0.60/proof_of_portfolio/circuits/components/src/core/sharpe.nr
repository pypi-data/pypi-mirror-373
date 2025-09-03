use crate::utils::{
    ann_excess_return::ann_excess_return,
    ann_volatility::ann_volatility,
    constants::{
        ARRAY_SIZE, SHARPE_NOCONFIDENCE_VALUE, SHARPE_STDDEV_MINIMUM, STATISTICAL_CONFIDENCE_MINIMUM_N, SCALE
    },
};

pub fn sharpe(
    daily_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    risk_free_rate: i64,
    use_weighting: bool,
    bypass_confidence: bool,
) -> i64 {
    let result = if !bypass_confidence & actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        SHARPE_NOCONFIDENCE_VALUE
    } else {
        let excess_return =
            ann_excess_return(daily_returns, actual_len, risk_free_rate, use_weighting);
        let volatility = ann_volatility(daily_returns, actual_len, use_weighting);
        let effective_volatility = if volatility < SHARPE_STDDEV_MINIMUM {
            SHARPE_STDDEV_MINIMUM
        } else {
            volatility
        };

        (excess_return * SCALE) / effective_volatility
    };
    result
}

#[test]
fn test_sharpe_normal_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -300;
    returns[4] = 600;

    let result = sharpe(returns, 5, 100, false, false);
    assert(result != 0);
}

#[test]
fn test_sharpe_low_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..10 {
        returns[i] = 50;
    }

    let result = sharpe(returns, 10, 10, false, false);
    assert(result == 0);
}

#[test]
fn test_sharpe_high_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 5000;
    returns[1] = -4000;
    returns[2] = 3000;
    returns[3] = -2000;
    returns[4] = 1000;

    let result = sharpe(returns, 5, 200, false, false);
    assert(result != 0);
}
