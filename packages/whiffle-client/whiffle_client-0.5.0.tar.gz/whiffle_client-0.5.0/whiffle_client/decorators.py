from pathlib import Path

from functools import wraps

from whiffle_client.io import load_yaml_with_include


def load_data(class_type, resource_type=None):
    def wrap(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            data = kwargs.get("data", None)

            # Set data if lists are provided
            if data is None and len(args) == 1:
                data = args[0]
                args = ()

            if isinstance(data, str) or isinstance(data, Path):
                data = load_yaml_with_include(data, relative_to_file=True)
                if isinstance(data, list):
                    data = class_type.from_list(data)
                else:
                    data = class_type.from_dict(data, input=True)
            elif isinstance(data, dict):
                # Data directly provided as dict
                data = class_type.from_dict(data, input=True)
            elif isinstance(data, list) and all(
                isinstance(element, dict) for element in data
            ):
                data = class_type.from_list(data)
            if data:
                # pylint: disable=protected-access
                if not isinstance(data, list):
                    kwargs["data"] = data._get_api_params()
                else:
                    kwargs["data"] = [element._get_api_params() for element in data]
            else:
                raise ValueError("Please provide valid data or path to valid data")
            return func(self, *args, **kwargs)

        return wrapper

    return wrap


def request_ok(func):
    """Wrapper that checks if http request is valid (raise for status is called)

    Parameters
    ----------
    func : function
        Function
    """

    def wrapper(self, *args, **kwargs):
        request = func(self, *args, **kwargs)
        try:
            request.raise_for_status()
            return request
        except Exception:
            raise ValueError(request.text)

    return wrapper


def with_token(func):
    def wrapper(self, *args, **kwargs):
        # Update the session headers with a valid token
        access_token = self.get_valid_access_token()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
        )
        return func(self, *args, **kwargs)

    return wrapper
