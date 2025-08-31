from abc import ABC, abstractmethod
from typing import Optional

from loguru import logger

from flowllm.context.flow_context import FlowContext
from flowllm.op.base_op import BaseOp
from flowllm.op.parallel_op import ParallelOp
from flowllm.op.sequential_op import SequentialOp
from flowllm.schema.flow_response import FlowResponse
from flowllm.utils.common_utils import camel_to_snake


class BaseFlow(ABC):

    def __init__(self, name: str = "", **kwargs):
        self.name: str = name or camel_to_snake(self.__class__.__name__)
        self.flow_params: dict = kwargs

        self.flow_op: BaseOp = self.build_flow()
        self.print_flow()

    @abstractmethod
    def build_flow(self):
        ...

    def print_flow(self):
        assert self.flow_op is not None, "flow_content is not parsed!"
        logger.info(f"---------- start print flow={self.name} ----------")
        self._print_operation_tree(self.flow_op, indent=0)
        logger.info(f"---------- end print flow={self.name} ----------")

    def _print_operation_tree(self, op: BaseOp, indent: int):
        """
        Recursively print the operation tree structure.

        Args:
            op: The operation to print
            indent: Current indentation level
        """
        prefix = "  " * indent
        if isinstance(op, SequentialOp):
            logger.info(f"{prefix}Sequential Execution:")
            for i, sub_op in enumerate(op.ops):
                logger.info(f"{prefix}  Step {i + 1}:")
                self._print_operation_tree(sub_op, indent + 2)

        elif isinstance(op, ParallelOp):
            logger.info(f"{prefix}Parallel Execution:")
            for i, sub_op in enumerate(op.ops):
                logger.info(f"{prefix}  Branch {i + 1}:")
                self._print_operation_tree(sub_op, indent + 2)

        else:
            logger.info(f"{prefix}Operation: {op.name}")

    def return_callback(self, context: FlowContext):
        logger.info(f"context.response={context.response.model_dump_json()}")
        return context.response

    def __call__(self, **kwargs) -> FlowResponse:
        context = FlowContext(**kwargs)
        logger.info(f"request.params={kwargs}")

        try:
            flow_op = self.build_flow()
            flow_op(context=context)

        except Exception as e:
            logger.exception(f"flow_name={self.name} encounter error={e.args}")
            context.response.success = False
            context.response.answer = str(e.args)

        return self.return_callback(context=context)
