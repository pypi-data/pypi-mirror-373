from typing import Literal
from typing import Union, List, Dict, Any

LogLevel = Literal["DEBUG", "INFO", "ERROR", "INTERNAL", "WARNING"]
JSON = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
