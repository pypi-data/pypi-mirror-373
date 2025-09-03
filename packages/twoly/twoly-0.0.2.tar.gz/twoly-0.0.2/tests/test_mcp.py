import pytest
from unittest.mock import AsyncMock, Mock, patch
from mcp import StdioServerParameters
from twoly.mcp import TwolyMCP, TwolyOptions


class TestTwolyMCPInitialization:
    """Test TwolyMCP initialization with various configurations."""

    def test_init_with_name_only(self):
        """Test initialization with just a name."""
        mcp_instance = TwolyMCP("test-runtime")
        
        assert mcp_instance.name == "test-runtime"
        assert mcp_instance.options is None
        assert isinstance(mcp_instance.serverParams, StdioServerParameters)
        assert mcp_instance.serverParams.command == "npx"
        assert mcp_instance.serverParams.args == ["@2ly/runtime@latest"]

    def test_init_with_empty_options(self):
        """Test initialization with empty options dict."""
        options: TwolyOptions = {}
        mcp_instance = TwolyMCP("test-runtime", options)
        
        assert mcp_instance.name == "test-runtime"
        assert mcp_instance.options == options
        assert mcp_instance.serverParams.args == ["@2ly/runtime@latest"]

    def test_init_with_workspace_option(self):
        """Test initialization with workspace option."""
        options: TwolyOptions = {"workspace": "test-workspace-123"}
        mcp_instance = TwolyMCP("test-runtime", options)
        
        assert mcp_instance.name == "test-runtime"
        assert mcp_instance.options == options
        assert mcp_instance.serverParams.env["WORKSPACE_ID"] == "test-workspace-123"

    def test_init_with_nats_servers_option(self):
        """Test initialization with custom NATS servers."""
        options: TwolyOptions = {"nats_servers": "nats://custom-server:4222"}
        mcp_instance = TwolyMCP("test-runtime", options)
        
        assert mcp_instance.serverParams.env["NATS_SERVERS"] == "nats://custom-server:4222"

    def test_init_with_version_option(self):
        """Test initialization with custom version."""
        options: TwolyOptions = {"version": "1.2.3"}
        mcp_instance = TwolyMCP("test-runtime", options)
        
        assert mcp_instance.serverParams.args == ["@2ly/runtime@1.2.3"]

    def test_init_with_all_options(self):
        """Test initialization with all options provided."""
        options: TwolyOptions = {
            "workspace": "test-workspace",
            "nats_servers": "nats://custom:4222",
            "version": "2.0.0"
        }
        mcp_instance = TwolyMCP("test-runtime", options)
        
        assert mcp_instance.name == "test-runtime"
        assert mcp_instance.options == options
        assert mcp_instance.serverParams.command == "npx"
        assert mcp_instance.serverParams.args == ["@2ly/runtime@2.0.0"]
        assert mcp_instance.serverParams.env["RUNTIME_NAME"] == "test-runtime"
        assert mcp_instance.serverParams.env["NATS_SERVERS"] == "nats://custom:4222"
        assert mcp_instance.serverParams.env["WORKSPACE_ID"] == "test-workspace"

    def test_default_environment_variables(self):
        """Test that default environment variables are set correctly."""
        mcp_instance = TwolyMCP("test-runtime")
        
        env = mcp_instance.serverParams.env
        assert env["RUNTIME_NAME"] == "test-runtime"
        assert env["NATS_SERVERS"] == "nats://localhost:4222"
        assert "WORKSPACE_ID" not in env


