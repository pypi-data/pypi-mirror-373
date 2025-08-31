from ..client.game_client import GameClient
from loguru import logger




class BuildingsInventory(GameClient):
    
    
    
    async def get_building_inventory(
        self,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("sin", {})
            if sync:
                response = await self.wait_for_response("sin")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def store_building(
        self,
        building_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("sob", {"OID": building_id})
            if sync:
                response = await self.wait_for_response("sob")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
    async def sell_building_inventory(
        self,
        wod_id: int,
        amount: int,
        unique_id: int = -1,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "sds", {"WID": wod_id, "AMT": amount, "UID": unique_id}
            )
            if sync:
                response = await self.wait_for_response("sds")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False