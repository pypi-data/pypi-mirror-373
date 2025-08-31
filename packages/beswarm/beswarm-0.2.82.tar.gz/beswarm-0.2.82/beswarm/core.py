import contextvars
from .broker import MessageBroker
from .bemcp.bemcp import MCPManager
from .taskmanager import TaskManager
from .knowledge_graph import KnowledgeGraphManager

"""
全局共享实例
"""

broker = MessageBroker()
mcp_manager = MCPManager()
kgm = KnowledgeGraphManager(broker=broker)
current_task_manager = contextvars.ContextVar('current_task_manager')
current_work_dir = contextvars.ContextVar('current_work_dir', default=None)

def get_task_manager():
    """Creates a new, isolated TaskManager instance."""
    return TaskManager()
