import os
import uuid
import asyncio
from enum import Enum
from pathlib import Path

# 1. 定义你的协程任务函数
async def worker_task_async(goal):
    """一个模拟工作的异步任务函数"""
    print(f"任务: 开始执行，预计耗时 {str(goal)} 秒...")
    # 必须使用 asyncio.sleep() 而不是 time.sleep()
    await asyncio.sleep(goal)
    result = "任务完成！"
    print("-> 任务: 已完成。")
    return result

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    NOT_FOUND = "NOT_FOUND"





class TaskManager:
    """一个简单的异步任务管理器"""
    def __init__(self):
        self.tasks = {}  # 使用字典来存储任务，key是task_id, value是task对象
        self.results_queue = asyncio.Queue()
        self.root_path = Path(os.getcwd())

    def create_tasks(self, task_coro, tasks_params):
        """
        批量创建并注册任务。

        Args:
            task_coro: 用于创建任务的协程函数。
            tasks_params (list): 包含任务参数的列表。

        Returns:
            list: 创建的任务ID列表。
        """
        task_ids = []
        for args in tasks_params:
            coro = task_coro(**args)
            task_id = self.create_task(coro)
            task_ids.append(task_id)
        return task_ids

    def create_task(self, coro):
        """
        创建并注册一个新任务。

        Args:
            coro: 要执行的协程。
            name (str, optional): 任务的可读名称。 Defaults to None.

        Returns:
            str: 任务的唯一ID。
        """
        task_id = str(uuid.uuid4())
        task_name = f"Task-{task_id[:8]}"

        # 使用 asyncio.create_task() 创建任务
        task = asyncio.create_task(coro, name=task_name)

        # 将任务存储在管理器中
        # 当任务完成时，通过回调函数将结果放入队列
        task.add_done_callback(
            lambda t: self._on_task_done(task_id, t)
        )
        self.tasks[task_id] = task
        print(f"任务已创建: ID={task_id}, Name={task_name}")
        return task_id

    def get_task_status(self, task_id):
        """
        查询特定任务的状态。

        Args:
            task_id (str): 要查询的任务ID。

        Returns:
            TaskStatus: 任务的当前状态。
        """
        task = self.tasks.get(task_id)
        if not task:
            return TaskStatus.NOT_FOUND

        if task.done():
            if task.cancelled():
                return TaskStatus.CANCELLED
            elif task.exception() is not None:
                return TaskStatus.ERROR
            else:
                return TaskStatus.DONE

        # asyncio.Task 没有直接的 'RUNNING' 状态。
        # 如果任务还没有完成，它要么是等待执行（PENDING），要么是正在执行（RUNNING）。
        # 这里我们简化处理，认为未完成的就是运行中。
        return TaskStatus.RUNNING

    def get_task_result(self, task_id):
        """获取已完成任务的结果，如果任务未完成或出错则返回相应信息。"""
        task = self.tasks.get(task_id)
        if self.get_task_status(task_id) == TaskStatus.DONE:
            return task.result()
        elif self.get_task_status(task_id) == TaskStatus.ERROR:
            return task.exception()
        return None

    def _on_task_done(self, task_id, task):
        """私有回调函数，在任务完成时将结果放入队列。"""
        try:
            # 将元组 (task_id, status, result) 放入队列
            self.results_queue.put_nowait(
                (task_id, TaskStatus.DONE, task.result())
            )
        except asyncio.CancelledError:
            self.results_queue.put_nowait(
                (task_id, TaskStatus.CANCELLED, None)
            )
        except Exception as e:
            self.results_queue.put_nowait(
                (task_id, TaskStatus.ERROR, e)
            )

    async def get_next_result(self):
        """
        等待并返回下一个完成的任务结果。

        如果所有任务都已提交，但没有任务完成，此方法将异步等待。

        Returns:
            tuple: 一个包含 (task_id, status, result) 的元组。
        """
        return await self.results_queue.get()

    def get_task_index(self, task_id):
        """
        获取任务在任务字典中的插入顺序索引。

        Args:
            task_id (str): 要查询的任务ID。

        Returns:
            int: 任务的索引（从0开始），如果未找到则返回-1。
        """
        try:
            # 将字典的键转换为列表并查找索引
            task_ids_list = list(self.tasks.keys())
            return task_ids_list.index(task_id)
        except ValueError:
            # 如果任务ID不存在，则返回-1
            return -1

    def set_root_path(self, root_path):
        self.root_path = Path(root_path)

async def main():
    manager = TaskManager()

    # --- 任务提交阶段 ---
    print("--- 任务提交 ---")

    tasks_to_run = [
        {"goal": 3},
        {"goal": 1},
        {"goal": 5},
        {"goal": 2},
        {"goal": 4},
    ]
    task_ids = manager.create_tasks(worker_task_async, tasks_to_run)
    print(f"\n主程序: {len(task_ids)} 个任务已提交，现在开始等待结果...\n")

    # --- 结果处理阶段 ---
    # 使用 get_next_result() 逐个获取已完成任务的结果
    print("--- 结果处理 ---")
    for i in range(len(task_ids)):
        print(f"等待第 {i + 1} 个任务完成...")
        # 此处会异步等待，直到队列中有可用的结果
        task_id, status, result = await manager.get_next_result()

        # 从管理器中获取任务名称（如果需要）
        task_name = manager.tasks[task_id].get_name()

        print(f"-> 收到结果: 任务 {task_name}, index: {manager.get_task_index(task_id)}")
        print(f"  - 状态: {status.value}")

        if status == TaskStatus.DONE:
            print(f"  - 结果: '{result}'")
        elif status == TaskStatus.ERROR:
            print(f"  - 错误: {result}")
        elif status == TaskStatus.CANCELLED:
            print("  - 结果: 任务被取消")
        print("-" * 20)

    print("\n--- 所有任务的结果都已处理完毕 ---")

    tasks_to_run = [
        {"goal": 30},
        {"goal": 10},
        {"goal": 50},
        {"goal": 20},
        {"goal": 40},
    ]
    task_ids = manager.create_tasks(worker_task_async, tasks_to_run)
    print(f"\n主程序: {len(task_ids)} 个任务已提交，现在开始等待结果...\n")

    # --- 结果处理阶段 ---
    # 使用 get_next_result() 逐个获取已完成任务的结果
    print("--- 结果处理 ---")
    for i in range(len(task_ids)):
        print(f"等待第 {i + 1} 个任务完成...")
        # 此处会异步等待，直到队列中有可用的结果
        task_id, status, result = await manager.get_next_result()

        # 从管理器中获取任务名称（如果需要）
        task_name = manager.tasks[task_id].get_name()

        print(f"-> 收到结果: 任务 {task_name}, index: {manager.get_task_index(task_id)}")
        print(f"  - 状态: {status.value}")

        if status == TaskStatus.DONE:
            print(f"  - 结果: '{result}'")
        elif status == TaskStatus.ERROR:
            print(f"  - 错误: {result}")
        elif status == TaskStatus.CANCELLED:
            print("  - 结果: 任务被取消")
        print("-" * 20)

    print("\n--- 所有任务的结果都已处理完毕 ---")


# 运行主协程
if __name__ == "__main__":
    asyncio.run(main())
    print("\n主程序: 所有任务都已完成并处理。")