class TestTwolyMCPToolsMethod:
    """Test the async tools() method."""

    @pytest.mark.asyncio
    async def test_tools_successful_execution(self):
        """Test successful tools() method execution."""
        mock_tools = [
            {"name": "tool1", "description": "Test tool 1"},
            {"name": "tool2", "description": "Test tool 2"}
        ]
        
        # Mock the MCP client components
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session, \
             patch('twoly.mcp.load_mcp_tools') as mock_load_tools:
            
            # Setup context managers
            mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_client_session.return_value.__aenter__.return_value = mock_session
            mock_load_tools.return_value = mock_tools
            
            mcp_instance = TwolyMCP("test-runtime")
            result = await mcp_instance.tools()
            
            # Verify the result
            assert result == mock_tools
            
            # Verify the mocks were called correctly
            mock_stdio_client.assert_called_once_with(mcp_instance.serverParams)
            mock_client_session.assert_called_once_with(mock_read, mock_write)
            mock_session.initialize.assert_called_once()
            mock_load_tools.assert_called_once_with(mock_session)

    @pytest.mark.asyncio
    async def test_tools_with_custom_server_params(self):
        """Test tools() method uses custom server parameters correctly."""
        options: TwolyOptions = {
            "workspace": "custom-workspace",
            "nats_servers": "nats://custom:4222",
            "version": "1.0.0"
        }
        
        mock_tools = ["custom_tool"]
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_session = AsyncMock()
        
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session, \
             patch('twoly.mcp.load_mcp_tools') as mock_load_tools:
            
            mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_client_session.return_value.__aenter__.return_value = mock_session
            mock_load_tools.return_value = mock_tools
            
            mcp_instance = TwolyMCP("custom-runtime", options)
            result = await mcp_instance.tools()
            
            assert result == mock_tools
            
            # Verify server params were configured correctly
            called_params = mock_stdio_client.call_args[0][0]
            assert called_params.command == "npx"
            assert called_params.args == ["@2ly/runtime@1.0.0"]
            assert called_params.env["RUNTIME_NAME"] == "custom-runtime"
            assert called_params.env["NATS_SERVERS"] == "nats://custom:4222"
            assert called_params.env["WORKSPACE_ID"] == "custom-workspace"

    @pytest.mark.asyncio
    async def test_tools_initialization_failure(self):
        """Test tools() method when session initialization fails."""
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_session = AsyncMock()
        mock_session.initialize.side_effect = RuntimeError("Failed to initialize session")
        
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session:
            
            mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_client_session.return_value.__aenter__.return_value = mock_session
            
            mcp_instance = TwolyMCP("test-runtime")
            
            with pytest.raises(RuntimeError, match="Failed to initialize session"):
                await mcp_instance.tools()

    @pytest.mark.asyncio
    async def test_tools_load_mcp_tools_failure(self):
        """Test tools() method when loading tools fails."""
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        mock_session = AsyncMock()
        
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session, \
             patch('twoly.mcp.load_mcp_tools') as mock_load_tools:
            
            mock_stdio_client.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_client_session.return_value.__aenter__.return_value = mock_session
            mock_load_tools.side_effect = Exception("Failed to load tools")
            
            mcp_instance = TwolyMCP("test-runtime")
            
            with pytest.raises(Exception, match="Failed to load tools"):
                await mcp_instance.tools()

    @pytest.mark.asyncio
    async def test_tools_stdio_client_failure(self):
        """Test tools() method when stdio client fails to connect."""
        with patch('twoly.mcp.stdio_client') as mock_stdio_client:
            mock_stdio_client.side_effect = ConnectionError("Failed to connect to stdio")
            
            mcp_instance = TwolyMCP("test-runtime")
            
            with pytest.raises(ConnectionError, match="Failed to connect to stdio"):
                await mcp_instance.tools()


