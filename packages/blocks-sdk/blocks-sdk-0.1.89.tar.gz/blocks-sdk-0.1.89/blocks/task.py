import contextlib
import inspect
from typing import Optional, Type, Literal, Callable, List
from pydantic import BaseModel

from .state import BlocksState
from .base import BaseTaskDecorator

RuntimeType = Optional[Literal["python3.9", "python3.10", "python3.11", "python3.12"]]
RunnerType = Optional[Literal["small.cpu", "medium.cpu", "large.cpu", "xlarge.cpu"]]
PluginType = Optional[Literal["CLAUDE_CODE", "OPENAI_CODEX"]]

class TaskClass(BaseTaskDecorator):

    def __init__(self, func, state: BlocksState):
        super().__init__(func, state)

    @staticmethod
    def get_decorator(state: BlocksState):
        def set_task(func, task_args=None, task_kwargs=None):
            new_task = TaskClass(func, state)         
            is_function_already_wrapped_in_decorator = False
            
            def run(*args, **kwargs):
                return func(*args, **kwargs)

            # In case trigger decorator(s) were applied before job decorator
            with contextlib.suppress(AttributeError):
                # Handle multiple triggers if they exist
                if hasattr(func, 'trigger_metadata_list') and func.trigger_metadata_list:
                    for trigger_metadata in func.trigger_metadata_list:
                        trigger_kwargs = trigger_metadata.get("trigger_kwargs")
                        function_name = trigger_metadata.get("function_name")
                        function_source_code = trigger_metadata.get("function_source_code")
                        function_arg_count = trigger_metadata.get("function_arg_count")
                        trigger_alias = trigger_metadata.get("trigger_alias")
                        config_schema = trigger_metadata.get("config_schema")
                        config_class = trigger_metadata.get("config_class")

                        state.add_automation({
                            "trigger_alias": trigger_alias,
                            "function_name": function_name,
                            "function_source_code": function_source_code,
                            "function_arg_count": function_arg_count,
                            "config_schema": config_schema,
                            "config_class": config_class,
                            "parent_type": "task",
                            "trigger_kwargs": trigger_kwargs,
                            "task_kwargs": task_kwargs,
                        })

                    is_function_already_wrapped_in_decorator = True
                # Fallback to single trigger for backward compatibility
                elif hasattr(func, 'trigger_metadata') and func.trigger_metadata:
                    trigger_metadata = func.trigger_metadata
                    trigger_kwargs = trigger_metadata.get("trigger_kwargs")
                    function_name = trigger_metadata.get("function_name")
                    function_source_code = trigger_metadata.get("function_source_code")
                    function_arg_count = trigger_metadata.get("function_arg_count")
                    function_kwarg_count = trigger_metadata.get("function_kwarg_count")
                    function_kwargs_info = trigger_metadata.get("function_kwargs_info")
                    trigger_alias = trigger_metadata.get("trigger_alias")
                    config_schema = trigger_metadata.get("config_schema")
                    config_class = trigger_metadata.get("config_class")

                    state.add_automation({
                        "trigger_alias": trigger_alias,
                        "function_name": function_name,
                        "function_source_code": function_source_code,
                        "function_arg_count": function_arg_count,
                        "function_kwarg_count": function_kwarg_count,
                        "function_kwargs_info": function_kwargs_info,
                        "config_schema": config_schema,
                        "config_class": config_class,
                        "parent_type": "task",
                        "trigger_kwargs": trigger_kwargs,
                        "task_kwargs": task_kwargs,
                    })

                    is_function_already_wrapped_in_decorator = True

            if not is_function_already_wrapped_in_decorator:
                config_class = new_task.get_config_class()
                config_schema = new_task.get_config_schema() 
                function_arg_count = new_task.get_function_arg_count()
                function_kwarg_count = new_task.get_function_kwarg_count()
                function_kwargs_info = new_task.get_function_kwargs_info()
                
                run.task_metadata = {
                    "type": "task",
                    "function_name": new_task.name,
                    "function_source_code": new_task.source_code,
                    "function_arg_count": function_arg_count,
                    "function_kwarg_count": function_kwarg_count,
                    "function_kwargs_info": function_kwargs_info,
                    "config_schema": config_schema,
                    "config_class": config_class,
                    "task_kwargs": task_kwargs,
                }
            else:
                # Use metadata from the first processed trigger for consistency
                if hasattr(func, 'trigger_metadata_list') and func.trigger_metadata_list:
                    first_trigger = func.trigger_metadata_list[0]
                    config_class = first_trigger.get("config_class")
                    config_schema = first_trigger.get("config_schema")
                    function_arg_count = first_trigger.get("function_arg_count")
                else:
                    # Fallback to creating new metadata
                    config_class = new_task.get_config_class()
                    config_schema = new_task.get_config_schema() 
                    function_arg_count = new_task.get_function_arg_count()
            
            # Always set task_metadata on the returned function so subsequent @on decorators can use it
            run.task_metadata = {
                "type": "task",
                "function_name": new_task.name,
                "function_source_code": new_task.source_code,
                "function_arg_count": function_arg_count,
                "config_schema": config_schema,
                "config_class": config_class,
                "task_kwargs": task_kwargs,
            }
            return run

        def decorator(
            *decorator_args,
            runtime: RuntimeType = None,
            runner: RunnerType = None,
            name: Optional[str] = None,
            plugins: List[PluginType] = [],
            required_env_vars: List[str] = [],
            **decorator_kwargs
        ) -> Callable:
            # If decorator is used without parentheses
            if len(decorator_args) == 1 and callable(decorator_args[0]) and not decorator_kwargs:
                return set_task(decorator_args[0])
            
            # If decorator is used with parentheses
            def wrapper(func):
                # Combine typed kwargs with remaining decorator_kwargs
                all_kwargs = {
                    "runtime": runtime,
                    "name": name,
                    "runner": runner,
                    "plugins": plugins,
                    "required_env_vars": required_env_vars,
                    **decorator_kwargs
                }
                # Filter out None values to maintain backward compatibility
                task_kwargs = {k: v for k, v in all_kwargs.items() if v is not None}
                return set_task(func, task_args=decorator_args, task_kwargs=task_kwargs)
            return wrapper

        decorator.blocks_state = state
        return decorator
