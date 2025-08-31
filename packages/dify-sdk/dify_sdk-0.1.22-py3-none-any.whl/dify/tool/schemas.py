from enum import Enum
from typing import Dict, List, Literal, Optional, Union, Any

from pydantic import BaseModel, Field


class ToolType(str, Enum):
    """工具类型枚举"""

    BUILTIN = "builtin"
    API = "api"
    WORKFLOW = "workflow"


class IconContent(BaseModel):
    """图标内容模型"""

    content: str = Field(..., description="图标内容")
    background: str = Field(..., description="图标背景色")


class MultiLanguageText(BaseModel):
    """多语言文本模型"""

    zh_Hans: Optional[str] = Field(None, description="简体中文")
    en_US: Optional[str] = Field(None, description="英文(美国)")
    pt_BR: Optional[str] = Field(None, description="葡萄牙语(巴西)")
    ja_JP: Optional[str] = Field(None, description="日语(日本)")


class ToolParameter(BaseModel):
    """工具参数模型"""

    name: str = Field(..., description="参数名称")
    label: MultiLanguageText = Field(..., description="参数标签")
    human_description: MultiLanguageText = Field(..., description="参数人类可读描述")
    type: str = Field(..., description="参数类型")
    required: bool = Field(..., description="是否必填")
    default: Optional[Any] = Field(None, description="默认值")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="选项列表")


class Tool(BaseModel):
    """工具模型"""

    name: str = Field(..., description="工具名称")
    label: MultiLanguageText = Field(..., description="工具标签")
    description: MultiLanguageText = Field(..., description="工具描述")
    parameters: List[ToolParameter] = Field(
        default_factory=list, description="工具参数列表"
    )


class ToolProvider(BaseModel):
    """工具提供者模型"""

    id: str = Field(..., description="工具提供者ID")
    author: str = Field(..., description="作者")
    name: str = Field(..., description="名称")
    plugin_id: Optional[str] = Field(None, description="插件ID")
    plugin_unique_identifier: Optional[str] = Field(None, description="插件唯一标识符")
    description: MultiLanguageText = Field(..., description="描述")
    icon: Union[str, IconContent] = Field(..., description="图标")
    label: MultiLanguageText = Field(..., description="标签")
    type: ToolType = Field(default=ToolType.API, description="类型")
    team_credentials: Dict[str, Any] = Field(
        default_factory=dict, description="团队凭证"
    )
    is_team_authorization: bool = Field(..., description="是否团队授权")
    allow_delete: bool = Field(..., description="是否允许删除")
    tools: List[Tool] = Field(default_factory=list, description="工具列表")
    labels: Optional[List[str]] = Field(default_factory=list, description="标签列表")


class ToolResponse(BaseModel):
    """工具响应模型"""

    result: Dict[str, Any] = Field(..., description="响应结果")
