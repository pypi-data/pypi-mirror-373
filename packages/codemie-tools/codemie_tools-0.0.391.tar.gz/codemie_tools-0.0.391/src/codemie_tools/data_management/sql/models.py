from typing import Optional, Dict, Any, TYPE_CHECKING
from enum import Enum
from pydantic import BaseModel, model_validator, field_validator, Field

if TYPE_CHECKING:
    from influxdb_client import InfluxDBClient


class SQLDialect(str, Enum):
    MYSQL = "mysql"
    POSTGRES = "postgres"
    INFLUXDB = "influxdb"
    MSSQL = "mssql"


class SQLConfig(BaseModel):
    # Common fields
    dialect: str
    host: str
    port: str

    # Authentication fields - Optional for InfluxDB 2.x
    username: Optional[str] = None
    password: Optional[str] = None
    database_name: Optional[str] = None

    # InfluxDB specific fields
    token: Optional[str] = None
    org: Optional[str] = None
    bucket: Optional[str] = None
    verify_ssl: Optional[bool] = Field(default=False, description="SSL verification for InfluxDB")

    @classmethod
    @field_validator("dialect")
    def validate_dialect(cls, v):
        if isinstance(v, str):
            return SQLDialect(v)
        return v

    @model_validator(mode="before")
    def validate_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        dialect = values.get("dialect")

        # Common validation for all dialects
        if not all(values.get(field) for field in ["host", "port", "dialect"]):
            raise ValueError("host, port, and dialect are required fields")

        if dialect == SQLDialect.INFLUXDB:
            # InfluxDB validation
            if not values.get("token"):
                raise ValueError("token is required for InfluxDB connections")
            if not values.get("org"):
                raise ValueError("org is required for InfluxDB connections")
            if not values.get("bucket"):
                raise ValueError("bucket is required for InfluxDB connections")
        else:
            # SQL database validation
            required_sql_fields = ["username", "password", "database_name"]
            missing_fields = [field for field in required_sql_fields if not values.get(field)]
            if missing_fields:
                raise ValueError(
                    f"For SQL databases, {', '.join(missing_fields)} are required fields"
                )

        return values

    def get_influxdb_client(self) -> "InfluxDBClient":
        """Creates and returns InfluxDB client instance"""
        if self.dialect != SQLDialect.INFLUXDB:
            raise ValueError("This method is only for InfluxDB configurations")

        from influxdb_client import InfluxDBClient

        return InfluxDBClient(
            url=f"http{'s' if self.verify_ssl else ''}://{self.host}:{self.port}",
            token=self.token,
            org=self.org,
            verify_ssl=self.verify_ssl
        )