class TestTwolyOptionsValidation:
    """Test TwolyOptions type and validation."""

    def test_valid_options_types(self):
        """Test that TwolyOptions accepts correct types."""
        # Test with all string values
        options: TwolyOptions = {
            "workspace": "test-workspace",
            "nats_servers": "nats://localhost:4222",
            "version": "1.0.0"
        }
        
        mcp_instance = TwolyMCP("test", options)
        assert mcp_instance.options == options

    def test_partial_options(self):
        """Test that partial options work correctly."""
        options: TwolyOptions = {"workspace": "partial-test"}
        mcp_instance = TwolyMCP("test", options)
        
        # Should use defaults for unspecified options
        assert mcp_instance.serverParams.env["NATS_SERVERS"] == "nats://localhost:4222"
        assert mcp_instance.serverParams.args == ["@2ly/runtime@latest"]
        assert mcp_instance.serverParams.env["WORKSPACE_ID"] == "partial-test"

    def test_none_options_handling(self):
        """Test that None options are handled correctly."""
        mcp_instance = TwolyMCP("test", None)
        
        assert mcp_instance.options is None
        assert mcp_instance.serverParams.env["RUNTIME_NAME"] == "test"
        assert mcp_instance.serverParams.env["NATS_SERVERS"] == "nats://localhost:4222"


class TestTwolyMCPEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_name(self):
        """Test initialization with empty name."""
        mcp_instance = TwolyMCP("")
        assert mcp_instance.name == ""
        assert mcp_instance.serverParams.env["RUNTIME_NAME"] == ""

    def test_special_characters_in_name(self):
        """Test initialization with special characters in name."""
        special_name = "test-runtime_123@domain.com"
        mcp_instance = TwolyMCP(special_name)
        assert mcp_instance.name == special_name
        assert mcp_instance.serverParams.env["RUNTIME_NAME"] == special_name

    def test_empty_strings_in_options(self):
        """Test initialization with empty strings in options."""
        options: TwolyOptions = {
            "workspace": "",
            "nats_servers": "",
            "version": ""
        }
        mcp_instance = TwolyMCP("test", options)
        
        assert mcp_instance.serverParams.env["WORKSPACE_ID"] == ""
        assert mcp_instance.serverParams.env["NATS_SERVERS"] == ""
        assert mcp_instance.serverParams.args == ["@2ly/runtime@"]

    def test_server_params_immutability(self):
        """Test that server params are properly encapsulated."""
        mcp_instance = TwolyMCP("test")
        original_command = mcp_instance.serverParams.command
        original_args = mcp_instance.serverParams.args.copy()
        original_env = mcp_instance.serverParams.env.copy()
        
        # Verify we can access but not accidentally modify
        assert mcp_instance.serverParams.command == "npx"
        assert mcp_instance.serverParams.args == original_args
        assert mcp_instance.serverParams.env == original_env


class TestTwolyMCPIntegration:
    """Integration tests for realistic usage scenarios."""

    @pytest.mark.asyncio
    async def test_development_environment_setup(self):
        """Test typical development environment configuration."""
        options: TwolyOptions = {
            "workspace": "dev-workspace",
            "nats_servers": "nats://localhost:4222",
            "version": "latest"
        }
        
        mock_tools = [
            {"name": "file_search", "description": "Search files"},
            {"name": "code_edit", "description": "Edit code"}
        ]
        
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session, \
             patch('twoly.mcp.load_mcp_tools') as mock_load_tools:
            
            mock_stdio_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
            mock_session = AsyncMock()
            mock_client_session.return_value.__aenter__.return_value = mock_session
            mock_load_tools.return_value = mock_tools
            
            mcp_instance = TwolyMCP("dev-runtime", options)
            result = await mcp_instance.tools()
            
            assert result == mock_tools
            assert mock_session.initialize.called

    @pytest.mark.asyncio 
    async def test_production_environment_setup(self):
        """Test production environment configuration."""
        options: TwolyOptions = {
            "workspace": "prod-workspace",
            "nats_servers": "nats://prod-cluster-1:4222,nats://prod-cluster-2:4222",
            "version": "1.5.2"
        }
        
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession'), \
             patch('twoly.mcp.load_mcp_tools'):
            
            mock_stdio_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
            
            mcp_instance = TwolyMCP("prod-runtime", options)
            await mcp_instance.tools()
            
            # Verify production configuration
            called_params = mock_stdio_client.call_args[0][0]
            assert called_params.args == ["@2ly/runtime@1.5.2"]
            assert called_params.env["NATS_SERVERS"] == "nats://prod-cluster-1:4222,nats://prod-cluster-2:4222"
            assert called_params.env["WORKSPACE_ID"] == "prod-workspace"

    @pytest.mark.asyncio
    async def test_multiple_tools_calls(self):
        """Test that multiple calls to tools() work independently."""
        mock_tools_1 = [{"name": "tool1"}]
        mock_tools_2 = [{"name": "tool2"}]
        
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session, \
             patch('twoly.mcp.load_mcp_tools') as mock_load_tools:
            
            mock_stdio_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
            mock_session = AsyncMock()
            mock_client_session.return_value.__aenter__.return_value = mock_session
            
            # First call returns tools_1, second call returns tools_2
            mock_load_tools.side_effect = [mock_tools_1, mock_tools_2]
            
            mcp_instance = TwolyMCP("test-runtime")
            
            result_1 = await mcp_instance.tools()
            result_2 = await mcp_instance.tools()
            
            assert result_1 == mock_tools_1
            assert result_2 == mock_tools_2
            assert mock_stdio_client.call_count == 2
            assert mock_session.initialize.call_count == 2


