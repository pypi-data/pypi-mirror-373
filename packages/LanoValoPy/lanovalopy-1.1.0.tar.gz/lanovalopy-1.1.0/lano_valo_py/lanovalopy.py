from typing import List, Optional

from .exeptions import UnauthorizedError
from .game_api import GameApi
from .game_stats import ValoGameStats
from .henrik_api import HenrikAPI
from .lanologger import LoggerBuilder
from .utils.const import TOKEN_MESSAGE_REQUERIED
from .valo_types.valo_models import (
    AccountFetchByPUUIDOptionsModel,
    AccountFetchOptionsModel,
    AccountFetchOptionsModelV2,
    GetAgentsModel,
    GetContentFetchOptionsModel,
    GetCrosshairFetchOptionsModel,
    GetEsportsMatchesFetchOptionsModel,
    GetFeaturedItemsFetchOptionsModel,
    GetGameBorderLevelsModel,
    GetGameGearModel,
    GetGameMapsModel,
    GetGameWeaponsModel,
    GetLeaderboardOptionsModel,
    GetLifetimeMMRHistoryFetchOptionsModel,
    GetMatchesByPUUIDFetchOptionsModel,
    GetMatchesFetchOptionsModel,
    GetMatchFetchOptionsModel,
    GetMMRByPUUIDFetchOptionsModel,
    GetMMRFetchOptionsModel,
    GetMMRHistoryByPUUIDFetchOptionsModel,
    GetMMRHistoryFetchOptionsModel,
    GetMMRStoredHistoryByPUUIDResponseModel,
    GetMMRStoredHistoryOptionsModel,
    GetPlayerCardModel,
    GetPlayerTitleModel,
    GetPremierTeamFetchOptionsModel,
    GetRawFetchOptionsModel,
    GetStatusFetchOptionsModel,
    GetStoredMatchesByPUUIDResponseModel,
    GetStoredMatchesOptionsModel,
    GetVersionFetchOptionsModel,
    GetWebsiteFetchOptionsModel,
)
from .valo_types.valo_responses import (
    AccountResponseModelV1,
    AccountResponseModelV2,
    AgentResponseModel,
    APIResponseModel,
    BinaryData,
    BorderLevelModelResponse,
    BuildGameInfoResponseModel,
    BundleResponseModelV2,
    ChromaGameWeaponResponseModel,
    CommunityNewsResponseModel,
    ContentResponseModel,
    DayMMRStats,
    EsportMatchDataResponseModel,
    FeaturedBundleResponseModelV1,
    GearModelResponse,
    HistoryMMRV2,
    LeaderboardDataResponseModelV2,
    LeaderboardDataResponseModelV3,
    LevelGameWeaponResponseModel,
    MapModelResponse,
    MatchDataV4,
    MatchResponseModel,
    MMRHistoryByPuuidResponseModelV1,
    MMRHistoryModelV2,
    MmrModelV3,
    MMRResponseModel,
    MostPlayedHeroesStats,
    PlayerCardModelResponse,
    PlayerTitleModelResponse,
    PremierLeagueMatchesWrapperResponseModel,
    PremierTeamResponseModel,
    ShortPlayerStats,
    StatusDataResponseModel,
    StoredMatchResponseModel,
    TotalPlayerStatsModel,
    V1StoredMmrHistoryResponse,
    WeaponResponseModel,
    WeaponSkinGameWeaponResponseModel,
)

logger = LoggerBuilder("HenrikAPI").add_stream_handler().build()


