


from .exceptions import BlackboardAPIError, CourseNotFoundError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_client import UserClient, User
    from .blackboard_client import BlackboardClient


class DiscussionClient:
    def __init__(self, parent_client: "BlackboardClient"):
        self.parent = parent_client

    def __get_discussions_ids(self, course_id: str) -> list:
        url = self.parent.endpoints.get_discussions(course_id=course_id)
        _all_users = []
        _users = []

        res_user_data = self.parent.get(url=url)

        if res_user_data.status_code == 200:
            _all_users = res_user_data.json().get("results", [])

            for user in _all_users:
                _users.append(user.get("id"))

            return _users
        else:
            self.parent.logger.error(f"Failed to get discussions for course {course_id}. Error {res_user_data.status_code}")


    def __get_messages(self, course_id: str, forum_id: str) -> list:
        get_list = self.parent.endpoints.get_messages(course_id=course_id, forum_id=forum_id)
        
        _all_users = []
        _users = []

        res_user_data = self.parent.get(url=get_list)

        if res_user_data.status_code == 200:
            _all_users = res_user_data.json().get("results", [])

            for user in _all_users:
                _users.append({"id": user.get("id"), "author": user.get("userId")})

            return _users


    def clear_discussion_student_replies(self, course_id: str, role: str = "Student") -> None:
        """_summary_

        Args:
            course_id (str): _description_
            role (str, optional): _description_. Defaults to "Student".

        Returns:
            list: _description_
        """
        all_forums = self.__get_discussions_ids(course_id)

        #TODO: TEST THIS! MIGHT BE BROKEN!
        for f in all_forums:
            for m in self.__get_messages(course_id, f):
                pass
                if self.parent.user.get_course_role(course_id, self.parent.user.get_local_username_from_id(m.get("author"))) == role:
                    self.__delete_post(course_id, f, m.get("id"))


    def __delete_post(self, course_id: str, forum_id: str, message_id: str) -> None:
        url = self.parent.endpoints.delete_message(course_id=course_id, forum_id=forum_id, message_id=message_id)

        response = self.parent.delete(url=url)

        if response.status_code == 200:
            self.parent.logger.info(f"{course_id} was deleted.")
        else:
            self.parent.logger.error(f"Failed to delete message from {course_id}. {response.text}")



