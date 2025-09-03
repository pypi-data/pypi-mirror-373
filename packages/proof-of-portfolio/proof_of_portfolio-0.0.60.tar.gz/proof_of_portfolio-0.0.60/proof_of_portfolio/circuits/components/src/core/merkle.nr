use dep::std;
use std::ops::WrappingAdd;

// Globals
pub global MERKLE_DEPTH: u32 = 8;
pub global MAX_RETURNS: u32 = 256;
pub global MAX_SIGNALS: u32 = 256;

pub struct TradingSignal {
    pub trade_pair: Field,
    pub order_type: u8,
    pub leverage: u64,
    pub price: Field,
    pub processed_ms: u64,
    pub order_uuid: Field,
    pub bid: Field,
    pub ask: Field,
}

pub fn hash_return(log_return: i64) -> Field {
    let unsigned_value = if log_return < 0 {
        (log_return as u64).wrapping_add(0x8000000000000000)
    } else {
        log_return as u64
    };
    std::hash::pedersen_hash([unsigned_value as Field])
}

pub fn hash_signal(signal: TradingSignal) -> Field {
    std::hash::pedersen_hash([
        signal.trade_pair,
        signal.order_type as Field,
        signal.leverage as Field,
        signal.price,
        signal.processed_ms as Field,
        signal.order_uuid,
        signal.bid,
        signal.ask,
    ])
}

// Verifies a merkle inclusion proof for a given leaf
pub fn merkle_inclusion_check(
    leaf: Field,
    root: Field,
    path_elements: [Field; MERKLE_DEPTH],
    path_indices: [Field; MERKLE_DEPTH],
) -> bool {
    let mut current_hash = leaf;

    for i in 0..MERKLE_DEPTH {
        let path_element = path_elements[i];
        let path_index = path_indices[i];

        // If path_index is 0, current_hash is left child, path_element is right
        // If path_index is 1, current_hash is right child, path_element is left
        let left = if path_index == 0 {
            current_hash
        } else {
            path_element
        };
        let right = if path_index == 0 {
            path_element
        } else {
            current_hash
        };

        current_hash = std::hash::pedersen_hash([left, right]);
    }

    current_hash == root
}

pub fn build_merkle_root(leaves: [Field; MAX_RETURNS], num_leaves: u32) -> Field {
    let mut nodes = leaves;
    let mut current_num_leaves = num_leaves;

    for _ in 0..8 {
        let mut next_level_nodes = [0; MAX_RETURNS];

        for i in 0..(MAX_RETURNS / 2) {
            if (i * 2) < current_num_leaves {
                let left = nodes[i * 2];
                let right = if (i * 2 + 1) < current_num_leaves {
                    nodes[i * 2 + 1]
                } else {
                    left
                };
                let mut hash_inputs = [left, right];
                next_level_nodes[i] = std::hash::pedersen_hash(hash_inputs);
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

pub fn build_merkle_root_from_signals(
    signals: [TradingSignal; MAX_RETURNS],
    n_signals: u32,
) -> Field {
    let mut leaves = [0; MAX_RETURNS];
    for i in 0..MAX_RETURNS {
        if (i as u32) < n_signals {
            leaves[i] = hash_signal(signals[i]);
        } else {
            leaves[i] = 0;
        }
    }
    build_merkle_root(leaves, n_signals)
}
