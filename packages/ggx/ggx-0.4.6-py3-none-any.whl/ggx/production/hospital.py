from ..client.game_client import GameClient
from loguru import logger





class Hospital(GameClient):
    
    
    
    
    async def heal(
        self, 
        wod_id: int, 
        amount: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("hru", {"U": wod_id, "A": amount})
            if sync:
                response = await self.wait_for_response("hru")
                return response
            return True
        
        
        except Exception as e:
            logger.error(e)
            
            
    async def cancel_heal(
        self, 
        slot_id: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("hcs", {"S": slot_id})
            if sync:
                response = self.wait_for_response("hcs")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
    async def skip_heal(
        self, 
        slot_id: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            self.send_json_message("hss", {"S": slot_id})
            if sync:
                response = await self.wait_for_response("hss")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
    
    async def delete_wounded(
        self, 
        wod_id: int, 
        amount: int, 
        sync: bool = True
    )-> dict | bool:
        
        try:
            await self.send_json_message("hdu", {"U": wod_id, "A": amount})
            if sync:
                response = await self.wait_for_response("hdu")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
    async def ask_alliance_help_heal(
        self, 
        package_id: int, 
        sync: bool = True
    )-> dict | bool:
        
        try:
            await self.send_json_message("ahr", {"ID": package_id, "T": 2})
            if sync:
                response = await self.wait_for_response("ahr")
                return response
            return True
        
        except Exception as e:
            logger.error(e)