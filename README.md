# LIA-Projekt-STI-26

## Data Pipeline

To use the projects data pipeline you need to have docker running and run "docker compose up -d" in the data pipeline folder.

To test the data pipeline in isolation remove the comment on "mqtt-test-publisher" as that will start creating test data for the pipeline.

To view the data you can connect to timescale via for example DBeaver or another plattform capable of viewing postgres.
    