from ..client.game_client import GameClient
from loguru import logger







class GlobalEffects(GameClient):
    
    
    
    async def get_global_effects(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("usg", {})
            if sync:
                response = await self.wait_for_response("usg")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def upgrade_global_effect(
        self,
        effect_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("agb", {"GEID": effect_id})
            if sync:
                response = await self.wait_for_response("agb")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False