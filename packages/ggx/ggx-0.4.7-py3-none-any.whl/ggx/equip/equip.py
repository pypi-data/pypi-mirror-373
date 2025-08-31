from ..client.game_client import GameClient
from loguru import logger







class Equip(GameClient):
    
    
    
    
    async def get_equip_inventory(
        self, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("gei", {})
            if sync:
                response = await self.wait_for_response("gei")
                return response
            return True
        
        except Exception as e:
            logger.error(e) 
            return False
        
    
    async def remove_equip(
        self, 
        equip_id: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "seq",
                {
                    "EID": equip_id,
                    "LID":-1,
                    "EX":0,
                    "LFID":-1
                }
            )
            if sync:
                response = await self.wait_for_response("nrf")
                return response
            return True
        
        except Exception as e:
            logger.error(e) 
            return False
        
    
    async def get_gems_inventory(
        self, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("ggm", {})
            if sync:
                response = await self.wait_for_response("ggm")
                return response
            return True

        except Exception as e:
            logger.error(e) 
            return False
    
    
    
        
    async def remove_gem(
        self, 
        gem_id: int, 
        sync: bool = True
    ) -> dict | bool:
        
        try:
            
            await self.send_json_message(
                "sge",
                {
                    "GID": gem_id,
                    "RGEM": 0,
                    "LFID": -1
                }
            )
            if sync:
                response = await self.wait_for_response("sge")
                return response
            return True  
            
        except Exception as e:
            logger.error(e) 
            return False
        
        
        
    async def gem_remover(
        self, 
        sync: bool = True
    ) -> None:
        
        gems_inventory = await self.get_gems_inventory()
        gem_data = gems_inventory["GEM"]
        for gem in gem_data:
            gem_id = gem[0]
            gem_qty = gem[1]
            for _ in range(gem_qty):
                
                try:
                    await self.remove_gem(gem_id, sync=sync)
                
                except Exception as e:
                    logger.error(e)
            
        logger.info("All useless gems has been removed")
        
        
        
        
    async def old_equip_remover(
        self, 
        sync: bool = True
    ) -> None:
        
        useless = [1, 2, 3, 11, 12, 13]
        equip_data = await self.get_equip_inventory()
        equip_obj = equip_data["I"]
        for equip in equip_obj:
            if equip[3] in useless and equip[4] > 0:
                
                try:
                    await self.remove_equip(equip_id=equip[0], sync=sync)
                
                except Exception as e:
                    logger.error(e)
                    return None
        
        logger.info("All useless equipements has been removed")
        
        
        
        
    async def handle_gems_from_npc(self, data):
        
        gem_list = data.get("GEM", [])
        for gem_detail in gem_list:
            gem_id = gem_detail[0]
            await self.remove_gem(gem_id)
            
        
  