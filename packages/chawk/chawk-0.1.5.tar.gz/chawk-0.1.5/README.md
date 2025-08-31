# Chawk 
A python wrapper of the blackboard api to simplify admin tasks such as managing courses.  

> [!WARNING]  
> This project is a work in progress. 

# Setup 
You will need to create an application to get the needed keys. You can request access to the Blackboard REST APIs through the [Developer Portal](https://developer.blackboard.com/).  


# Example of using the library 
```python

from chawk.blackboard_client import BlackboardClient


base_url = "https://blackboard.xxxx.edu"
client_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
client_secret = "xxxxxxxxxxxxxxxxxxxxxxxxx"

# Create client
client = BlackboardClient(client_id, client_secret, base_url, "example.log")

# Example usage
print(client.user.does_user_exist("00000_0"))
print(client.course.does_course_exist("00000_1"))

client.course.enroll_user(username="wilson1234", course_id="math101213", role="Student")
```

# Current Functions  

## User
```python
    create_user(username: str, f_name: str, l_name: str, email: str, password: str) -> None
    does_user_exist(username: str) -> bool
    update_email(username: str, email: str) -> None
    update_availability(username: str, availability: str) -> None
    update_data_source(username: str, data_source_id: str) -> None
    get_course_role(username: str, course_id: str) -> str
    add_institution_roles(username: str, roles: list) -> None
    get_enrollments(username: str) -> list[Course]

```

## Course
```python
    add_child_course(course_id: str, child_id: str) -> None
    enroll_user(username: str, course_id: str, role: str = "Student") -> None
    does_course_exist(course_id: str) -> bool
    remove_user_from_course(username: str, course_id: str) -> None
    get_course_student_list(course_id: str) -> list
    create_empty_course(course_id: str, course_name: str) -> None
    copy_course_exact(master_id: str, copy_id: str) -> None
    delete_course(course_id: str) -> None
    change_user_availability(student_id: str, course_id: str, available: str = "No")
    update_course_title(course_id: str, new_name: str) -> None
    update_course_term(course_id: str, term_id: str) -> None
    update_course_availability(course_id: str, availability: str) -> None
    rename_course(course_id: str, new_name: str) -> None
    get_users_in_course_by_role(course_id: str, role: str = "") -> list[str]
```

## Discussion
```markdown

```

## Gradebook
```python
    update_grade(course_id: str, column_id: str, username: str, new_value: str) -> None
    update_column_due_date(course_id: str, column_id: str, due_date: str) -> None
    create_gradebook_column(course_id: str, column_name: str, description: str, score: int) -> None
```
