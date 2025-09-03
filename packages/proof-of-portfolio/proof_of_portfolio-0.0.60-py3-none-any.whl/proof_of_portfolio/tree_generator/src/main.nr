use components::core::merkle::{hash_signal, MERKLE_DEPTH, TradingSignal};
use std::hash::pedersen_hash;

global MAX_SIGNALS: u32 = 256;

// A struct to hold all the Merkle tree data
struct MerkleTree {
    root: Field,
    path_elements: [[Field; MERKLE_DEPTH]; MAX_SIGNALS],
    path_indices: [[Field; MERKLE_DEPTH]; MAX_SIGNALS],
    leaf_hashes: [Field; MAX_SIGNALS],
}

// Builds a Merkle tree and returns all necessary components.
fn build_merkle_tree(signals: [TradingSignal; MAX_SIGNALS], actual_len: u32) -> MerkleTree {
    assert(MAX_SIGNALS > 0);
    assert((MAX_SIGNALS & (MAX_SIGNALS - 1)) == 0);
    let mut tree: [[Field; MAX_SIGNALS]; MERKLE_DEPTH + 1] = [[0; MAX_SIGNALS]; MERKLE_DEPTH + 1];

    // 1. Create the leaf layer (level 0)
    for i in 0..MAX_SIGNALS {
        if (i as u32) < actual_len {
            tree[0][i] = hash_signal(signals[i]);
        } else {
            // Use a zero hash for padding to ensure the tree is full.
            tree[0][i] = 0;
        }
    }

    // 2. Build the tree from the bottom up
    for d in 0..MERKLE_DEPTH {
        let layer_width = 1 << ((MERKLE_DEPTH - d) as u32);
        let next_layer_width = layer_width / 2;
        for i in 0..MAX_SIGNALS {
            if (i as u32) < next_layer_width {
                let left = tree[d][2 * i];
                let right = tree[d][2 * i + 1];
                tree[d + 1][i] = pedersen_hash([left, right]);
            }
        }
    }

    // 3. For each leaf, find its Merkle path and indices
    let mut path_elements = [[0; MERKLE_DEPTH]; MAX_SIGNALS];
    let mut path_indices = [[0; MERKLE_DEPTH]; MAX_SIGNALS];

    for i in 0..MAX_SIGNALS {
        // For each leaf
        let mut current_index_in_layer = i;
        for d in 0..MERKLE_DEPTH {
            // For each level of the tree
            let sibling_index_in_layer = current_index_in_layer ^ 1;
            path_elements[i][d] = tree[d][sibling_index_in_layer];
            path_indices[i][d] = (current_index_in_layer % 2) as Field;
            // Move up to the parent's index for the next level
            current_index_in_layer = current_index_in_layer / 2;
        }
    }

    MerkleTree { root: tree[MERKLE_DEPTH][0], path_elements, path_indices, leaf_hashes: tree[0] }
}

fn main(signals: [TradingSignal; MAX_SIGNALS], actual_len: u32) -> pub MerkleTree {
    build_merkle_tree(signals, actual_len)
}
