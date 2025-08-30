import contextlib
import inspect

from .state import BlocksState
from .base import BaseTaskDecorator

class OnClass(BaseTaskDecorator):

    def __init__(self, func, state: BlocksState):
        super().__init__(func, state)

    @staticmethod
    def get_decorator(state: BlocksState):
        def set_trigger(func, trigger_alias=None, trigger_kwargs=None):
            new_trigger = OnClass(func, state)
            trigger_kwargs = trigger_kwargs or {}

            is_function_already_wrapped_in_task_decorator = False

            # Check if the function is already wrapped in a @task decorator
            with contextlib.suppress(AttributeError):
                if func.task_metadata:
                    function_name = func.task_metadata.get("function_name")
                    parent_type = func.task_metadata.get("type")
                    function_source_code = func.task_metadata.get("function_source_code")
                    function_arg_count = func.task_metadata.get("function_arg_count")
                    function_kwarg_count = func.task_metadata.get("function_kwarg_count")
                    function_kwargs_info = func.task_metadata.get("function_kwargs_info")
                    task_kwargs = func.task_metadata.get("task_kwargs")
                    config_schema = func.task_metadata.get("config_schema")
                    config_class = func.task_metadata.get("config_class")

                    # Create automation entry for this trigger
                    state.add_automation({
                        "trigger_alias": trigger_alias,
                        "function_name": function_name,
                        "function_source_code": function_source_code,
                        "function_arg_count": function_arg_count,
                        "function_kwarg_count": function_kwarg_count,
                        "function_kwargs_info": function_kwargs_info,
                        "config_schema": config_schema,
                        "config_class": config_class,
                        "parent_type": parent_type,
                        "trigger_kwargs": trigger_kwargs,
                        "task_kwargs": task_kwargs,
                    })

                    is_function_already_wrapped_in_task_decorator = True
            
            # Handle case where @on decorators are applied before @task
            if not is_function_already_wrapped_in_task_decorator:
                config_class = new_trigger.get_config_class()
                config_schema = new_trigger.get_config_schema() 
                function_arg_count = new_trigger.get_function_arg_count()
                function_kwarg_count = new_trigger.get_function_kwarg_count()
                function_kwargs_info = new_trigger.get_function_kwargs_info()
                
                # Initialize trigger_metadata_list if it doesn't exist
                if not hasattr(func, 'trigger_metadata_list'):
                    func.trigger_metadata_list = []
                
                # Add this trigger to the list
                func.trigger_metadata_list.append({
                    "type": "trigger",
                    "trigger_alias": trigger_alias,
                    "function_name": new_trigger.name,
                    "function_source_code": new_trigger.source_code,
                    "function_arg_count": function_arg_count,
                    "trigger_kwargs": trigger_kwargs,
                    "config_schema": config_schema,
                    "config_class": config_class
                })
                
                # Keep the old single trigger_metadata for backward compatibility
                # This will be the last applied trigger
                func.trigger_metadata = {
                    "type": "trigger",
                    "trigger_alias": trigger_alias,
                    "function_name": new_trigger.name,
                    "function_source_code": new_trigger.source_code,
                    "function_arg_count": function_arg_count,
                    "function_kwarg_count": function_kwarg_count,
                    "function_kwargs_info": function_kwargs_info,
                    "trigger_kwargs": trigger_kwargs,
                    "config_schema": config_schema,
                    "config_class": config_class
                }
            
            return func

        def decorator(*decorator_args, **decorator_kwargs):
            # If decorator is used without parentheses
            if len(decorator_args) == 1 and callable(decorator_args[0]) and not decorator_kwargs:
                return set_trigger(decorator_args[0])
            
            # If decorator is used with parentheses
            def wrapper(func):
                return set_trigger(func, decorator_args[0] if decorator_args else None, decorator_kwargs)
            return wrapper
            
        decorator.blocks_state = state
        return decorator
