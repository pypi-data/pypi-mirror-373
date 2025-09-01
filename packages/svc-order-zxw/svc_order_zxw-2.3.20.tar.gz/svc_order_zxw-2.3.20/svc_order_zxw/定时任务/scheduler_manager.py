"""
定时任务管理器
用于统一管理应用中的所有定时任务
"""
import asyncio
from typing import Dict, Callable, Any
from datetime import datetime, timedelta
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

from .task1_定时更新商品表 import TASK1_更新苹果内购商品表
from .task2_定时获取动态配置 import TASK2_定时获取动态配置

logger = setup_logger(__name__)


class TaskSchedulerManager:
    """定时任务管理器"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False

    def register_task(
            self,
            task_name: str,
            task_func: Callable,
            get_db: Any = None,
            interval_minutes: int = 60,
            run_immediately: bool = True,
            **kwargs
    ):
        """
        注册定时任务

        Args:
            task_name: 任务名称
            task_func: 任务函数
            get_db: 数据库连接函数，如果为None则表示任务不需要数据库
            interval_minutes: 执行间隔（分钟）
            run_immediately: 是否启动时立即执行一次
            **kwargs: 传递给任务函数的额外参数
        """
        self.tasks[task_name] = {
            "func": task_func,
            "get_db": get_db,
            "interval": timedelta(minutes=interval_minutes),
            "run_immediately": run_immediately,
            "kwargs": kwargs,
            "last_run": None,
            "next_run": None,
            "enabled": True
        }
        logger.info(f"已注册定时任务: {task_name}, 间隔: {interval_minutes}分钟")

    async def _execute_task(self, task_name: str, task_info: Dict[str, Any]):
        """执行单个任务"""
        try:
            task_func = task_info["func"]
            get_db = task_info.get("get_db")
            kwargs = task_info.get("kwargs", {})

            logger.info(f"开始执行定时任务: {task_name}")
            start_time = datetime.now()

            # 检查是否需要数据库连接
            if get_db is not None:
                # 使用传入的get_db函数获取数据库会话
                db_generator = get_db()
                db = await db_generator.__anext__()
                try:
                    if asyncio.iscoroutinefunction(task_func):
                        await task_func(db, **kwargs)
                    else:
                        task_func(db, **kwargs)
                finally:
                    # 关闭数据库会话
                    try:
                        await db_generator.__anext__()
                    except StopAsyncIteration:
                        pass
                    await db.close()
            else:
                # 不需要数据库的任务
                if asyncio.iscoroutinefunction(task_func):
                    await task_func(**kwargs)
                else:
                    task_func(**kwargs)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 更新任务执行时间
            task_info["last_run"] = end_time
            task_info["next_run"] = end_time + task_info["interval"]

            logger.info(f"定时任务 {task_name} 执行完成，耗时: {duration:.2f}秒")

        except Exception as e:
            logger.error(f"定时任务 {task_name} 执行失败: {str(e)}", exc_info=True)

    async def _task_loop(self, task_name: str):
        """任务循环"""
        task_info = self.tasks[task_name]

        # 如果设置了立即执行，先执行一次
        if task_info["run_immediately"]:
            await self._execute_task(task_name, task_info)

        # 设置下次执行时间
        if task_info["next_run"] is None:
            task_info["next_run"] = datetime.now() + task_info["interval"]

        # 定时循环执行
        while self.is_running and task_info["enabled"]:
            try:
                now = datetime.now()
                next_run = task_info["next_run"]

                if now >= next_run:
                    await self._execute_task(task_name, task_info)

                # 等待一段时间再检查（避免过于频繁检查）
                await asyncio.sleep(30)  # 每30秒检查一次

            except asyncio.CancelledError:
                logger.info(f"定时任务 {task_name} 被取消")
                break
            except Exception as e:
                logger.error(f"定时任务 {task_name} 循环出错: {str(e)}", exc_info=True)
                await asyncio.sleep(60)  # 出错后等待1分钟再继续

    async def start_all_tasks(self):
        """启动所有已注册的任务"""
        if self.is_running:
            logger.warning("svc_order_zxw定时任务管理器已在运行")
            return

        self.is_running = True
        logger.info("svc_order_zxw启动定时任务管理器...")

        for task_name, task_info in self.tasks.items():
            if task_info["enabled"]:
                task = asyncio.create_task(self._task_loop(task_name))
                self.running_tasks[task_name] = task
                logger.info(f"启动定时任务: {task_name}")

        logger.info(f"定时任务管理器启动完成，共启动 {len(self.running_tasks)} 个任务")

    async def stop_all_tasks(self):
        """停止所有任务"""
        if not self.is_running:
            logger.warning("定时任务管理器未在运行")
            return

        self.is_running = False
        logger.info("停止定时任务管理器...")

        for task_name, task in self.running_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            logger.info(f"停止定时任务: {task_name}")

        self.running_tasks.clear()
        logger.info("定时任务管理器已停止")

    def enable_task(self, task_name: str):
        """启用任务"""
        if task_name in self.tasks:
            self.tasks[task_name]["enabled"] = True
            logger.info(f"已启用定时任务: {task_name}")

    def disable_task(self, task_name: str):
        """禁用任务"""
        if task_name in self.tasks:
            self.tasks[task_name]["enabled"] = False
            logger.info(f"已禁用定时任务: {task_name}")

    def get_task_status(self) -> Dict[str, Any]:
        """获取所有任务状态"""
        status = {
            "manager_running": self.is_running,
            "total_tasks": len(self.tasks),
            "running_tasks": len(self.running_tasks),
            "tasks": {}
        }

        for task_name, task_info in self.tasks.items():
            status["tasks"][task_name] = {
                "enabled": task_info["enabled"],
                "interval_minutes": task_info["interval"].total_seconds() / 60,
                "last_run": task_info["last_run"].isoformat() if task_info["last_run"] else None,
                "next_run": task_info["next_run"].isoformat() if task_info["next_run"] else None,
                "is_running": task_name in self.running_tasks
            }

        return status


# 创建全局任务管理器实例
task_manager = TaskSchedulerManager()


def register_default_tasks():
    """注册默认的定时任务"""

    # 注册商品表更新任务 - 启动时立即执行一次，之后每24小时执行一次
    task_manager.register_task(
        task_name="更新商品表",
        task_func=TASK1_更新苹果内购商品表.run,
        get_db=TASK1_更新苹果内购商品表.get_db,
        interval_minutes=TASK1_更新苹果内购商品表.interval_minutes,  # 24小时
        run_immediately=True
    )

    task_manager.register_task(
        task_name="获取动态配置",
        task_func=TASK2_定时获取动态配置.run,
        interval_minutes=TASK2_定时获取动态配置.interval_minutes,
        run_immediately=True
    )

    # 可以在这里添加更多的默认任务
    # task_manager.register_task(
    #     task_name="清理过期数据",
    #     task_func=some_cleanup_function,
    #     get_db=some_task_class.get_db,  # 如果需要数据库
    #     interval_minutes=6 * 60,  # 6小时
    #     run_immediately=False
    # )


async def start_scheduler():
    """启动定时任务调度器"""
    register_default_tasks()
    await task_manager.start_all_tasks()


async def stop_scheduler():
    """停止定时任务调度器"""
    await task_manager.stop_all_tasks()


def get_scheduler_status():
    """获取调度器状态"""
    return task_manager.get_task_status()
