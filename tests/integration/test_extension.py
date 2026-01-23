"""Integration tests for the extension setup."""

from __future__ import annotations

from collections.abc import Callable

from docutils.parsers.rst import directives
from sphinx.testing.util import SphinxTestApp


class TestExtensionSetup:
    """Tests for extension loading and setup."""

    def test_extension_loads_successfully(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that the extension loads without errors."""
        app = make_app()

        # Check that our extension is in the list of extensions
        assert "sphinxcontrib.pydantic" in app.extensions

    def test_extension_returns_metadata(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that extension metadata is correct."""
        app = make_app()

        ext = app.extensions["sphinxcontrib.pydantic"]

        # Check version is set
        assert ext.version is not None
        assert isinstance(ext.version, str)

        # Check parallel safety flags
        assert ext.parallel_read_safe is True
        assert ext.parallel_write_safe is True


class TestConfigRegistration:
    """Tests for configuration option registration."""

    def test_model_config_options_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that model configuration options are registered."""
        app = make_app()

        assert hasattr(app.config, "sphinxcontrib_pydantic_model_show_json")
        assert hasattr(app.config, "sphinxcontrib_pydantic_model_show_field_summary")
        assert hasattr(
            app.config, "sphinxcontrib_pydantic_model_show_validator_summary"
        )
        assert hasattr(app.config, "sphinxcontrib_pydantic_model_show_config")
        assert hasattr(app.config, "sphinxcontrib_pydantic_model_signature_prefix")

    def test_field_config_options_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that field configuration options are registered."""
        app = make_app()

        assert hasattr(app.config, "sphinxcontrib_pydantic_field_show_alias")
        assert hasattr(app.config, "sphinxcontrib_pydantic_field_show_default")
        assert hasattr(app.config, "sphinxcontrib_pydantic_field_show_required")
        assert hasattr(app.config, "sphinxcontrib_pydantic_field_show_constraints")

    def test_validator_config_options_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that validator configuration options are registered."""
        app = make_app()

        assert hasattr(app.config, "sphinxcontrib_pydantic_validator_list_fields")

    def test_settings_config_options_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that settings configuration options are registered."""
        app = make_app()

        assert hasattr(app.config, "sphinxcontrib_pydantic_settings_show_json")
        assert hasattr(app.config, "sphinxcontrib_pydantic_settings_show_field_summary")
        assert hasattr(
            app.config, "sphinxcontrib_pydantic_settings_show_validator_summary"
        )
        assert hasattr(app.config, "sphinxcontrib_pydantic_settings_show_config")
        assert hasattr(app.config, "sphinxcontrib_pydantic_settings_signature_prefix")

    def test_default_values_are_set(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that default values are correctly set."""
        app = make_app()

        # Model defaults
        assert app.config.sphinxcontrib_pydantic_model_show_json is False
        assert app.config.sphinxcontrib_pydantic_model_show_field_summary is True
        assert app.config.sphinxcontrib_pydantic_model_show_validator_summary is True
        assert app.config.sphinxcontrib_pydantic_model_show_config is False
        assert app.config.sphinxcontrib_pydantic_model_signature_prefix == "model"

        # Field defaults
        assert app.config.sphinxcontrib_pydantic_field_show_alias is True
        assert app.config.sphinxcontrib_pydantic_field_show_default is True
        assert app.config.sphinxcontrib_pydantic_field_show_required is True
        assert app.config.sphinxcontrib_pydantic_field_show_constraints is True

        # Validator defaults
        assert app.config.sphinxcontrib_pydantic_validator_list_fields is True

        # Settings defaults
        assert app.config.sphinxcontrib_pydantic_settings_signature_prefix == "settings"

    def test_config_can_be_overridden(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that configuration values can be overridden."""
        app = make_app(
            confoverrides={
                "sphinxcontrib_pydantic_model_show_json": True,
                "sphinxcontrib_pydantic_model_signature_prefix": "pydantic model",
            }
        )

        assert app.config.sphinxcontrib_pydantic_model_show_json is True
        assert (
            app.config.sphinxcontrib_pydantic_model_signature_prefix == "pydantic model"
        )


class TestDirectiveRegistration:
    """Tests for directive registration."""

    def test_pydantic_model_directive_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that pydantic-model directive is registered."""
        _ = make_app()

        # The directive should be registered after app creation
        assert "pydantic-model" in directives._directives

    def test_autopydantic_model_directive_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that autopydantic-model directive is registered."""
        _ = make_app()

        assert "autopydantic-model" in directives._directives

    def test_pydantic_settings_directive_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that pydantic-settings directive is registered."""
        _ = make_app()

        assert "pydantic-settings" in directives._directives

    def test_autopydantic_settings_directive_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that autopydantic-settings directive is registered."""
        _ = make_app()

        assert "autopydantic-settings" in directives._directives


class TestAutodocHandlerRegistration:
    """Tests for autodoc event handler registration."""

    def test_autodoc_skip_member_handler_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that autodoc-skip-member handler is registered."""
        app = make_app()

        # Check that a listener is connected to the event
        listeners = app.events.listeners.get("autodoc-skip-member", [])
        assert len(listeners) > 0

        # Verify our handler is among the listeners
        handler_names = [listener.handler.__name__ for listener in listeners]
        assert "autodoc_skip_member" in handler_names

    def test_autodoc_process_docstring_handler_registered(
        self, make_app: Callable[..., SphinxTestApp]
    ) -> None:
        """Test that autodoc-process-docstring handler is registered."""
        app = make_app()

        listeners = app.events.listeners.get("autodoc-process-docstring", [])
        assert len(listeners) > 0

        handler_names = [listener.handler.__name__ for listener in listeners]
        assert "autodoc_process_docstring" in handler_names
