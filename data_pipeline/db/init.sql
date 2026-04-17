-- Enable Timescale extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ----------------------------
-- Time-Series Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS robot_data(
    ts TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,

    event_state INT, 
    state_message TEXT,

    event_value DOUBLE PRECISION,

    error_code INT,

    error_message TEXT

);

-- Convert to hypertable
SELECT create_hypertable('robot_data', 'ts', if_not_exists => TRUE);

-- Helpful index
CREATE INDEX IF NOT EXISTS idx_robot_device_time
ON robot_data (device_id, ts DESC);

