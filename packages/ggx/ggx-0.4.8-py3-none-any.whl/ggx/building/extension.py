from ..client.game_client import GameClient
from loguru import logger





class Extension(GameClient):
    
    
    
    async def buy_extension(
        self,
        x: int,
        y: int,
        rotated: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("ebe", {"X": x, "Y": y, "R": rotated, "CT": 1})
            if sync:
                response = await self.wait_for_response("ebe")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
    async def collect_extension_gift(
        self,
        building_id: int,
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("etc", {"OID": building_id})
            if sync:
                response = await self.wait_for_response("etc")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False