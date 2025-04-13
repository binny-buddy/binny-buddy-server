from binny_buddy.core.client import BBAIClient
from binny_buddy.core.dto import BinnyDTO


class BBService:
    bbai_client = BBAIClient()

    def get_binny_from_image(self) -> BinnyDTO: ...


bb_service = BBService()
