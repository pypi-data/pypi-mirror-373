from pydfs_lineup_optimizer_enhanced.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer_enhanced.constants import Sport, Site
from pydfs_lineup_optimizer_enhanced.sites.fanteam.importer import FanTeamCSVImporter
from pydfs_lineup_optimizer_enhanced.sites.sites_registry import SitesRegistry

class FanTeamSettings(BaseSettings):
    site = Site.FANTEAM
    budget = 1_000_000
    csv_importer = FanTeamCSVImporter

@SitesRegistry.register_settings
class FanTeamSoccerSettings(FanTeamSettings):
    sport = Sport.SOCCER
    min_teams = 3
    max_from_one_team = 4
    # set_min_teams = True
    # set_max_from_one_team = True

    positions = [
        LineupPosition('GK', ('GK',)),
        LineupPosition('D', ('D',)),
        LineupPosition('D', ('D',)),
        LineupPosition('D', ('D',)),
        LineupPosition('M', ('M',)),
        LineupPosition('M', ('M',)),
        LineupPosition('F', ('F',)),
        LineupPosition('FLEX', ('D', 'M', 'F')),
        LineupPosition('FLEX', ('D', 'M', 'F')),
        LineupPosition('FLEX', ('D', 'M', 'F')),
        LineupPosition('FLEX', ('D', 'M', 'F')),
    ]