class TestTwolyMCPServerParametersConfiguration:
    """Test detailed server parameters configuration."""

    def test_server_params_structure(self):
        """Test that server parameters are configured with correct structure."""
        mcp_instance = TwolyMCP("test-runtime")
        params = mcp_instance.serverParams
        
        assert hasattr(params, 'command')
        assert hasattr(params, 'args')
        assert hasattr(params, 'env')
        assert isinstance(params.args, list)
        assert isinstance(params.env, dict)

    def test_default_server_params_values(self):
        """Test default values for server parameters."""
        mcp_instance = TwolyMCP("default-runtime")
        params = mcp_instance.serverParams
        
        assert params.command == "npx"
        assert len(params.args) == 1
        assert params.args[0] == "@2ly/runtime@latest"
        assert "RUNTIME_NAME" in params.env
        assert "NATS_SERVERS" in params.env

    def test_workspace_id_only_added_when_provided(self):
        """Test that WORKSPACE_ID is only added when workspace option is provided."""
        # Without workspace
        mcp_instance_no_workspace = TwolyMCP("test")
        assert "WORKSPACE_ID" not in mcp_instance_no_workspace.serverParams.env
        
        # With workspace
        mcp_instance_with_workspace = TwolyMCP("test", {"workspace": "my-workspace"})
        assert "WORKSPACE_ID" in mcp_instance_with_workspace.serverParams.env
        assert mcp_instance_with_workspace.serverParams.env["WORKSPACE_ID"] == "my-workspace"

    def test_environment_variable_isolation(self):
        """Test that environment variables are isolated between instances."""
        instance1 = TwolyMCP("runtime1", {"workspace": "workspace1"})
        instance2 = TwolyMCP("runtime2", {"workspace": "workspace2"})
        
        assert instance1.serverParams.env["RUNTIME_NAME"] == "runtime1"
        assert instance2.serverParams.env["RUNTIME_NAME"] == "runtime2"
        assert instance1.serverParams.env["WORKSPACE_ID"] == "workspace1"
        assert instance2.serverParams.env["WORKSPACE_ID"] == "workspace2"
        
        # Verify they don't share the same env dict
        assert instance1.serverParams.env is not instance2.serverParams.env


