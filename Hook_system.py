import time


def fire_packet_event(environment,request_type,name,start,exception=None):
    rt = (time.perf_counter() - start) * 1000
    environment.events.request.fire(
        request_type=request_type,
        name=name,
        response_time=rt,
        response_length=0,
        exception=exception,
    )

def on_response_received(environment,protocol,start,success,error=None):
    name = f"{protocol.lower()}_response"
    fire_packet_event(
        environment,
        request_type=protocol.upper(),
        name=name,
        start=start,
        exception=None if success else (error or Exception("No response / timeout")),
    )