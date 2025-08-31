from ..client.game_client import GameClient
from loguru import logger
from ..utils.utils import Utils
import asyncio






class Castle(GameClient):
    
    
    async def get_castles(self, sync: bool = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("gcl", {})
            if sync:
                response = await self.wait_for_response("gcl")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        
        
    
      
    async def get_detailed_castles(self, sync: bool = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("dcl", {})
            if sync:
                response = await self.wait_for_response("dcl")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        
        
    
       
    async def relocate_main_castle(
        self,
        x: int,
        y: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("rst", {"PX": x, "PY": y})
            if sync:
                response = await self.wait_for_response("rst")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
                
    

    async def go_to_castle(
        self,
        kingdom: int,
        castle_id: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message("jca", {"CID": castle_id, "KID": kingdom})
            if sync:
                response = await self.wait_for_response("jaa")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
    
    
    
    async def rename_castle(
        self,
        kingdom: int,
        castle_id: int,
        castle_type: int,
        name: str,
        paid: int = 0,
        sync: bool = True
    ) -> dict | bool:
        
        
        try:
            await self.send_json_message(
                "arc",
                {
                    "CID": castle_id,
                    "P": paid,
                    "KID": kingdom,
                    "AT": castle_type,
                    "N": name
                }
            )
            if sync:
                response = await self.wait_for_response("arc")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        
    
       
    async def get_castle_resources(self, sync: bool = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("grc", {})
            if sync:
                response = await self.wait_for_response("grc")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
    


    async def get_castle_production(self, sync: bool = True) -> dict | bool:
        
        try:
            
            await self.send_json_message("gpa", {})
            if sync:
                response = await self.wait_for_response("gpa")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
    


    async def send_resources_to_kingdom(
        self,
        id_sender: int,
        sender_kid: int,
        target_kid: int,
        resources: list[list[str, int]],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "kgt",
                {
                   "SCID": id_sender,
                   "SKID": sender_kid,
                   "TKID": target_kid,
                   "G": resources
                }
            )
            if sync:
                response = await self.wait_for_response("kgt")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
    async def send_units_to_kingdom(
        self,
        id_sender: int,
        sender_kid: int,
        target_kid: int,
        units: list[list[int, int]],
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "kut",
                {
                   "SCID": id_sender,
                   "SKID": sender_kid,
                   "TKID": target_kid,
                   "CID": -1,
                   "A": units
                }
            )
            if sync:
                response = await self.wait_for_response("kut")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def skip_kingdom_transfer(
        self,
        skip: str,
        target_kid: int,
        transfer_type: int,
        sync: bool = True
    ) -> dict | bool:
        
        try:
            await self.send_json_message(
                "msk",
                {
                    "MST": skip,
                    "KID": target_kid,
                    "TT": transfer_type
                }
            )
            if sync:
                response = await self.wait_for_response("msk")
                return response
            return True
        
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def auto_units_kingdom_transfer(
        self,
        id_sender: int,
        sender_kid: int,
        target_kid: int,
        units: list,
        skips: list = None,
        sync: bool = True  
    ) -> dict | bool:
        
        
        utils = Utils()
        send_units = await self.send_units_to_kingdom(id_sender, sender_kid, target_kid, units)
        if not isinstance(send_units, dict):
            logger.error(f"Failed to send units to kingdom: {target_kid}")
            return
        
        kpi = send_units.get("kpi", {})
        ut_list = kpi.get("UT")
        if not ut_list or not isinstance(ut_list, list):
            logger.error("Unknown transfer time data!")
            return
        
        time_to_transfer = ut_list[0].get("RS")
        if not isinstance(time_to_transfer, int):
            logger.error(f"Invalid time value: {ut_list[0]}")
            return
        
        skip_list = utils.skip_calculator(time_to_transfer, skips)
        for skip in skip_list:
            await self.skip_kingdom_transfer(skip, target_kid, transfer_type=1, sync=sync)
        
        logger.info(f"All units has been sent succesfully to kingdom {target_kid}!")
        
        
        
        
        
    async def auto_res_kingdom_transfer(
        self,
        id_sender: int,
        sender_kid: int,
        target_kid: int,
        resources: list,
        skips: list = None,
        sync: bool = True  
    ) -> dict | bool:
        
        
        utils = Utils()
        resources_sender = await self.send_resources_to_kingdom(id_sender, sender_kid, target_kid, resources)
        if not isinstance(resources_sender, dict):
            logger.error(f"Failed to send resources to kingdom: {target_kid}")
            return
        
        kpi = resources_sender.get("kpi", {})
        rt_list = kpi.get("RT")
        if not rt_list or not isinstance(rt_list, list):
            logger.error("Unknown transfer time data!")
            return
        
        time_to_transfer = rt_list[0].get("RS")
        if not isinstance(time_to_transfer, int):
            logger.error(f"Invalid time value: {rt_list[0]}")
            return

        skip_list = utils.skip_calculator(time_to_transfer, skips)
        for skip in skip_list:
            await self.skip_kingdom_transfer(skip, target_kid, transfer_type=2, sync=sync)
        
        logger.info(f"All resources has been sent succesfully to kingdom {target_kid}!")    





    async def units_replenish(
        self,
        target_kid: int,
        wod_id: int,
        amount: int
    ) -> None:
        
        
        try:
            
            account_inventory = await self.get_detailed_castles()
            inventory_data = account_inventory["C"]
            donors = []
            
            
            for kingdom in inventory_data:
                kid = kingdom.get("KID")
                if kid == target_kid:
                    continue
                
                for ai_block in kingdom.get("AI", []):
                    aid = ai_block.get("AID")
                    for wod, amt in ai_block.get("AC", []):
                        if wod == wod_id and amt > amount:
                            donors.append({"aid": aid, "kid":kid, "amount": amt})
                            break
                        
            if not donors:
                logger.warning("I can't find any eligible location!")
                return False
                            
            else:
                best = max(donors, key=lambda d: d["amount"])
                donor_aid = best["aid"]
                donor_amt = best["amount"]
                donor_kid = best["kid"]
                send_amt = min(donor_amt, amount)
                
                await self.auto_units_kingdom_transfer(donor_aid, donor_kid, target_kid, [[wod_id, send_amt]])
                logger.info(f"Kingdom {target_kid} refilled with {send_amt} units!")
                     
        except Exception as e:
            logger.error(e)
            return False
        
        
        
    async def kingdom_auto_feeder(
        self,
        target_kid: int,
        min_food: int,
        min_mead: int,
        skips: list = None,
        interval: float = 60.0,
        max_transfers: int = 3,
        sync: bool = True,
        stop_event: asyncio.Event = None,
        min_donor_stock_food: int = 100_000,
        min_donor_stock_mead: int = 100_000,
    ) -> None:


        if stop_event is None:
            stop_event = asyncio.Event()

        while not stop_event.is_set():
            try:
                castles_inventory = await self.get_detailed_castles(sync=sync)
                resource_inventory = castles_inventory["C"]

                donors_food = []
                donors_mead = []
                targets = []

            
                for items in resource_inventory:
                    kid = items.get("KID")
                    if kid == target_kid:
                        targets.append(items)
                        continue

                    for ai_item in items.get("AI", []):
                        aid = ai_item.get("AID")
                        mead_value = ai_item.get("MEAD")
                        food_value = ai_item.get("F")
                        mead_prod = ai_item.get("gpa", {}).get("DMEAD", 0)
                        food_prod = ai_item.get("gpa", {}).get("DF", 0)

                        if food_value > min_donor_stock_food and food_prod > 0:
                            donors_food.append((kid, aid, food_value))
                        if mead_value > min_donor_stock_mead and mead_prod > 0:
                            donors_mead.append((kid, aid, mead_value))

                # Sortare donori după resurse disponibile
                donors_food.sort(key=lambda x: x[2], reverse=True)
                donors_mead.sort(key=lambda x: x[2], reverse=True)

                # Verificare ținte
                for t in targets:
                    kid = t.get("KID")
                    for ai_item in t.get("AI", []):
                        food_value = ai_item.get("F")
                        mead_value = ai_item.get("MEAD")
                        food_cap = ai_item.get("gpa", {}).get("MRF", 0)
                        mead_cap = ai_item.get("gpa", {}).get("MRMEAD", 0)

                        fcap_var = max(0, int(food_cap - 5) - int(food_value))
                        mcap_var = max(0, int(mead_cap - 5) - int(mead_value))

                        # Transfer mâncare
                        if food_value < min_food and donors_food:
                            for _ in range(min(max_transfers, len(donors_food))):
                                donor_kid, donor_aid, _ = donors_food.pop(0)
                                await self.auto_res_kingdom_transfer(
                                    donor_aid, donor_kid, kid, [["F", fcap_var]], skips, sync
                                )
                                logger.info(f"[FOOD] {fcap_var} sent from {donor_kid} to {kid}")

                        # Transfer mied
                        if mead_value < min_mead and donors_mead:
                            for _ in range(min(max_transfers, len(donors_mead))):
                                donor_kid, donor_aid, _ = donors_mead.pop(0)
                                await self.auto_res_kingdom_transfer(
                                    donor_aid, donor_kid, kid, [["MEAD", mcap_var]], skips, sync
                                )
                                logger.info(f"[MEAD] {mcap_var} sent from {donor_kid} to {kid}")

            except asyncio.TimeoutError:
                logger.warning("Timeout occured. Retry!")
            except Exception as e:
                logger.error(e)

            await asyncio.sleep(interval)
