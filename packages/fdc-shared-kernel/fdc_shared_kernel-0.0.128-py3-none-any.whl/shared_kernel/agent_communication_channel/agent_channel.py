from shared_kernel.agent_communication_channel.event_channel import EventChannel


class AgentChannel:
    def __init__(self, base_channel: EventChannel):
        self.channel: EventChannel = base_channel
        self._processing_started = False
        self._step_open = False
        self._streaming = False

    # ---------- public contexts ----------
    def wait_for_user_input(self):
        """Context that blocks for user input and auto-ends processing on exit."""

        class _UserInputCtx:
            def __init__(_self, outer: "AgentChannel"):
                _self._outer = outer

            def __enter__(_self):
                return _self._outer.channel.wait_for_user_input()

            def __exit__(_self, exc_type, exc, tb):
                if _self._outer._processing_started:
                    _self._outer._ensure_no_open_step()
                    _self._outer._publish("AgentProcessingEnd")
                    _self._outer._processing_started = False

        return _UserInputCtx(self)

    def start_step(self, message: str, *, is_streaming: bool = False):
        class _StepCtx:
            def __init__(_self, outer: "AgentChannel", message: str, is_streaming: bool):
                _self._outer = outer
                _self._message = message
                _self._is_streaming = is_streaming
                _self._stream_started_here = False

            def __enter__(_self):
                if not _self._outer._processing_started:
                    _self._outer._processing_started = True
                    _self._outer._publish("AgentProcessingStart")

                _self._outer._ensure_no_open_step()
                _self._outer._step_open = True
                _self._outer._publish(
                    "AgentStepExecutionStart",
                    {"message": _self._message, "is_streaming": _self._is_streaming},
                )

                if _self._is_streaming:
                    if _self._outer._streaming:
                        raise RuntimeError("Streaming already active in another step.")
                    _self._outer._streaming = True
                    _self._outer._publish("AgentDataStreamingStart")
                    _self._stream_started_here = True

                return _self

            def __exit__(_self, exc_type, exc, tb):
                if _self._stream_started_here:
                    if not _self._outer._streaming:
                        raise RuntimeError("Streaming state inconsistent at step end.")
                    _self._outer._publish("AgentDataStreamingEnd")
                    _self._outer._streaming = False

                _self._outer._ensure_step_open()
                _self._outer._publish("AgentStepExecutionEnd")
                _self._outer._step_open = False

            def send_data_response(_self, data):
                _self._outer._ensure_processing_started()
                _self._outer._publish("AgentDataResponse", {"response": data})

            def stream_chunk(_self, chunk: str):
                if not _self._is_streaming or not _self._outer._streaming:
                    raise RuntimeError("stream_chunk() called outside a streaming step.")
                _self._outer._publish("AgentDataStreamChunk", {"chunk": chunk})

        return _StepCtx(self, message, is_streaming)

    # ---------- internal helpers ----------
    def _publish(self, event: str, payload: dict = None):
        self.channel.agent_to_user_queue.put({"event": event, "payload": payload or {}})

    def _ensure_processing_started(self):
        if not self._processing_started:
            raise RuntimeError("Action requires AgentProcessingStart (not started).")

    def _ensure_step_open(self):
        if not self._step_open:
            raise RuntimeError("Action requires an open step (no step active).")

    def _ensure_no_open_step(self):
        if self._step_open:
            raise RuntimeError("A step is still open; close it before this action.")
