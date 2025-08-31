from typing import Optional, List, Union, Any

from pydantic import BaseModel, Field


class MultiLanguage(BaseModel):
    """标签Schema

    Attributes:
        en: 英文标签
        zh: 中文标签
    """

    zh_Hans: Optional[str] = Field(description="中文标签")
    en_US: Optional[str] = Field(description="英文标签")


class ModelProperties(BaseModel):
    """模型属性Schema

    Attributes:
        max_tokens: 最大令牌数
        temperature: 温度
    """

    context_size: Optional[int] = Field(description="上下文大小")
    mode: Optional[str] = Field(description="模式")


class Model(BaseModel):
    """LLM模型Schema

    Attributes:
        model: 模型名称
        label: 模型标签，包含中英文
        model_type: 模型类型
        features: 模型支持的功能列表
        fetch_from: 模型来源
        model_properties: 模型属性
        deprecated: 是否已弃用
        status: 模型状态
        load_balancing_enabled: 是否启用负载均衡
    """

    model: Optional[str] = Field(description="模型名称")
    label: Optional[MultiLanguage] = Field(description="模型标签，包含中英文")
    model_type: Optional[str] = Field(description="模型类型")
    features: Optional[list[str]] = Field(default=None, description="模型支持的功能列表")
    fetch_from: Optional[str] = Field(description="模型来源")
    model_properties: Optional[ModelProperties] = Field(description="模型属性")
    deprecated: Optional[bool] = Field(default=None, description="是否已弃用")
    status: Optional[str] = Field(description="模型状态")
    load_balancing_enabled: Optional[bool] = Field(default=None, description="是否启用负载均衡")


class LLM(BaseModel):
    """LLM模型提供者Schema

    Attributes:
        tenant_id: 租户ID
        provider: 模型提供者
        label: 模型标签，包含中英文
        icon_small: 小图标，包含中英文
        icon_large: 大图标，包含中英文
        status: 模型状态
    """

    tenant_id: Optional[str] = Field(description="租户ID")
    provider: Optional[str] = Field(description="模型提供者")
    label: Optional[MultiLanguage] = Field(description="模型标签，包含中英文")
    icon_small: Optional[MultiLanguage] = Field(description="小图标，包含中英文")
    icon_large: Optional[MultiLanguage] = Field(description="大图标，包含中英文")
    status: Optional[str] = Field(description="模型状态")
    models: Optional[list[Model]] = Field(default=None, description="模型列表")


class LLMList(BaseModel):
    """LLM模型列表Schema

    Attributes:
        data: 模型列表
        total: 模型总数
    """

    data: Optional[list[LLM]] = Field(default=None, description="模型列表")


class ModelParameterRule(BaseModel):
    """模型参数规则Schema

    Attributes:
        name: 参数名称
        use_template: 使用模板
        label: 参数标签，包含中英文
        type: 参数类型
        help: 参数帮助信息，包含中英文
        required: 是否必需
        default: 默认值
        min: 最小值
        max: 最大值
        precision: 精度
        options: 选项列表
    """

    name: str = Field(description="参数名称")
    use_template: Optional[str] = Field(default=None, description="使用模板")
    label: MultiLanguage = Field(description="参数标签，包含中英文")
    type: str = Field(description="参数类型")
    help: MultiLanguage = Field(description="参数帮助信息，包含中英文")
    required: bool = Field(description="是否必需")
    default: Optional[Union[str, int, float, bool]] = Field(default=None, description="默认值")
    min: Optional[float] = Field(default=None, description="最小值")
    max: Optional[float] = Field(default=None, description="最大值")
    precision: Optional[int] = Field(default=None, description="精度")
    options: List[str] = Field(default_factory=list, description="选项列表")


class ModelParameterRuleList(BaseModel):
    """模型参数规则列表Schema

    Attributes:
        data: 参数规则列表
    """

    data: List[ModelParameterRule] = Field(description="参数规则列表")
