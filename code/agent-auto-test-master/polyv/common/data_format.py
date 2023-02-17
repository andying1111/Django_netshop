import traceback
import typing
from functools import wraps


class DataFormat(object):
    """
    接口统一返回结果格式
    """
    code: int
    status: bool
    message: object
    data: object

    def set(self, code=200, status=True, message='ok', data=None):
        self.code = code
        self.status = status
        self.message = message
        self.data = data
        return self

    def __str__(self):
        return f'{self.code}\n {self.status}\n {self.message}\n {self.data}'


def safe_agent(func: typing.Callable) -> typing.Callable:

    @wraps(func)
    def _wrapper(*args, **kwargs) -> DataFormat:
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            return DataFormat().set(
                code=400,
                status=False,
                # message=str(e),
                message=traceback.format_exc()
            )
        return DataFormat().set(
            data=result
        )

    return _wrapper
