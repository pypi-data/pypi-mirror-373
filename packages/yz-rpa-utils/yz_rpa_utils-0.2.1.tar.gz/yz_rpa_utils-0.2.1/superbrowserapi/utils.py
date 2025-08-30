import os
import platform
import subprocess
import psutil
import time
import logging
from typing import List, Optional, Tuple, Set

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('process_terminator')


def get_process_tree(pid: int) -> List[psutil.Process]:
    """获取指定进程ID的整个进程树（包括父进程和所有子进程）"""
    try:
        main_process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return []

    processes = [main_process]
    try:
        # 递归获取所有子进程
        for child in main_process.children(recursive=True):
            processes.append(child)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass  # 进程可能在获取过程中退出

    return processes


def terminate_process_tree_windows(pid: int, timeout: int = 5, force: bool = False) -> Tuple[bool, List[int]]:
    """
    在Windows上终止进程树，可选择强制终止

    参数:
    pid: 进程ID
    timeout: 等待进程退出的超时时间（秒）
    force: 是否强制终止进程

    返回: (是否成功, 未退出的进程ID列表)
    """
    # 先尝试使用taskkill正常终止
    if not force:
        try:
            logger.info(f"尝试使用taskkill正常终止进程树 (PID: {pid})")
            result = subprocess.run(
                ['taskkill', '/pid', str(pid), '/t'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                logger.info(f"taskkill成功终止进程树 (PID: {pid})")
                return True, []

            # 检查常见错误代码
            if result.returncode == 128:
                logger.warning(f"进程 {pid} 已经终止")
                return True, []

            logger.warning(f"taskkill返回错误 (code={result.returncode}): {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.warning(f"taskkill命令超时 (PID: {pid})")

    # 如果强制终止或正常终止失败，尝试强制终止
    if force:
        try:
            logger.warning(f"尝试强制终止进程树 (PID: {pid})")
            result = subprocess.run(
                ['taskkill', '/f', '/t', '/pid', str(pid)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                logger.info(f"强制终止成功 (PID: {pid})")
                return True, []

            # 检查常见错误代码
            if result.returncode == 128:
                logger.warning(f"进程 {pid} 已经终止")
                return True, []

            logger.error(f"强制终止失败 (code={result.returncode}): {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.error(f"强制终止命令超时 (PID: {pid})")

    # 检查进程是否已退出
    if not psutil.pid_exists(pid):
        logger.info(f"进程 {pid} 已退出")
        return True, []

    # 如果taskkill失败，尝试使用psutil的terminate
    logger.info(f"尝试使用psutil终止进程树 (PID: {pid})")
    processes = get_process_tree(pid)
    alive_pids = []

    # 先终止子进程再终止父进程
    for proc in reversed(processes):
        try:
            if proc.is_running():
                if force:
                    logger.warning(f"强制终止进程 (PID: {proc.pid})")
                    proc.kill()  # 强制终止
                else:
                    proc.terminate()  # 正常终止
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 等待进程退出
    time.sleep(0.5)

    # 检查哪些进程仍然存活
    for proc in processes:
        try:
            if proc.is_running():
                alive_pids.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return len(alive_pids) == 0, alive_pids


def find_process_ids(process_names: List[str]) -> List[int]:
    """根据进程名列表查找所有匹配的进程ID"""
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name']
            # 检查进程名是否在目标列表中,区分大小写
            if any(target_name in proc_name for target_name in process_names):
                pids.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue
    return pids


def terminate_processes_by_names(
        process_names: List[str],
        timeout: int = 5,
        max_attempts: int = 2,
        force: bool = True
) -> Tuple[bool, List[int]]:
    """
    通过进程名列表终止多个进程树（仅支持Windows系统）

    参数:
    process_names: 要终止的进程名列表（支持部分匹配）
    timeout: 等待进程退出的超时时间（秒）
    max_attempts: 最大尝试次数
    force: 是否强制终止无法正常结束的进程

    返回: (是否成功终止所有进程, 未能终止的进程ID列表)
    """
    # 检查操作系统
    if platform.system() != 'Windows':
        logger.error("此功能仅支持Windows系统")
        return False, []

    if not process_names:
        logger.warning("进程名列表为空，无需操作")
        return True, []

    logger.info(f"开始终止进程: {', '.join(process_names)}")
    if force:
        logger.warning("启用强制终止模式")

    # 获取所有匹配的进程ID
    target_pids = find_process_ids(process_names)
    if not target_pids:
        logger.info("未找到匹配的进程")
        return True, []

    logger.info(f"找到匹配的进程ID: {target_pids}")

    # 用于跟踪终止结果
    all_success = True
    terminated_pids: Set[int] = set()
    failed_pids: List[int] = []

    # 多次尝试终止
    for attempt in range(1, max_attempts + 1):
        logger.info(f"终止尝试 {attempt}/{max_attempts}")

        # 本次尝试中未终止的进程
        remaining_pids = []

        for pid in target_pids:
            # 跳过已终止的进程
            if pid in terminated_pids:
                continue

            # 检查进程是否还存在
            if not psutil.pid_exists(pid):
                logger.info(f"进程 {pid} 已退出")
                terminated_pids.add(pid)
                continue

            # 在最后一次尝试时启用强制终止
            use_force = force or (attempt == max_attempts)

            # 终止进程树
            success, alive_pids = terminate_process_tree_windows(pid, timeout, use_force)
            if success:
                logger.info(f"成功终止进程树 (PID: {pid})")
                terminated_pids.add(pid)
            else:
                logger.warning(f"未能完全终止进程树 (PID: {pid}), 存活的进程: {alive_pids}")
                remaining_pids.append(pid)
                all_success = False
                # 添加到失败列表（如果尚未添加）
                if pid not in failed_pids:
                    failed_pids.append(pid)

        # 更新需要处理的进程列表
        target_pids = remaining_pids

        # 如果所有进程都已终止，提前退出
        if not target_pids:
            break

        # 如果还有未终止的进程，等待一段时间后重试
        logger.info(f"等待 {timeout} 秒后重试...")
        time.sleep(timeout)

    # 最终检查
    final_failed = []
    for pid in failed_pids:
        if psutil.pid_exists(pid):
            logger.error(f"进程 {pid} 仍然在运行")
            final_failed.append(pid)

    if final_failed:
        logger.error(f"无法终止以下进程: {final_failed}")
        return False, final_failed

    logger.info("所有目标进程已终止")
    return True, []


def terminate_browser_processes(
        browser_names: List[str],
        timeout: int = 10,
        force: bool = False
) -> Tuple[bool, List[int]]:
    """
    终止浏览器进程的专用函数（仅支持Windows）
    支持常见浏览器: chrome, firefox, edge, safari

    返回: (是否成功, 未能终止的进程ID列表)
    """
    # 浏览器进程名映射
    browser_mapping = {
        'chrome': ['chrome'],
        'firefox': ['firefox'],
        'edge': ['msedge'],
        'safari': ['safari'],
        'ie': ['iexplore'],
        'opera': ['opera'],
        'brave': ['brave'],
        'chromium': ['chromium']
    }

    # 转换为小写以进行不区分大小写的匹配
    browser_names = [name.lower() for name in browser_names]

    # 收集所有目标进程名
    target_names = []
    for name in browser_names:
        if name in browser_mapping:
            target_names.extend(browser_mapping[name])
        else:
            logger.warning(f"不支持的浏览器名称: {name}")

    if not target_names:
        logger.error("没有有效的浏览器进程名")
        return False, []

    return terminate_processes_by_names(target_names, timeout, force=force)


def terminate_process_tree_force(pid: int, timeout: int = 5) -> bool:
    """
    强制终止进程树（包括所有子进程）

    参数:
    pid: 要终止的进程ID
    timeout: 等待超时时间（秒）

    返回: 是否成功终止
    """
    logger.warning(f"强制终止进程树 (PID: {pid})")
    success, failed_pids = terminate_process_tree_windows(pid, timeout, force=True)
    return success and not failed_pids
