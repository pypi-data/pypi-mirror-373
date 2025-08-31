from typing import List, Dict, Any

from dify.http import AdminClient
from .schemas import ToolProvider, Tool, ToolType


class DifyTool:
    def __init__(self, admin_client: AdminClient) -> None:
        self.admin_client = admin_client

    async def list_providers(self) -> List[ToolProvider]:
        """获取工具提供者列表

        Returns:
            List[ToolProvider]: 工具提供者对象列表

        Raises:
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        # 发送GET请求获取工具提供者列表
        response_data = await self.admin_client.get("/workspaces/current/tool-providers")

        # 将响应数据转换为ToolProvider对象列表
        return [ToolProvider(**provider_data) for provider_data in response_data]


    async def get_provider_tools(self, provider_id: str) -> List[Tool]:
        """获取特定工具提供者的工具列表

        Args:
            provider_id: 工具提供者ID

        Returns:
            List[Tool]: 工具对象列表

        Raises:
            ValueError: 当工具提供者ID为空时抛出
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        if not provider_id:
            raise ValueError("工具提供者ID不能为空")

        # 发送GET请求获取工具列表
        response_data = await self.admin_client.get(f"/workspaces/current/tool-provider/{provider_id}/tools")

        # 返回工具对象列表
        return [Tool(**tool_data) for tool_data in response_data]

    async def list_tools(self , type: ToolType) -> List[ToolProvider]:
        """获取API工具列表

        Returns:
            List[ToolProvider]: API工具列表

        Raises:
            httpx.HTTPStatusError: 当API请求失败时抛出
        """
        # 发送GET请求获取API工具列表
        response_data = await self.admin_client.get(f"/workspaces/current/tools/{type.value}")

        # 直接返回原始数据
        return [ToolProvider(**provider_data) for provider_data in response_data]


__all__ = ["DifyTool"]
