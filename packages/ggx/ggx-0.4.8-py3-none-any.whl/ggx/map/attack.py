from ..client.game_client import GameClient
from ..utils.utils import Utils
from loguru import logger
from typing import Any





class Attack(GameClient):
    
    
    
    
    async def send_attack(
        self,
        kingdom: int,
        sx: int,
        sy: int,
        tx: int,
        ty: int,
        army: list,
        lord_id: int = 0,
        horses_type: int = -1,
        feathers: int = 0,
        slowdown: int = 0,
        boosters: list = [],
        support_tools: list = [],
        final_wave: list = [],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            
            await self.send_json_message(
                "cra",
                {
                    "SX": sx,
                    "SY": sy,
                    "TX": tx,
                    "TY": ty,
                    "KID": kingdom,
                    "LID": lord_id,
                    "WT": 0,
                    "HBW": horses_type,
                    "BPC": 0,
                    "ATT": 0,
                    "AV": 0,
                    "LP": 0,
                    "FC": 0,
                    "PTT": feathers,
                    "SD": slowdown,
                    "ICA": 0,
                    "CD": 99,
                    "A": army,
                    "BKS": boosters,
                    "AST": support_tools,
                    "RW": final_wave,
                    "ASCT": 0, 
                }
            )
            if sync:
                response = await self.wait_for_response("cra")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    
        
        
    async def get_presets(self, sync: bool = True) -> dict | bool:
        
        try:
            await self.send_json_message("gas", {})
            if sync:
                response = await self.wait_for_response("gas")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
     
     
        
        
    async def time_skip_npc_cooldown(
        self,
        kingdom: int,
        tx: int,
        ty: int,
        time_skip: str,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "msd",
                {
                    "X": tx,
                    "Y": ty,
                    "MID": -1,
                    "NID": -1,
                    "MST": time_skip,
                    "KID": str(kingdom)
                }
            )
            if sync:
                response = await self.wait_for_response("msd")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
    
    
    async def autoskip_npc_cooldown(
        self,
        kingdom: int,
        tx: int,
        ty: int,
        cooldown_time: int,
        skips: list = None
    ) -> None:
        
        utils = Utils()
        if cooldown_time > 0:
            
            skips_list = utils.skip_calculator(cooldown_time, skips)
            for skip in skips_list:
                await self.time_skip_npc_cooldown(kingdom, tx, ty, skip, sync=False)
        
        
        

    

        
    
    async def select_preset(
        self,
        preset_name: Any
    ) -> list:
        
        preset_list = await self.get_presets()
        preset_data = preset_list["S"]
        for presets in preset_data:
            preset_server_name = presets.get("SN")
            preset_set = presets.get("A")
            if preset_name == preset_server_name:
                return preset_set
            else:
                logger.error("Unknown preset!")
                    
                
            
        
            




