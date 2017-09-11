"""This module defines classes for the hjg6 door system."""

class Person(object):
    """Person class for hjg6 door system:
    Attributes:
        name: A string representing the person's name.
        email: A string representing person's email.
        nickname: A string representing person's nickname.
    """
    def __init__(self, name, email, nickname):
        self.name = name
        self.email = email
        self.nickname = nickname

    def get_email(self):
        """Returns persons email string."""
        return self.email

    def get_name(self):
        """Returns persons name string."""
        return self.name

    def get_nickname(self):
        """Returns persons nickname string."""
        return self.nickname
