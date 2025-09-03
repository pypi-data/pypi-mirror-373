pub global ARRAY_SIZE: u32 = 256;
pub global SCALE: i64 = 10_000_000;
pub global DAYS_IN_YEAR: i64 = 365;
pub global STATISTICAL_CONFIDENCE_MINIMUM_N: u32 = 60;

// Risk-free rate (as basis points, e.g., 200 = 2%)
pub global ANNUAL_RISK_FREE_RATE_BP: i64 = 200;
pub global DAILY_LOG_RISK_FREE_RATE: i64 = 1124;

// Minimum values for ratio calculations (scaled for integer math)
pub global SHARPE_STDDEV_MINIMUM: i64 = 100; // Minimum volatility for Sharpe
pub global OMEGA_LOSS_MINIMUM: i64 = 1; // Minimum negative returns for Omega
pub global SORTINO_DOWNSIDE_MINIMUM: i64 = 100; // Minimum downside volatility for Sortino

// Scaling factors for precision in integer calculations
pub global OMEGA_SCALE_FACTOR: i64 = 10000000; // 10M for Omega precision
pub global SHARPE_SCALE_FACTOR: i64 = 1000000; // 1M for Sharpe precision

// Default return values for insufficient confidence
pub global CALMAR_NOCONFIDENCE_VALUE: i64 = -100000000000; // -100 * 10^9 (SCALING_FACTOR)
pub global SHARPE_NOCONFIDENCE_VALUE: i64 = -100000000000; // -100 * 10^9 (SCALING_FACTOR)
pub global OMEGA_NOCONFIDENCE_VALUE: i64 = 0; // Omega uses 0.0 in subnet
pub global SORTINO_NOCONFIDENCE_VALUE: i64 = -100000000000; // -100 * 10^9 (SCALING_FACTOR)
pub global STATISTICAL_CONFIDENCE_NOCONFIDENCE_VALUE: i64 = -100000000000; // -100 * 10^9 (SCALING_FACTOR)
