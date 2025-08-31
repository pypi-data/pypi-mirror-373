from ..client.game_client import GameClient
from loguru import logger
import asyncio
from ..utils.utils import Utils




class Buildings(GameClient):
    
    
    
    async def build(
        self,
        wod_id: int,
        x: int,
        y: int,
        rotated: int = 0,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "ebu",
                {
                    "WID": wod_id,
                    "X": x,
                    "Y": y,
                    "R": rotated,
                    "PWR": 0,
                    "PO": -1,
                    "DOID": -1,
                }
            )
            if sync:
                response = await self.wait_for_response("ebu")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
            
            
    async def upgrade_building(
        self, building_id: int, sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("eup", {"OID": building_id, "PWR": 0, "PO": -1})
            if sync:
                response = await self.wait_for_response("eup")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
     
     
    async def move_building(
        self,
        building_id: int,
        x: int,
        y: int,
        rotated: int = 0,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "emo", {"OID": building_id, "X": x, "Y": y, "R": rotated}
            )
            if sync:
                response = await self.wait_for_response("emo") 
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            
            
    async def sell_building(
        self, building_id: int, sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("sbd", {"OID": building_id})
            if sync:
                response = await self.wait_for_response("sbd") 
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
    
    
    async def destroy_building(
        self, building_id: int, sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("edo", {"OID": building_id})
            if sync:
                response = await self.wait_for_response("edo") 
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
            

    
    
    
    async def skip_construction_free(
        self,
        building_id: int,
        free_skip: int = 1,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("fco", {"OID": building_id, "FS": free_skip})
            if sync:
                response = await self.wait_for_response("fco") 
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
            
            
    async def time_skip_construction(
        self,
        building_id: int,
        time_skip: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("msb", {"OID": building_id, "MST": time_skip})
            if sync:
                response = await self.wait_for_response("msb") 
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
    
    async def wait_finish_construction(
        self, building_id: int, timeout: int
    ) -> dict | bool:
        
        try:
            response = await self.wait_for_response(
                "fbe", {"OID": building_id}, timeout=timeout
            )
            return response
        except Exception as e:
            logger.error(e)
            return False
    
    
    
    
            
    async def instant_build(
        self,
        building_id: int,
        wod_id: int,
        x: int,
        y: int,
        rotated: int = 0,
        time_skips: list[str] = [],
        cooldown: int = 0,
        free_skip: int = 1,
        sync: bool = True
    ) -> None:
        
        try:
            await self.build(wod_id, x, y, rotated, sync=sync)
            for skip in time_skips:
                await self.time_skip_construction(building_id, skip, sync=sync)   
            asyncio.sleep(cooldown)
            await self.skip_construction_free(building_id, free_skip, sync=sync)
            if sync:
                await self.wait_finish_construction(building_id)
        
        except Exception as e:
            logger.error(e)
        
       
    async def instant_upgrade(
        self,
        building_id: int,
        time_skips: list[str] = [],
        cooldown: int = 0,
        free_skip: int = 1,
        sync: bool = True
    ) -> None:
        
        try:
            await self.upgrade_building(building_id, sync=sync) 
            for skip in time_skips or []:
                await self.time_skip_construction(building_id, skip, sync=sync)
            asyncio.sleep(cooldown)
            await self.skip_construction_free(building_id, free_skip, sync=sync)
            if sync:
                await self.wait_finish_construction(building_id)
        
        except Exception as e:
            logger.error(e)
            
    
    async def instant_destroy(
        self,
        building_id: int,
        time_skips: list[str] = [],
        cooldown: int = 0,
        free_skip: int = 1,
        sync: bool = True
    ) -> None:
        
        try:
            await self.destroy_building(building_id, sync=sync) 
            for skip in time_skips or []:
                await self.time_skip_construction(building_id, skip, sync=sync)
            asyncio.sleep(cooldown)
            await self.skip_construction_free(building_id, free_skip, sync=sync)
            
        
        except Exception as e:
            logger.error(e)
            
            
