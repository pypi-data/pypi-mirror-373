from typing import TYPE_CHECKING

from .exceptions import (
    AuthenticationError,
    ChawkError,
    BlackboardAPIError,
    UserNotFoundError,
)

if TYPE_CHECKING:
    from .blackboard_client import BlackboardClient
    from .course_client import Course


class User:
    """
    A class to represent a user in Blackboard
    """
    username: str
    first_name: str
    last_name: str
    email: str
    roles: list


class UserClient:
    def __init__(self, parent_client: "BlackboardClient"):
        self.parent = parent_client

    def create_user(
        self, username: str, f_name: str, l_name: str, email: str, password: str
    ) -> None:
        """Creates a user.

        Args:
            username (str): New user's ID number
            f_name (str): New user's first name
            l_name (str): New user's last name
            email (str): New user's email address
            password (str): New user's password

        Returns:
            int: _description_
        """
        username = username.strip()
        f_name = f_name.strip()
        l_name = l_name.strip()
        email = email.strip()
        password = password.strip()

        if not all([username, f_name, l_name]):
            raise ValueError(
                "Missing parameters (username, f_name, l_name)."
            )
        else:
            _data = {
                "userName": f"{username}",
                "password": f"{password}",
                "availability": {"available": "Yes"},
                "name": {
                    "given": f"{f_name}",
                    "family": f"{l_name}",
                    "preferredDisplayName": "GivenName",
                },
                "contact": {
                    "email": f"{email}",
                },
            }
            _make_user = self.parent.endpoints.create_user()
            _response = self.parent.post(_make_user, json=_data)

            match _response.status_code:
                case 201:
                    self.parent.logger.info(f"User {username}, was created successfully")
                case 403:
                    self.parent.logger.error(
                        "The currently authenticated user has insufficient privileges to create a new user."
                    )
                case 409:
                    self.parent.logger.error(
                        f"A user with the ID of {username} already exists."
                    )
                case 400:
                    self.parent.logger.error(
                        f"An error occurred while creating the new user. {_response.text}"
                    )


    def does_user_exist(self, username: str) -> bool:
        """Checks to see if a user is already added to the system.

        Args:
            username (str): _description_

        Returns:
            bool: True if user is already in the system.
        """
        url = self.parent.endpoints.get_user(username=username)

        response = self.parent.get(url)
        if response.status_code == 404:
            return False
        elif response.status_code == 401:
            raise AuthenticationError("Invalid or expired token.")
        elif response.status_code != 200:
            raise BlackboardAPIError(
                f"Unexpected response: {response.status_code} {response.text}"
            )
        return True

    # TODO: What this do?
    def get_user_object(self, username: str) -> User:
        """
        Gets a user from the system and loads their data in BBUser object.

        Args:
            username (str): The unique user ID of the user to be gathered.

        Returns:
            BBUser: _description_
        """

        username = username.strip()

        if self.does_user_exist(username):
            user: User = User()
            get_user_url = self.parent.endpoints.get_user(username=username)

            response = self.parent.get(get_user_url)
            if response.status_code == 200:
                data = response.json()
                user.roles = data["institutionRoleIds"]
                user.first_name = data["name"]["given"]
                user.last_name = data["name"]["family"]
                # TODO: Add email??
                return user
            else:
                return None



    # This works. been tested
    def get_local_username_from_id(self, username: str) -> str:
        """
        Gets a user from the system and loads their data in BBUser object.

        Args:
            username (str): The unique user ID of the user to be gathered.

        Returns:
            BBUser: _description_
        """

        get_user_data = self.parent.endpoints.get_username(username=username)

        
        response = self.parent.get(get_user_data)
        if response.status_code == 200:
            data = response.json()
            return data.get("userName", "")
        else:
            return ""


    def update_institution_email(self, username: str, i_email: str) -> None:
        _data = {
            "contact": {
                "institutionEmail": f"{i_email}",
            },
        }
        _update_i_email = (
            f"{self.parent.get_base_url()}/learn/api/public/v1/users/userName:{username}"
        )

        _response = self.parent.patch(_update_i_email, json=_data)


        if _response.status_code == 200:
            self.parent.logger.info(f"{username}'s institution email was updated to {i_email}")
        else:
            self.parent.logger.error(f"Updating {username}'s institution email failed. {_response}")

    # Good
    def update_email(self, username: str, email: str) -> None:
        # TODO: check for user first
        _data = {
            "contact": {
                "email": f"{email.strip()}",
            }
        }

        url = self.parent.endpoints.update_user(username=username)
        response = self.parent.patch(url=url, json=_data)

        if response.status_code == 200:
            self.parent.logger.info(f"User {username} email has been changed to {email}")
        else:
            self.parent.logger.error(f"Failed to update {username}. {response.text}")

    def delete_user(username: str) -> int:
        """
        Delete a user from the system.

        Args:
            username (str): The unique user ID of the user to be deleted.

        Returns:
            int: _description_
        """
        # TODO: Maybe return status code??
        # TODO: Create this function
        pass

    def update_availability(self, username: str, availability: str) -> None:
        # TODO: check for user first
        availability = availability.strip()

        if availability not in ["Disabled", "Yes", "No"]:
            raise ChawkError("'Disabled', 'Yes' or 'No' for availability")

        if self.does_user_exist(username):
            _data = {
                "availability": {"available": f"{availability}"},
            }

            # update_user = f"{ORG_DOMAIN}/learn/api/public/v1/users/userName:{username}"
            update_user = self.parent.endpoints.update_user(username=username)

            # response = patch(
            #     update_user,
            #     headers={
            #         "Authorization": "Bearer " + get_access_token(),
            #         "Content-Type": "application/json",
            #     },
            #     json=_data,
            # )

            response = self.parent.patch(url=update_user, json=_data)

            if response.status_code == 200:
                ##data = res_user_data.json()
                self.parent.logger.info(f"User {username} availability been set to {availability}")
        else:
            self.parent.logger.error(f"User {username} does not exist")

    def update_data_source(self, username: str, data_source_id: str) -> None:
        if self.does_user_exist(username):
            _data = {"dataSourceId": data_source_id}

            update_user = self.parent.endpoints.update_user(username=username)
            response = self.parent.patch(url=update_user, json=_data)

            if response.status_code == 200:
                self.parent.logger.info(f"User {username} data source set to {data_source_id}")
        else:
            raise UserNotFoundError()

    def get_course_role(self, username: str, course_id: str) -> str:
        # get_list = f"{ORG_DOMAIN}/learn/api/public/v1/courses/courseId:{course_id}/users/userName:{username}"

        url = self.parent.endpoints.course_user(course_id=course_id, username=username)

        res_user_data = self.parent.get(url=url)

        if res_user_data.status_code == 200:
            data = res_user_data.json()
            role = data["courseRoleId"]
            return role
        else:
            raise BlackboardAPIError(res_user_data.status_code)

    def add_institution_roles(self, username: str, roles: list) -> None:
        _data = {"institutionRoleIds": roles}

        url = self.parent.endpoints.update_user(username=username)
        response = self.parent.patch(url=url, json=_data)

        if response.status_code == 200:
            self.parent.logger.info(
                f"User {username} has been assigned the following roles: {', '.join(roles)}"
            )
        else:
            self.parent.logger.error(
                f"Failed to assign roles to {username}. Status Code: {response.status_code}, Response: {response.text}"
            )

    def get_enrollments(self, username: str) -> list["Course"]:
        """
        Returns a list of course objects the user is enrolled in.
        """
        url = self.parent.endpoints.user_enrollments(username=username)
        response = self.parent.get(url=url)

        if response.status_code != 200:
            self.parent.logger.error(
                f"Failed to fetch enrollments for {username}: {response.status_code}"
            )
            return []

        course_ids = []
        data = response.json().get("results", [])
        for course in data:
            course_id = course.get("courseId")
            if course_id:
                course_ids.append(course_id)

        courses = []
        for cid in course_ids:
            course_obj = self.parent.course._get_course(course_raw_id=cid)
            courses.append(course_obj)

        return courses
