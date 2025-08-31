from dify.http import AdminClient
from .schemas import LLM, LLMList, ModelParameterRuleList


class DifyLLM:
    def __init__(self, admin_client: AdminClient) -> None:
        self.admin_client = admin_client

    async def find_list(self) -> LLMList:
        response_data = await self.admin_client.get(
            "/workspaces/current/models/model-types/llm",
        )
        return LLMList(**response_data)

    async def get_model_parameter_rules(self, provider: str,  model: str) -> ModelParameterRuleList:
        """获取模型参数规则

        Args:
            provider: 模型提供者，例如 'langgenius'
            provider_model: 提供者模型，例如 'openai_api_compatible'
            model: 模型名称，例如 'openai/gpt-4.1'

        Returns:
            ModelParameterRuleList: 模型参数规则列表
        """
        response_data = await self.admin_client.get(
            f"/workspaces/current/model-providers/{provider}/models/parameter-rules",
            params={"model": model}
        )
        return ModelParameterRuleList(**response_data)


__all__ = ["DifyLLM"]
