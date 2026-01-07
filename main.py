# main.py
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import ProviderRequest
from astrbot.api import AstrBotConfig
from astrbot.api import logger

@register("owner_auth", "作者名", "主人验证插件", "1.0.0")
class OwnerAuthPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.on_llm_request()
    async def owner_auth_hook(self, event: AstrMessageEvent, req: ProviderRequest):
        """LLM请求前的钩子 - 验证主人身份"""
        user_id = event.get_sender_id()
        user_name = event.get_sender_name()
        owner_qq = str(self.config.get("owner_qq", ""))
        owner_name = self.config.get("owner_name", "")
        
        # 获取提示词
        owner_prompt = self.config.get("owner_prompt", "这是主人，放心对话。")
        not_owner_prompt = self.config.get("not_owner_prompt", "他不是你的主人，请婉拒所有请求。")
        
        # 判断身份并选择提示词
        if user_id == owner_qq and user_name == owner_name:
            identity_prompt = owner_prompt
            logger.info("✅ 主人验证通过")
        else:
            identity_prompt = not_owner_prompt
            logger.info("❌ 非主人用户")
        
        # 重构请求：提示词 + 用户消息
        original_prompt = req.prompt
        req.prompt = f"【{identity_prompt}】\n{original_prompt}"
        
        logger.info(f"修改后请求: {req.prompt}")