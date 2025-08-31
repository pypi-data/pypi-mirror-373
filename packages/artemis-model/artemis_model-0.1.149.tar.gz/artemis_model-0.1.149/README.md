# artemis-model

Welcome to `artemis-model`, the backbone repository that contains all the essential models used in both the `artemis-api` and the `prophet` project. This project includes asynchronous models used by `artemis-api`, such as `Artist`, and synchronous models like `ArtistSync` for other implementations.

## Getting Started

To set up your development environment for `artemis-model`, follow these initial setup steps:

1. **Environment Setup**

```shell
cp ./alembic/.env.example ./alembic/.env
```

After copying the example environment file, make sure to fill in the `.env` file with your specific configurations.

2. **Install Dependencies**

```shell
poetry install --all-extras
```

This will install all necessary dependencies to get you started with `artemis-models` and `alembic`.

## Creating a New Model

To introduce a new model in the project, you should start by creating a mixin and then define two different model classes that inherit from this mixin.

### Example: Adding a `LoginHistory` Model

1. **Define the Mixin**
This mixin will include all the common attributes of your model.

```python
class LoginHistoryMixin:
    """
    Stores the login history of users.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_account.id"), nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(nullable=True)
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    @declared_attr
    def account(cls) -> Mapped["UserAccount"]:
        return relationship("UserAccount", back_populates="login_histories")
```

2. **Inherit from Base Classes**
Create two classes that inherit from CustomBase and CustomSyncBase respectively, using the mixin for shared attributes.

```python
class LoginHistorySync(CustomSyncBase, LoginHistoryMixin):
    pass

class LoginHistory(CustomBase, LoginHistoryMixin):
    pass
```

## Version Management and Builds

1. **Update the Project Version**

Open pyproject.toml and increment the minor version number.

2. **Build the Project**

```shell
poetry build
```

3. **Update Dependency in artemis-api/prophet**

If the build succeeds, remember to also bump the version number in the pyproject.toml of artemis-api and prophet to match the new version of artemis-model.

## Using Alembic for Model Changes

If modifications are necessary for any model:

1. **Modify the Model**
2. **Create an Alembic Revision**

```shell
alembic revision --autogenerate -m "Description of changes"
```

3. **Upgrade Database Schema**

```shell
alembic upgrade head
```

Ensure that the new Alembic script in the versions directory is committed to your git repository.
Repeat the build and version update steps as necessary after making changes.

