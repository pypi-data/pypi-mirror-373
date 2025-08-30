import pytest
from unittest.mock import Mock
from blocks import task, on, state


class TestMultipleOnDecorators:
    """Test class for multiple @on decorator functionality."""

    def setup_method(self):
        """Clear automations before each test."""
        state.automations.clear()

    def test_multiple_on_before_task(self):
        """Test multiple @on decorators applied before @task decorator."""
        @task(name="test_multiple_before")
        @on("slack.mention")
        @on("github.issue_comment")
        def test_func(input_data):
            return input_data

        # Should create 2 automations
        assert len(state.automations) == 2
        
        # Verify both triggers are registered
        triggers = [auto["trigger_alias"] for auto in state.automations]
        assert "slack.mention" in triggers
        assert "github.issue_comment" in triggers
        
        # All should point to the same function
        for automation in state.automations:
            assert automation["function_name"] == "test_func"
            assert automation["parent_type"] == "task"

    def test_multiple_on_after_task(self):
        """Test multiple @on decorators applied after @task decorator."""
        @on("slack.mention")
        @on("github.issue_comment")
        @task(name="test_multiple_after")
        def test_func(input_data):
            return input_data

        # Should create 2 automations
        assert len(state.automations) == 2
        
        # Verify both triggers are registered
        triggers = [auto["trigger_alias"] for auto in state.automations]
        assert "slack.mention" in triggers
        assert "github.issue_comment" in triggers
        
        # All should point to the same function
        for automation in state.automations:
            assert automation["function_name"] == "test_func"
            assert automation["parent_type"] == "task"

    def test_mixed_decorator_order(self):
        """Test @on decorators mixed with @task decorator."""
        @on("github.pull_request")
        @task(name="test_mixed_order")
        @on("slack.mention")
        @on("github.issue_comment")
        def test_func(input_data):
            return input_data

        # Should create 3 automations
        assert len(state.automations) == 3
        
        # Verify all triggers are registered
        triggers = [auto["trigger_alias"] for auto in state.automations]
        assert "github.pull_request" in triggers
        assert "slack.mention" in triggers
        assert "github.issue_comment" in triggers
        
        # All should point to the same function
        for automation in state.automations:
            assert automation["function_name"] == "test_func"
            assert automation["parent_type"] == "task"

    def test_single_on_backward_compatibility(self):
        """Test that single @on decorator still works (backward compatibility)."""
        @task(name="test_single")
        @on("slack.mention")
        def test_func(input_data):
            return input_data

        # Should create 1 automation
        assert len(state.automations) == 1
        
        # Verify trigger is registered correctly
        automation = state.automations[0]
        assert automation["trigger_alias"] == "slack.mention"
        assert automation["function_name"] == "test_func"
        assert automation["parent_type"] == "task"

    def test_on_with_parameters(self):
        """Test multiple @on decorators with parameters work correctly."""
        @task(name="test_with_params")
        @on("slack.mention", param1="value1")
        @on("github.issue_comment", param2="value2")
        def test_func(input_data):
            return input_data

        # Should create 2 automations
        assert len(state.automations) == 2
        
        # Find automations by trigger
        slack_auto = next(a for a in state.automations if a["trigger_alias"] == "slack.mention")
        github_auto = next(a for a in state.automations if a["trigger_alias"] == "github.issue_comment")
        
        # Verify trigger parameters are preserved
        assert slack_auto["trigger_kwargs"] == {"param1": "value1"}
        assert github_auto["trigger_kwargs"] == {"param2": "value2"}

    def test_many_on_decorators(self):
        """Test that many @on decorators work correctly."""
        @task(name="test_many")
        @on("trigger1")
        @on("trigger2")
        @on("trigger3")
        @on("trigger4")
        @on("trigger5")
        def test_func(input_data):
            return input_data

        # Should create 5 automations
        assert len(state.automations) == 5
        
        # Verify all triggers are present
        expected_triggers = {"trigger1", "trigger2", "trigger3", "trigger4", "trigger5"}
        actual_triggers = {auto["trigger_alias"] for auto in state.automations}
        assert actual_triggers == expected_triggers

    def test_duplicate_triggers_allowed(self):
        """Test that duplicate triggers are allowed (each creates separate automation)."""
        @task(name="test_duplicates") 
        @on("slack.mention")
        @on("slack.mention")
        def test_func(input_data):
            return input_data

        # Should create 2 automations (duplicates allowed)
        assert len(state.automations) == 2
        
        # Both should be for slack.mention
        for automation in state.automations:
            assert automation["trigger_alias"] == "slack.mention"
            assert automation["function_name"] == "test_func"