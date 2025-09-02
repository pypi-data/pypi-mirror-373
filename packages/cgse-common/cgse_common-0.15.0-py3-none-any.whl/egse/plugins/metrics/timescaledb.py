from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from urllib.parse import urlparse

import psycopg
import psycopg.rows

from egse.metrics import DataPoint


class TimeScaleDBRepository:
    """
    TimeScaleDB TimeSeriesRepository implementation.

    TimeScaleDB is a PostgreSQL extension optimized for time-series data.
    It uses hypertables for automatic partitioning and provides excellent
    performance for time-series workloads.

    Data model:
    - Each measurement becomes a hypertable
    - Time column for timestamps
    - Tag columns for indexed metadata
    - Field columns for actual values
    - Automatic partitioning by time
    """

    def __init__(
        self,
        connection_string: str,
        database: str = "timeseries",
        create_hypertables: bool = True,
        chunk_time_interval: str = "1 day",
    ):
        """
        Initialize TimeScaleDB repository.

        Args:
            connection_string: PostgreSQL connection string
                             (e.g., "postgresql://user:pass@localhost:5432/dbname")
            database: Database name
            create_hypertables: Whether to automatically create hypertables
            chunk_time_interval: Hypertable chunk interval (e.g., "1 day", "1 hour")
        """
        self.connection_string = connection_string
        self.database = database
        self.create_hypertables = create_hypertables
        self.chunk_time_interval = chunk_time_interval
        self.conn = None
        self.cursor = None
        self._known_measurements = set()

    def connect(self) -> None:
        """Connect to TimeScaleDB and ensure extensions are installed."""
        try:
            self.conn = psycopg.connect(
                self.connection_string, row_factory=psycopg.rows.dict_row, options="-c search_path=public"
            )
            self.conn.autocommit = False
            self.cursor = self.conn.cursor()

            # Ensure TimescaleDB extension is installed
            self.cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
            self.conn.commit()

            # Create metadata table for tracking measurements
            self._create_metadata_table()

        except psycopg.Error as exc:
            raise ConnectionError(f"Failed to connect to TimeScaleDB: {exc}")

    def _create_metadata_table(self) -> None:
        """Create metadata table to track measurements and their schemas."""
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS _timeseries_metadata (
                    measurement VARCHAR(255) PRIMARY KEY,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    tag_columns TEXT[],
                    field_columns TEXT[],
                    last_updated TIMESTAMPTZ DEFAULT NOW()
                );
            """
            )
            self.conn.commit()
        except psycopg.Error as exc:
            raise RuntimeError(f"Failed to create metadata table: {exc}")

    def _ensure_measurement_table(self, measurement: str, tags: Dict[str, str], fields: Dict[str, Any]) -> None:
        """Create measurement table and hypertable if it doesn't exist."""
        if measurement in self._known_measurements:
            return

        try:
            # Check if table exists
            self.cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """,
                (measurement,),
            )

            table_exists = self.cursor.fetchone()["exists"]

            if not table_exists:
                # Analyze tags and fields to determine column types
                tag_columns = []
                field_columns = []

                for tag_key in tags.keys():
                    tag_columns.append(f"{tag_key} TEXT")

                for field_key, field_value in fields.items():
                    if isinstance(field_value, (int, float)):
                        field_columns.append(f"{field_key} DOUBLE PRECISION")
                    elif isinstance(field_value, bool):
                        field_columns.append(f"{field_key} BOOLEAN")
                    else:
                        field_columns.append(f"{field_key} TEXT")

                # Build CREATE TABLE statement
                all_columns = ["time TIMESTAMPTZ NOT NULL"] + tag_columns + field_columns

                create_sql = f"""
                    CREATE TABLE {measurement} (
                        {", ".join(all_columns)}
                    );
                """

                self.cursor.execute(create_sql)

                # Create hypertable if enabled
                if self.create_hypertables:
                    self.cursor.execute(
                        f"""
                        SELECT create_hypertable('{measurement}', 'time',
                                                chunk_time_interval => INTERVAL '{self.chunk_time_interval}');
                    """
                    )

                # Create indices on tag columns for better query performance
                for tag_key in tags.keys():
                    index_name = f"idx_{measurement}_{tag_key}"
                    self.cursor.execute(
                        f"""
                        CREATE INDEX IF NOT EXISTS {index_name} 
                        ON {measurement} ({tag_key});
                    """
                    )

                # Update metadata
                self.cursor.execute(
                    """
                    INSERT INTO _timeseries_metadata 
                    (measurement, tag_columns, field_columns) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT (measurement) DO UPDATE SET
                        tag_columns = EXCLUDED.tag_columns,
                        field_columns = EXCLUDED.field_columns,
                        last_updated = NOW();
                """,
                    (measurement, list(tags.keys()), list(fields.keys())),
                )

                self.conn.commit()
                print(
                    f"Created hypertable '{measurement}' with {len(tag_columns)} tag columns and {len(field_columns)} field columns"
                )

            self._known_measurements.add(measurement)

        except psycopg.Error as exc:
            self.conn.rollback()
            raise RuntimeError(f"Failed to create measurement table '{measurement}': {exc}")

    def write_points(self, points: List[DataPoint]) -> None:
        """Write data points to TimeScaleDB."""
        if not self.conn or not self.cursor:
            raise ConnectionError("Not connected. Call connect() first.")

        if not points:
            return

        # Group points by measurement
        points_by_measurement = {}
        for point in points:
            if point.measurement not in points_by_measurement:
                points_by_measurement[point.measurement] = []
            points_by_measurement[point.measurement].append(point)

        try:
            # Process each measurement
            for measurement, measurement_points in points_by_measurement.items():
                # Ensure table exists (analyze first point for schema)
                first_point = measurement_points[0]
                self._ensure_measurement_table(measurement, first_point.tags, first_point.fields)

                # Prepare batch insert
                self._batch_insert_points(measurement, measurement_points)

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"Failed to write data points: {e}")

    def _batch_insert_points(self, measurement: str, points: List[DataPoint]) -> None:
        """Batch insert points for a specific measurement."""
        if not points:
            return

        # Get all unique columns from all points
        all_tags = set()
        all_fields = set()

        for point in points:
            all_tags.update(point.tags.keys())
            all_fields.update(point.fields.keys())

        # Build column list
        columns = ["time"] + sorted(all_tags) + sorted(all_fields)

        # Prepare values
        values = []
        for point in points:
            # Handle timestamp
            timestamp = point.timestamp
            if timestamp is None:
                timestamp = datetime.now()
            elif isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            row = [timestamp]

            # Add tag values
            for tag in sorted(all_tags):
                row.append(point.tags.get(tag))

            # Add field values
            for field in sorted(all_fields):
                row.append(point.fields.get(field))

            values.append(row)

        # Build INSERT statement
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"""
            INSERT INTO {measurement} ({", ".join(columns)})
            VALUES ({placeholders})
        """

        # Execute batch insert
        # psycopg.extras.execute_batch(
        #     self.cursor, insert_sql, values, page_size=1000
        # )
        self.cursor.executemany(insert_sql, values, page_size=1000)

    def query(self, query_str: str, params: Optional[tuple] = None) -> List[Dict]:
        """Execute SQL query and return results."""
        if not self.conn or not self.cursor:
            raise ConnectionError("Not connected. Call connect() first.")

        try:
            if params:
                self.cursor.execute(query_str, params)
            else:
                self.cursor.execute(query_str)

            # Fetch results as dictionaries
            results = self.cursor.fetchall()

            # Convert RealDictRow to regular dict and handle datetime serialization
            formatted_results = []
            for row in results:
                row_dict = dict(row)
                # Convert datetime objects to ISO strings
                for key, value in row_dict.items():
                    if isinstance(value, datetime):
                        row_dict[key] = value.isoformat()
                formatted_results.append(row_dict)

            return formatted_results

        except psycopg2.Error as e:
            raise RuntimeError(f"Failed to execute query: {e}")

    def close(self) -> None:
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

    # Schema exploration methods
    def get_tables(self) -> List[str]:
        """Get all measurements (hypertables)."""
        try:
            # Get all hypertables
            self.cursor.execute(
                """
                SELECT hypertable_name 
                FROM timescaledb_information.hypertables
                ORDER BY hypertable_name;
            """
            )

            hypertables = [row["hypertable_name"] for row in self.cursor.fetchall()]

            # Also get regular tables that might be measurements
            self.cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name NOT LIKE '_%'
                AND table_name NOT IN (
                    SELECT hypertable_name 
                    FROM timescaledb_information.hypertables
                )
                ORDER BY table_name;
            """
            )

            regular_tables = [row["table_name"] for row in self.cursor.fetchall()]

            return sorted(set(hypertables + regular_tables))

        except psycopg2.Error as e:
            print(f"Error getting tables: {e}")
            return []

    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a measurement."""
        try:
            self.cursor.execute(
                """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """,
                (table_name,),
            )

            columns = []
            for row in self.cursor.fetchall():
                columns.append(
                    {
                        "column_name": row["column_name"],
                        "data_type": row["data_type"],
                        "is_nullable": row["is_nullable"],
                        "column_default": row["column_default"],
                    }
                )

            return columns

        except psycopg2.Error as e:
            print(f"Error getting columns for {table_name}: {e}")
            return []

    def get_schema_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed schema information for a measurement."""
        columns = self.get_columns(table_name)

        schema = {
            "table_name": table_name,
            "time_column": None,
            "tag_columns": [],
            "field_columns": [],
            "is_hypertable": self._is_hypertable(table_name),
        }

        # Get metadata if available
        try:
            self.cursor.execute(
                """
                SELECT tag_columns, field_columns 
                FROM _timeseries_metadata 
                WHERE measurement = %s;
            """,
                (table_name,),
            )

            metadata = self.cursor.fetchone()
            known_tags = set(metadata["tag_columns"]) if metadata else set()
            known_fields = set(metadata["field_columns"]) if metadata else set()
        except:
            known_tags = set()
            known_fields = set()

        for col in columns:
            col_name = col["column_name"]

            if col_name == "time":
                schema["time_column"] = col
            elif col_name in known_tags or col["data_type"] in ["text", "character varying"]:
                schema["tag_columns"].append(col)
            elif col_name in known_fields or col["data_type"] in ["double precision", "integer", "boolean"]:
                schema["field_columns"].append(col)

        # Add row count and time range
        try:
            self.cursor.execute(
                f"""
                SELECT 
                    COUNT(*) as row_count,
                    MIN(time) as earliest_time,
                    MAX(time) as latest_time
                FROM {table_name};
            """
            )

            stats = self.cursor.fetchone()
            if stats:
                schema.update(
                    {
                        "row_count": stats["row_count"],
                        "earliest_time": stats["earliest_time"].isoformat() if stats["earliest_time"] else None,
                        "latest_time": stats["latest_time"].isoformat() if stats["latest_time"] else None,
                    }
                )
        except:
            schema.update({"row_count": 0, "earliest_time": None, "latest_time": None})

        return schema

    def _is_hypertable(self, table_name: str) -> bool:
        """Check if table is a hypertable."""
        try:
            self.cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM timescaledb_information.hypertables
                    WHERE hypertable_name = %s
                );
            """,
                (table_name,),
            )

            return self.cursor.fetchone()["exists"]
        except:
            return False

    def inspect_database(self) -> Dict[str, Any]:
        """Get complete database schema information."""
        measurements = self.get_tables()

        database_info = {
            "database": self.database,
            "connection_string": self._sanitize_connection_string(),
            "total_measurements": len(measurements),
            "measurements": {},
        }

        # Get TimescaleDB specific info
        try:
            self.cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';")
            version = self.cursor.fetchone()
            database_info["timescaledb_version"] = version["extversion"] if version else "Unknown"
        except:
            database_info["timescaledb_version"] = "Not installed"

        # Get schema info for each measurement
        for measurement in measurements:
            database_info["measurements"][measurement] = self.get_schema_info(measurement)

        return database_info

    def _sanitize_connection_string(self) -> str:
        """Remove sensitive info from connection string for logging."""
        try:
            parsed = urlparse(self.connection_string)
            return f"{parsed.scheme}://**:**@{parsed.hostname}:{parsed.port}{parsed.path}"
        except:
            return "postgresql://***:***@***:***/***"

    def query_latest(self, measurement: str, limit: int = 20) -> List[Dict]:
        """Get latest records for a measurement."""
        try:
            query = f"""
                SELECT * FROM {measurement}
                ORDER BY time DESC
                LIMIT %s;
            """

            return self.query(query, (limit,))

        except Exception as e:
            print(f"Error getting latest records for {measurement}: {e}")
            return []

    def query_time_range(
        self, measurement: str, start_time: str, end_time: str, limit: Optional[int] = None
    ) -> List[Dict]:
        """Query records within a time range."""
        try:
            limit_clause = f"LIMIT {limit}" if limit else ""

            query = f"""
                SELECT * FROM {measurement}
                WHERE time >= %s AND time <= %s
                ORDER BY time DESC
                {limit_clause};
            """

            return self.query(query, (start_time, end_time))

        except Exception as e:
            print(f"Error querying time range for {measurement}: {e}")
            return []

    def aggregate_by_time(
        self, measurement: str, field_name: str, time_bucket: str = "1 hour", aggregation: str = "AVG"
    ) -> List[Dict]:
        """Aggregate field values using TimescaleDB time_bucket function."""
        try:
            agg_func = aggregation.upper()
            if agg_func not in ["AVG", "SUM", "COUNT", "MIN", "MAX"]:
                raise ValueError(f"Unsupported aggregation function: {aggregation}")

            query = f"""
                SELECT 
                    time_bucket(INTERVAL '{time_bucket}', time) as time_bucket,
                    {agg_func}({field_name}) as {field_name}_{agg_func.lower()}
                FROM {measurement}
                WHERE {field_name} IS NOT NULL
                GROUP BY time_bucket
                ORDER BY time_bucket;
            """

            return self.query(query)

        except Exception as e:
            print(f"Error in time aggregation: {e}")
            return []

    def get_hypertable_info(self, measurement: str) -> Dict[str, Any]:
        """Get TimescaleDB specific hypertable information."""
        try:
            if not self._is_hypertable(measurement):
                return {"is_hypertable": False}

            # Get hypertable stats
            self.cursor.execute(
                """
                SELECT 
                    h.table_name,
                    h.compression_enabled,
                    h.chunk_time_interval,
                    s.num_chunks,
                    s.total_chunks,
                    s.approximate_row_count,
                    s.total_bytes
                FROM timescaledb_information.hypertables h
                LEFT JOIN timescaledb_information.hypertable_stats s 
                    ON h.hypertable_name = s.hypertable_name
                WHERE h.hypertable_name = %s;
            """,
                (measurement,),
            )

            info = self.cursor.fetchone()
            if info:
                return {
                    "is_hypertable": True,
                    "compression_enabled": info["compression_enabled"],
                    "chunk_time_interval": str(info["chunk_time_interval"]),
                    "num_chunks": info["num_chunks"],
                    "total_chunks": info["total_chunks"],
                    "approximate_row_count": info["approximate_row_count"],
                    "total_bytes": info["total_bytes"],
                }

            return {"is_hypertable": True}

        except Exception as e:
            print(f"Error getting hypertable info: {e}")
            return {"is_hypertable": False, "error": str(e)}


def get_repository_class():
    """Return the repository class for the plugin manager."""
    return TimeScaleDBRepository
