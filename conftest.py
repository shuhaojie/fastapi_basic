import asyncio
import threading


async def another_coroutine():
    print("another_coroutine")


# 1. 定义协程函数（用 async def 标记）
async def simple_coroutine_1(name, sleep_time):
    # 2. await 挂起协程，释放事件循环（模拟耗时操作，如网络请求/数据库查询）
    print("协程内部执行了")
    _another_coroutine = another_coroutine()
    print("先打印这个, 再打印another_coroutine")
    await _another_coroutine
    await asyncio.sleep(sleep_time)  # asyncio.sleep 是 Python 内置的异步等待函数
    return f"{name} 完成，等待了 {sleep_time} 秒"


async def simple_coroutine_2(name, sleep_time):
    # 2. await 挂起协程，释放事件循环（模拟耗时操作，如网络请求/数据库查询）
    print("协程内部执行了")
    await asyncio.sleep(sleep_time)  # asyncio.sleep 是 Python 内置的异步等待函数
    return f"{name} 完成，等待了 {sleep_time} 秒"


# 3. 主函数（事件循环的入口，必须也是协程）
async def main():
    # 启动两个协程，让事件循环调度执行
    coroutine1 = simple_coroutine_1("A", 2)
    print(f"type coroutine1:{type(coroutine1)}", f"request id: {threading.get_ident()}")
    result1 = await coroutine1
    print(result1)
    coroutine2 = simple_coroutine_2("B", 3)
    print(f"type coroutine2:{type(coroutine2)}", f"request id: {threading.get_ident()}")
    result2 = await coroutine2  # 协程 A 完成后，再执行协程 B（1秒）
    print(result2)


# 4. 启动事件循环（运行主协程）
if __name__ == "__main__":
    asyncio.run(main())  # 唯一的同步入口，负责启动和关闭事件循环
