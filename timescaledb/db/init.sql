-- Enable Timescale extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ----------------------------
-- Metadata Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS component (
    component_id BIGSERIAL PRIMARY KEY,
    serial_number TEXT NOT NULL UNIQUE,
    model TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ----------------------------
-- Time-Series Table
-- ----------------------------
CREATE TABLE IF NOT EXISTS event_data (
    ts TIMESTAMPTZ NOT NULL,
    component_id BIGINT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    payload JSONB,
    CONSTRAINT fk_component
        FOREIGN KEY(component_id)
        REFERENCES component(component_id)
        ON DELETE CASCADE
);

-- Convert to hypertable
SELECT create_hypertable('event_data', 'ts', if_not_exists => TRUE);

-- Helpful index
CREATE INDEX IF NOT EXISTS idx_event_component_time
ON event_data (component_id, ts DESC);