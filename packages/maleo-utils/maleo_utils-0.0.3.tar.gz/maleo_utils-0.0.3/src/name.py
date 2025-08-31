import inspect
from maleo.types.base.string import OptionalString


def get_fully_qualified_name() -> OptionalString:
    frame = inspect.currentframe()
    if not frame or not frame.f_back:
        return None  # No caller frame available

    caller_frame = frame.f_back
    module = inspect.getmodule(caller_frame)
    module_name = module.__name__ if module else "<unknown_module>"

    func_name = getattr(caller_frame.f_code, "co_name", "<unknown_function>")
    cls_name = None

    # Detect if we're in a class method
    if "self" in caller_frame.f_locals:
        cls_name = type(caller_frame.f_locals["self"]).__name__
    elif "cls" in caller_frame.f_locals:
        cls_name = caller_frame.f_locals["cls"].__name__

    if cls_name:
        return f"{module_name}.{cls_name}.{func_name}"
    else:
        return f"{module_name}.{func_name}"
