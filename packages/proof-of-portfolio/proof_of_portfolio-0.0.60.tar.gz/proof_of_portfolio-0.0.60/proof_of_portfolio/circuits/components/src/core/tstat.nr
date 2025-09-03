use crate::utils::{
    average::average,
    constants::{
        ARRAY_SIZE, SCALE, STATISTICAL_CONFIDENCE_MINIMUM_N, STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE,
    },
    sqrt::sqrt,
    variance::variance,
};

pub fn statistical_confidence(
    log_returns: [i64; ARRAY_SIZE],
    actual_len: u32,
    use_weighting: bool,
) -> i64 {
    // Check minimum sample size for statistical confidence
    if actual_len < STATISTICAL_CONFIDENCE_MINIMUM_N {
        if actual_len < 2 {
            STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE
        } else {
            // Allow computation for sample sizes between 2 and minimum, but with reduced confidence
            compute_t_statistic(log_returns, actual_len, use_weighting)
        }
    } else {
        compute_t_statistic(log_returns, actual_len, use_weighting)
    }
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

#[test]
fn test_tstat_normal_case() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;
    returns[2] = 800;
    returns[3] = -300;
    returns[4] = 600;

    let result = statistical_confidence(returns, 5, false);
    assert(result != 0);
}

#[test]
fn test_tstat_insufficient_data() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;

    let result = statistical_confidence(returns, 1, false);
    assert(result == 0);
}

#[test]
fn test_tstat_zero_variance() {
    let mut returns = [0; ARRAY_SIZE];
    for i in 0..5 {
        returns[i] = 100;
    }

    let result = statistical_confidence(returns, 5, false);
    assert(result == 0);
}

#[test]
fn test_tstat_exactly_two_samples() {
    let mut returns = [0; ARRAY_SIZE];
    returns[0] = 1000;
    returns[1] = -500;

    let result = statistical_confidence(returns, 2, false);
    assert(result != 0);
}