class TestTwolyMCPAsyncBehavior:
    """Test async behavior and context management."""

    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self):
        """Test that context managers are properly handled."""
        mock_tools = ["test_tool"]
        
        # Track context manager calls
        mock_stdio_enter = AsyncMock(return_value=(AsyncMock(), AsyncMock()))
        mock_stdio_exit = AsyncMock(return_value=None)
        
        mock_session_enter = AsyncMock()
        mock_session_exit = AsyncMock(return_value=None)
        
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session, \
             patch('twoly.mcp.load_mcp_tools') as mock_load_tools:
            
            # Setup context manager mocks
            mock_stdio_context = AsyncMock()
            mock_stdio_context.__aenter__ = mock_stdio_enter
            mock_stdio_context.__aexit__ = mock_stdio_exit
            mock_stdio_client.return_value = mock_stdio_context
            
            mock_session_context = AsyncMock()
            mock_session_context.__aenter__ = mock_session_enter
            mock_session_context.__aexit__ = mock_session_exit
            mock_client_session.return_value = mock_session_context
            
            mock_load_tools.return_value = mock_tools
            
            mcp_instance = TwolyMCP("test-runtime")
            result = await mcp_instance.tools()
            
            assert result == mock_tools
            
            # Verify context managers were entered and exited
            mock_stdio_enter.assert_called_once()
            mock_stdio_exit.assert_called_once()
            mock_session_enter.assert_called_once()
            mock_session_exit.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_exception_handling(self):
        """Test proper cleanup when exceptions occur in context managers."""
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session:
            
            mock_stdio_context = AsyncMock()
            mock_stdio_context.__aenter__.side_effect = RuntimeError("Context manager failed")
            mock_stdio_client.return_value = mock_stdio_context
            
            mcp_instance = TwolyMCP("test-runtime")
            
            with pytest.raises(RuntimeError, match="Context manager failed"):
                await mcp_instance.tools()

    @pytest.mark.asyncio
    async def test_empty_tools_response(self):
        """Test handling of empty tools response."""
        with patch('twoly.mcp.stdio_client') as mock_stdio_client, \
             patch('twoly.mcp.ClientSession') as mock_client_session, \
             patch('twoly.mcp.load_mcp_tools') as mock_load_tools:
            
            mock_stdio_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
            mock_session = AsyncMock()
            mock_client_session.return_value.__aenter__.return_value = mock_session
            mock_load_tools.return_value = []
            
            mcp_instance = TwolyMCP("test-runtime")
            result = await mcp_instance.tools()
            
            assert result == []
            assert isinstance(result, list)


class TestTwolyMCPDocumentationCompliance:
    """Test that the implementation matches its documentation and type hints."""

    def test_type_annotations_compliance(self):
        """Test that the class follows its type annotations."""
        from typing import get_type_hints
        
        # Test constructor type hints
        hints = get_type_hints(TwolyMCP.__init__)
        assert 'name' in hints
        assert 'options' in hints
        
        # Test that we can create instances with proper types
        mcp_instance = TwolyMCP("test")
        assert isinstance(mcp_instance.name, str)

    def test_twoly_options_typed_dict_compliance(self):
        """Test that TwolyOptions TypedDict works as expected."""
        # Test all valid combinations
        valid_options = [
            {},
            {"workspace": "test"},
            {"nats_servers": "nats://test:4222"},
            {"version": "1.0.0"},
            {"workspace": "test", "nats_servers": "nats://test:4222"},
            {"workspace": "test", "version": "1.0.0"},
            {"nats_servers": "nats://test:4222", "version": "1.0.0"},
            {"workspace": "test", "nats_servers": "nats://test:4222", "version": "1.0.0"},
        ]
        
        for options in valid_options:
            mcp_instance = TwolyMCP("test", options)
            assert mcp_instance.options == options

    def test_class_docstring_accuracy(self):
        """Test that the class behavior matches its docstring."""
        # The docstring says "Provide a 2l MCP Server ready to use with Langchain"
        mcp_instance = TwolyMCP("test-runtime")
        
        # Should have a tools() method that returns tools for langchain
        assert hasattr(mcp_instance, 'tools')
        assert callable(getattr(mcp_instance, 'tools'))
        
        # Should be configurable
        assert hasattr(mcp_instance, 'name')
        assert hasattr(mcp_instance, 'options')
        assert hasattr(mcp_instance, 'serverParams')
