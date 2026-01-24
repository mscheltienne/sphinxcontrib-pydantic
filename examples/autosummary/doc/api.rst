API Reference
=============

Configuration Models
--------------------

Application configuration is managed through Pydantic models that provide
validation and type safety.

.. currentmodule:: example_autosummary.models

.. autosummary::
    :toctree: generated/api
    :template: autosummary/models.rst

    UserConfig
    DatabaseConfig
    AppConfig

Database
--------

Data Transfer Objects
~~~~~~~~~~~~~~~~~~~~~

DTOs define the core data schema without persistence details.

.. currentmodule:: example_autosummary.database.dto

.. autosummary::
    :toctree: generated/api
    :template: autosummary/models.rst

    UserDTO

Table Objects
~~~~~~~~~~~~~

SQLModel table definitions for the database schema.

.. currentmodule:: example_autosummary.database.table

.. autosummary::
    :toctree: generated/api
    :template: autosummary/models.rst

    UserTable