class LanoValoPy:
    def __init__(
        self,
        henrik_token: Optional[str] = None,
        henrik_api: Optional[HenrikAPI] = None,
        game_api: Optional[GameApi] = None,
        game_stats: Optional[ValoGameStats] = None,
    ):
        self.henrik_api = henrik_api or HenrikAPI(henrik_token)
        self.game_api = game_api or GameApi()
        self.game_stats = game_stats or ValoGameStats()

        if henrik_token is None:
            logger.info(TOKEN_MESSAGE_REQUERIED)

    @property
    def get_game_data(self) -> HenrikAPI:
        return self.henrik_api

    @property
    def get_game_api(self) -> GameApi:
        return self.game_api

    async def get_account(
        self, options: AccountFetchOptionsModel
    ) -> AccountResponseModelV1 | AccountResponseModelV2:
        """
        Gets the account information for a given name and tag.

        Args:
            options (AccountFetchOptionsModel): The options for the request.

        Returns:
            AccountResponseModelV1 | AccountResponseModelV2: The account information.
        """
        return await self.henrik_api.get_account(options)

    async def get_account_by_puuid(
        self, options: AccountFetchByPUUIDOptionsModel
    ) -> AccountResponseModelV1:
        """
        Gets the account information for a given puuid.

        Args:
            options (AccountFetchByPUUIDOptionsModel): The options for the request.

        Returns:
            AccountResponseModelV1: The account information.
        """
        return await self.henrik_api.get_account_by_puuid(options)

    async def get_mmr_by_puuid(
        self, options: GetMMRByPUUIDFetchOptionsModel
    ) -> MMRResponseModel | MmrModelV3:
        """
        Gets the MMR information for a given puuid.

        Args:
            options (GetMMRByPUUIDFetchOptionsModel): The options for the request.

        Returns:
            MMRResponseModel: The MMR information.
        """
        return await self.henrik_api.get_mmr_by_puuid(options)

    async def get_mmr_history_by_puuid(
        self, options: GetMMRHistoryByPUUIDFetchOptionsModel
    ) -> MMRHistoryByPuuidResponseModelV1 | MMRHistoryModelV2:
        """
        Gets the MMR history for a given puuid.

        Args:
            options (GetMMRHistoryByPUUIDFetchOptionsModel): The options for the request.

        Returns:
            MMRHistoryByPuuidResponseModelV1: The MMR history | MMRHistoryModelV2.
        """
        return await self.henrik_api.get_mmr_history_by_puuid(options)

    async def get_matches_by_puuid(
        self, options: GetMatchesByPUUIDFetchOptionsModel
    ) -> List[MatchResponseModel] | List[MatchDataV4]:
        return await self.henrik_api.get_matches_by_puuid(options)

    async def get_content(
        self, options: GetContentFetchOptionsModel
    ) -> ContentResponseModel:
        """
        Gets the content for the given locale. This endpoints returns basic contant data like season id's or skins.
        If you need more data, please refer to https://valorant-api.com which also has image data

        Args:
            options (GetContentFetchOptionsModel): The options for the request.

        Returns:
            ContentResponseModel: The content.
        """
        return await self.henrik_api.get_content(options)

    async def get_leaderboard(
        self, options: GetLeaderboardOptionsModel
    ) -> LeaderboardDataResponseModelV3 | LeaderboardDataResponseModelV2:
        """
        Gets the leaderboard for the given options.

        Args:
            options (GetLeaderboardOptionsModel): The options for the request.

        Returns:
            LeaderboardDataResponseModelV3 | LeaderboardDataResponseModelV2: The leaderboard data.
        """
        return await self.henrik_api.get_leaderboard(options)

    async def get_matches(
        self, options: GetMatchesFetchOptionsModel
    ) -> List[MatchResponseModel] | List[MatchDataV4]:
        return await self.henrik_api.get_matches(options)

    async def get_match(
        self, options: GetMatchFetchOptionsModel
    ) -> MatchResponseModel | MatchDataV4:
        """
        Gets the match data for the given match id.

        Args:
            options (GetMatchFetchOptionsModel): The options for the request.

        Returns:
            MatchResponseModel: The match data.
        """
        return await self.henrik_api.get_match(options)

    async def get_mmr_history(
        self, options: GetMMRHistoryFetchOptionsModel
    ) -> MMRResponseModel | MMRHistoryModelV2:
        """
        Returns the latest competitive games with RR movement for each game

        Args:
            options (GetMMRHistoryFetchOptionsModel): The options for the request.

        Returns:
            MMRResponseModel: The MMR history.
        """
        return await self.henrik_api.get_mmr_history(options)

    async def get_lifetime_mmr_history(
        self, options: GetLifetimeMMRHistoryFetchOptionsModel
    ) -> APIResponseModel:
        return await self.henrik_api.get_lifetime_mmr_history(options)

    async def get_mmr(
        self, options: GetMMRFetchOptionsModel
    ) -> MMRResponseModel | MmrModelV3:
        """
        Gets the MMR information for a given name and tag.

        Args:
            options (GetMMRFetchOptionsModel): The options for the request.

        Returns:
            MMRResponseModel: The MMR information.
        """
        return await self.henrik_api.get_mmr(options)

    async def get_raw_data(self, options: GetRawFetchOptionsModel) -> APIResponseModel:
        """
        Make direct requests to the riot server and get the response without additional parsing from us

        Args:
            options (GetRawFetchOptionsModel): The options for the request.

        Returns:
            errors (APIResponseModel): The response from the server.
        """
        return await self.henrik_api.get_raw_data(options)

    async def get_status(
        self, options: GetStatusFetchOptionsModel
    ) -> StatusDataResponseModel:
        """
        Gets the status server for the given region.

        Args:
            options (GetStatusFetchOptionsModel): The options for the request.

        Returns:
            StatusDataResponseModel: The status server for the given region.
        """
        return await self.henrik_api.get_status(options)

    async def get_featured_items(
        self, options: GetFeaturedItemsFetchOptionsModel
    ) -> APIResponseModel | FeaturedBundleResponseModelV1 | List[BundleResponseModelV2]:
        return await self.henrik_api.get_featured_items(options)

    async def get_version(
        self, options: GetVersionFetchOptionsModel
    ) -> BuildGameInfoResponseModel:
        """
        Gets the current build version and branch for a given region.

        Args:
            options (GetVersionFetchOptionsModel): The options for the request.

        Returns:
            BuildGameInfoResponseModel: The current build version and branch.
        """
        return await self.henrik_api.get_version(options)

    async def get_website(
        self, options: GetWebsiteFetchOptionsModel
    ) -> List[CommunityNewsResponseModel]:
        """
        Gets the community news for a given country code and filter.

        Args:
            options (GetWebsiteFetchOptionsModel): The options for the request.

        Returns:
            List[CommunityNewsResponseModel]: The community news.
        """
        return await self.henrik_api.get_website(options)

    async def get_crosshair(self, options: GetCrosshairFetchOptionsModel) -> BinaryData:
        """
        Gets a crosshair image as a binary response.

        Args:
            options (GetCrosshairFetchOptionsModel): The options for the request.

        Returns:
            BinaryData: The binary response from the server. This binary response is a PNG image.
        """
        return await self.henrik_api.get_crosshair(options)

    async def get_esports_matches(
        self, options: GetEsportsMatchesFetchOptionsModel
    ) -> List[EsportMatchDataResponseModel]:
        """
        Gets the current esports matches.

        Returns:
            List[EsportsMatchResponseModel]: The current esports matches.
        """
        return await self.henrik_api.get_esports_matches(options)

    async def get_premier_team(
        self, options: GetPremierTeamFetchOptionsModel
    ) -> PremierTeamResponseModel:
        """
        Gets the premier team.

        Args:
            options (GetPremierTeamFetchOptionsModel): The options for the request.

        Returns:
            PremierTeamResponseModel: The premier team.
        """
        return await self.henrik_api.get_premier_team(options)

    async def get_premier_team_history(
        self, options: GetPremierTeamFetchOptionsModel
    ) -> PremierLeagueMatchesWrapperResponseModel:
        """
        Gets the premier team history.

        Args:
            options (GetPremierTeamFetchOptionsModel): The options for the request.

        Returns:
            PremierLeagueMatchesWrapperResponseModel: The premier team history.
        """
        return await self.henrik_api.get_premier_team_history(options)

    async def get_premier_team_by_id(self, team_id: str) -> PremierTeamResponseModel:
        """
        Gets the premier team.

        Args:
            options (GetPremierTeamFetchOptionsModel): The options for the request.

        Returns:
            PremierTeamResponseModel: The premier team.
        """
        return await self.henrik_api.get_premier_team_by_id(team_id)

    async def get_premier_team_history_by_id(
        self, team_id: str
    ) -> PremierLeagueMatchesWrapperResponseModel:
        """
        Gets the premier team history.

        Args:
            options (GetPremierTeamFetchOptionsModel): The options for the request.

        Returns:
            PremierLeagueMatchesWrapperResponseModel: The premier team history.
        """
        return await self.henrik_api.get_premier_team_history_by_id(team_id)

    async def get_player_cards(
        self, options: GetPlayerCardModel
    ) -> List[PlayerCardModelResponse]:
        return await self.game_api.get_player_cards(options)

    async def get_player_card_by_uuid(
        self, options: GetPlayerCardModel
    ) -> PlayerCardModelResponse:
        return await self.game_api.get_player_card_by_uuid(options)

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
        return await self.game_api.get_player_titles(options)

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
        return await self.game_api.get_player_title_by_uuid(options)

    async def get_agents(self, options: GetAgentsModel) -> List[AgentResponseModel]:
        return await self.game_api.get_agents(options)

    async def get_agent_by_uuid(self, options: GetAgentsModel) -> AgentResponseModel:
        return await self.game_api.get_agent_by_uuid(options)

    async def get_maps(self, options: GetGameMapsModel) -> List[MapModelResponse]:
        return await self.game_api.get_maps(options)

    async def get_map_by_uuid(self, options: GetGameMapsModel) -> MapModelResponse:
        return await self.game_api.get_map_by_uuid(options)

    async def get_weapons(
        self, options: GetGameWeaponsModel
    ) -> List[WeaponResponseModel]:
        return await self.game_api.get_weapons(options)

    async def get_weapons_by_uuid(
        self, options: GetGameWeaponsModel
    ) -> WeaponResponseModel:
        return await self.game_api.get_weapons_by_uuid(options)

    async def get_weapons_skins(
        self, options: GetGameWeaponsModel
    ) -> List[WeaponSkinGameWeaponResponseModel]:
        return await self.game_api.get_weapons_skins(options)

    async def get_weapons_skins_by_uuid(
        self, options: GetGameWeaponsModel
    ) -> WeaponSkinGameWeaponResponseModel:
        return await self.game_api.get_weapons_skins_by_uuid(options)

    async def get_weapons_skins_chromas(
        self, options: GetGameWeaponsModel
    ) -> List[ChromaGameWeaponResponseModel]:
        return await self.game_api.get_weapons_skins_chromas(options)

    async def get_weapons_skins_chromas_by_uuid(
        self, options: GetGameWeaponsModel
    ) -> ChromaGameWeaponResponseModel:
        return await self.game_api.get_weapons_skins_chromas_by_uuid(options)

    async def get_weapons_skins_levels(
        self, options: GetGameWeaponsModel
    ) -> List[LevelGameWeaponResponseModel]:
        return await self.game_api.get_weapons_skins_levels(options)

    async def get_weapons_skins_levels_by_uuid(
        self, options: GetGameWeaponsModel
    ) -> LevelGameWeaponResponseModel:
        return await self.game_api.get_weapons_skins_levels_by_uuid(options)

    async def get_border_levels(
        self, options: GetGameBorderLevelsModel
    ) -> List[BorderLevelModelResponse]:
        return await self.game_api.get_border_levels(options)

    async def get_border_levels_by_uuid(
        self, options: GetGameBorderLevelsModel
    ) -> BorderLevelModelResponse:
        return await self.game_api.get_border_levels_by_uuid(options)

    async def get_gear(self, options: GetGameGearModel) -> List[GearModelResponse]:
        return await self.game_api.get_gear(options)

    async def get_gear_by_uuid(self, options: GetGameGearModel) -> GearModelResponse:
        return await self.game_api.get_gear_by_uuid(options)

    async def get_stored_mmr_history(
        self, options: GetMMRStoredHistoryOptionsModel
    ) -> List[V1StoredMmrHistoryResponse] | List[HistoryMMRV2]:
        return await self.henrik_api.get_stored_mmr_history(options)

    async def get_stored_mmr_history_by_puuid(
        self, options: GetMMRStoredHistoryByPUUIDResponseModel
    ) -> List[V1StoredMmrHistoryResponse] | List[HistoryMMRV2]:
        return await self.henrik_api.get_stored_mmr_history_by_puuid(options)

    async def get_stored_matches(
        self, options: GetStoredMatchesOptionsModel
    ) -> List[StoredMatchResponseModel]:
        return await self.henrik_api.get_stored_matches(options)

    async def get_stored_matches_by_puuid(
        self, options: GetStoredMatchesByPUUIDResponseModel
    ) -> List[StoredMatchResponseModel]:
        return await self.henrik_api.get_stored_matches_by_puuid(options)

    async def get_player_match_stats(
        self,
        player_options: AccountFetchOptionsModelV2,
        match_options: GetMatchFetchOptionsModel,
    ) -> TotalPlayerStatsModel:
        try:
            match_data = await self.get_match(match_options)

            if not isinstance(match_data, MatchResponseModel):
                raise ValueError(
                    "get_player_match_stats - now work only with MatchVersion.v3"
                )

            stats = await self.game_stats.get_player_match_stats(
                player_options, match_data
            )
            return stats
        except UnauthorizedError:
            logger.error(
                "Unauthorized error occurred while fetching match data. Please check your API key and try again."
            )
            return TotalPlayerStatsModel(stats=None, duels=None)
        except ValueError as e:
            logger.error(f"{e}")
            return TotalPlayerStatsModel(stats=None, duels=None)

    async def get_player_day_wins_loses_stats(
        self, options: GetMMRHistoryByPUUIDFetchOptionsModel
    ) -> DayMMRStats:
        if options.puuid is None and options.version:
            pass

        try:
            mmr_history = await self.get_mmr_history_by_puuid(options=options)
            if not isinstance(mmr_history, MMRHistoryModelV2):
                raise ValueError("Work only with MMRHistoryVersions.v1")

            data = await self.game_stats.get_day_win_lose(mmr_history.history)

            if not data:
                raise ValueError("Not found Stats Data")

            return data
        except ValueError as e:
            logger.error(f"{e}")
            return DayMMRStats(
                mmr=0, mmr_difference=0, wins=0, losses=0, wins_percentage=0
            )

    async def get_most_played(
        self, match_options: GetMatchesFetchOptionsModel, most_common: int
    ) -> list[tuple[str, int]]:
        try:
            matches = await self.get_matches(match_options)

            converted_matches = []
            for match in matches:
                if isinstance(match, MatchResponseModel):
                    converted_matches.append(match.to_match_data_v4())
                elif isinstance(match, MatchDataV4):
                    converted_matches.append(match)

            most_played = await self.game_stats.get_most_player_played(
                converted_matches, match_options, most_common
            )
            return most_played

        except ValueError as e:
            logger.error(e)
            return []

    async def get_short_player_stats(
        self, stored_matches_options: GetStoredMatchesOptionsModel
    ) -> ShortPlayerStats:
        try:
            stored_matches_data = await self.get_stored_matches(stored_matches_options)
            short_player_stats = await self.game_stats.get_short_player_stats(
                stored_matches_data
            )
            return short_player_stats
        except ValueError as e:
            logger.error(f"{e}")

    async def get_most_played_heroes(
        self, stored_matches_options: GetStoredMatchesOptionsModel
    ) -> List[MostPlayedHeroesStats]:
        try:
            stored_matches_data = await self.get_stored_matches(stored_matches_options)
            most_played_heroes = await self.game_stats.get_most_played_heroes(
                stored_matches_data
            )
            return most_played_heroes
        except ValueError as e:
            logger.error(f"{e}")
