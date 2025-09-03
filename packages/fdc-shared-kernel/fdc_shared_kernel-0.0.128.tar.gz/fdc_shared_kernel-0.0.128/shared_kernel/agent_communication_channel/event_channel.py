import queue


class EventChannel:
    def __init__(self):
        self.user_to_agent_queue = queue.Queue()
        self.agent_to_user_queue = queue.Queue()

    # --- user -> agent ---
    def send_user_query(self, user_query: str):
        self.user_to_agent_queue.put(
            {"event": "UserSendsInput", "payload": {"message": user_query}}
        )

    def wait_for_user_input(self) -> str:
        while True:
            event = self.user_to_agent_queue.get()
            if event.get("event") == "UserSendsInput":
                return event["payload"]["message"]

    # --- agent -> user ---
    def publish_event(self, event_name: str, payload: dict = None):
        self.agent_to_user_queue.put({"event": event_name, "payload": payload or {}})

    # --- user-side convenience ---
    def provide_user_query(self, query: str):
        from shared_kernel.agent_communication_channel.contexts import TaskContext

        return TaskContext(self, query)
