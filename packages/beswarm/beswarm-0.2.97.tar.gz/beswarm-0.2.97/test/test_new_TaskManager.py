import asyncio
import random
import uuid
from enum import Enum
from pathlib import Path
import json

# --- 核心组件 ---

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"
    ERROR = "ERROR"
    NOT_FOUND = "NOT_FOUND"

class TaskManager:
    """
    一个带并发控制的异步任务管理器。

    核心功能:
    - 维护一个待办任务队列。
    - 启动一个固定大小的并发工作者池来处理队列中的任务。
    - 确保任何时候只有指定数量的任务在“运行中”。
    - 追踪每个任务的生命周期状态（等待、运行、完成、失败）。
    - 提供异步接口来获取已完成任务的结果。
    """
    def __init__(self, concurrency_limit=5):
        if concurrency_limit <= 0:
            raise ValueError("并发限制必须大于0")

        self.concurrency_limit = concurrency_limit
        self.tasks_cache = {}          # 存储所有任务的状态和元数据, key: task_id

        self._pending_queue = asyncio.Queue() # 内部待办任务队列
        self._results_queue = asyncio.Queue() # 内部已完成任务结果队列
        self._workers = []                    # 持有工作者任务的引用
        self._is_running = False              # 标记工作者池是否在运行

        # 模拟持久化
        self.cache_dir = Path("./.beswarm_test_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.task_cache_file = self.cache_dir / "tasks.json"
        self._load_tasks_from_cache()

        print(f"TaskManager 初始化，并发限制为: {self.concurrency_limit}")

    def start(self):
        """启动并发工作者池。这个方法应该在事件循环开始后被调用一次。"""
        if self._is_running:
            print("工作者池已经在运行。")
            return

        self._is_running = True
        for i in range(self.concurrency_limit):
            worker = asyncio.create_task(self._worker_loop(f"Worker-{i+1}"))
            self._workers.append(worker)
        print(f"已启动 {self.concurrency_limit} 个并发工作者。")

    async def stop(self):
        """优雅地停止所有工作者。"""
        if not self._is_running:
            return

        print("\n正在停止 TaskManager...")
        # 等待队列中的所有任务都被领取
        await self._pending_queue.join()

        # 取消正在运行的工作者任务（如果它们还在等待队列）
        for worker in self._workers:
            worker.cancel()

        # 等待所有工作者任务完成取消操作
        await asyncio.gather(*self._workers, return_exceptions=True)

        self._is_running = False
        print("所有工作者已停止。")

    async def _worker_loop(self, worker_name: str):
        """每个工作者的主循环。"""
        print(f"[{worker_name}] 已就绪，等待任务...")
        while self._is_running:
            try:
                # 从待处理队列中异步获取任务定义
                # 这将阻塞，直到有任务可用
                task_id, coro, args = await self._pending_queue.get()

                print(f"[{worker_name}] 领到了任务 <{task_id[:8]}>，开始执行...")
                self._update_task_status(task_id, TaskStatus.RUNNING)

                try:
                    result = await coro
                    # 任务成功完成
                    self._handle_task_completion(task_id, TaskStatus.DONE, result)
                except Exception as e:
                    # 任务执行中抛出异常
                    self._handle_task_completion(task_id, TaskStatus.ERROR, e)
                finally:
                    # 确保即使任务失败，队列的计数器也能正确减少
                    self._pending_queue.task_done()

            except asyncio.CancelledError:
                # 当 stop() 方法被调用时，工作者会被取消
                print(f"[{worker_name}] 被取消，正在退出...")
                break
            except Exception as e:
                print(f"[{worker_name}] 循环中遇到严重错误: {e}")

    def create_tasks_batch(self, task_coro_func, tasks_params_list):
        """
        批量创建任务，但不是立即执行，而是将它们放入待处理队列。
        """
        if not self._is_running:
            raise RuntimeError("TaskManager尚未启动。请先调用 start() 方法。")

        task_ids = []
        for params in tasks_params_list:
            task_id = str(uuid.uuid4())
            coro = task_coro_func(**params)

            # 初始化任务状态为 PENDING
            self._update_task_status(task_id, TaskStatus.PENDING, args=params)

            # 将任务定义放入队列
            self._pending_queue.put_nowait((task_id, coro, params))
            task_ids.append(task_id)

        print(f"已将 {len(task_ids)} 个新任务加入待处理队列。队列当前大小: {self._pending_queue.qsize()}")
        return task_ids

    def _handle_task_completion(self, task_id, status, result):
        """处理任务完成（成功或失败）的统一逻辑。"""
        if status == TaskStatus.DONE:
            print(f"✅ 任务 <{task_id[:8]}> 执行成功，结果: '{result}'")
        else: # ERROR
            print(f"❌ 任务 <{task_id[:8]}> 执行失败: {result}")

        self._update_task_status(task_id, status, result=str(result))
        self._results_queue.put_nowait((task_id, status, result))

    def _update_task_status(self, task_id, status: TaskStatus, args=None, result=None):
        """统一更新任务状态缓存并持久化。"""
        if task_id not in self.tasks_cache:
            self.tasks_cache[task_id] = {}

        current_task = self.tasks_cache[task_id]
        current_task['status'] = status.value
        if args is not None:
            current_task['args'] = args
        if result is not None:
            current_task['result'] = result

        self._save_tasks_to_cache()

    def _save_tasks_to_cache(self):
        """将当前任务缓存写入文件。"""
        try:
            with self.task_cache_file.open('w', encoding='utf-8') as f:
                json.dump(self.tasks_cache, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"警告：无法将任务状态持久化到文件: {e}")

    def _load_tasks_from_cache(self):
        """从文件加载任务缓存。"""
        try:
            content = self.task_cache_file.read_text(encoding='utf-8')
            if content:
                self.tasks_cache = json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks_cache = {}

    async def get_next_result(self):
        """异步地从结果队列中获取下一个已完成的任务结果。"""
        return await self._results_queue.get()

    def get_all_tasks_status(self):
        """获取所有已知任务的当前状态。"""
        return self.tasks_cache

# --- 模拟任务和测试主程序 ---

async def mock_worker_task(paper_id: int, fail_rate: float = 0.2):
    """
    一个模拟分析单篇论文的异步任务。
    它会随机耗时，并有一定概率失败。
    """
    sleep_time = random.uniform(2, 5)
    print(f"   [Task {paper_id}] 开始分析... (预计耗时: {sleep_time:.2f}s)")
    await asyncio.sleep(sleep_time)

    if random.random() < fail_rate:
        raise ValueError(f"分析论文 {paper_id} 时遇到随机错误！")

    return f"论文 {paper_id} 分析摘要完成"

async def main():
    """测试主函数"""
    print("--- 启动测试 ---")

    task_manager = TaskManager(concurrency_limit=3)

    try:
        task_manager.start()

        all_papers = [{"paper_id": i} for i in range(1, 11)]

        print("\n>>> 批量提交10个分析任务...")
        task_ids = task_manager.create_tasks_batch(mock_worker_task, all_papers)
        print(f"已提交的任务ID: {[tid[:8] for tid in task_ids]}")

        total_tasks_to_process = len(all_papers)
        completed_count = 0

        while completed_count < total_tasks_to_process:
            print(f"\n[主线程] 等待下一个任务完成... (已完成: {completed_count}/{total_tasks_to_process})")

            task_id, status, result = await task_manager.get_next_result()

            print(f"[主线程] 收到结果! 任务<{task_id[:8]}>, 状态: {status.value}")
            if status == TaskStatus.ERROR:
                print(f"           错误详情: {result}")
            else:
                print(f"           结果内容: {result}")

            completed_count += 1

            # 演示动态追加任务
            if completed_count == 5:
                print("\n>>> 检测到已完成5个任务，动态追加2个新任务...")
                new_papers = [{"paper_id": i} for i in range(11, 13)]
                task_manager.create_tasks_batch(mock_worker_task, new_papers)
                total_tasks_to_process += len(new_papers) # 更新总任务数

    finally:
        await task_manager.stop()
        print("\n--- 测试结束 ---")
        print("\n最终任务状态概览:")
        print(json.dumps(task_manager.get_all_tasks_status(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户手动中断。")