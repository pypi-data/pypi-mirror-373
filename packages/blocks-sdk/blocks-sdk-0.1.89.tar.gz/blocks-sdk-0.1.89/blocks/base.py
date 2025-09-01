import inspect
from typing import Optional, Type
from pydantic import BaseModel
from .state import BlocksState

class BaseTaskDecorator:
    def __init__(self, func, state: BlocksState):
        self.func = func
        self.state = state
        self.source_code = inspect.getsource(func)
        self.name = func.__name__

    def get_config_class(self):
        func = self.func
        sig = inspect.signature(func)
        params = list(sig.parameters.values())
        
        config_class: Optional[Type] = None
        is_pydantic_model = False

        if params and len(params) == 2 and params[1].annotation is not inspect.Parameter.empty:
            _config_class = params[1].annotation  # Extract the type hint
            is_pydantic_model = isinstance(_config_class, type) and issubclass(_config_class, BaseModel)
            if is_pydantic_model:
                config_class = _config_class

        return config_class

    def get_config_schema(self):
        config_class = self.get_config_class()
        if config_class:
            return config_class.model_json_schema()
        return None
    
    def get_function_arg_count(self):
        """
        Inspects a function and returns the number of required positional arguments.
        Returns:
            min_args: int - the number of required positional arguments
        """
        sig = inspect.signature(self.func)
        min_args = 0
        for param in sig.parameters.values():
            if (param.default == inspect.Parameter.empty and 
                param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD):
                min_args += 1
        
        return min_args

    def get_function_kwarg_count(self):
        """
        Inspects a function and returns the number of required keyword arguments.
        Returns:
            min_kwargs: int - the number of required keyword-only arguments
        """
        sig = inspect.signature(self.func)
        min_kwargs = 0
        for param in sig.parameters.values():
            if (param.default == inspect.Parameter.empty and 
                param.kind == inspect.Parameter.KEYWORD_ONLY):
                min_kwargs += 1
        
        return min_kwargs

    def get_function_kwargs_info(self):
        """
        Inspects a function and returns detailed information about keyword arguments.
        Returns:
            kwargs_info: list - list of dictionaries containing kwarg details
        """
        sig = inspect.signature(self.func)
        kwargs_info = []
        
        for param in sig.parameters.values():
            if param.kind == inspect.Parameter.KEYWORD_ONLY:
                param_info = {
                    "name": param.name,
                    "required": param.default == inspect.Parameter.empty,
                    "default": None if param.default == inspect.Parameter.empty else param.default,
                    "annotation": None if param.annotation == inspect.Parameter.empty else str(param.annotation)
                }
                kwargs_info.append(param_info)
        
        return kwargs_info

class BaseRepoProvider:
    def request(self, endpoint: str, params=None, method='GET', data=None):
        raise NotImplementedError
    
    def update_pull_request(self, pull_request_number = None, title = None, body = None, assignees = None, labels = None, state = None, maintainer_can_modify = None, target_branch = None):
        raise NotImplementedError

    def update_issue(self, issue_number = None, title = None, body = None, assignees = None, labels = None, state = None, state_reason = None, milestone = None):
        raise NotImplementedError

    def create_issue(self, title = None, body = None, assignees = None, labels = None, milestone = None):
        raise NotImplementedError

    def create_pull_request(self, source_branch = None, target_branch = None, title = None, body = None, draft = False, issue_number = None):
        raise NotImplementedError

    def comment_on_pull_request(self, pull_request_number = None, body = None):
        raise NotImplementedError

    def update_pull_request_comment(self, comment_id = None, body = None):
        raise NotImplementedError

    def delete_pull_request_comment(self, comment_id = None):
        raise NotImplementedError

    def comment_on_pull_request_file(self, commit_id = None, file_path = None, pull_request_number = None, body = None, line = None, position = None, side = None, start_line = None, start_side = None, reply_to_id = None, subject_type = None):
        raise NotImplementedError

    def update_issue_comment(self, comment_id = None, body = None):
        raise NotImplementedError

    def delete_issue_comment(self, comment_id = None):
        raise NotImplementedError

    def comment_on_issue(self, issue_number = None, body = None):
        raise NotImplementedError

    def reply_to_pull_request_comment(self, reply_to_id = None, pull_request_number = None, body = None):
        raise NotImplementedError

    def review_pull_request(self, pull_request_number = None, body = None, commit_id = None, comments = None):
        raise NotImplementedError
