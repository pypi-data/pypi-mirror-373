use crate::utils::{
    ann_excess_return::ann_excess_return,
    constants::{
        ARRAY_SIZE, DAILY_LOG_RISK_FREE_RATE, DAYS_IN_YEAR, SORTINO_DOWNSIDE_MINIMUM,
        SORTINO_NOCONFIDENCE_VALUE, STATISTICAL_CONFIDENCE_MINIMUM_N,
    },
    sqrt::sqrt,
};

pub fn sortino(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    RISK_FREE_RATE: i64,
    use_weighting: bool,
) -> i64 {
    // Check minimum sample size for statistical confidence
    if actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        SORTINO_NOCONFIDENCE_VALUE
    } else {
        let excess_return =
            ann_excess_return(log_returns, actual_len, RISK_FREE_RATE, use_weighting);

        let mut downside_variance_sum: u64 = 0;
        let mut negative_count: u32 = 0;
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
            let downside_volatility = sqrt(downside_variance * (DAYS_IN_YEAR as u64)) as i64;

            // Use minimum downside volatility to avoid division by zero/small numbers
            let effective_downside_volatility = if downside_volatility > SORTINO_DOWNSIDE_MINIMUM {
                downside_volatility
            } else {
                SORTINO_DOWNSIDE_MINIMUM
            };

            (excess_return * 100000000) / effective_downside_volatility
        } else {
            // No negative returns means infinite Sortino ratio, return a large value
            100000000
        }
    }
}

#[test]
fn test_sortino_normal_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -300;
    returns[4] = 600;

    let result = sortino(returns, 5, 100, false);
    assert(result != 0);
}

#[test]
fn test_sortino_no_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 1000;
    }

    let result = sortino(returns, 5, 100, false);
    assert(result == 0);
}

#[test]
fn test_sortino_all_negative_returns() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = -500;
    }

    let result = sortino(returns, 5, 0, false);
    assert(result != 0);
}

#[test]
fn test_sortino_high_downside_volatility() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 2000;
    returns[1] = -1500;
    returns[2] = 1800;
    returns[3] = -1200;
    returns[4] = 1600;

    let result = sortino(returns, 5, 200, false);
    assert(result != 0);
}
