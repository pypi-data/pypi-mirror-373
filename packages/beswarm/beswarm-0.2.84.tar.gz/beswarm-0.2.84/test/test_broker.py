import asyncio
from typing import Any, List

# 将项目根目录添加到 sys.path，以便能够导入 beswarm 包
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 从 beswarm 包中导入 MessageBroker 和必要的 reaktiv 组件
from beswarm.broker import MessageBroker, Signal, untracked

# --- 模拟程序 ---

async def main():
    log_level = Signal("INFO") # "INFO" 或 "DEBUG"

    # 1. 定义几个不同的订阅者（消费者）
    # 全局配置 Signal，用于演示 untracked

    def logger_subscriber(message: Any):
        """一个记录日志的订阅者，它会参考全局 log_level 但不依赖于它。"""
        # 使用 untracked 读取 log_level 的值，这样 log_level 的变化不会触发此订阅者。
        current_level = untracked(log_level)
        if current_level == "DEBUG":
            print(f"    [详细日志]: {message}")
        else:
            # 在 INFO 级别，我们简化日志输出
            if "init" not in str(message): # 过滤掉内部的init消息
                 print(f"    [日志记录]: 收到一条新消息。")

    def auditor_subscriber(message: Any):
        """一个用于审计的订阅者，只关心包含'支付'关键字的消息"""
        if "支付" in str(message):
            print(f"    [审计跟踪]: 检测到敏感操作 -> {message}")

    async def async_notification_subscriber(message: Any):
        """一个模拟发送异步通知的订阅者"""
        print(f"    [通知服务]: 准备发送通知: '{message}'...")
        await asyncio.sleep(0.5) # 模拟网络延迟
        print(f"    [通知服务]: 通知已发送: '{message}'")

    def all_topics_subscriber(message: Any):
        """一个订阅所有主题的订阅者，用于监控"""
        print(f"    [全局监控]: 收到消息 -> {message}")

    def payment_processor_subscriber(message: Any):
        """一个只处理支付订单的订阅者"""
        print(f"    [支付处理]: 正在处理订单 -> {message}")

    async def iterator_consumer(broker: MessageBroker):
        """一个使用 async for 循环消费消息的订阅者"""
        print("迭代器消费者已启动，正在等待'系统警报'...")
        async for message in broker.iter_topic("系统警报"):
            print(f"    [迭代器消费]: !! 收到警报 !! -> {message}")
            # 在这里可以编写复杂的状态管理或流程控制逻辑
            await asyncio.sleep(0.5) # 模拟处理时间
        print("迭代器消费者已结束。")


    broker = MessageBroker(debug=True)
    # 初始化原始主题，否则派生主题会失败
    broker.publish("init", topic="常规日志")
    broker.publish("init", topic="系统警报")


    # 2. 从"常规日志"创建一个只包含支付信息的"派生主题"
    print("\n--- 创建派生主题 ---")
    def filter_payment_orders(messages: List[Any]) -> List[Any]:
        # 过滤掉初始化消息 "init"
        return [msg for msg in messages if "支付" in str(msg)]

    broker.create_derived_topic(
        new_topic_name="支付订单",
        source_topic="常规日志",
        transform_fn=filter_payment_orders
    )

    # 3. 订阅不同的主题。必须将返回的 Effect 实例存储在变量中！
    print("\n--- 创建订阅者并订阅不同主题 ---")
    sub_logger = broker.subscribe(logger_subscriber, topic="常规日志")
    sub_auditor = broker.subscribe(auditor_subscriber, topic="常规日志")
    sub_alerter = broker.subscribe(async_notification_subscriber, topic="系统警报")
    sub_payment = broker.subscribe(payment_processor_subscriber, topic="支付订单")
    sub_all_topics = broker.subscribe(all_topics_subscriber, topic=["常规日志", "系统警报"])

    # 启动新的基于迭代器的消费者
    iterator_task = asyncio.create_task(iterator_consumer(broker))

    await asyncio.sleep(1)  # 等待初始 Effect 运行

    # 4. 开始向原始主题发布消息
    print("\n--- 开始发布消息 ---")

    print("\n>>> 向 [常规日志] 主题发布 (混合消息)...")
    broker.publish("用户 'Alice' 已登录。", topic="常规日志")
    await asyncio.sleep(2)
    broker.publish("用户 'Bob' 创建了一笔价值 ¥150 的支付订单。", topic="常规日志")
    await asyncio.sleep(2)

    print("\n>>> 向 [系统警报] 主题发布...")
    broker.publish("警告: CPU 使用率超过 90%。", topic="系统警报")
    await asyncio.sleep(2)

    print("\n>>> 再次向 [常规日志] 主题发布 (另一笔支付)...")
    broker.publish("用户 'Charlie' 创建了一笔价值 ¥800 的大额支付。", topic="常规日志")
    await asyncio.sleep(2)

    # 演示 untracked 的效果
    print("\n>>> 切换日志级别为 DEBUG (不应触发任何消息处理)...")
    log_level.set("DEBUG")
    await asyncio.sleep(1)
    print("...正如所料，没有新的消息处理被触发。")

    print("\n>>> 现在发布一条新消息，应该会看到 DEBUG 格式的日志...")
    broker.publish("系统健康检查通过。", topic="常规日志")
    await asyncio.sleep(2)

    # 演示发布到多个主题
    print("\n>>> 向 [常规日志] 和 [系统警报] 同时发布一条重要消息...")
    broker.publish("警告：系统将在5分钟后重启维护！", topic=["常规日志", "系统警报"])
    await asyncio.sleep(2)

    # 5. 演示暂停和恢复功能
    print("\n--- 演示暂停和恢复功能 ---")
    print("\n>>> 暂停 [常规日志] 的日志记录器订阅...")
    sub_logger.pause()
    await asyncio.sleep(1)

    print("\n>>> 向 [常规日志] 主题发布一条消息 (日志记录器应被暂停)...")
    broker.publish("这条消息在暂停期间发出。", topic="常规日志")
    await asyncio.sleep(2) # 审计和其他订阅者应该仍然会收到此消息

    print("\n>>> 恢复 [常规日志] 的日志记录器订阅...")
    sub_logger.resume()
    await asyncio.sleep(1)

    print("\n>>> 再次向 [常规日志] 主题发布一条消息 (日志记录器应能收到)...")
    broker.publish("这条消息在恢复后发出。", topic="常规日志")
    await asyncio.sleep(2)


    # 6. 演示申请频道功能
    print("\n--- 演示申请频道功能 ---")

    # 申请一个默认前缀的频道
    new_channel_1 = broker.request_channel()
    print(f"申请到的第一个频道: {new_channel_1}")

    # 申请另一个默认前缀的频道，名称应该是唯一的
    new_channel_2 = broker.request_channel()
    print(f"申请到的第二个频道: {new_channel_2}")

    # 申请一个自定义前缀的频道
    worker_channel = broker.request_channel(prefix="worker_")
    print(f"申请到的自定义前缀频道: {worker_channel}")

    # 在新申请的频道上发布和订阅
    def new_channel_subscriber(message: Any):
        print(f"    [{new_channel_1} 订阅者]: 收到消息 -> {message}")

    sub_new = broker.subscribe(new_channel_subscriber, topic=new_channel_1)
    await asyncio.sleep(0.5)

    print(f"\n>>> 向 [{new_channel_1}] 发布消息...")
    broker.publish(f"这是发送到 {new_channel_1} 的第一条消息", topic=new_channel_1)
    await asyncio.sleep(1)

    print(f"\n>>> 向 [{new_channel_2}] 发布消息 (此频道无订阅者)...")
    broker.publish(f"一条无人理会的消息", topic=new_channel_2)
    await asyncio.sleep(1)

    print("\n--- 模拟结束 ---")

    # 在真实应用中，需要妥善管理订阅的生命周期
    all_subscriptions = [
        sub_logger,
        sub_auditor,
        sub_alerter,
        sub_payment,
        sub_all_topics,
        sub_new, # 添加新的订阅
    ]

    for sub in all_subscriptions:
        sub.dispose()
    print("所有订阅已取消。")

    # 给予迭代器任务一点时间来正常结束（虽然在真实应用中它会一直运行）
    # 在这个模拟中，当主函数结束，任务也会被取消。
    await asyncio.sleep(0.1)
    iterator_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())