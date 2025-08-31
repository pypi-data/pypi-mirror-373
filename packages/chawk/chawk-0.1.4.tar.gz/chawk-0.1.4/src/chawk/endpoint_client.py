

class EndpointClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get_token(self) -> str:
        return f"{self.base_url}/learn/api/public/v1/oauth2/token"

    #COURSE 
    def add_child(self, course_id: str, child_id:str) -> str:
        return f"{self.base_url}/learn/api/public/v1/courses/courseId:{course_id}/children/courseId:{child_id}"

    def create_course(self) -> str:
        return f"{self.base_url}/learn/api/public/v3/courses"
    

    def get_course_by_raw_id(self, course_raw_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v3/courses/{course_raw_id}"

    def get_course(self, course_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v3/courses/courseId:{course_id}"

    def copy_course(self, course_id: str) -> str:
        """_summary_

        Args:
            course_id (str): The ID of the course to copy. 

        Returns:
            str: _description_
        """
        return f"{self.base_url}/learn/api/public/v2/courses/courseId:{course_id}/copy"

    def course_user(self, course_id: str, username: str) -> str:
        return f"{self.base_url}/learn/api/public/v1/courses/courseId:{course_id}/users/userName:{username}"
    
    def course_users(self, course_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v1/courses/externalId:{course_id}/users"

    def gradebook_columns(self, course_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns"
    
    def enroll_user(self, course_id: str, username: str) -> str:
        return self.course_user(course_id, username)
    
    def course_content(self, course_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v1/courses/courseId:{course_id}/contents"

    #USER 
    def create_user(self) -> str:
        return f"{self.base_url}/learn/api/public/v1/users"

    def get_user(self, username: str) -> str:
        """Return the URL for retrieving a user's info."""
        return f"{self.base_url}/learn/api/public/v1/users/userName:{username}"

    def update_user(self, username: str) -> str:
        """Return the URL for updating a user's info."""
        return self.get_user(username)

    def get_username(self, username: str) -> str:
        return f"{self.base_url}/learn/api/public/v1/users/{username}"
    
    def user_enrollments(self, username: str) -> str:
        return f"{self.base_url}/learn/api/public/v1/users/userName:{username}/courses"


    #DISCUSSION
    def get_discussions(self, course_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v1/courses/courseId:{course_id}/discussions/"

    def get_messages(self, course_id: str, forum_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v1/courses/courseId:{course_id}/discussions/{forum_id}/messages/"

    def delete_message(self, course_id: str, forum_id: str, message_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v1/courses/courseId:{course_id}/discussions/{forum_id}/messages/{message_id}/?deleteReplies=true"


    #GRADEBOOK
    def create_column(self, course_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns"
    
    def get_gradebook_columns(self, course_id: str) -> str:
        return self.create_column(course_id=course_id)

    def get_gradebook_column(self, course_id: str, column_id: str) -> str:
        return f"{self.base_url}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns/{column_id}"

    def update_grade(self, course_id: str, column_id: str, username: str) -> str:
        return f"{self.base_url}/learn/api/public/v2/courses/courseId:{course_id}/gradebook/columns/{column_id}/users/userName:{username}"


    #ANNOUNCEMENT
    def get_announcements(self, course_id: str) -> str:
        return f"learn/api/public/v1/courses/courseId:{course_id}/announcements"
    
    def post_announcements(self, course_id: str) -> str:
        return self.get_announcements(course_id)
    
    def get_announcement(self, course_id: str, announcement_id: str) -> str:
        return f"/learn/api/public/v1/courses/{course_id}/announcements/{announcement_id}"
    
    def patch_announcement(self, course_id: str, announcement_id: str) -> str:
        return self.get_announcement(course_id, announcement_id)
    