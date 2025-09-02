from geodesic.bases import _APIObject
from geodesic.account.user import User
from geodesic import raise_on_error
from geodesic.descriptors import _IntDescr, _StringDescr
from geodesic.service import RequestsServiceClient

from typing import List, Union

# Organizations client
organizations_client = RequestsServiceClient("krampus", api="organizations", version=1)


def get_organization(name: str = None):
    if name is None:
        raise ValueError("must provide organization name")
    res = raise_on_error(organizations_client.get(name))
    p = res.json()["organization"]
    if p is None:
        return None
    return Organization(**p)


def get_organizations():
    res = raise_on_error(organizations_client.get(""))
    return [Organization(**o) for o in res.json()["organizations"]]


class Organization(_APIObject):
    """The Organization class to manage groups users.

    Args:
        **organization: metadata about a particular Organization
    """

    _limit_setitem = ["name", "alias", "description", "homepage", "total_seats"]

    name = _StringDescr(doc="name of this organization")
    alias = _StringDescr(doc="alias for this organization")
    description = _StringDescr(doc="description of this organization")
    homepage = _StringDescr(doc="homepage for this organization")
    total_seats = _IntDescr(doc="total number of user seats for this organization")

    def __init__(self, **organization):
        self._client = organizations_client
        for k, v in organization.items():
            if k in ("name", "remaining_seats"):
                self._set_item(k, v)
            else:
                setattr(self, k, v)

    def create(self) -> None:
        """Creates a new Organization."""
        raise_on_error(self._client.post("", json=dict(organization=self)))

    def delete(self) -> None:
        """Deletes an Organization."""
        raise_on_error(self._client.delete(self.name))

    def save(self) -> None:
        """Updates an existing Organization."""
        raise_on_error(self._client.put(self.name, json=dict(organization=self)))

    def get_members(self) -> List[User]:
        """All of the members and admins."""
        res = raise_on_error(self._client.get(f"{self.name}/members"))
        return {
            "admins": [User(**m) for m in res.json().get("admins", [])],
            "members": [User(**m) for m in res.json().get("members", [])],
        }

    def add_members(self, members: List[User] = [], admins: List[User] = []) -> None:
        """Add members to this Organization.

        Args:
            members: a list of users to give ordinary membership to
            admins: a list of users to give admin privileges to
        """
        member_subjects = []
        for member in members:
            if isinstance(member, str):
                member_subjects.append(member)
            elif isinstance(member, User):
                member_subjects.append(member.subject)

        admin_subjects = []
        for admin in admins:
            if isinstance(admin, str):
                admin_subjects.append(admin)
            elif isinstance(admin, User):
                admin_subjects.append(admin.subject)

        raise_on_error(
            self._client.post(
                f"{self.name}/members", json=dict(members=member_subjects, admins=admin_subjects)
            )
        )

    def remove_member(self, u: Union[User, str]):
        """Remove a member from this Organization.

        Args:
            u: A User to remove
        """
        u = User(subject=u) if isinstance(u, str) else u
        raise_on_error(self._client.delete(f"{self.name}/members/{u.subject}"))

    def get_remaining_seats(self):
        """Gets the number of seats remaining in this Organization (total_seats - # of users)."""
        res = raise_on_error(self._client.get(self.name))
        return res.json()["organization"].get("remaining_seats", 0)
