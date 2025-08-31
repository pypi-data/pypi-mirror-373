from ..client.game_client import GameClient
from loguru import logger





class Account(GameClient):





    async def get_account_infos(self, sync: bool = True) -> dict | bool:

        try:
            await self.send_json_message("gpi", {})
            if sync:
                response = await self.wait_for_response("gpi")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False
        



    async def register_email(
        self,
        email: str,
        subscribe: bool = False,
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("vpm", {"MAIL": email, "NEWSLETTER": subscribe})
            if sync:
                response = await self.wait_for_response("vpm")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False




    async def get_username_change_infos(
        self, sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("gnci", {})
            if sync:
                response = await self.wait_for_response("gnci")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False




    async def change_username(
        self, new_username: str, sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("cpne", {"PN": new_username})
            if sync:
                response = await self.wait_for_response("cpne")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False




    async def change_password(
        self,
        old_password: str,
        new_password: str,
        sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("scp", {"OPW": old_password, "NPW": new_password})
            if sync:
                response = await self.wait_for_response("scp")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False




    async def ask_email_change(
        self, new_email: str, sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("rmc", {"PMA": new_email})
            if sync:
                response = await self.wait_for_response("rmc")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False



    async def get_email_change_status(
        self, sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("mns", {})
            if sync:
                response = await self.wait_for_response("mns")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False



    async def cancel_email_change(
        self, sync: bool = True
    ) -> dict | bool:

        try:
            await self.send_json_message("cmc", {})
            if sync:
                response = await self.wait_for_response("cmc")
                return response
            return True
        except Exception as e:
            logger.error(e)
            return False