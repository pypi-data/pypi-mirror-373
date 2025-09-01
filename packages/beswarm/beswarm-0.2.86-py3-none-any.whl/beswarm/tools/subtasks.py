import ast
from pathlib import Path
from ..core import current_task_manager
from ..aient.aient.plugins import register_tool, registry

worker_fun = registry.tools["worker"]

@register_tool()
def create_task(goal, tools, work_dir):
    """
    启动一个子任务来自动完成指定的任务目标 (`goal`)。

    这个子任务接收一个清晰的任务描述、一组可供调用的工具 (`tools`)，以及一个工作目录 (`work_dir`)。
    它会结合可用的工具，自主规划并逐步执行必要的操作，直到最终完成指定的任务目标。
    核心功能是根据输入的目标，驱动整个任务执行流程。
    子任务下上文为空，因此需要细致的背景信息。

    Args:
        goal (str): 需要完成的具体任务目标描述。子任务将围绕此目标进行工作。必须清晰、具体。必须包含背景信息，完成指标等。写清楚什么时候算任务完成，同时交代清楚任务的背景信息，这个背景信息可以是需要读取的文件等一切有助于完成任务的信息。
        tools (list[str]): 一个包含可用工具函数对象的列表。子任务在执行任务时可能会调用这些工具来与环境交互（例如读写文件、执行命令等）。
        work_dir (str): 工作目录的绝对路径。子任务将在此目录上下文中执行操作。子任务的工作目录位置在主任务的工作目录的子目录。子任务工作目录**禁止**设置为主任务目录本身。

    Returns:
        str: 当任务成功完成时，返回字符串 "任务已完成"。
    """
    task_manager = current_task_manager.get()
    # 获取 worker 函数，这是正确的
    worker_fun = registry.tools["worker"]

    # 将单个任务的参数封装成一个列表
    tasks_params = [
        {
            "goal": goal,
            "tools": ast.literal_eval(tools) if isinstance(tools, str) else tools,
            "work_dir": work_dir,
            "cache_messages": True
        }
    ]

    if work_dir == str(task_manager.root_path):
        return f"<tool_error>子任务的工作目录位置在主任务的工作目录的子目录。子任务工作目录**禁止**设置为主任务目录本身。请重新创建子任务。当前主任务工作目录：{task_manager.root_path}</tool_error>"

    # 调用新的批量创建接口
    task_ids = task_manager.create_tasks_batch(worker_fun, tasks_params)

    # 返回新创建的单个任务ID
    return f"子任务已提交到队列，ID: {task_ids[0]}" if task_ids else "<tool_error>任务提交失败</tool_error>"

@register_tool()
def resume_task(task_id, goal):
    """
    恢复一个子任务。
    """
    task_manager = current_task_manager.get()
    if task_id not in task_manager.tasks_cache:
        return f"任务 {task_id} 不存在"
    tasks_params = task_manager.tasks_cache[task_id]["args"]
    tasks_params["goal"] = goal
    tasks_params["cache_messages"] = True
    task_id = task_manager.resume_task(task_id, worker_fun, tasks_params)
    return f"任务 {task_id} 已恢复"

@register_tool()
def get_all_tasks_status():
    """
    获取所有任务的状态。
    子任务状态会持久化到磁盘，因此即使历史记录为空，之前的子任务仍然存在。

    Returns:
        str: 所有任务的状态。每个任务的id，状态，结果。
    """
    task_manager = current_task_manager.get()
    return task_manager.tasks_cache

@register_tool()
async def get_task_result(reduce: bool = False):
    """
    等待并获取子任务的执行结果。

    如果 `reduce` 为 `False`（默认），此工具会等待并返回任何一个子任务完成的结果。
    一旦有任务完成，它会立即获取并返回该任务的结果。如果调用时没有任务完成，它会阻塞并等待。

    如果 `reduce` 为 `True`，此工具会进入“规约”模式，等待 **所有** 正在运行或待处理的子任务都执行完毕后，
    才将所有任务的结果汇总并返回。这在子任务之间无依赖、可以完全并行执行的场景下非常有用，
    可以避免为了获取每个任务的结果而进行多次轮询，从而节省token。

    警告：当子任务之间存在依赖关系，或者需要根据一个任务的结果来决定下一步操作时，**禁止** 使用 `reduce=True`。

    Args:
        reduce (bool, optional): 是否启用规约模式。默认为 `False`。

    Returns:
        str:
        - 当 `reduce=False` 时，返回单个子任务的执行结果。
        - 当 `reduce=True` 时，返回一个包含所有任务最终状态和结果的汇总字符串。
    """
    task_manager = current_task_manager.get()
    def get_running_tasks_count():
        return len([
            task_id for task_id, task in task_manager.tasks_cache.items()
            if task_id != "root_path" and task.get("status") in ["PENDING", "RUNNING"]
        ])

    if get_running_tasks_count() == 0:
        return "All tasks are finished."

    if not reduce:
        # 默认行为：获取下一个完成的任务结果
        task_id, status, result = await task_manager.get_next_result()

        unfinished_tasks = [tid for tid, task in task_manager.tasks_cache.items() if tid != "root_path" and task.get("status") not in ["DONE", "ERROR"]]
        text = "".join([
            f"Task ID: {task_id}\n",
            f"Status: {status.value}\n",
            f"Result: {result}\n\n",
            f"There are {len(unfinished_tasks)} unfinished tasks, unfinished task ids: {unfinished_tasks[:5]} ..." if unfinished_tasks else "All tasks are finished.",
        ])
        return text
    else:
        # 规约模式：等待所有任务完成
        while get_running_tasks_count() > 0:
            await task_manager.get_next_result()

        # 收集所有任务的结果
        all_results = []
        for task_id, task in task_manager.tasks_cache.items():
            if task_id == "root_path":
                continue

            status = task.get('status', 'UNKNOWN')
            result = task.get('result', 'No result available')
            all_results.append(
                f"Task ID: {task_id}\nStatus: {status}\nResult: {result}"
            )

        summary = f"All {len(all_results)} subtasks have been completed.\n\n"
        summary += "\n\n".join(all_results)
        return summary

