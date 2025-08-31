from ..client.game_client import GameClient
from loguru import logger








class Tutorial(GameClient):
    
    
    
    async def choose_hero(
        self,
        hero_id: int = 802,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("hdc", {"HID": hero_id})
            if sync:
                response = await self.wait_for_response("hdc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def skip_generals_intro(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("sgi", {})
            if sync:
                response = await self.wait_for_response("sgi")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def collect_noob_gift(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("uoa", {})
            if sync:
                response = await self.wait_for_response("uoa")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False