from typing import List

from pydantic import ValidationError

from .utils import ResponceHelper
from .utils.const import VALIDATE_DATA_MESSAGE_ERROR

from .based_api import BasedApi

from .valo_types.valo_enums import (
    Locales
)

from .valo_types.valo_models import (
    FetchOptionsModel,
    GetAgentsModel,
    GetGameBorderLevelsModel,
    GetGameGearModel,
    GetGameMapsModel,
    GetGameWeaponsModel,
    GetPlayerCardModel,
    GetPlayerTitleModel,
)
from .valo_types.valo_responses import (
    AgentResponseModel,
    BorderLevelModelResponse,
    ChromaGameWeaponResponseModel,
    GearModelResponse,
    LevelGameWeaponResponseModel,
    MapModelResponse,
    PlayerCardModelResponse,
    PlayerTitleModelResponse,
    WeaponResponseModel,
    WeaponSkinGameWeaponResponseModel,
)


class GameApi(BasedApi):
    BASE_URL = "https://valorant-api.com"

    def __init__(self):
        self.headers = {"User-Agent": "LanoValoPy"}
        self.res_helper = ResponceHelper()

    async def get_player_cards(
        self, options: GetPlayerCardModel
    ) -> List[PlayerCardModelResponse]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/playercards"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [PlayerCardModelResponse.model_validate(x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e
            

    async def get_player_card_by_uuid(
        self, options: GetPlayerCardModel
    ) -> PlayerCardModelResponse:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/playercards/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try: 
            return PlayerCardModelResponse.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_player_titles(
        self, options: GetPlayerTitleModel
    ) -> List[PlayerTitleModelResponse]:
        """
        Gets the player titles.

        Args:
            options (GetPlayerTitleModel): The options for the request.

        Returns:
            List[PlayerTitleModelResponse]: The player titles.
        """
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/playertitles"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        
        try:
            data = self.res_helper.data_convertor(result)
            return [PlayerTitleModelResponse.model_validate(x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e
        

    async def get_player_title_by_uuid(
        self, options: GetPlayerTitleModel
    ) -> PlayerTitleModelResponse:
        """
        Fetches a player title by UUID.

        Args:
            options (GetPlayerTitleModel): The options containing the UUID of the player title
            and optional language preference.

        Returns:
            PlayerTitleModelResponse: The response model containing details of the player title.

        Raises:
            ValidationError: If the UUID is not provided in the options.
        """
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/playertitles/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            return PlayerTitleModelResponse.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_agents(self, options: GetAgentsModel) -> List[AgentResponseModel]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/agents"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [AgentResponseModel.model_validate(x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_agent_by_uuid(self, options: GetAgentsModel) -> AgentResponseModel:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/agents/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            return AgentResponseModel.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_maps(self, options: GetGameMapsModel) -> List[MapModelResponse]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/maps"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [MapModelResponse.model_validate(x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_map_by_uuid(self, options: GetGameMapsModel) -> MapModelResponse:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/maps/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            return MapModelResponse.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_weapons(
        self, options: GetGameWeaponsModel
    ) -> List[WeaponResponseModel]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/weapons"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [WeaponResponseModel.model_validate(x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_weapons_by_uuid(
        self, options: GetGameWeaponsModel
    ) -> WeaponResponseModel:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/weapons/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            return WeaponResponseModel.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_weapons_skins(
        self, options: GetGameWeaponsModel
    ) -> List[WeaponSkinGameWeaponResponseModel]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/weapons/skins"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [WeaponSkinGameWeaponResponseModel.model_validate(x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_weapons_skins_by_uuid(
        self, options: GetGameWeaponsModel
    ) -> WeaponSkinGameWeaponResponseModel:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/weapons/skins/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            return WeaponSkinGameWeaponResponseModel.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_weapons_skins_chromas(
        self, options: GetGameWeaponsModel
    ) -> List[ChromaGameWeaponResponseModel]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/weapons/skinchromas"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [ChromaGameWeaponResponseModel.model_validate(x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_weapons_skins_chromas_by_uuid(
        self, options: GetGameWeaponsModel
    ) -> ChromaGameWeaponResponseModel:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/weapons/skinchromas/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            return ChromaGameWeaponResponseModel.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_weapons_skins_levels(
        self, options: GetGameWeaponsModel
    ) -> List[LevelGameWeaponResponseModel]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/weapons/skinlevels"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [LevelGameWeaponResponseModel(**x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_weapons_skins_levels_by_uuid(
        self, options: GetGameWeaponsModel
    ) -> LevelGameWeaponResponseModel:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/weapons/skinlevels/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)

        try:
            return LevelGameWeaponResponseModel.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_border_levels(
        self, options: GetGameBorderLevelsModel
    ) -> List[BorderLevelModelResponse]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/levelborders"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [BorderLevelModelResponse.model_validate(x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_border_levels_by_uuid(
        self, options: GetGameBorderLevelsModel
    ) -> BorderLevelModelResponse:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/levelborders/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            return BorderLevelModelResponse.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_gear(self, options: GetGameGearModel) -> List[GearModelResponse]:
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/gear"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            data = self.res_helper.data_convertor(result)
            return [GearModelResponse(**x) for x in data]
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e

    async def get_gear_by_uuid(self, options: GetGameGearModel) -> GearModelResponse:
        self._validate(options.model_dump(), ["uuid"])
        query = self._query({"language": options.language.value if options.language else Locales.en_US.value})
        url = f"{self.BASE_URL}/v1/gear/{options.uuid}"

        if query:
            url += f"?{query}"

        fetch_options = FetchOptionsModel(url=url)
        result = await self._fetch(fetch_options)
        try:
            return GearModelResponse.model_validate(result.data)
        except ValidationError as e:
            raise ValueError(f"{VALIDATE_DATA_MESSAGE_ERROR}: {e}") from e
        
