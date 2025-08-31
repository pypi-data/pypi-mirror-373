from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field

from dify.tag import Tag


class KeywordSetting(BaseModel):
    """关键词权重设置Schema

    Attributes:
        keyword_weight: 关键词权重，取值范围0-1，默认0.3
    """

    keyword_weight: float = Field(default=0.3, ge=0, le=1, description="关键词权重")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class VectorSetting(BaseModel):
    """向量权重设置Schema

    Attributes:
        vector_weight: 向量权重，取值范围0-1，默认0.7
        embedding_provider_name: 嵌入模型提供商名称
        embedding_model_name: 嵌入模型名称
    """

    vector_weight: float = Field(default=0.7, ge=0, le=1, description="向量权重")
    embedding_provider_name: str = Field(default="", description="嵌入模型提供商名称")
    embedding_model_name: str = Field(default="", description="嵌入模型名称")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class Weights(BaseModel):
    """权重设置Schema

    Attributes:
        keyword_setting: 关键词权重设置
        vector_setting: 向量权重设置
    """

    weight_type: str = Field(default="customized", description="权重类型")
    vector_setting: VectorSetting = Field(
        default=VectorSetting(), description="向量权重设置"
    )
    keyword_setting: KeywordSetting = Field(
        default=KeywordSetting(), description="关键词权重设置"
    )

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class RerankingModel(BaseModel):
    """重排序设置Schema

    Attributes:
        reranking_provider_name: 重排序模型提供商名称
        reranking_model_name: 重排序模型名称
    """

    reranking_provider_name: str = Field(
        default="langgenius/tongyi/tongyi", description="重排序模型提供商名称"
    )
    reranking_model_name: str = Field(
        default="gte-rerank", description="重排序模型名称"
    )

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class RetrievalModel(BaseModel):
    """检索模型Schema

    Attributes:
        search_method: 搜索方法
        reranking_enable: 是否启用重排序
        reranking_model: 重排序模型设置
        top_k: 返回结果数量
        score_threshold_enabled: 是否启用分数阈值
        score_threshold: 分数阈值
        reranking_mode: 重排序模式
        weights: 权重设置
    """

    search_method: str = Field(default="hybrid_search", description="搜索方法")
    reranking_enable: bool = Field(default=True, description="是否启用重排序")
    reranking_model: RerankingModel = Field(
        default=RerankingModel(), description="重排序模型设置"
    )
    top_k: int = Field(default=3, description="返回结果数量")
    score_threshold_enabled: bool = Field(default=False, description="是否启用分数阈值")
    score_threshold: float = Field(default=0.5, description="分数阈值")
    reranking_mode: str = Field(default="reranking_model", description="重排序模式")
    weights: Weights = Field(default=Weights(), description="权重设置")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class ProcessRule(BaseModel):
    """数据处理规则Schema

    Attributes:
        rules: 预处理规则配置
        mode: 处理模式
    """

    rules: dict = Field(
        default={
            "pre_processing_rules": [
                {"id": "remove_extra_spaces", "enabled": True},
                {"id": "remove_urls_emails", "enabled": False},
            ],
            "segmentation": {
                "separator": "\n\n",
                "max_tokens": 500,
                "chunk_overlap": 50,
            },
        },
        description="预处理规则配置",
    )
    mode: str = Field(default="custom", description="处理模式")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class FileInfoList(BaseModel):
    """文件信息列表Schema

    Attributes:
        file_ids: 文件ID列表
    """

    file_ids: List[str] = Field(default_factory=list, description="文件ID列表")


class InfoList(BaseModel):
    data_source_type: str = Field(default="upload_file", description="数据源类型")
    file_info_list: FileInfoList = Field(
        default=FileInfoList(), description="文件信息列表"
    )


class UploadFileDetail(BaseModel):
    """上传文件详情Schema

    Attributes:
        id: 文件ID
        name: 文件名称
        size: 文件大小（字节）
        extension: 文件扩展名
        mime_type: MIME类型
        created_by: 创建者ID
        created_at: 创建时间戳
    """

    id: str = Field(description="文件ID")
    name: str = Field(description="文件名称")
    size: int = Field(description="文件大小（字节）")
    extension: str = Field(description="文件扩展名")
    mime_type: str = Field(description="MIME类型")
    created_by: str = Field(description="创建者ID")
    created_at: float = Field(description="创建时间戳")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DataSourceDetailDict(BaseModel):
    """数据源详细信息Schema

    Attributes:
        upload_file: 上传文件详情
    """

    upload_file: UploadFileDetail = Field(description="上传文件详情")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DataSource(BaseModel):
    """数据源Schema

    Attributes:
        data_source_type: 数据源类型
        file_info_list: 文件信息列表
    """

    type: str = Field(default="upload_file", description="数据源类型")
    info_list: InfoList = Field(default=InfoList(), description="文件信息列表")


