from langgraph.graph import MessagesState


class State(MessagesState):
    """State for the LangGraph graph."""

    mem0_user_id: str
