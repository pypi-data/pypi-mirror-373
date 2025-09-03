import logging

from xgae.utils.setup_env import setup_langfuse, setup_logging

setup_logging()
langfuse = setup_langfuse()

langfuse.span()
trace_id = langfuse.trace(name="xgae_test_trace").trace_id
logging.info(f"1 trace_id={trace_id}")
trace = langfuse.trace(id=trace_id)
logging.info(f"2 trace_id={trace.trace_id}")

trace.update(input={"task_id": "trace_input"})
trace.event(name="trace_event1", input="trace event1 input", output="trace event1 output")

span1 = trace.span(name="x_span_1", input={"task_id": "span1"})
logging.info(f"span1_name={span1}")
span1.event(name="span1_event", input="span1 event input", output="span1 event output")
span1.end(output={"result": "span1_result"})


span1 = langfuse.span(trace_id=trace.id, id=span1.id)
span2_id = span1.span(name="x_span_2", input={"task_id": "span2"}).id
logging.info(f"span2_id={span2_id}")
span2 = trace.span(id=span2_id)
span2.event(name="span2_event", input="span1 event input", output="span2 event output")
span2.end(output={"result": "span2_result"})

trace.event(name="trace_event2", input="trace event2 input", output="trace event2 output")
trace.update(output={"result": "trace_output"})