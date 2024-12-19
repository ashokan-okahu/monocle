from monocle_apptrace.instrumentation.metamodel.langchain import _helper

WORKFLOW = {
    "type": "workflow",
    "events": [
        {
            "name": "data.input",
            "attributes": [
                {
                    "_comment": "this is instruction and user query to LLM",
                    "attribute": "input",
                    "accessor": lambda arguments: _helper.extract_prompt_input(
                        arguments["args"]
                    ),
                }
            ],
        },
        {
            "name": "data.output",
            "attributes": [
                {
                    "_comment": "this is result from LLM",
                    "attribute": "response",
                    "accessor": lambda arguments: _helper.extract_prompt_output(
                        arguments["result"]
                    ),
                }
            ],
        },
    ],
}
