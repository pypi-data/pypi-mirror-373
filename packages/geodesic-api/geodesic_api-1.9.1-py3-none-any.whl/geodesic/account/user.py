from geodesic.bases import _APIObject
from geodesic.descriptors import _StringDescr
from geodesic.service import RequestsServiceClient
from geodesic.client import raise_on_error
from typing import List

# ServiceClient for the Krampus Version 1 users API.
users_client = RequestsServiceClient("krampus", api="users", version=1)

KRAMPUS_READ = "krampus:read"
KRAMPUS_WRITE = "krampus:write"
SPACETIME_READ = "spacetime:read"
SPACETIME_WRITE = "spacetime:write"
ENTANGLEMENT_READ = "entanglement:read"
ENTANGLEMENT_WRITE = "entanglement:write"
ENTANGLEMENT_SCHEMA = "entanglement:schema"
TESSERACT_READ = "tesseract:read"
TESSERACT_WRITE = "tesseract:write"
BOSON_READ = "boson:read"
BOSON_WRITE = "boson:write"
TED_WRITE = "ted:write"
FLOCK_READ = "flock:read"
FLOCK_WRITE = "flock:write"
VERTEX_WRITE = "vertex:write"

valid_permissions = [
    KRAMPUS_READ,
    KRAMPUS_WRITE,
    SPACETIME_READ,
    SPACETIME_WRITE,
    ENTANGLEMENT_READ,
    ENTANGLEMENT_WRITE,
    ENTANGLEMENT_SCHEMA,
    TESSERACT_READ,
    TESSERACT_WRITE,
    BOSON_READ,
    BOSON_WRITE,
    TED_WRITE,
    FLOCK_READ,
    FLOCK_WRITE,
    VERTEX_WRITE,
]


class User(_APIObject):
    """Represents a user in the system.

    The User class to represent user info and control/update profile and permissions.
    Certain functionality will be restricted to admins.

    Args:
        **info: metadata about a particular user, this can be used to create or update
        the User's profile.
    """

    _limit_setitem = [
        "subject",
        "alias",
        "first_name",
        "last_name",
        "middle_name",
        "email",
        "avatar",
        "pronouns",
        "bio",
    ]

    subject = _StringDescr(doc="the unique identifer of the subject")
    alias = _StringDescr(doc="the user's common name", default="")
    first_name = _StringDescr(doc="user's first name", default="")
    middle_name = _StringDescr(doc="user's middle name", default="")
    last_name = _StringDescr(doc="user's last name", default="")
    email = _StringDescr(doc="user's email address", default="")
    avatar = _StringDescr(
        doc="publically accessible link to the user's avatar/profile pic", default=""
    )
    pronouns = _StringDescr(doc="user's preferred personal pronouns", default="")
    bio = _StringDescr(doc="user's short bio", default="")
    org = _StringDescr(doc="user's organization")

    def __init__(self, **info) -> None:
        # client for the users API
        self._client = users_client
        super().__init__(**info)

    def get_roles(self) -> List[str]:
        """Gets and returns all of the roles for this user: admin/internal/user.

        Global roles CANNOT be set through the REST API.
        """
        res = raise_on_error(self._client.get(f"{self.subject}/roles"))
        return res.json()["roles"]

    def get_permissions(self) -> List[str]:
        """Gets and returns the user's permissions as a list of strings.

        Returns:
            permissions: the user's permissions for various services.
        """
        res = raise_on_error(self._client.get(f"{self.subject}/permissions"))
        return res.json()["permissions"]

    def update_permissions(self, permissions: List[str]) -> None:
        """Sets the user's permissions on the server side.

        Args:
            permissions: a list of permission strings. Only certain permissions are valid.
        """
        for permission in permissions:
            if permission not in valid_permissions:
                raise ValueError(
                    f"{permission} is not valid. Valid options are {valid_permissions}"
                )

        raise_on_error(
            self._client.put(f"{self.subject}/permissions", json=dict(permissions=permissions))
        )

    @property
    def enabled(self) -> bool:
        """Checks if this user's account is currently enabled in the system.

        Disabled accounts can't do anything.

        Returns:
            enabled: whether or not the user's account is enabled.
        """
        res = raise_on_error(self._client.get(f"{self.subject}/naughty"))
        if res.json()["naughty"]:
            return False
        return True

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Enable or disable a user's account. Only available to admins.

        Args:
            enabled: Whether to enable or disable this user's account
        """
        raise_on_error(self._client.put(f"{self.subject}/naughty", json=dict(naughty=not enabled)))

    def create(self) -> None:
        """Creates this user on the server side. Only available to admins."""
        if self.subject is None:
            raise ValueError("must create user with a 'subject' specified")
        raise_on_error(self._client.post("", json=dict(user=self)))

    def save(self) -> None:
        """Updates this user on the server side.

        Only available to the admins or the current user
        """
        if self.subject is None:
            raise ValueError("cannot update a User with no subject")
        raise_on_error(self._client.put(f"{self.subject}", json=dict(user=self)))

    def delete(self):
        """Delete this account and all associations.

        Only available to admins or the current user.
        """
        if self.subject is None:
            raise ValueError("cannot delete a User without specifying a subject")
        raise_on_error(self._client.delete(f"{self.subject}"))

    def __repr__(self) -> str:
        return f"User(subject={self.subject})"

    def __str__(self) -> str:
        st = "User:\n"
        st += f"  Subject: {self.subject}\n" if self.subject else ""
        st += f"  Alias: {self.alias}\n" if self.alias else ""
        st += f"  First Name: {self.first_name}\n" if self.first_name else ""
        st += f"  Middle Name: {self.middle_name}\n" if self.middle_name else ""
        st += f"  Last Name: {self.last_name}\n" if self.last_name else ""
        st += f"  Email: {self.email}\n" if self.email else ""
        st += f"  Avatar: {self.avatar}\n" if self.avatar else ""
        st += f"  Pronouns: {self.pronouns}\n" if self.pronouns else ""
        st += f"  Bio: {self.bio}\n" if self.bio else ""
        return st


def myself() -> User:
    """Returns the current logged in user.

    Returns:
        user: The currently logged in User.
    """
    res = raise_on_error(users_client.get("self"))
    return User(**res.json()["user"])


def get_user(subject: str) -> User:
    """Returns the requested user if the requestor has permissions.

    Args:
        subject: the subject of the requested user

    Returns:
        user: the requested User
    """
    res = raise_on_error(users_client.get(subject))
    return User(**res.json()["user"])


def get_users() -> List[User]:
    """Returns all users, if the current user has permission.

    Returns:
        users: a list of all users.
    """
    res = raise_on_error(users_client.get(""))
    return [User(**u) for u in res.json()["users"]]
