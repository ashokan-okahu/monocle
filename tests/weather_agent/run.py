import os

from agents import weather_agent
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from swarm.repl import run_demo_loop

from monocle_apptrace.instrumentor import setup_monocle_telemetry
from monocle_apptrace.wrap_common import llm_wrapper, task_wrapper
from monocle_apptrace.wrapper import WrapperMethod

setup_monocle_telemetry(
    workflow_name="pytorch_1",
    span_processors=[BatchSpanProcessor(ConsoleSpanExporter())],
    # wrapper_methods=[
    #             WrapperMethod(
    #                 package="swarm",
    #                 object_name="Swarm",
    #                 method="get_chat_completion",
    #                 span_name="jlt",
    #                 wrapper= llm_wrapper)
    #         ]
    )


if __name__ == "__main__":
    run_demo_loop(weather_agent, stream=True, debug=True)
