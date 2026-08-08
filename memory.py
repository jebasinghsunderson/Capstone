import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver


def get_memory():

    conn = sqlite3.connect(
        "agent_memory.db",
        check_same_thread=False
    )

    return SqliteSaver(conn)