class DataSetCreatePayloads(BaseModel):
    """数据集创建请求Schema

    Attributes:
        data_source: 数据源配置
        indexing_technique: 索引技术
        process_rule: 处理规则
        doc_form: 文档格式
        doc_language: 文档语言
        retrieval_model: 检索模型配置
        embedding_model: 嵌入模型
        embedding_model_provider: 嵌入模型提供商
    """

    data_source: DataSource = Field(description="数据源配置")
    indexing_technique: str = Field(default="high_quality", description="索引技术")
    process_rule: ProcessRule = Field(default=ProcessRule(), description="处理规则")
    doc_form: str = Field(default="text_model", description="文档格式")
    doc_language: str = Field(default="Chinese", description="文档语言")
    retrieval_model: RetrievalModel = Field(
        default=RetrievalModel(), description="检索模型配置"
    )
    embedding_model: str = Field(
        default="text-embedding-3-large", description="嵌入模型"
    )
    embedding_model_provider: str = Field(
        default="langgenius/openai/openai", description="嵌入模型提供商"
    )

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DataSetInCreate(BaseModel):
    """数据集Schema

    Attributes:
        id: 数据集ID
        name: 数据集名称
        description: 数据集描述
        permission: 数据集权限
        data_source_type: 数据源类型
        indexing_technique: 索引技术
        created_by: 创建者ID
        created_at: 创建时间戳
    """

    id: str = Field(description="数据集ID")
    name: str = Field(description="数据集名称")
    description: Optional[str] = Field(default=None, description="数据集描述")
    permission: Optional[str] = Field(default="only_me", description="数据集权限")
    data_source_type: Optional[str] = Field(
        default="upload_file", description="数据源类型"
    )
    indexing_technique: Optional[str] = Field(
        default="high_quality", description="索引技术"
    )
    created_by: Optional[str] = Field(description="创建者ID")
    created_at: Optional[int] = Field(description="创建时间戳")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class Document(BaseModel):
    """文档Schema

    Attributes:
        id: 文档ID
        position: 文档位置
        data_source_type: 数据源类型
        data_source_info: 数据源信息
        data_source_detail_dict: 数据源详细信息
        dataset_process_rule_id: 数据集处理规则ID
        name: 文档名称
        created_from: 创建来源
        created_by: 创建者ID
        created_at: 创建时间戳
        tokens: 文档token数
        indexing_status: 索引状态
        error: 错误信息
        enabled: 是否启用
        disabled_at: 禁用时间
        disabled_by: 禁用者
        archived: 是否归档
        display_status: 显示状态
        word_count: 字数统计
        hit_count: 命中次数
        doc_form: 文档格式
        doc_metadata: 文档元数据
    """

    id: str = Field(description="文档ID")
    position: int = Field(description="文档位置")
    data_source_type:  Optional[str] = Field(default="upload_file", description="数据源类型")
    data_source_info: Optional[dict] = Field(default=None, description="数据源信息")
    data_source_detail_dict: Optional[DataSourceDetailDict] = Field(default=None, description="数据源详细信息")
    dataset_process_rule_id: Optional[str] = Field(default=None, description="数据集处理规则ID")
    name: str = Field(description="文档名称")
    created_from:  Optional[str] = Field(description="创建来源")
    created_by: Optional[str] = Field(default="", description="创建者ID")
    created_at: Optional[int] = Field(default=0, description="创建时间戳")
    tokens: Optional[int] = Field(default=0, description="文档token数")
    indexing_status: Optional[str] = Field(default="waiting", description="索引状态")
    error: Optional[str] = Field(default=None, description="错误信息")
    enabled: Optional[bool] = Field(default=True, description="是否启用")
    disabled_at: Optional[int] = Field(default=None, description="禁用时间")
    disabled_by: Optional[str] = Field(default=None, description="禁用者")
    archived: Optional[bool] = Field(default=False, description="是否归档")
    display_status: Optional[str] = Field(default="queuing", description="显示状态")
    word_count: Optional[int] = Field(default=0, description="字数统计")
    hit_count: Optional[int] = Field(default=0, description="命中次数")
    doc_form: Optional[str] = Field(default="text_model", description="文档格式")
    doc_metadata: Optional[Any] = Field(default=None, description="文档元数据")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DataSetCreateResponse(BaseModel):
    """数据集创建响应Schema

    Attributes:
        dataset: 数据集
        documents: 文档列表
    """

    dataset: DataSetInCreate = Field(description="数据集")
    documents: List[Document] = Field(description="文档列表")
    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DataSetInList(BaseModel):
    """数据集列表Schema

    Attributes:
        id: 数据集ID
        name: 数据集名称
        description: 数据集描述
        permission: 数据集权限
        data_source_type: 数据源类型
        indexing_technique: 索引技术
        app_count: 应用数量
        document_count: 文档数量
        word_count: 字数统计
        created_by: 创建者ID
        created_at: 创建时间戳
        updated_by: 更新者ID
        updated_at: 更新时间戳
        tags: 数据集标签
    """

    id: str = Field(description="数据集ID")
    name: str = Field(description="数据集名称")
    description: Optional[str] = Field(default=None, description="数据集描述")
    permission: Optional[str] = Field(default="only_me", description="数据集权限")
    data_source_type: Optional[str] = Field(default=None, description="数据源类型")
    indexing_technique: Optional[str] = Field(default=None, description="索引技术")
    app_count: Optional[int] = Field(default=0, description="应用数量")
    document_count: Optional[int] = Field(default=0, description="文档数量")
    word_count: Optional[int] = Field(default=0, description="字数统计")
    created_by: Optional[str] = Field(default="", description="创建者ID")
    created_at: Optional[int] = Field(default=0, description="创建时间戳")
    updated_by: Optional[str] = Field(default="", description="更新者ID")
    updated_at: Optional[int] = Field(default=0, description="更新时间戳")
    tags: Optional[List[Tag]] = Field(default=None, description="数据集标签")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DataSetList(BaseModel):
    """知识库列表Schema

    Attributes:
        data: 知识库列表
        total: 知识库总数
        has_more: 是否有更多知识库
        limit: 每页数量
        page: 当前页码
    """

    data: List[DataSetInList] = Field(default_factory=list, description="知识库列表")
    total: int = Field(default=0, description="知识库总数")
    has_more: bool = Field(default=False, description="是否有更多知识库")
    limit: int = Field(default=20, description="每页数量")
    page: int = Field(default=1, description="当前页码")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentCreateByTextPayload(BaseModel):
    """通过文本创建文档请求Schema

    Attributes:
        document: 文档信息
        batch: 批次ID
    """

    document: dict = Field(
        default={
            "id": "",
            "position": 1,
            "data_source_type": "upload_file",
            "data_source_info": {
                "upload_file_id": ""
            },
            "dataset_process_rule_id": "",
            "name": "text.txt",
            "created_from": "api",
            "created_by": "",
            "created_at": 0,
            "tokens": 0,
            "indexing_status": "waiting",
            "error": None,
            "enabled": True,
            "disabled_at": None,
            "disabled_by": None,
            "archived": False,
            "display_status": "queuing",
            "word_count": 0,
            "hit_count": 0,
            "doc_form": "text_model"
        },
        description="文档信息"
    )
    batch: str = Field(default="", description="批次ID")
    content: Optional[str] = Field(description="文档内容")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentCreateByTextResponse(BaseModel):
    """通过文本创建文档响应Schema

    Attributes:
        document: 文档信息
    """

    document: Document = Field(description="文档信息")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentCreateByFilePayload(BaseModel):
    """通过文件创建文档请求Schema

    Attributes:
        document: 文档信息
        batch: 批次ID
    """

    document: dict = Field(
        default={
            "id": "",
            "position": 1,
            "data_source_type": "upload_file",
            "data_source_info": {
                "upload_file_id": ""
            },
            "dataset_process_rule_id": "",
            "name": "file.txt",
            "created_from": "api",
            "created_by": "",
            "created_at": 0,
            "tokens": 0,
            "indexing_status": "waiting",
            "error": None,
            "enabled": True,
            "disabled_at": None,
            "disabled_by": None,
            "archived": False,
            "display_status": "queuing",
            "word_count": 0,
            "hit_count": 0,
            "doc_form": "text_model"
        },
        description="文档信息"
    )
    batch: str = Field(default="", description="批次ID")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentCreateByFileResponse(BaseModel):
    """通过文件创建文档响应Schema

    Attributes:
        document: 文档信息
    """

    document: Document = Field(description="文档信息")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class EmptyDataSetCreatePayload(BaseModel):
    """创建空知识库请求Schema

    Attributes:
        name: 知识库名称
        description: 知识库描述
        permission: 知识库权限
        provider: 提供商
    """

    name: str = Field(description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    permission: Optional[str] = Field(default="only_me", description="知识库权限")
    provider: Optional[str] = Field(default="vendor", description="提供商")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class EmptyDataSetCreateResponse(BaseModel):
    """创建空知识库响应Schema

    Attributes:
        id: 知识库ID
        name: 知识库名称
        description: 知识库描述
        provider: 提供商
        permission: 知识库权限
        data_source_type: 数据源类型
        indexing_technique: 索引技术
        app_count: 应用数量
        document_count: 文档数量
        word_count: 字数统计
        created_by: 创建者ID
        created_at: 创建时间戳
        updated_by: 更新者ID
        updated_at: 更新时间戳
        embedding_model: 嵌入模型
        embedding_model_provider: 嵌入模型提供商
        embedding_available: 嵌入是否可用
    """

    id: str = Field(description="知识库ID")
    name: str = Field(description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    provider: Optional[str] = Field(default="vendor", description="提供商")
    permission: Optional[str] = Field(default="only_me", description="知识库权限")
    data_source_type: Optional[str] = Field(default=None, description="数据源类型")
    indexing_technique: Optional[str] = Field(default=None, description="索引技术")
    app_count: Optional[int] = Field(default=0, description="应用数量")
    document_count:  Optional[int] = Field(default=0, description="文档数量")
    word_count:  Optional[int] = Field(default=0, description="字数统计")
    created_by: Optional[str] = Field(default="", description="创建者ID")
    created_at: Optional[int] = Field(default=0, description="创建时间戳")
    updated_by: Optional[str] = Field(default="", description="更新者ID")
    updated_at: Optional[int] = Field(default=0, description="更新时间戳")
    embedding_model: Optional[str] = Field(default=None, description="嵌入模型")
    embedding_model_provider: Optional[str] = Field(default=None, description="嵌入模型提供商")
    embedding_available: Optional[bool] = Field(default=None, description="嵌入是否可用")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class RetrievalModelDictReranking(BaseModel):
    """检索模型重排序配置Schema

    Attributes:
        reranking_provider_name: 重排序提供商名称
        reranking_model_name: 重排序模型名称
    """

    reranking_provider_name: str = Field(default="", description="重排序提供商名称")
    reranking_model_name: str = Field(default="", description="重排序模型名称")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class RetrievalModelDict(BaseModel):
    """检索模型配置Schema

    Attributes:
        search_method: 搜索方法
        reranking_enable: 是否启用重排序
        reranking_mode: 重排序模式
        reranking_model: 重排序模型配置
        weights: 权重配置
        top_k: 返回结果数量
        score_threshold_enabled: 是否启用分数阈值
        score_threshold: 分数阈值
    """

    search_method: str = Field(default="hybrid_search", description="搜索方法")
    reranking_enable: bool = Field(default=False, description="是否启用重排序")
    reranking_mode: Optional[str] = Field(default=None, description="重排序模式")
    reranking_model: RetrievalModelDictReranking = Field(
        default=RetrievalModelDictReranking(), description="重排序模型配置"
    )
    weights: Optional[dict] = Field(default=None, description="权重配置")
    top_k: int = Field(default=2, description="返回结果数量")
    score_threshold_enabled: bool = Field(default=False, description="是否启用分数阈值")
    score_threshold: Optional[float] = Field(default=None, description="分数阈值")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class ExternalKnowledgeInfo(BaseModel):
    """外部知识信息Schema

    Attributes:
        external_knowledge_id: 外部知识ID
        external_knowledge_api_id: 外部知识API ID
        external_knowledge_api_name: 外部知识API名称
        external_knowledge_api_endpoint: 外部知识API端点
    """

    external_knowledge_id: Optional[str] = Field(default=None, description="外部知识ID")
    external_knowledge_api_id: Optional[str] = Field(default=None, description="外部知识API ID")
    external_knowledge_api_name: Optional[str] = Field(default=None, description="外部知识API名称")
    external_knowledge_api_endpoint: Optional[str] = Field(default=None, description="外部知识API端点")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class ExternalRetrievalModel(BaseModel):
    """外部检索模型Schema

    Attributes:
        top_k: 返回结果数量
        score_threshold: 分数阈值
        score_threshold_enabled: 是否启用分数阈值
    """

    top_k: int = Field(default=2, description="返回结果数量")
    score_threshold: float = Field(default=0.0, description="分数阈值")
    score_threshold_enabled: Optional[bool] = Field(default=None, description="是否启用分数阈值")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DataSetDetail(BaseModel):
    """知识库详情Schema

    Attributes:
        id: 知识库ID
        name: 知识库名称
        description: 知识库描述
        provider: 提供商
        permission: 知识库权限
        data_source_type: 数据源类型
        indexing_technique: 索引技术
        app_count: 应用数量
        document_count: 文档数量
        word_count: 字数统计
        created_by: 创建者ID
        created_at: 创建时间戳
        updated_by: 更新者ID
        updated_at: 更新时间戳
        embedding_model: 嵌入模型
        embedding_model_provider: 嵌入模型提供商
        embedding_available: 嵌入是否可用
        retrieval_model_dict: 检索模型配置
        tags: 标签列表
        doc_form: 文档格式
        external_knowledge_info: 外部知识信息
        external_retrieval_model: 外部检索模型
    """

    id: str = Field(description="知识库ID")
    name: str = Field(description="知识库名称")
    description: Optional[str] = Field(default="", description="知识库描述")
    provider: Optional[str] = Field(description="提供商")
    permission: Optional[str] = Field(description="知识库权限")
    data_source_type: Optional[str] = Field(default=None, description="数据源类型")
    indexing_technique: Optional[str] = Field(default=None, description="索引技术")
    app_count: Optional[int] = Field(default=0, description="应用数量")
    document_count: Optional[int] = Field(default=0, description="文档数量")
    word_count: Optional[int] = Field(default=0, description="字数统计")
    created_by: Optional[str] = Field(default="", description="创建者ID")
    created_at: Optional[int] = Field(default=None, description="创建时间戳")
    updated_by: Optional[str] = Field(default="", description="更新者ID")
    updated_at: Optional[int] = Field(default=None, description="更新时间戳")
    embedding_model: Optional[str] = Field(default=None, description="嵌入模型")
    embedding_model_provider: Optional[str] = Field(default=None, description="嵌入模型提供商")
    embedding_available: Optional[bool] = Field(default=None, description="嵌入是否可用")
    retrieval_model_dict: Optional[RetrievalModelDict] = Field(default=None, description="检索模型配置")
    tags: List[Tag] = Field(default_factory=list, description="标签列表")
    doc_form: Optional[str] = Field(default=None, description="文档格式")
    external_knowledge_info: Optional[ExternalKnowledgeInfo] = Field(default=None, description="外部知识信息")
    external_retrieval_model: Optional[ExternalRetrievalModel] = Field(default=None, description="外部检索模型")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentUpdateByTextPayload(BaseModel):
    """通过文本更新文档请求Schema

    Attributes:
        name: 文档名称
        text: 文档内容
    """

    name: str = Field(description="文档名称")
    text: str = Field(description="文档内容")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentUpdateByTextResponse(BaseModel):
    """通过文本更新文档响应Schema

    Attributes:
        document: 文档信息
        batch: 批次ID
    """

    document: Document = Field(description="文档信息")
    batch: str = Field(default="", description="批次ID")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentUpdateByFileResponse(BaseModel):
    """通过文件更新文档响应Schema

    Attributes:
        document: 文档信息
        batch: 批次ID
    """

    document: Document = Field(description="文档信息")
    batch: str = Field(default="", description="批次ID")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentIndexingStatus(BaseModel):
    """文档索引状态Schema

    Attributes:
        id: 文档ID
        indexing_status: 索引状态
        processing_started_at: 处理开始时间
        parsing_completed_at: 解析完成时间
        cleaning_completed_at: 清洗完成时间
        splitting_completed_at: 分割完成时间
        completed_at: 完成时间
        paused_at: 暂停时间
        error: 错误信息
        stopped_at: 停止时间
        completed_segments: 已完成分段数
        total_segments: 总分段数
    """

    id: str = Field(description="文档ID")
    indexing_status: Optional[str] = Field(description="索引状态")
    processing_started_at: Optional[float] = Field(default=None, description="处理开始时间")
    parsing_completed_at: Optional[float] = Field(default=None, description="解析完成时间")
    cleaning_completed_at: Optional[float] = Field(default=None, description="清洗完成时间")
    splitting_completed_at: Optional[float] = Field(default=None, description="分割完成时间")
    completed_at: Optional[float] = Field(default=None, description="完成时间")
    paused_at: Optional[float] = Field(default=None, description="暂停时间")
    error: Optional[str] = Field(default=None, description="错误信息")
    stopped_at: Optional[float] = Field(default=None, description="停止时间")
    completed_segments: Optional[int] = Field(default=0, description="已完成分段数")
    total_segments: Optional[int] = Field(default=0, description="总分段数")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentIndexingStatusResponse(BaseModel):
    """文档索引状态响应Schema

    Attributes:
        data: 文档索引状态列表
    """

    data: List[DocumentIndexingStatus] = Field(default_factory=list, description="文档索引状态列表")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentInList(BaseModel):
    """文档列表项Schema

    Attributes:
        id: 文档ID
        position: 文档位置
        data_source_type: 数据源类型
        data_source_info: 数据源信息
        dataset_process_rule_id: 数据集处理规则ID
        name: 文档名称
        created_from: 创建来源
        created_by: 创建者ID
        created_at: 创建时间戳
        tokens: 文档token数
        indexing_status: 索引状态
        error: 错误信息
        enabled: 是否启用
        disabled_at: 禁用时间
        disabled_by: 禁用者
        archived: 是否归档
    """

    id: str = Field(description="文档ID")
    position: Optional[int] = Field(description="文档位置")
    data_source_type: Optional[str] = Field(description="数据源类型")
    data_source_info: Optional[dict] = Field(default=None, description="数据源信息")
    dataset_process_rule_id: Optional[str] = Field(default=None, description="数据集处理规则ID")
    name: str = Field(description="文档名称")
    created_from: str = Field(description="创建来源")
    created_by: Optional[str] = Field(default="", description="创建者ID")
    created_at: int = Field(description="创建时间戳")
    tokens: Optional[int] = Field(default=0, description="文档token数")
    indexing_status: Optional[str] = Field(description="索引状态")
    error: Optional[str] = Field(default=None, description="错误信息")
    enabled: Optional[bool] = Field(description="是否启用")
    disabled_at: Optional[int] = Field(default=None, description="禁用时间")
    disabled_by: Optional[str] = Field(default=None, description="禁用者")
    archived: Optional[bool] = Field(description="是否归档")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentList(BaseModel):
    """文档列表Schema

    Attributes:
        data: 文档列表
        has_more: 是否有更多
        limit: 每页数量
        total: 总数
        page: 当前页码
    """

    data: List[Document] = Field(default_factory=list, description="文档列表")
    has_more: bool = Field(default=False, description="是否有更多")
    limit: int = Field(default=20, description="每页数量")
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页码")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentSegment(BaseModel):
    """文档分段Schema

    Attributes:
        content: 分段内容
        answer: 分段答案
        keywords: 关键词列表
    """

    content: Optional[str] = Field(description="分段内容")
    answer: Optional[str] = Field(default=None, description="分段答案")
    keywords: Optional[List[str]] = Field(default=None, description="关键词列表")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentSegmentCreatePayload(BaseModel):
    """创建文档分段请求Schema

    Attributes:
        segments: 分段列表
    """

    segments: List[DocumentSegment] = Field(description="分段列表")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentSegmentDetail(BaseModel):
    """文档分段详情Schema

    Attributes:
        id: 分段ID
        position: 分段位置
        document_id: 文档ID
        content: 分段内容
        answer: 分段答案
        word_count: 字数统计
        tokens: token数
        keywords: 关键词列表
        index_node_id: 索引节点ID
        index_node_hash: 索引节点哈希
        hit_count: 命中次数
        enabled: 是否启用
        disabled_at: 禁用时间
        disabled_by: 禁用者
        status: 状态
        created_by: 创建者ID
        created_at: 创建时间戳
        indexing_at: 索引时间
        completed_at: 完成时间
        error: 错误信息
        stopped_at: 停止时间
    """

    id: str = Field(description="分段ID")
    position: int = Field(description="分段位置")
    document_id: str = Field(description="文档ID")
    content: str = Field(description="分段内容")
    answer: Optional[str] = Field(default=None, description="分段答案")
    word_count: int = Field(description="字数统计")
    tokens: Optional[int] = Field(default=0, description="token数")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    index_node_id: str = Field(description="索引节点ID")
    index_node_hash: str = Field(description="索引节点哈希")
    hit_count: int = Field(description="命中次数")
    enabled: bool = Field(description="是否启用")
    disabled_at: Optional[int] = Field(default=None, description="禁用时间")
    disabled_by: Optional[str] = Field(default=None, description="禁用者")
    status: str = Field(description="状态")
    created_by: Optional[str] = Field(default="", description="创建者ID")
    created_at: int = Field(description="创建时间戳")
    indexing_at: int = Field(description="索引时间")
    completed_at: int = Field(description="完成时间")
    error: Optional[str] = Field(default=None, description="错误信息")
    stopped_at: Optional[int] = Field(default=None, description="停止时间")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentSegmentResponse(BaseModel):
    """文档分段响应Schema

    Attributes:
        data: 分段列表
        doc_form: 文档格式
    """

    data: List[DocumentSegmentDetail] = Field(default_factory=list, description="分段列表")
    doc_form: str = Field(description="文档格式")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentSegmentUpdatePayload(BaseModel):
    """更新文档分段请求Schema

    Attributes:
        segment: 分段信息
    """

    segment: dict = Field(description="分段信息")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class MetadataField(BaseModel):
    """元数据字段Schema

    Attributes:
        id: 元数据字段ID
        type: 元数据字段类型
        name: 元数据字段名称
        use_count: 使用次数
    """

    id: str = Field(description="元数据字段ID")
    type: str = Field(description="元数据字段类型")
    name: str = Field(description="元数据字段名称")
    use_count: Optional[int] = Field(default=None, description="使用次数")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class MetadataCreatePayload(BaseModel):
    """创建元数据字段请求Schema

    Attributes:
        type: 元数据字段类型
        name: 元数据字段名称
    """

    type: str = Field(description="元数据字段类型")
    name: str = Field(description="元数据字段名称")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class MetadataUpdatePayload(BaseModel):
    """更新元数据字段请求Schema

    Attributes:
        name: 元数据字段名称
    """

    name: str = Field(description="元数据字段名称")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class MetadataListResponse(BaseModel):
    """元数据列表响应Schema

    Attributes:
        doc_metadata: 元数据字段列表
        built_in_field_enabled: 是否启用内置字段
    """

    doc_metadata: List[MetadataField] = Field(default_factory=list, description="元数据字段列表")
    built_in_field_enabled: bool = Field(default=True, description="是否启用内置字段")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentMetadataItem(BaseModel):
    """文档元数据项Schema

    Attributes:
        id: 元数据字段ID
        value: 元数据值
        name: 元数据字段名称
    """

    id: str = Field(description="元数据字段ID")
    value: str = Field(description="元数据值")
    name: str = Field(description="元数据字段名称")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentMetadataOperation(BaseModel):
    """文档元数据操作Schema

    Attributes:
        document_id: 文档ID
        metadata_list: 元数据列表
    """

    document_id: str = Field(description="文档ID")
    metadata_list: List[DocumentMetadataItem] = Field(default_factory=list, description="元数据列表")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentMetadataUpdatePayload(BaseModel):
    """文档元数据更新请求Schema

    Attributes:
        operation_data: 操作数据
    """

    operation_data: List[DocumentMetadataOperation] = Field(default_factory=list, description="操作数据")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentRenamePayload(BaseModel):
    """文档重命名请求Schema

    Attributes:
        name: 新文档名称
    """

    name: str = Field(description="新文档名称")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentRenameResponse(BaseModel):
    """文档重命名响应Schema

    Attributes:
        id: 文档ID
        name: 新文档名称
    """

    id: str = Field(description="文档ID")
    name: str = Field(description="新文档名称")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentUploadPayload(BaseModel):
    """文档上传请求Schema

    Attributes:
        data_source: 数据源配置
    """

    data_source: DataSource = Field(description="数据源配置")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentUploadResponse(BaseModel):
    """文档上传响应Schema

    Attributes:
        documents: 文档列表
    """

    documents: List[Document] = Field(default_factory=list, description="文档列表")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentCreateByFileIdsPayload(BaseModel):
    """通过文件ID列表创建文档请求Schema

    Attributes:
        data_source: 数据源配置，包含文件ID列表
        indexing_technique: 索引技术
        process_rule: 处理规则
        doc_form: 文档格式
        doc_language: 文档语言
        retrieval_model: 检索模型配置
        embedding_model: 嵌入模型
        embedding_model_provider: 嵌入模型提供商
    """

    data_source: Dict[str, Any] = Field(
        description="数据源配置，包含文件ID列表"
    )
    indexing_technique: str = Field(default="high_quality", description="索引技术")
    process_rule: Dict[str, Any] = Field(
        default={
            "rules": {
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": False}
                ],
                "segmentation": {
                    "separator": "\n\n",
                    "max_tokens": 1024,
                    "chunk_overlap": 50
                }
            },
            "mode": "custom"
        },
        description="处理规则"
    )
    doc_form: str = Field(default="text_model", description="文档格式")
    doc_language: str = Field(default="Chinese Simplified", description="文档语言")
    retrieval_model: Dict[str, Any] = Field(
        default={
            "search_method": "hybrid_search",
            "reranking_enable": True,
            "reranking_mode": "reranking_model",
            "reranking_model": {
                "reranking_provider_name": "langgenius/tongyi/tongyi",
                "reranking_model_name": "gte-rerank"
            },
            "weights": {
                "weight_type": "customized",
                "keyword_setting": {
                    "keyword_weight": 0.3
                },
                "vector_setting": {
                    "vector_weight": 0.7,
                    "embedding_model_name": "",
                    "embedding_provider_name": ""
                }
            },
            "top_k": 3,
            "score_threshold_enabled": False,
            "score_threshold": 0.5
        },
        description="检索模型配置"
    )
    embedding_model: str = Field(
        default="text-embedding-3-large", description="嵌入模型"
    )
    embedding_model_provider: str = Field(
        default="langgenius/openai/openai", description="嵌入模型提供商"
    )

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


class DocumentCreateByFileIdsResponse(BaseModel):
    """通过文件ID列表创建文档响应Schema

    Attributes:
        dataset: 数据集信息
        documents: 文档列表
        batch: 批次ID
    """

    dataset: Optional[DataSetInCreate] = Field(default=None, description="数据集信息")
    documents: List[Document] = Field(default_factory=list, description="文档列表")
    batch: Optional[str] = Field(default=None, description="批次ID")

    # Pydantic V2 配置
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": (),
    }


