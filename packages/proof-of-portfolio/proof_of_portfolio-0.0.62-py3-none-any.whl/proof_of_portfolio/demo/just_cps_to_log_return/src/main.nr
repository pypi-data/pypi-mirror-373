pub global MAX_CHECKPOINTS: u32 = 200;
pub global MAX_DAYS: u32 = 120;
global SCALE: i64 = 10_000_000;
global DAILY_CHECKPOINTS: u32 = 2;
global SECONDS_PER_DAY: u64 = 86400;

pub fn calculate_daily_returns(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
) -> ([i64; MAX_DAYS], u32) {
    let mut daily_returns: [i64; MAX_DAYS] = [0; MAX_DAYS];
    let mut daily_counts: [u32; MAX_DAYS] = [0; MAX_DAYS];
    let mut daily_sums: [i64; MAX_DAYS] = [0; MAX_DAYS];
    let mut unique_days: [u64; MAX_DAYS] = [0; MAX_DAYS];
    let mut num_days: u32 = 0;

    for i in 0..MAX_CHECKPOINTS {
        if (i as u32) < checkpoint_count {
            if accum_times[i] == target_duration {
                let start_time = last_update_times[i] - accum_times[i];
                let day_timestamp = start_time / (SECONDS_PER_DAY * 1000);

                let mut day_index: u32 = MAX_DAYS as u32;
                let mut found = false;

                for j in 0..MAX_DAYS {
                    if !found {
                        if unique_days[j] == day_timestamp {
                            day_index = j as u32;
                            found = true;
                        } else {
                            if unique_days[j] == 0 {
                                if day_index == (MAX_DAYS as u32) {
                                    unique_days[j] = day_timestamp;
                                    day_index = j as u32;
                                    if (j as u32) >= num_days {
                                        num_days = (j as u32) + 1;
                                    }
                                    found = true;
                                }
                            }
                        }
                    }
                }

                if day_index < (MAX_DAYS as u32) {
                    daily_sums[day_index] += gains[i] + losses[i];
                    daily_counts[day_index] += 1;
                }
            }
        }
    }

    let mut valid_days: u32 = 0;
    for i in 0..MAX_DAYS {
        if daily_counts[i] == DAILY_CHECKPOINTS {
            if valid_days < (MAX_DAYS as u32) {
                daily_returns[valid_days] = daily_sums[i];
                valid_days += 1;
            }
        }
    }

    (daily_returns, valid_days)
}

pub fn main(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
) -> pub ([i64; MAX_DAYS], u32) {
    calculate_daily_returns(
        gains,
        losses,
        last_update_times,
        accum_times,
        checkpoint_count,
        target_duration,
    )
}
