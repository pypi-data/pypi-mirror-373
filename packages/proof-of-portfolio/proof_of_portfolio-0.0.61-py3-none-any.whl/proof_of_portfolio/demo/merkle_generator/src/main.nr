use std::hash::pedersen_hash;

global MAX_RETURNS: u32 = 256;

fn hash_return(log_return: i64) -> Field {
    pedersen_hash([log_return as Field])
}

fn build_merkle_root(leaves: [Field; MAX_RETURNS], num_leaves: u32) -> Field {
    let mut nodes = leaves;
    let mut current_num_leaves = num_leaves;

    for _ in 0..8 {
        let mut next_level_nodes = [0; MAX_RETURNS];
        for i in 0..(MAX_RETURNS / 2) {
            if (i*2) < current_num_leaves {
                let left = nodes[i*2];
                let right = if (i*2 + 1) < current_num_leaves { nodes[i*2 + 1] } else { left };
                next_level_nodes[i] = pedersen_hash([left, right]);
            }
        }
        nodes = next_level_nodes;
        let next_num_leaves = (current_num_leaves + 1) / 2;
        current_num_leaves = if current_num_leaves <= 1 { current_num_leaves } else { next_num_leaves };
    }

    if num_leaves == 0 { 0 } else { nodes[0] }
}

fn main(
    log_returns: [i64; MAX_RETURNS],
    n_returns: u32,
) -> pub Field {
    let mut leaves = [0; MAX_RETURNS];
    for i in 0..MAX_RETURNS {
        if (i as u32) < n_returns {
            leaves[i] = hash_return(log_returns[i]);
        }
    }
    build_merkle_root(leaves, n_returns)
}
