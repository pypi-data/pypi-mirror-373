from ..client.game_client import GameClient
from loguru import logger





class Wall(GameClient):
    
    
    
    async def upgrade_wall(
        self,
        building_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("eud", {"OID": building_id, "PWR": 0, "PO": -1})
            if sync:
                response = await self.wait_for_response("eud")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False