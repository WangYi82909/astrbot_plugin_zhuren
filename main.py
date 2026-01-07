from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import ProviderRequest
from astrbot.api import AstrBotConfig
from astrbot.api import logger

@register("owner_auth", "梦千秋", "基于最底层的qq号认证主人，自定义“主人”“非主人”提示词", "1.0.0")
class OwnerAuthPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.enabled = True
        logger.info(f"主人验证插件加载 - 主人QQ: {config.get('owner_qq')}")

    @filter.on_llm_request()
    async def owner_auth_hook(self, event: AstrMessageEvent, req: ProviderRequest):
        if not self.enabled:
            return
        
        try:
            user_id = event.get_sender_id()
            user_name = event.get_sender_name()
            owner_qq = str(self.config.get("owner_qq"))
            owner_name = self.config.get("owner_name")
            
            logger.info(f"用户验证: {user_id}/{user_name} vs 主人: {owner_qq}/{owner_name}")
            
            if user_id == owner_qq and user_name == owner_name:
                identity_prompt = self.config.get("owner_prompt")
                logger.info("✅ 主人验证通过")
            else:
                identity_prompt = self.config.get("not_owner_prompt")
                logger.info("❌ 非主人用户")
            
            if identity_prompt and req.prompt:
                original_prompt = req.prompt
                req.prompt = f"【{identity_prompt}】\n{original_prompt}"
                logger.info(f"请求修改完成 - 添加提示: {identity_prompt}")
                
        except Exception as e:
            logger.error(f"主人验证钩子错误: {e}")
            return

    async def terminate(self):
        self.enabled = False
        logger.info("主人验证插件已卸载")