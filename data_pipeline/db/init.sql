-- Enable Timescale extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ----------------------------
-- Time-series table
-- ----------------------------
CREATE TABLE IF NOT EXISTS robot_status_events (
    ts TIMESTAMPTZ NOT NULL,
    robot_address TEXT NOT NULL,
    raw_message TEXT,
    enriched_data JSONB
);
-- ----------------------------
-- Convert to hypertable
-- ----------------------------

-- Convert to hypertable
SELECT create_hypertable('robot_status_events', 'ts', if_not_exists => TRUE);

-- Helpful index
CREATE INDEX IF NOT EXISTS idx_robot_device_time
ON robot_status_events (robot_address, ts DESC);


