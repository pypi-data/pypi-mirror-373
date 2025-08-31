
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from .exceptions import GradebookColumnNotFoundError, ChawkError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_client import User
    from .blackboard_client import BlackboardClient


class GradeColumn:
    def __init__(self, name: str, points: int, owner: str):
        #TODO: Add other useful things
        self.name = name
        self.col_type = ""
        self.points = points
        self.owner = owner

def convert_to_iso8601(date_str, time_str):
    # Combine date and time strings into one
    date_string = f"{date_str} {time_str}"

    # Parse into naive datetime
    date_obj = datetime.strptime(date_string, '%m-%d-%Y %I:%M %p')

    # Set to US/Central, respecting DST automatically
    #TODO: Get timezone from device
    local_time = date_obj.replace(tzinfo=ZoneInfo("US/Central"))

    # Convert to UTC
    utc_time = local_time.astimezone(timezone.utc)

    # Format as ISO 8601 with no seconds/milliseconds
    return utc_time.strftime('%Y-%m-%dT%H:%M:00Z')


def convert_from_iso8601(iso8601_str):
    # Replace 'Z' with '+00:00' so fromisoformat can handle it
    dt = datetime.fromisoformat(iso8601_str.replace("Z", "+00:00"))
    
    # Add utc timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to US/Central
    # TODO: Get local timezone instead of central
    local_time = dt.astimezone(ZoneInfo("US/Central"))
    
    return local_time.strftime('%m-%d-%Y %I:%M %p')

#TODO: Test these functions

class GradeClient:
    def __init__(self, parent_client: "BlackboardClient"):
        self.parent = parent_client

    def update_grade(
        self, course_id: str, column_id: str, username: str, new_value: str
    ) -> None:
        """Updates a grade in a specific column (only handles text right now)

        Args:
            course_id (str): _description_
            column_id (str): _description_
            username (str): The student in the course to update grade
            new_value (str): _description_
        """

        # Get column data for logs
        col_name = ""

        # User is made to get the name, for the logs
        user: User = self.parent.user.get_user_object(username)

        url = self.parent.endpoints.get_gradebook_column(course_id, column_id)


        response2 = self.parent.get(url)

        if response2.status_code == 200:
            data = response2.json()
            col_name = data["name"]
        else:
            raise GradebookColumnNotFoundError()

        if type(new_value) is str:
            _data = {
            "text": f"{new_value}",
        }
        elif type(new_value) is int:
            _data = {
            "score": new_value,
        } 
        else:
            raise ChawkError("Unsupported value for new_value")

        _update_grade = self.parent.endpoints.update_grade(
            course_id, column_id, username
        )

        response = self.parent.patch(url=_update_grade, json=_data)

        if response.status_code == 200:
            self.parent.logger.info(
                msg=f"{col_name} for {user.first_name} {user.last_name} was updated to: {new_value}"
            )

        else:
            try:
                error_message = response.json().get(
                    "message"
                )  # Assuming error details are in JSON format
            except ValueError:
                error_message = (
                    response.text
                )  # Fallback to plain text response if JSON parsing fails

            self.parent.logger.error(
                msg=f"Failed to update {col_name} for {user.first_name} {user.last_name}. Error: {error_message}"
            )

    # TODO: Test to make sure date format works
    def update_column_due_date(
        self, course_id: str, column_id: str, due_date: str
    ):  # column_id: str, new_date: str) -> None:
        _data = {"grading": {"due": f"{due_date}"}}

        if due_date == "":
            _data = {"grading": {"due": None}}

        url = self.parent.endpoints.get_gradebook_column(
            course_id=course_id, column_id=column_id
        )

        response = self.parent.patch(url=url, json=_data)

        if response.status_code == 200:
            # TODO: Finish this. Can it be done without 3rd party lib?
            # self.parent.logger.info(f"Assignment: {col.name} due date has been set to {convert_from_iso8601(col.due_date)}")
            pass
        else:
            try:
                # Assuming error detail are in JSON format
                error_message = response.json().get("message")
            except ValueError:
                # Fallback to plain text response if JSON parsing fails
                error_message = response.text

            self.parent.logger.error(error_message)

    # FIXME: Works in old way, update to package
    def create_gradebook_column(
        self, course_id: str, column_name: str, description: str, score: int
    ) -> None:
        data = {
            "name": f"{column_name}",
            # "displayName": f"{column_name}",
            "description": f"{description}",
            "score": {"possible": score},
            "availability": {
                "available": "Yes",
            },
        }


        make_col = self.parent.endpoints.create_column(course_id)

        response = self.parent.post(url=make_col, json=data)

        # TODO: Add other possible response codes
        if response.status_code == 201:
            self.parent.logger.info(f"Column {column_name} has been made in course {course_id}")
        else:
            raise ChawkError(f"{response.status_code}: {response.text}")


    def get_columns(self, course_id: str) -> list:
 
        url = self.parent.endpoints.get_gradebook_columns(course_id=course_id)
        all_cols = []

        response = self.parent.get(url=url) 

        if response.status_code == 200:
            data = response.json()
            #data = json.dumps(response)
            #print(data)
            all_columns = data["results"]
            #print(len(all_columns))
            #FIXME: Make this more better
            for c in all_columns:
                _name = c["name"]
                _points = c.get("score", {}).get("possible", 0)
                _cc = GradeColumn(name=_name, points=_points, owner=course_id)
                _cc.col_type = c.get("grading", {}).get("type", "Unknown")
                all_cols.append(_cc)
            
            return all_cols