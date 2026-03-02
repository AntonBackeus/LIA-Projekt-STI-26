CREATE TABLE IF NOT EXISTS test_data (
    ts TIMESTAMP,
    value DOUBLE
) TIMESTAMP(ts)
PARTITION BY DAY;

CREATE TABLE IF NOT EXISTS component (
    componentID LONG,
    serialnumber STRING,
    model STRING,
    PRIMARY KEY (componentID)
);