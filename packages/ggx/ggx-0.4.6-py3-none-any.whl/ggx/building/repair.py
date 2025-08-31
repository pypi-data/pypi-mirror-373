from ..client.game_client import GameClient
from loguru import logger





class Repair(GameClient):
    
    
    
    async def repair_building(
        self,
        building_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("rbu", {"OID": building_id, "PO": -1, "PWR": 0})
            if sync:
                response = await self.wait_for_response("rbu")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
    async def ask_alliance_help_repair(
        self,
        building_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("ahr", {"ID": building_id, "T": 3})
            if sync:
                response = await self.wait_for_response("ahr")
                return response
            return True
        except Exception as e:
            logger.error(e)
        