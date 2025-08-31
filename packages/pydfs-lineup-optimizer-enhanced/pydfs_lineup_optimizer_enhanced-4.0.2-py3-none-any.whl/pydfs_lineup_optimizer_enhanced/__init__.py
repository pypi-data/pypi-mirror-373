from pydfs_lineup_optimizer_enhanced.version import __version__
from pydfs_lineup_optimizer_enhanced.constants import Site, Sport
from pydfs_lineup_optimizer_enhanced.player import Player, LineupPlayer
from pydfs_lineup_optimizer_enhanced.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName, LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer_enhanced.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer_enhanced.lineup import Lineup
from pydfs_lineup_optimizer_enhanced.sites import SitesRegistry
from pydfs_lineup_optimizer_enhanced.lineup_exporter import CSVLineupExporter, FantasyDraftCSVLineupExporter
from pydfs_lineup_optimizer_enhanced.tz import set_timezone
from pydfs_lineup_optimizer_enhanced.stacks import PlayersGroup, TeamStack, PositionsStack, Stack
from pydfs_lineup_optimizer_enhanced.exposure_strategy import TotalExposureStrategy, AfterEachExposureStrategy
from pydfs_lineup_optimizer_enhanced.fantasy_points_strategy import StandardFantasyPointsStrategy, RandomFantasyPointsStrategy, \
    ProgressiveFantasyPointsStrategy
from pydfs_lineup_optimizer_enhanced.player_pool import PlayerFilter


__all__ = [
    'get_optimizer', 'Site', 'Sport', 'Player', 'LineupOptimizerException', 'LineupOptimizerIncorrectTeamName',
    'LineupOptimizerIncorrectPositionName', 'LineupOptimizerIncorrectCSV', 'LineupOptimizer', 'Lineup',
    'CSVLineupExporter', 'set_timezone', 'FantasyDraftCSVLineupExporter', 'PlayersGroup', 'TeamStack', 'PositionsStack',
    'Stack', 'TotalExposureStrategy', 'AfterEachExposureStrategy', 'StandardFantasyPointsStrategy',
    'RandomFantasyPointsStrategy', 'ProgressiveFantasyPointsStrategy', 'LineupPlayer', 'PlayerFilter',
]


def get_optimizer(site: str, sport: str, **kwargs) -> LineupOptimizer:
    return LineupOptimizer(SitesRegistry.get_settings(site, sport), **kwargs)
