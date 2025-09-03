global ARRAY_SIZE: u32 = 120;
global SCALE: i64 = 1000000000000000000;

fn exp_scaled(x_scaled: i64) -> i64 {
    // Implements Taylor series for exp(x) = 1 + x + x^2/2! + x^3/3! + ...
    // This is for x <= 0

    // Scale down to prevent overflow, then scale back up at the end.
    let reduction_factor = 1000000000;
    let x_scaled_down = x_scaled / reduction_factor;
    let scale_down = SCALE / reduction_factor;

    let x_pow_2 = (x_scaled_down * x_scaled_down) / scale_down;
    let x_pow_3 = (x_pow_2 * x_scaled_down) / scale_down;
    let x_pow_4 = (x_pow_3 * x_scaled_down) / scale_down;
    let x_pow_5 = (x_pow_4 * x_scaled_down) / scale_down;

    let term1 = x_scaled_down;
    let term2 = x_pow_2 / 2;
    let term3 = x_pow_3 / 6;
    let term4 = x_pow_4 / 24;
    let term5 = x_pow_5 / 120;

    (scale_down + term1 + term2 + term3 + term4 + term5) * reduction_factor
}

fn daily_max_drawdown(log_returns: [i64; ARRAY_SIZE], n_returns: u32) -> i64 {
    let mut max_drawdown = 0;
    if n_returns > 0 {
        let mut cumulative_log_returns = [0; ARRAY_SIZE];
        cumulative_log_returns[0] = log_returns[0];
        for i in 1..ARRAY_SIZE {
            if (i as u32) < n_returns {
                cumulative_log_returns[i] = cumulative_log_returns[i-1] + log_returns[i];
            }
        }

        let mut running_max_log = [0; ARRAY_SIZE];
        running_max_log[0] = cumulative_log_returns[0];
        for i in 1..ARRAY_SIZE {
             if (i as u32) < n_returns {
                if cumulative_log_returns[i] > running_max_log[i-1] {
                    running_max_log[i] = cumulative_log_returns[i];
                } else {
                    running_max_log[i] = running_max_log[i-1];
                }
            }
        }

        for i in 0..ARRAY_SIZE {
            if (i as u32) < n_returns {
                let diff = cumulative_log_returns[i] - running_max_log[i];
                let drawdown = SCALE - exp_scaled(diff);
                if drawdown > max_drawdown {
                    max_drawdown = drawdown;
                }
            }
        }
    }
    max_drawdown
}

fn main(log_returns: pub [i64; ARRAY_SIZE], n_returns: pub u32) -> pub i64 {
    daily_max_drawdown(log_returns, n_returns)
}
