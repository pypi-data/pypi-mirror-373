from collections import Counter
from datetime import datetime, timezone
from typing import List, Optional

from lano_valo_py.valo_types.valo_models.match import GetMatchesFetchOptionsModel

from .valo_types.valo_models import AccountFetchOptionsModelV2
from .valo_types.valo_responses import (
    DayMMRStats,
    HistoryMMRV2,
    MatchDataV4,
    MatchKillsResponseModel,
    MatchPlayerModel,
    MatchResponseModel,
    MatchRoundModel,
    PlayerStatsModel,
    ShortPlayerStats,
    StoredMatchResponseModel,
    TotalPlayerStatsModel,
    MostPlayedHeroesStats,
)


class ValoGameStats:
    async def get_player_match_stats(
        self,
        player_options: AccountFetchOptionsModelV2,
        match: MatchResponseModel,
    ) -> TotalPlayerStatsModel:
        if not player_options.puuid and not (player_options.name or player_options.tag):
            return TotalPlayerStatsModel(stats=None, duels=None)

        if player_options.puuid:
            player = self.find_player_by_puuid(match, player_options.puuid)
        else:
            player = self.find_player_by_name_or_tag(
                match, player_options.name, player_options.tag
            )

        if not player:
            return TotalPlayerStatsModel(stats=None, duels=None)

        total_rounds = match.metadata.rounds_played

        stats = await self.calculate_stats(match.rounds, player, total_rounds)
        duels = await self.calculate_duels(match.kills)
        return TotalPlayerStatsModel(
            stats=stats, duels=duels[f"{player.name}#{player.tag}"]
        )

    async def get_day_win_lose(
        self, mmr_data: List[HistoryMMRV2]
    ) -> Optional[DayMMRStats]:
        if not mmr_data:
            return None

        today = datetime.now(timezone.utc).date()
        day_matches = list(
            filter(
                lambda obj: datetime.fromisoformat(
                    obj.date.replace("Z", "+00:00")
                ).date()
                == today,
                mmr_data,
            )
        )

        if not day_matches:
            return None

        loses_day_matches = list(
            filter(
                lambda obj: datetime.fromisoformat(
                    obj.date.replace("Z", "+00:00")
                ).date()
                == today
                and obj.last_change < 0,
                mmr_data,
            )
        )
        wins_day_matches = list(
            filter(
                lambda obj: datetime.fromisoformat(
                    obj.date.replace("Z", "+00:00")
                ).date()
                == today
                and obj.last_change > 0,
                mmr_data,
            )
        )
        sorted_data = sorted(
            day_matches,
            key=lambda obj: datetime.fromisoformat(obj.date.replace("Z", "+00:00")),
        )

        mmr_dif = sorted_data[-1].elo - sorted_data[0].elo
        win_count = len(wins_day_matches)
        lose_count = len(loses_day_matches)
        win_percent = win_count / (win_count + lose_count)
        total_mmr = sorted_data[-1].elo

        return DayMMRStats(
            mmr=total_mmr,
            mmr_difference=mmr_dif,
            wins=win_count,
            losses=lose_count,
            wins_percentage=win_percent,
        )

    def find_player_by_puuid(
        self, match_data: MatchResponseModel, puuid: Optional[str] = None
    ) -> Optional[MatchPlayerModel]:
        for player in match_data.players.all_players:
            if puuid and player.puuid == puuid:
                return player

        return None

    def find_player_by_name_or_tag(
        self,
        match_data: MatchResponseModel,
        name: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> Optional[MatchPlayerModel]:
        for player in match_data.players.all_players:
            if name and player.name == name and player.tag == tag:
                return player

        return None

    async def calculate_stats(
        self, rounds: List[MatchRoundModel], player: MatchPlayerModel, total_rounds: int
    ) -> PlayerStatsModel:
        """Calculate various player performance statistics."""
        stats = player.stats
        kill_diff = stats.kills - stats.deaths
        kd_ratio = stats.kills / stats.deaths if stats.deaths > 0 else stats.kills
        avg_kills_per_round = stats.kills / total_rounds if total_rounds > 0 else 0
        headshot_percent = (
            (
                stats.headshots
                / (stats.headshots + stats.bodyshots + stats.legshots)
                * 100
            )
            if (stats.headshots + stats.bodyshots + stats.legshots) > 0
            else 0
        )
        avg_damage_per_round = (
            player.damage_made / total_rounds if total_rounds > 0 else 0
        )
        kast = (
            (
                (stats.kills + stats.assists + (total_rounds - stats.deaths))
                / total_rounds
            )
            * 100
            if total_rounds > 0
            else 0
        )

        first_kills = 0
        first_deaths = 0

        multi_kills = 0

        for round_data in rounds:
            earliest_kill = None

            for kill_event in round_data.player_stats:
                for kill in kill_event.kill_events:
                    if (
                        earliest_kill is None
                        or kill.kill_time_in_round < earliest_kill.kill_time_in_round
                    ):
                        earliest_kill = kill

            if earliest_kill:
                if earliest_kill.killer_puuid == player.puuid:
                    first_kills += 1
                if earliest_kill.victim_puuid == player.puuid:
                    first_deaths += 1

            multi_kills += sum(
                len(s.kill_events) - 1
                for s in round_data.player_stats
                if s.player_puuid == player.puuid and len(s.kill_events) >= 3
            )

        return PlayerStatsModel(
            kill_diff=kill_diff,
            kd_ratio=round(kd_ratio, 2),
            avg_kills_per_round=round(avg_kills_per_round, 2),
            headshot_percent=round(headshot_percent, 2),
            kast=round(kast, 2),
            first_kills=first_kills,
            first_deaths=first_deaths,
            multi_kills=multi_kills,
            avg_damage_per_round=round(avg_damage_per_round, 2),
        )

    async def calculate_duels(
        self, kills: List[MatchKillsResponseModel]
    ) -> dict[str, dict[str, int]]:
        player_duel_stats: dict[str, dict[str, int]] = {}

        for round_kill in kills:
            if round_kill.killer_display_name not in player_duel_stats:
                player_duel_stats[round_kill.killer_display_name] = {}

            if (
                round_kill.victim_display_name
                not in player_duel_stats[round_kill.killer_display_name]
            ):
                player_duel_stats[round_kill.killer_display_name][
                    round_kill.victim_display_name
                ] = 0

            player_duel_stats[round_kill.killer_display_name][
                round_kill.victim_display_name
            ] += 1

        return player_duel_stats

    async def get_most_player_played(
        self,
        matches: List[MatchDataV4],
        match_options: GetMatchesFetchOptionsModel,
        most_common: int,
    ) -> list[tuple[str, int]]:
        if most_common > 10 or most_common <= 0:
            most_common = 10

        most_played = Counter(
            player.name
            for match in matches
            for player in match.players
            if player.name.lower() != match_options.name.lower()
            and player.tag.lower() != match_options.tag.lower()
        )

        return most_played.most_common(most_common)

    async def get_short_player_stats(
        self, matches: List[StoredMatchResponseModel]
    ) -> ShortPlayerStats:
        total_matches = len(matches)
        total_ties = sum(1 for match in matches if match.teams.red == match.teams.blue)

        total_wins = sum(
            1
            for match in matches
            if match.teams.red != match.teams.blue
            and match.stats.team
            == ("Red" if match.teams.red > match.teams.blue else "Blue")
        )

        total_losses = total_matches - total_wins - total_ties
        total_kills = sum(match.stats.kills for match in matches)
        total_deaths = sum(match.stats.deaths for match in matches)
        avg_kd = (
            round(total_kills / total_deaths, 2) if total_deaths > 0 else total_kills
        )
        winrate = (
            round((total_wins / total_matches) * 100, 2) if total_matches > 0 else 0
        )

        total_damage_dealt = sum(match.stats.damage.made for match in matches)
        total_rounds = sum((match.teams.red + match.teams.blue) for match in matches)

        adr_dealt = (
            round(total_damage_dealt / total_rounds, 2) if total_rounds > 0 else 0.0
        )

        most_pick_hero = Counter(
            [match.stats.character.name for match in matches]
        ).most_common()[0][0]

        return ShortPlayerStats(
            winrate=winrate,
            total_wins=total_wins,
            total_losses=total_losses,
            kd=avg_kd,
            adr=adr_dealt,
            most_picked_hero=most_pick_hero,
        )

    async def get_most_played_heroes(
        self, matches: List[StoredMatchResponseModel]
    ) -> List[MostPlayedHeroesStats]:
        most_played_heroes = Counter(
            [match.stats.character.id for match in matches]
        ).most_common(3)

        result = []
        for hero_id, _ in most_played_heroes:
            hero_matches = list(
                filter(lambda match: match.stats.character.id == hero_id, matches)
            )
            hero_matches_stats = await self.get_short_player_stats(hero_matches)
            result.append(
                MostPlayedHeroesStats(
                    hero_name=hero_matches_stats.most_picked_hero,
                    hero_id=hero_id,
                    kd=hero_matches_stats.kd,
                    total_losses=hero_matches_stats.total_losses,
                    total_wins=hero_matches_stats.total_wins,
                    winrate=hero_matches_stats.winrate,
                )
            )

        return result
