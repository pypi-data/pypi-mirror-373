from bosa_server_plugins.auth.scheme import AuthenticationScheme as AuthenticationScheme
from bosa_server_plugins.cache import CacheService as CacheService
from bosa_server_plugins.github.helper.contributions import UserContributionStats as UserContributionStats, get_user_statistics as get_user_statistics
from bosa_server_plugins.github.helper.metrics import get_all_contributor_commit_activity as get_all_contributor_commit_activity, get_last_year_commit_activity as get_last_year_commit_activity, get_weekly_commit_count as get_weekly_commit_count
from bosa_server_plugins.github.requests import BasicRepositoryRequest as BasicRepositoryRequest
from bosa_server_plugins.github.requests.statistics import StatisticsRequest as StatisticsRequest
from bosa_server_plugins.handler import ExposedDefaultHeaders as ExposedDefaultHeaders, Router as Router
from typing import Callable

class GithubMetricsRoutes:
    """Github metrics Routes."""
    def __init__(self, router: Router, get_auth_scheme: Callable[[ExposedDefaultHeaders], AuthenticationScheme], cache_service: CacheService) -> None:
        """Initialize the Github metrics routes.

        Args:
            router: The router.
            get_auth_scheme: The function to get the authentication scheme.
            cache_service: The cache service.

        Returns:
            None
        """
    def exclude_breakdowns(self, obj, detailed_exclusion_only: bool = False, in_breakdown: bool = False):
        """Exclude breakdowns from a dictionary or list.

        Args:
            obj: The dictionary or list to exclude breakdowns from.
            detailed_exclusion_only: Whether to exclude detailed breakdowns only.
            in_breakdown: Whether we are currently in a breakdown field.
        """
