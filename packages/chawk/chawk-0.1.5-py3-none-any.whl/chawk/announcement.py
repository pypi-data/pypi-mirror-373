
from .exceptions import BlackboardAPIError, CourseNotFoundError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .blackboard_client import BlackboardClient


class AnnouncementClient:
    def __init__(self, parent_client: "BlackboardClient"):
        self.parent = parent_client

    def get_announcements(self) -> list:
        pass

    def get_announcement(self) -> list:
        pass

    #TODO: Look at how I did the 
    def update_announcement(self) -> list:
        pass

