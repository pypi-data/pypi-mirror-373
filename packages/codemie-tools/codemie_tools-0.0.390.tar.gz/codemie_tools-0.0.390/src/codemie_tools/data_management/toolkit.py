from typing import Optional, Dict, Any

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.data_management.elastic.generic_elastic_tools import SearchElasticIndex
from codemie_tools.data_management.elastic.models import ElasticConfig
from codemie_tools.data_management.elastic.tools_vars import SEARCH_ES_INDEX_TOOL
from codemie_tools.data_management.sql.models import SQLConfig
from codemie_tools.data_management.sql.tools import SQLTool
from codemie_tools.data_management.sql.tools_vars import SQL_TOOL


class DataManagementToolkit(BaseToolkit):
    elastic_config: Optional[ElasticConfig] = None
    sql_config: Optional[SQLConfig] = None

    @classmethod
    def get_tools_ui_info(cls):
        tools = [
            Tool.from_metadata(SEARCH_ES_INDEX_TOOL, settings_config=True),
            Tool.from_metadata(SQL_TOOL, settings_config=True),
        ]
        return ToolKit(
            toolkit=ToolSet.DATA_MANAGEMENT,
            tools=tools,
        ).model_dump()

    def get_tools(self) -> list:
        tools = [
            SQLTool(sql_config=self.sql_config),
            SearchElasticIndex(elastic_config=self.elastic_config)
        ]
        return tools

    @classmethod
    def get_toolkit(cls, configs: Dict[str, Any]):
        elastic_config = ElasticConfig(**configs["elastic"]) if "elastic" in configs else None
        sql_config = SQLConfig(**configs["sql"]) if "sql" in configs else None
        return DataManagementToolkit(elastic_config=elastic_config, sql_config=sql_config)
