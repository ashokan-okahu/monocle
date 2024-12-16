# pylint: disable=too-few-public-methods
from monocle_apptrace.instrumentation.common.wrapper import task_wrapper
from monocle_apptrace.instrumentation.langchain import LANGCHAIN_METHODS


class WrapperMethod:
    def __init__(
            self,
            package: str,
            object_name: str,
            method: str,
            span_name: str = None,
            output_processor : list[str] = None,
            wrapper = task_wrapper
            ):
        self.package = package
        self.object = object_name
        self.method = method
        self.span_name = span_name
        self.output_processor=output_processor

        self.wrapper = wrapper

    def to_dict(self) -> dict:
        # Create a dictionary representation of the instance
        instance_dict = {
            'package': self.package,
            'object': self.object,
            'method': self.method,
            'span_name': self.span_name,
            'output_processor': self.output_processor,
            'wrapper': self.wrapper
        }
        return instance_dict


INBUILT_METHODS_LIST = LANGCHAIN_METHODS