from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.account.account import account_with_name_password
from cattle_grid.database.account import Account, ActorStatus, ActorForAccount
from cattle_grid.account.permissions import allowed_base_urls
from cattle_grid.model.account import ActorInformation


def actor_to_information(actor: ActorForAccount) -> ActorInformation:
    """Transform ActorForAccount to its information ActorInformation

    ```pycon
    >>> actor = ActorForAccount(actor="http://base.example/actor", name="Alice")
    >>> actor_to_information(actor)
    ActorInformation(id='http://base.example/actor', name='Alice')

    ```
    """
    return ActorInformation(id=actor.actor, name=actor.name)


@dataclass
class AccountManager:
    """Access for managing accounts from outside cattle_grid, e.g.
    by an extension"""

    account: Account
    session: AsyncSession

    @staticmethod
    async def for_name_and_password(
        session: AsyncSession, name: str, password: str
    ) -> "AccountManager":
        """Returns an AccountManager for the given name and password"""
        account = await account_with_name_password(session, name, password)

        if account is None:
            raise ValueError("Account not found")

        return AccountManager(account=account, session=session)

    @staticmethod
    async def for_name(session: AsyncSession, name: str) -> "AccountManager":
        """Returns an AccountManager for a given name"""

        account = await session.scalar(select(Account).where(Account.name == name))

        if account is None:
            raise ValueError("Account not found")

        return AccountManager(account=account, session=session)

    def account_information(self) -> list[ActorInformation]:
        """Returns the actors belonging to the account"""

        return [
            actor_to_information(x)
            for x in self.account.actors
            if x.status == ActorStatus.active
        ]

    async def allowed_base_urls(self) -> list[str]:
        """Returns the list of base urls allowed for the account"""
        return await allowed_base_urls(self.session, self.account)
