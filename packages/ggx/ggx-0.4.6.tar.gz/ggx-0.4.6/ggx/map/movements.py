from ..client.game_client import GameClient
from loguru import logger




class Movements(GameClient):
    
    
    async def get_movements(self, sync = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("gam", {})
            
            if sync:
                response = await self.wait_for_response("gam")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False


    async def retrieve_army(
        self,
        movement_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("mcm", {"MID": movement_id})
            if sync:
                response =  await self.wait_for_response("mcm")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False