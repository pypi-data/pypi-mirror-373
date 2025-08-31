"""
定时任务管理API
提供查看和管理定时任务的接口
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from svc_order_zxw.定时任务 import task_manager, get_scheduler_status
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/svc_order/scheduler", tags=["定时任务管理"])


@router.get("/status", summary="获取定时任务状态")
async def get_tasks_status() -> Dict[str, Any]:
    """
    获取所有定时任务的状态信息
    """
    try:
        status = get_scheduler_status()
        return {
            "success": True,
            "message": "获取定时任务状态成功",
            "data": status
        }
    except Exception as e:
        logger.error(f"获取定时任务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.post("/task/{task_name}/enable", summary="启用定时任务")
async def enable_task(task_name: str) -> Dict[str, Any]:
    """
    启用指定的定时任务
    """
    try:
        if task_name not in task_manager.tasks:
            raise HTTPException(status_code=404, detail=f"任务 {task_name} 不存在")

        task_manager.enable_task(task_name)
        return {
            "success": True,
            "message": f"任务 {task_name} 已启用"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启用任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启用任务失败: {str(e)}")


@router.post("/task/{task_name}/disable", summary="禁用定时任务")
async def disable_task(task_name: str) -> Dict[str, Any]:
    """
    禁用指定的定时任务
    """
    try:
        if task_name not in task_manager.tasks:
            raise HTTPException(status_code=404, detail=f"任务 {task_name} 不存在")

        task_manager.disable_task(task_name)
        return {
            "success": True,
            "message": f"任务 {task_name} 已禁用"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"禁用任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"禁用任务失败: {str(e)}")


@router.get("/tasks", summary="获取所有任务列表")
async def get_all_tasks() -> Dict[str, Any]:
    """
    获取所有已注册的定时任务列表
    """
    try:
        tasks = list(task_manager.tasks.keys())
        return {
            "success": True,
            "message": "获取任务列表成功",
            "data": {
                "total": len(tasks),
                "tasks": tasks
            }
        }
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")