__all__ = [
    "KeywordSetting",
    "VectorSetting",
    "Weights",
    "RerankingModel",
    "RetrievalModel",
    "ProcessRule",
    "FileInfoList",
    "InfoList",
    "UploadFileDetail",
    "DataSourceDetailDict",
    "DataSource",
    "DataSetCreatePayloads",
    "DataSetCreateResponse",
    "DataSetInList",
    "Document",
    "DataSetInCreate",
    "DataSetList",
    "DocumentCreateByTextPayload",
    "DocumentCreateByTextResponse",
    "DocumentCreateByFilePayload",
    "DocumentCreateByFileResponse",
    "DocumentCreateByFileIdsPayload",
    "DocumentCreateByFileIdsResponse",
    "EmptyDataSetCreatePayload",
    "EmptyDataSetCreateResponse",
    "RetrievalModelDictReranking",
    "RetrievalModelDict",
    "ExternalKnowledgeInfo",
    "ExternalRetrievalModel",
    "DataSetDetail",
    "DocumentUpdateByTextPayload",
    "DocumentUpdateByTextResponse",
    "DocumentUpdateByFileResponse",
    "DocumentIndexingStatus",
    "DocumentIndexingStatusResponse",
    "DocumentInList",
    "DocumentList",
    "DocumentSegment",
    "DocumentSegmentCreatePayload",
    "DocumentSegmentDetail",
    "DocumentSegmentResponse",
    "DocumentSegmentUpdatePayload",
    "MetadataField",
    "MetadataCreatePayload",
    "MetadataUpdatePayload",
    "MetadataListResponse",
    "DocumentMetadataItem",
    "DocumentMetadataOperation",
    "DocumentMetadataUpdatePayload",
    "DocumentRenamePayload",
    "DocumentRenameResponse",
]
