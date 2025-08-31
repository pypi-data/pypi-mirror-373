from typing import List, Optional, BinaryIO, Dict, Any, Literal

from dify.http import AdminClient
from .schemas import (
    DataSetCreatePayloads,
    DataSetCreateResponse,
    DataSetList,
    DocumentCreateByTextPayload,
    DocumentCreateByTextResponse,
    DocumentCreateByFilePayload,
    DocumentCreateByFileResponse,
    DocumentCreateByFileIdsPayload,
    DocumentCreateByFileIdsResponse,
    EmptyDataSetCreatePayload,
    EmptyDataSetCreateResponse,
    DataSetDetail,
    DocumentUpdateByTextPayload,
    DocumentUpdateByTextResponse,
    DocumentUpdateByFileResponse,
    DocumentIndexingStatusResponse,
    DocumentList,
    DocumentSegmentCreatePayload,
    DocumentSegmentResponse,
    DocumentSegmentUpdatePayload,
    MetadataCreatePayload,
    MetadataField,
    MetadataUpdatePayload,
    MetadataListResponse,
    DocumentMetadataUpdatePayload,
    DocumentRenamePayload,
    DocumentRenameResponse
)


class DifyDataset:
    def __init__(self, admin_client: AdminClient) -> None:
        self.admin_client = admin_client

    async def create(self, payload: DataSetCreatePayloads) -> DataSetCreateResponse:
        """创建新的知识库

        Args:
            payload: 知识库创建参数

        Returns:
            DataSetCreateResponse: 知识库创建响应对象，包含知识库信息和文档列表

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not payload:
            raise ValueError("知识库创建参数不能为空")

        # 发送POST请求创建知识库
        response_data = await self.admin_client.post(
            "/datasets/init",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )

        # 返回知识库创建响应对象
        return DataSetCreateResponse(**response_data)

    async def find_list(
        self,
        page: int = 1,
        limit: int = 30,
        include_all: bool = False,
        tag_ids: Optional[List[str]] = None
    ) -> DataSetList:
        """查询知识库列表

        Args:
            page: 页码，默认为1
            limit: 每页数量，默认为30
            include_all: 是否包含所有知识库，默认为False
            tag_ids: 标签ID列表，用于筛选特定标签的知识库，默认为None

        Returns:
            DataSetList: 知识库列表对象，包含知识库列表、总数和是否有更多

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if page < 1:
            raise ValueError("页码不能小于1")

        if limit < 1:
            raise ValueError("每页数量不能小于1")

        # 准备查询参数
        params = {
            "page": page,
            "limit": limit,
            "include_all": str(include_all).lower()
        }

        # 如果提供了标签ID列表，则添加到查询参数中
        if tag_ids:
            params["tag_ids"] = ",".join(tag_ids)

        # 发送GET请求查询知识库列表
        response_data = await self.admin_client.get("/datasets", params=params)

        # 返回知识库列表对象
        return DataSetList(**response_data)

    async def delete(self, dataset_id: str) -> bool:
        """删除知识库

        Args:
            dataset_id: 知识库ID

        Returns:
            bool: 删除成功返回True

        Raises:
            ValueError: 当知识库ID为空时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        # 发送DELETE请求删除知识库
        await self.admin_client.delete(f"/datasets/{dataset_id}")

        # 根据curl命令返回204状态码，表示删除成功
        return True

    async def create_document_by_text(
        self,
        dataset_id: str,
        payload: DocumentCreateByTextPayload
    ) -> DocumentCreateByTextResponse:
        """通过文本创建文档

        Args:
            dataset_id: 知识库ID
            payload: 文档创建参数，包含文档信息和文本内容

        Returns:
            DocumentCreateByTextResponse: 文档创建响应对象，包含创建的文档信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not payload:
            raise ValueError("文档创建参数不能为空")

        if not payload.content:
            raise ValueError("文档内容不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送POST请求创建文档
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/document/create-by-text",
            json=request_data
        )

        # 返回文档创建响应对象
        return DocumentCreateByTextResponse(**response_data)

    async def create_document_by_file(
        self,
        dataset_id: str,
        payload: DocumentCreateByFilePayload,
        file: BinaryIO,
        file_name: str
    ) -> DocumentCreateByFileResponse:
        """通过文件创建文档

        Args:
            dataset_id: 知识库ID
            payload: 文档创建参数，包含文档信息
            file: 文件对象，可以是打开的文件句柄
            file_name: 文件名

        Returns:
            DocumentCreateByFileResponse: 文档创建响应对象，包含创建的文档信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not payload:
            raise ValueError("文档创建参数不能为空")

        if not file:
            raise ValueError("文件不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 准备文件数据
        files = {
            "file": (file_name, file, "application/octet-stream")
        }

        # 发送POST请求创建文档
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/document/create-by-file",
            json=request_data,
            files=files
        )

        # 返回文档创建响应对象
        return DocumentCreateByFileResponse(**response_data)

    async def create_empty(self, payload: EmptyDataSetCreatePayload) -> EmptyDataSetCreateResponse:
        """创建空知识库

        Args:
            payload: 知识库创建参数，包含知识库名称、描述等信息

        Returns:
            EmptyDataSetCreateResponse: 知识库创建响应对象，包含创建的知识库信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not payload:
            raise ValueError("知识库创建参数不能为空")

        if not payload.name:
            raise ValueError("知识库名称不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送POST请求创建知识库
        response_data = await self.admin_client.post(
            "/datasets",
            json=request_data
        )

        # 返回值格式示例:
        # {
        #   "id": "",
        #   "name": "name",
        #   "description": null,
        #   "provider": "vendor",
        #   "permission": "only_me",
        #   "data_source_type": null,
        #   "indexing_technique": null,
        #   "app_count": 0,
        #   "document_count": 0,
        #   "word_count": 0,
        #   "created_by": "",
        #   "created_at": 1695636173,
        #   "updated_by": "",
        #   "updated_at": 1695636173,
        #   "embedding_model": null,
        #   "embedding_model_provider": null,
        #   "embedding_available": null
        # }

        # 返回知识库创建响应对象
        return EmptyDataSetCreateResponse(**response_data)

    async def get_detail(self, dataset_id: str) -> DataSetDetail:
        """获取知识库详情

        Args:
            dataset_id: 知识库ID

        Returns:
            DataSetDetail: 知识库详情对象，包含知识库的详细信息

        Raises:
            ValueError: 当知识库ID为空时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        # 发送GET请求获取知识库详情
        response_data = await self.admin_client.get(f"/datasets/{dataset_id}")

        # 返回知识库详情对象
        return DataSetDetail(**response_data)

    async def update(self, dataset_id: str, payload: dict) -> dict:
        """更新知识库信息

        Args:
            dataset_id: 知识库ID
            payload: 更新参数，可包含name和description

        Returns:
            dict: 更新结果

        Raises:
            ValueError: 当知识库ID为空或参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not payload:
            raise ValueError("更新参数不能为空")

        # 验证payload中至少包含name或description
        if "name" not in payload and "description" not in payload:
            raise ValueError("更新参数必须包含name或description")

        # 发送PATCH请求更新知识库
        response_data = await self.admin_client.patch(
            f"/datasets/{dataset_id}",
            json=payload
        )

        # 返回更新结果
        return response_data

    async def update_document_by_text(
        self,
        dataset_id: str,
        document_id: str,
        payload: DocumentUpdateByTextPayload
    ) -> DocumentUpdateByTextResponse:
        """通过文本更新文档

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            payload: 文档更新参数，包含文档名称和文本内容

        Returns:
            DocumentUpdateByTextResponse: 文档更新响应对象，包含更新后的文档信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_id:
            raise ValueError("文档ID不能为空")

        if not payload:
            raise ValueError("文档更新参数不能为空")

        if not payload.text:
            raise ValueError("文档内容不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送POST请求更新文档
        response_data = await self.admin_client.patch(
            f"/datasets/{dataset_id}/documents/{document_id}/update_by_text",
            json=request_data
        )

        # 返回文档更新响应对象
        return DocumentUpdateByTextResponse(**response_data)

    async def update_document_by_file(
        self,
        dataset_id: str,
        document_id: str,
        file: BinaryIO,
        file_name: str,
        data: Optional[Dict[str, Any]] = None
    ) -> DocumentUpdateByFileResponse:
        """通过文件更新文档

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            file: 文件对象，可以是打开的文件句柄
            file_name: 文件名
            data: 额外的数据，如索引技术、处理规则等

        Returns:
            DocumentUpdateByFileResponse: 文档更新响应对象，包含更新后的文档信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_id:
            raise ValueError("文档ID不能为空")

        if not file:
            raise ValueError("文件不能为空")

        # 准备文件数据
        files = {
            "file": (file_name, file, "application/octet-stream")
        }

        # 准备表单数据
        form_data = {}
        if data:
            form_data["data"] = str(data)

        # 发送POST请求更新文档
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/documents/{document_id}/update_by_file",
            files=files,
            data=form_data
        )

        # 返回文档更新响应对象
        return DocumentUpdateByFileResponse(**response_data)

    async def get_document_indexing_status(
        self,
        dataset_id: str,
        batch: str
    ) -> DocumentIndexingStatusResponse:
        """获取文档索引状态

        Args:
            dataset_id: 知识库ID
            batch: 批次ID

        Returns:
            DocumentIndexingStatusResponse: 文档索引状态响应对象，包含文档的索引状态信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not batch:
            raise ValueError("批次ID不能为空")

        # 发送GET请求获取文档索引状态
        response_data = await self.admin_client.get(
            f"/datasets/{dataset_id}/documents/{batch}/indexing-status"
        )

        # 返回文档索引状态响应对象
        return DocumentIndexingStatusResponse(**response_data)

    async def delete_document(self, dataset_id: str, document_id: str) -> bool:
        """删除文档

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            bool: 删除成功返回True

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_id:
            raise ValueError("文档ID不能为空")

        # 发送DELETE请求删除文档
        response_data = await self.admin_client.delete(
            f"/datasets/{dataset_id}/documents/{document_id}"
        )

        # 返回删除结果
        return response_data

    async def batch_delete_documents(self, dataset_id: str, document_ids: List[str]) -> Dict[str, Any]:
        """批量删除文档

        Args:
            dataset_id: 知识库ID
            document_ids: 文档ID列表

        Returns:
            Dict[str, Any]: 批量删除结果，包含成功和失败的文档ID

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_ids:
            raise ValueError("文档ID列表不能为空")

        # 准备查询参数
        params = {}
        # 对于每个文档ID，添加一个document_id参数
        # 这样URL会变成 /datasets/{dataset_id}/documents?document_id=id1&document_id=id2
        params["document_id"] = document_ids

        # 发送DELETE请求批量删除文档
        response_data = await self.admin_client.delete(
            f"/datasets/{dataset_id}/documents",
            params=params
        )

        # 返回批量删除结果
        return response_data

    async def get_document_list(
        self,
        dataset_id: str,
        page: int = 1,
        limit: int = 20
    ) -> DocumentList:
        """获取知识库文档列表

        Args:
            dataset_id: 知识库ID
            page: 页码，默认为1
            limit: 每页数量，默认为20

        Returns:
            DocumentList: 文档列表对象，包含文档列表、总数和是否有更多

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if page < 1:
            raise ValueError("页码不能小于1")

        if limit < 1:
            raise ValueError("每页数量不能小于1")

        # 准备查询参数
        params = {
            "page": page,
            "limit": limit
        }

        # 发送GET请求获取文档列表
        response_data = await self.admin_client.get(
            f"/datasets/{dataset_id}/documents",
            params=params
        )

        # 返回文档列表对象
        return DocumentList(**response_data)

    async def create_document_segments(
        self,
        dataset_id: str,
        document_id: str,
        payload: DocumentSegmentCreatePayload
    ) -> DocumentSegmentResponse:
        """新增文档分段

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            payload: 分段创建参数，包含分段列表

        Returns:
            DocumentSegmentResponse: 分段创建响应对象，包含创建的分段列表

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_id:
            raise ValueError("文档ID不能为空")

        if not payload or not payload.segments:
            raise ValueError("分段列表不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送POST请求创建分段
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/documents/{document_id}/segments",
            json=request_data
        )

        # 返回分段创建响应对象
        return DocumentSegmentResponse(**response_data)

    async def get_document_segments(
        self,
        dataset_id: str,
        document_id: str
    ) -> DocumentSegmentResponse:
        """查询文档分段

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            DocumentSegmentResponse: 分段查询响应对象，包含文档的分段列表

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_id:
            raise ValueError("文档ID不能为空")

        # 发送GET请求查询分段
        response_data = await self.admin_client.get(
            f"/datasets/{dataset_id}/documents/{document_id}/segments"
        )

        # 返回分段查询响应对象
        return DocumentSegmentResponse(**response_data)

    async def delete_document_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str
    ) -> bool:
        """删除文档分段

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID

        Returns:
            bool: 删除成功返回True

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_id:
            raise ValueError("文档ID不能为空")

        if not segment_id:
            raise ValueError("分段ID不能为空")

        # 发送DELETE请求删除分段
        response_data = await self.admin_client.delete(
            f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"
        )

        # 返回删除结果
        return response_data.get("result") == "success"

    async def update_document_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        payload: DocumentSegmentUpdatePayload
    ) -> DocumentSegmentResponse:
        """更新文档分段

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            segment_id: 分段ID
            payload: 分段更新参数，包含分段信息

        Returns:
            DocumentSegmentResponse: 分段更新响应对象，包含更新后的分段信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_id:
            raise ValueError("文档ID不能为空")

        if not segment_id:
            raise ValueError("分段ID不能为空")

        if not payload:
            raise ValueError("分段更新参数不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送POST请求更新分段
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}",
            json=request_data
        )

        # 返回分段更新响应对象
        return DocumentSegmentResponse(**response_data)

    async def get_metadata_list(self, dataset_id: str) -> MetadataListResponse:
        """获取知识库元数据列表

        Args:
            dataset_id: 知识库ID

        Returns:
            MetadataListResponse: 元数据列表响应对象，包含元数据字段列表和内置字段启用状态

        Raises:
            ValueError: 当知识库ID为空时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        # 发送GET请求获取元数据列表
        response_data = await self.admin_client.get(
            f"/datasets/{dataset_id}/metadata"
        )

        # 返回元数据列表响应对象
        return MetadataListResponse(**response_data)

    async def create_metadata(
        self,
        dataset_id: str,
        payload: MetadataCreatePayload
    ) -> MetadataField:
        """新增知识库元数据字段

        Args:
            dataset_id: 知识库ID
            payload: 元数据创建参数，包含字段类型和名称

        Returns:
            MetadataField: 元数据字段对象，包含创建的元数据字段信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not payload:
            raise ValueError("元数据创建参数不能为空")

        if not payload.name:
            raise ValueError("元数据字段名称不能为空")

        if not payload.type:
            raise ValueError("元数据字段类型不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送POST请求创建元数据字段
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/metadata",
            json=request_data
        )

        # 返回元数据字段对象
        return MetadataField(**response_data)

    async def update_metadata(
        self,
        dataset_id: str,
        metadata_id: str,
        payload: MetadataUpdatePayload
    ) -> MetadataField:
        """修改知识库元数据字段

        Args:
            dataset_id: 知识库ID
            metadata_id: 元数据字段ID
            payload: 元数据更新参数，包含字段名称

        Returns:
            MetadataField: 元数据字段对象，包含更新后的元数据字段信息

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not metadata_id:
            raise ValueError("元数据字段ID不能为空")

        if not payload:
            raise ValueError("元数据更新参数不能为空")

        if not payload.name:
            raise ValueError("元数据字段名称不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送PUT请求更新元数据字段
        response_data = await self.admin_client.put(
            f"/datasets/{dataset_id}/metadata/{metadata_id}",
            json=request_data
        )

        # 返回元数据字段对象
        return MetadataField(**response_data)

    async def delete_metadata(self, dataset_id: str, metadata_id: str) -> bool:
        """删除知识库元数据字段

        Args:
            dataset_id: 知识库ID
            metadata_id: 元数据字段ID

        Returns:
            bool: 删除成功返回True

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not metadata_id:
            raise ValueError("元数据字段ID不能为空")

        # 发送DELETE请求删除元数据字段
        response_data = await self.admin_client.delete(
            f"/datasets/{dataset_id}/metadata/{metadata_id}"
        )

        # 返回删除结果
        return response_data.get("result") == "success"

    async def toggle_built_in_metadata(
        self,
        dataset_id: str,
        action: Literal["enable", "disable"]
    ) -> bool:
        """启用/禁用知识库元数据中的内置字段

        Args:
            dataset_id: 知识库ID
            action: 操作类型，enable表示启用，disable表示禁用

        Returns:
            bool: 操作成功返回True

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if action not in ["enable", "disable"]:
            raise ValueError("操作类型必须为enable或disable")

        # 准备请求数据
        request_data = {
            "action": action
        }

        # 发送POST请求启用/禁用内置字段
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/metadata/built-in-field",
            json=request_data
        )

        # 返回操作结果
        return response_data.get("result") == "success"

    async def create_documents_by_file_ids(
        self,
        dataset_id: str,
        payload: DocumentCreateByFileIdsPayload
    ) -> DocumentCreateByFileIdsResponse:
        """通过文件ID列表创建文档

        Args:
            dataset_id: 知识库ID
            payload: 文档创建参数，包含文件ID列表和处理配置

        Returns:
            DocumentCreateByFileIdsResponse: 文档创建响应对象，包含操作结果

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not payload:
            raise ValueError("文档创建参数不能为空")

        if not payload.data_source:
            raise ValueError("数据源配置不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送POST请求创建文档
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/documents",
            json=request_data
        )

        # 返回文档创建响应对象
        return DocumentCreateByFileIdsResponse(**response_data)

    async def update_document_metadata(
        self,
        dataset_id: str,
        payload: DocumentMetadataUpdatePayload
    ) -> bool:
        """修改文档的元数据（赋值）

        Args:
            dataset_id: 知识库ID
            payload: 文档元数据更新参数，包含操作数据

        Returns:
            bool: 更新成功返回True

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not payload or not payload.operation_data:
            raise ValueError("文档元数据更新参数不能为空")

        # 准备请求数据
        request_data = payload.model_dump(by_alias=True, exclude_none=True)

        # 发送POST请求更新文档元数据
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/documents/metadata",
            json=request_data
        )

        # 返回更新结果
        if isinstance(response_data, dict):
            return response_data.get("result") == "success"
        elif isinstance(response_data, bool):
            return response_data
        elif isinstance(response_data, int):
            # 如果返回的是状态码，200表示成功
            return response_data == 200
        else:
            # 默认返回True，因为如果请求成功但没有明确的成功标志，我们认为操作成功
            return True

    async def enable_documents(
        self,
        dataset_id: str,
        document_ids: List[str]
    ) -> bool:
        """启用知识库文档

        Args:
            dataset_id: 知识库ID
            document_ids: 文档ID列表

        Returns:
            bool: 启用成功返回True

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_ids:
            raise ValueError("文档ID列表不能为空")

        # 准备查询参数
        params = {}
        for doc_id in document_ids:
            # 添加多个document_id参数
            if "document_id" not in params:
                params["document_id"] = []
            params["document_id"].append(doc_id)

        # 发送POST请求启用文档
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/documents/status/enable/batch",
            params=params
        )

        # 返回启用结果
        if isinstance(response_data, dict):
            return response_data.get("result") == "success"
        elif isinstance(response_data, bool):
            return response_data
        else:
            # 默认返回True，因为如果请求成功但没有明确的成功标志，我们认为操作成功
            return True

    async def disable_documents(
        self,
        dataset_id: str,
        document_ids: List[str]
    ) -> bool:
        """禁用知识库文档

        Args:
            dataset_id: 知识库ID
            document_ids: 文档ID列表

        Returns:
            bool: 禁用成功返回True

        Raises:
            ValueError: 当参数无效时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not dataset_id:
            raise ValueError("知识库ID不能为空")

        if not document_ids:
            raise ValueError("文档ID列表不能为空")

        # 准备查询参数
        params = {}
        for doc_id in document_ids:
            # 添加多个document_id参数
            if "document_id" not in params:
                params["document_id"] = []
            params["document_id"].append(doc_id)

        # 发送POST请求禁用文档
        response_data = await self.admin_client.post(
            f"/datasets/{dataset_id}/documents/status/disable/batch",
            params=params
        )

        # 返回禁用结果
        if isinstance(response_data, dict):
            return response_data.get("result") == "success"
        elif isinstance(response_data, bool):
            return response_data
        else:
            # 默认返回True，因为如果请求成功但没有明确的成功标志，我们认为操作成功
            return True

__all__ = ["DifyDataset"]
