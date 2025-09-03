pub fn test_function() -> u64 {
    1
}

pub struct Order {
    pub order_type: u8,
    pub leverage: i32,
    pub price: u64,
    pub processed_ms: u64,
    pub slippage: u64,
    pub src: u8,
}

pub struct Position {
    pub miner_hotkey: Field,
    pub position_uuid: Field,
    pub orders: [Order; 8],
    pub orders_len: u32,
    pub net_leverage: i32,
    pub average_entry_price: u64,
    pub initial_entry_price: u64,
    pub is_closed_position: bool,
    pub close_ms: u64,
    pub position_type: u8,
    pub realized_pnl: i64,
}

pub struct TradePairExtended {
    pub fees: u64,
    pub asset_type: u8,
}

global PRICE_SCALE: u64 = 1_000_000_000_000;
global LEVERAGE_SCALE: u32 = 10_000;

global ORDER_TYPE_LONG: u8 = 1;
global ORDER_TYPE_SHORT: u8 = 2;
global ORDER_TYPE_FLAT: u8 = 0;

global ORDER_SRC_ORGANIC: u8 = 1;

global FEE_V6_TIME_MS: u64 = 1720843707000;
global SLIPPAGE_V1_TIME_MS: u64 = 1739937600000;

fn abs_i32(x: i32) -> u32 {
    if x >= 0 {
        x as u32
    } else {
        (-x) as u32
    }
}

fn abs_i64(x: i64) -> u64 {
    if x >= 0 {
        x as u64
    } else {
        (-x) as u64
    }
}

fn leverage_flipped(prev_leverage: i32, cur_leverage: i32) -> bool {
    (prev_leverage * cur_leverage < 0) | ((prev_leverage != 0) & (cur_leverage == 0))
}

pub fn get_cumulative_leverage(position: Position) -> u32 {
    let mut current_leverage: i32 = 0;
    let mut cumulative_leverage: u32 = 0;
    let mut position_closed = false;

    for i in 0..position.orders_len {
        if (i as u32) < position.orders_len & !position_closed {
            let order = position.orders[i];

            if order.src == ORDER_SRC_ORGANIC {
                if order.order_type == ORDER_TYPE_FLAT {
                    cumulative_leverage += abs_i32(current_leverage);
                    position_closed = true;
                } else {
                    let prev_leverage = current_leverage;
                    current_leverage += order.leverage;

                    if (current_leverage == 0) | leverage_flipped(prev_leverage, current_leverage) {
                        cumulative_leverage += abs_i32(prev_leverage);
                        position_closed = true;
                    } else {
                        cumulative_leverage += abs_i32(current_leverage - prev_leverage);
                    }
                }
            }
        }
    }

    cumulative_leverage
}

pub fn calculate_pnl_with_slippage(
    position: Position,
    current_price: u64,
    timestamp_ms: u64,
) -> u64 {
    if position.initial_entry_price == 0 {
        LEVERAGE_SCALE as u64
    } else {
        let use_slippage = timestamp_ms >= SLIPPAGE_V1_TIME_MS;

        if use_slippage {
            let realized_pnl = position.realized_pnl as Field;
            let current_price_field = current_price as Field;
            let avg_entry_price_field = position.average_entry_price as Field;
            let net_leverage_field = position.net_leverage as Field;

            let unrealized_pnl = (current_price_field - avg_entry_price_field) * net_leverage_field;
            let total_pnl = realized_pnl + unrealized_pnl;
            let gain = total_pnl / (position.initial_entry_price as Field);

            let net_return_field = (LEVERAGE_SCALE as Field) + gain;

            let net_return_u64 = net_return_field as u64;
            if net_return_u64 > 0 {
                net_return_u64
            } else {
                0
            }
        } else {
            let current_price_field = current_price as Field;
            let avg_entry_price_field = position.average_entry_price as Field;
            let initial_entry_price_field = position.initial_entry_price as Field;
            let net_leverage_field = position.net_leverage as Field;

            let price_diff = current_price_field - avg_entry_price_field;
            let numerator = price_diff * net_leverage_field;
            let gain = numerator / initial_entry_price_field;
            let net_return_field = (LEVERAGE_SCALE as Field) + gain;

            let net_return_u64 = net_return_field as u64;
            if net_return_u64 > 0 {
                net_return_u64
            } else {
                0
            }
        }
    }
}

pub fn get_spread_fee(
    trade_pair: TradePairExtended,
    cumulative_leverage: u32,
    timestamp_ms: u64,
) -> u64 {
    let use_slippage = timestamp_ms >= SLIPPAGE_V1_TIME_MS;

    if use_slippage {
        PRICE_SCALE
    } else {
        let cumulative_leverage_field = cumulative_leverage as Field;
        let fees_field = trade_pair.fees as Field;
        let price_scale_field = PRICE_SCALE as Field;

        let fee_component = (cumulative_leverage_field * fees_field) / 2;
        let fee_component_u64 = fee_component as u64;
        let result_field = if fee_component_u64 >= PRICE_SCALE {
            0 as Field
        } else {
            price_scale_field - fee_component
        };

        let result_u64 = result_field as u64;
        if result_u64 > 0 {
            result_u64
        } else {
            0
        }
    }
}

pub fn calculate_position_return_with_fees(
    position: Position,
    trade_pair: TradePairExtended,
    current_price: u64,
    cumulative_leverage: u32,
    timestamp_ms: u64,
) -> u64 {
    let base_return = calculate_pnl_with_slippage(position, current_price, timestamp_ms);

    if timestamp_ms < FEE_V6_TIME_MS {
        let fee_amount = trade_pair.fees * (abs_i32(position.net_leverage) as u64);
        let fee_multiplier = if fee_amount >= PRICE_SCALE {
            0
        } else {
            PRICE_SCALE - fee_amount
        };
        (base_return * fee_multiplier) / PRICE_SCALE
    } else {
        let spread_fee = get_spread_fee(trade_pair, cumulative_leverage, timestamp_ms);
        (base_return * spread_fee) / PRICE_SCALE
    }
}

pub fn validate_position_calculation(
    position: Position,
    trade_pair: TradePairExtended,
    current_price: u64,
    expected_return: u64,
    timestamp_ms: u64,
) -> bool {
    let cumulative_leverage = get_cumulative_leverage(position);
    let calculated_return = calculate_position_return_with_fees(
        position,
        trade_pair,
        current_price,
        cumulative_leverage,
        timestamp_ms,
    );

    calculated_return == expected_return
}
