import os

import click
from click import Group
from litestar.plugins import CLIPluginProtocol
from sqlalchemy import delete
import yaml

from ..core.cli import coro
from ..core.database import session_maker
from .auth_core import hash_password
from .models import PermissionModel, RoleModel, RolePermissionAssociation, UserModel, UserRoleAssociation
from .repositories.permission_repository import PermissionRepository
from .repositories.role_repository import RoleRepository
from .repositories.user_repository import UserRepository
from .services import AuthService


def _emit_event(*args, **kwargs):
    print(*args, **kwargs)


class AuthLoader:
    def __init__(self, session):
        self.session = session
        self.permission_repository = PermissionRepository(session=self.session)
        self.role_repository = RoleRepository(session=self.session)
        self.user_repository = UserRepository(session=self.session)

    async def clear_data(self):
        await self.session.execute(delete(RolePermissionAssociation))
        await self.session.execute(delete(UserRoleAssociation))

        await self.permission_repository.delete_where(auto_commit=True)
        await self.role_repository.delete_where(auto_commit=True)
        await self.user_repository.delete_where(auto_commit=True)

    async def generate_data(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "./fixtures/auth.yaml"), "r") as stream:
            data_loaded = yaml.safe_load(stream)
            permissions = await self.permission_repository.add_many(
                [
                    PermissionModel(
                        label=permission_data.get("label"),
                        name=permission_data.get("name"),
                        app=permission_data.get("app"),
                        action=permission_data.get("action"),
                    )
                    for permission_data in data_loaded.get("permissions")
                ],
                auto_commit=True,
            )

            roles = []
            for role_data in data_loaded.get("roles"):
                role = RoleModel(
                    name=role_data.get("name"),
                    label=role_data.get("label"),
                )

                for permission in permissions:
                    if permission.name in role_data.get("permissions"):
                        role.permissions.append(permission)
                roles.append(role)

            await self.role_repository.add_many(roles, auto_commit=True)
            users = []

            for user_data in data_loaded.get("users"):
                email = user_data.get("email")
                users_roles = {role for role in user_data.get("roles")}

                user = UserModel(
                    email=email,
                    password=hash_password("password"),
                    is_enabled=True,
                    is_active=user_data.get("is_active"),
                )
                for role in roles:
                    if role.name in users_roles:
                        user.roles.append(role)
                users.append(user)
            await self.user_repository.add_many(users, auto_commit=True)

        click.secho("Success loaded auth data", fg="green")

    async def reset(self):
        await self.clear_data()
        await self.generate_data()


class AuthCLIPlugin(CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        @cli.group(help="Manage auth, load data with ``load`` command")
        @click.version_option(prog_name="mycli")
        def auth(): ...

        @auth.command(help="Load auth initial data")
        @coro
        async def load():
            async with session_maker() as session:
                auth_loader = AuthLoader(session)
                await auth_loader.clear_data()
                await auth_loader.generate_data()

        @auth.command(help="Clear auth data")
        @coro
        async def clear():
            async with session_maker() as session:
                auth_loader = AuthLoader(session)
                await auth_loader.clear_data()

        @auth.command(help="Set user password")
        @coro
        @click.argument("email")
        @click.argument("newpassword")
        async def set_user_password(email: str, newpassword: str):
            async with session_maker() as session:
                auth_service = AuthService(session=session, emit_event=_emit_event)
                await auth_service.set_user_password(email, newpassword)
