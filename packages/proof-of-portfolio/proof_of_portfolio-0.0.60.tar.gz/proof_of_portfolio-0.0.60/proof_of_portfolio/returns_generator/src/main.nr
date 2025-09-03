use dep::std;
use std::ops::WrappingAdd;

pub global MAX_CHECKPOINTS: u32 = 200;
pub global MAX_DAYS: u32 = 120;
pub global MERKLE_DEPTH: u32 = 8;
pub global MAX_RETURNS: u32 = 256;
global DAILY_CHECKPOINTS: u32 = 2;
global SECONDS_PER_DAY: u64 = 86400;

// Hashes a single 64-bit log return into a Field element.
pub fn hash_return(log_return: i64) -> Field {
    let unsigned_value = if log_return < 0 {
        (log_return as u64).wrapping_add(0x8000000000000000)
    } else {
        log_return as u64
    };
    std::hash::pedersen_hash([unsigned_value as Field])
}

// Builds a Merkle root from a set of leaves.
pub fn build_merkle_root(leaves: [Field; MAX_RETURNS], num_leaves: u32) -> Field {
    let mut nodes = leaves;
    let mut current_num_leaves = num_leaves;

    for _ in 0..MERKLE_DEPTH {
        let mut next_level_nodes = [0; MAX_RETURNS];
        for i in 0..(MAX_RETURNS / 2) {
            if (i * 2) < current_num_leaves {
                let left = nodes[i * 2];
                let right = if (i * 2 + 1) < current_num_leaves {
                    nodes[i * 2 + 1]
                } else {
                    left
                };
                next_level_nodes[i] = std::hash::pedersen_hash([left, right]);
            }
        }
        nodes = next_level_nodes;
        let next_num_leaves = (current_num_leaves + 1) / 2;
        current_num_leaves = if current_num_leaves <= 1 {
            current_num_leaves
        } else {
            next_num_leaves
        };
    }
    if num_leaves == 0 {
        0
    } else {
        nodes[0]
    }
}

// Accepts pre-processed daily returns directly (no filtering/aggregation)
pub fn calculate_daily_returns(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
) -> ([i64; MAX_DAYS], u32) {
    let mut daily_returns: [i64; MAX_DAYS] = [0; MAX_DAYS];

    // Since Python pre-processes the data to match subnet logic,
    // we just pass through the aggregated daily returns directly
    for i in 0..MAX_DAYS {
        if (i as u32) < checkpoint_count {
            daily_returns[i] = gains[i] + losses[i];
        }
    }

    (daily_returns, checkpoint_count)
}

pub fn cps_to_log_returns(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
) -> ([i64; MAX_DAYS], u32) {
    calculate_daily_returns(
        gains,
        losses,
        last_update_times,
        accum_times,
        checkpoint_count,
        target_duration,
    )
}

// Main logic
struct ReturnsData {
    returns_merkle_root: Field,
    log_returns: [i64; MAX_DAYS],
    valid_days: u32,
}

fn main(
    gains: [i64; MAX_CHECKPOINTS],
    losses: [i64; MAX_CHECKPOINTS],
    last_update_times: [u64; MAX_CHECKPOINTS],
    accum_times: [u64; MAX_CHECKPOINTS],
    checkpoint_count: u32,
    target_duration: u64,
) -> pub ReturnsData {
    let (log_returns, valid_days) = cps_to_log_returns(
        gains,
        losses,
        last_update_times,
        accum_times,
        checkpoint_count,
        target_duration,
    );
    let mut leaves = [0; MAX_RETURNS];
    for i in 0..MAX_RETURNS {
        if (i as u32) < valid_days {
            leaves[i] = hash_return(log_returns[i]);
        }
    }
    let computed_returns_root = build_merkle_root(leaves, valid_days);
    ReturnsData {
        returns_merkle_root: computed_returns_root,
        log_returns: log_returns,
        valid_days: valid_days,
    }
}
