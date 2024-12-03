import os

from opentelemetry.sdk.trace.export import BatchSpanProcessor

from monocle_apptrace.exporters.file_exporter import FileSpanAppender
from monocle_apptrace.instrumentor import setup_monocle_telemetry

setup_monocle_telemetry(
    workflow_name="weather_flow",
    span_processors=[BatchSpanProcessor(FileSpanAppender())],
    # wrapper_methods=[
    #             WrapperMethod(
    #                 package="swarm",
    #                 object_name="Swarm",
    #                 method="get_chat_completion",
    #                 span_name="jlt",
    #                 wrapper= llm_wrapper)
    #         ]
    )

from agents import weather_agent
from swarm.repl import run_demo_loop

if __name__ == "__main__":
    run_demo_loop(weather_agent, stream=True) #debug=True