import os
import csv
import json
@register_tool()
def create_tasks_from_csv(goal_template: str, csv_file_path: str, tools_json_str: str, base_work_dir: str):
    """
    从一个CSV文件批量创建子任务。
    此工具读取CSV文件的每一行，使用行数据填充goal模板，然后为每一行创建一个新的子任务。
    可以使用 get_task_result 工具获取每个子任务的运行结果。

    Args:
        goal_template (str): 一个包含占位符的字符串模板。占位符的格式应为 `{column_name}`，
                             其中 `column_name` 对应CSV文件中的列名。
        csv_file_path (str): 输入的CSV文件的完整路径。CSV文件的第一行必须是列标题。
        tools_json_str (str): 一个JSON格式的字符串，表示所有子任务可用的工具列表。
                              例如: '["read_file", "write_to_file"]'。
        base_work_dir (str): 所有子任务工作目录的根路径。每个子任务将在此目录下，**必须**使用绝对路径。
                             创建一个以其唯一标识（如CSV中的id列）命名的子目录。base_work_dir **禁止** 设置为主任务目录本身。

    Returns:
        str: 批量创建任务的执行摘要，或在发生错误时返回错误信息。
    """
    task_manager = current_task_manager.get()
    # 1. 校验输入参数
    if not os.path.exists(csv_file_path):
        return f"<tool_error>CSV文件不存在: {csv_file_path}</tool_error>"

    Path(base_work_dir).mkdir(parents=True, exist_ok=True)

    try:
        tools_list = json.loads(tools_json_str)
        if not isinstance(tools_list, list):
            raise ValueError("工具列表必须是一个JSON数组。")
    except (json.JSONDecodeError, ValueError) as e:
        return f"<tool_error>解析工具列表时出错: {e}</tool_error>"

    tasks_params_list = []

    try:
        # 2. 读取并处理CSV文件
        # 增加CSV字段大小限制以处理大字段
        csv.field_size_limit(min(2**31-1, 2**20))  # 设置为1MB或系统最大值
        with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
            # 使用 DictReader 可以方便地通过列名访问数据
            reader = csv.DictReader(csvfile)

            for index, row in enumerate(reader):
                try:
                    # 3. 填充goal模板
                    # 使用.format_map()可以安全地处理模板中不存在的占位符
                    final_goal = goal_template.format_map(row)

                    # 4. 为每个任务创建独立的子工作目录
                    # 优先使用名为 'id' 或 'paper_id' 的列作为子目录名，以保证唯一性
                    # 如果没有，则使用行号作为后备
                    sub_dir_name = row.get('id', f"task_{index+1}")
                    task_work_dir = Path(base_work_dir) / sub_dir_name
                    # task_work_dir.mkdir(parents=True, exist_ok=True)

                    # 5. 准备任务参数
                    params = {
                        "goal": final_goal,
                        "tools": tools_list,
                        "work_dir": str(task_work_dir),
                        "cache_messages": True
                    }
                    tasks_params_list.append(params)

                except KeyError as e:
                    return f"<tool_error>模板填充错误：CSV文件中缺少名为 '{e}' 的列。</tool_error>"

    except Exception as e:
        return f"<tool_error>处理CSV文件时发生错误: {e}</tool_error>"

    if not tasks_params_list:
        return "CSV文件为空或格式不正确，没有创建任何任务。"

    # 6. 调用TaskManager批量提交任务
    try:
        task_ids = task_manager.create_tasks_batch(worker_fun, tasks_params_list)
        return f"成功从CSV文件提交了 {len(task_ids)} 个任务到待处理队列。"
    except Exception as e:
        return f"<tool_error>提交任务到TaskManager时发生错误: {e}</tool_error>"
