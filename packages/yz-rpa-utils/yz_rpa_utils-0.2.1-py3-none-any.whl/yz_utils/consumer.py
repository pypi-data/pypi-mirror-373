import json, traceback, pretty_errors, asyncio
import gc
import sys
import multiprocessing
import tkinter as tk
import queue
from datetime import datetime
from .web_api import AsyncApiClient
import threading, time, copy
from typing import Callable, Optional


class YuanmeiJob:
    def __init__(self,
                 jobId: str,
                 status: str,
                 companyCode: str,
                 platform: str,
                 queueName: str,
                 jobData: str,
                 resultData: str,
                 msg: str,
                 fileName: str,
                 errorFile: str,
                 shopId: int,
                 startDate: int,
                 endDate: int,
                 totalTime: int,
                 createDate: int,
                 successCount: int,
                 errorCount: int,
                 errorMsg: str,
                 taskName: str,
                 requestId: str,
                 createStaffId: str,
                 lastHeartbeatTime: int,
                 jobLockKey: str):
        self.jobId = jobId
        self.status = status
        self.companyCode = companyCode
        self.platform = platform
        self.queueName = queueName
        self.jobData = jobData
        self.resultData = resultData
        self.msg = msg
        self.fileName = fileName
        self.errorFile = errorFile
        self.shopId = shopId
        self.startDate = self.date_str_to_int(startDate)
        self.endDate = self.date_str_to_int(endDate)
        self.totalTime = totalTime
        self.createDate = self.date_str_to_int(createDate)
        self.successCount = successCount
        self.errorCount = errorCount
        self.errorMsg = errorMsg
        self.taskName = taskName
        self.requestId = requestId
        self.createStaffId = createStaffId
        self.lastHeartbeatTime = self.date_str_to_int(lastHeartbeatTime)
        self.jobLockKey = jobLockKey
        # 临时信息
        self.error_msg_list = []
        self.log_list = []

    @staticmethod
    def date_str_to_int(date_str):
        if type(date_str) == str:
            return int(time.mktime(time.strptime(date_str, '%Y-%m-%d %H:%M:%S')))
        else:
            return date_str

    @staticmethod
    def date_int_to_str(obj: dict):
        for key in ["startDate", "endDate", "createDate", "lastHeartbeatTime"]:
            if obj.get(key):
                if len(str(obj[key])) == 10:
                    lt = time.localtime(obj[key])
                else:
                    lt = time.localtime(obj[key] / 1000)
                obj[key] = time.strftime('%Y-%m-%d %H:%M:%S', lt)

    def sum_total_time(self):
        self.totalTime = self.endDate - self.startDate

    def to_json(self):
        res_json = copy.deepcopy(self.__dict__)
        self.date_int_to_str(res_json)
        if self.error_msg_list is not None:
            self.errorMsg = json.dumps(self.error_msg_list, ensure_ascii=False)
        return res_json

    def get_job_vars(self):
        local_vars = {}
        if self.jobData:
            job_data = json.loads(self.jobData)
            for job_param in job_data:
                if job_param.get("yingdaoFlag"):
                    local_vars[job_param.get("name")] = job_param.get("value")
        return local_vars


class AutoRefreshWindow:
    def __init__(self, initial_text="", refresh_interval=1000):
        """异步友好的Tkinter窗口类"""
        # 状态变量
        self.initial_text = initial_text
        self.root = None
        self.screen_width = None
        self.screen_height = None
        self.window_height = None
        self.font_size = None
        self.label = None
        self.refresh_interval = refresh_interval
        self.is_running = True
        self.drag_data = None
        self.window_thread = None

        # 消息队列（用于线程间通信）
        self.message_queue = queue.Queue()

        # 启动窗口线程
        self.start_window_thread()

    def create_window(self):
        """在窗口线程中创建Tkinter对象"""
        # 创建根窗口但初始隐藏
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg="black")

        # 屏幕尺寸和窗口高度
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.window_height = max(self.screen_height // 30, 20)
        self.root.geometry(f"{self.screen_width}x{self.window_height}+0+0")

        # 字体设置
        self.font_size = max(self.window_height // 2, 10)

        # 内容标签
        self.label = tk.Label(
            self.root,
            text=self.initial_text,
            font=("Arial", self.font_size, "bold"),
            fg="white",
            bg="black",
            justify="center"
        )
        self.label.pack(expand=True, fill=tk.BOTH)

        # 拖拽功能
        self.drag_data = {"y": 0, "dragging": False}
        self.label.bind("<ButtonPress-1>", self.start_drag)
        self.label.bind("<ButtonRelease-1>", self.stop_drag)
        self.label.bind("<B1-Motion>", self.on_drag)

    def start_drag(self, event):
        """开始拖拽窗口"""
        self.drag_data["y"] = event.y
        self.drag_data["dragging"] = True

    def stop_drag(self, event):
        """停止拖拽窗口"""
        self.drag_data["dragging"] = False

    def on_drag(self, event):
        """处理拖拽事件"""
        if self.drag_data["dragging"]:
            delta = event.y - self.drag_data["y"]
            new_y = self.root.winfo_y() + delta
            # 确保窗口不会移出屏幕
            new_y = max(0, min(new_y, self.screen_height - self.window_height))
            self.root.geometry(f"+0+{new_y}")

    def update_content(self, new_text: str = None):
        """更新窗口内容"""
        if self.is_running and self.label:
            self.label.config(text=new_text)

    def safe_call(self, func, *args):
        """线程安全调用Tkinter方法"""
        if self.is_running:
            self.root.after(0, func, *args)

    def check_queue(self):
        """检查消息队列（线程安全）"""
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                if message == "SHOW":
                    self.root.deiconify()  # 显示窗口
                elif message == "DESTROY":
                    self.is_running = False
                    self.root.destroy()
                    return
        except queue.Empty:
            pass

        # 继续检查队列
        if self.is_running:
            self.root.after(100, self.check_queue)

    def show(self):
        """显示窗口（线程安全）"""
        self.message_queue.put("SHOW")

    def destroy(self):
        """安全关闭窗口（线程安全）"""
        self.message_queue.put("DESTROY")

    def start_window_thread(self):
        """启动专用的窗口线程"""

        def run_window():
            """窗口线程的主函数"""
            try:
                # 在窗口线程中创建所有Tkinter对象
                self.create_window()

                # 启动窗口功能
                self.root.after(0, self.show)
                self.root.after(0, self.check_queue)

                # 启动Tkinter主循环
                self.root.mainloop()
            except Exception as e:
                print(f"窗口线程错误: {e}")
            finally:
                print("窗口线程已退出")

        # 创建并启动窗口线程
        self.window_thread = threading.Thread(target=run_window, daemon=True)
        self.window_thread.start()

    def close(self):
        """安全关闭窗口并等待线程结束"""
        if self.is_running:
            self.destroy()
            self.window_thread.join(timeout=1.0)
            if self.window_thread.is_alive():
                print("警告: 窗口线程仍在运行，强制退出")
            else:
                print("窗口已安全关闭")
            self.is_running = False


class AsyncConsumer:
    def __init__(self, api_client: AsyncApiClient, queue_name: str = None, _print: Callable = print, consumer_name: str = "AsyncConsumer"):
        self.api_client = api_client
        self.queue_name = queue_name
        self.print = _print
        self.currentJob: Optional[YuanmeiJob] = None
        self.consumer_running = True
        self.heart_beat_task: Optional[asyncio.Task] = None
        self.auto_refresh_window: Optional[AutoRefreshWindow] = None
        self.consumer_name = consumer_name
        self.current_exec_line = None
        self.heart_count = 0
        # 使用线程池执行同步代码
        self.loop = asyncio.get_running_loop()

    async def start(self):
        """启动消费者"""
        # 启动心跳任务
        self.heart_beat_task = asyncio.create_task(self.heart_beat_loop())
        # 启动主任务处理循环
        await self.async_run()

    async def async_run(self):
        self.auto_refresh_window = AutoRefreshWindow(
            initial_text="消费者已经启动..等待任务中",
            refresh_interval=1000
        )
        """异步任务处理循环"""
        while self.consumer_running:
            try:
                await self.get_job()
                if self.currentJob:
                    app_code, max_exec_time = await self.get_app_code()
                    self.auto_refresh_window.update_content(f"正在执行任务:{self.currentJob.jobId}")
                    try:
                        await self.start_job()
                        # 准备执行环境
                        local_vars = self.currentJob.get_job_vars()
                        local_vars["log"] = self.log
                        local_vars["error_log"] = self.error_log
                        local_vars["api_client"] = self.api_client
                        local_vars["job"] = self.currentJob
                        # 执行用户代码 - 在单独的线程中执行以避免阻塞事件循环
                        code_block = "def run_code():\n"
                        for line in str(app_code).splitlines():
                            code_block += f"    {line}\n"
                        code_block += "run_code()\n"
                        exec_flag, result = await self.async_run_time_out(code_block, local_vars, max_exec_time)
                        # 没有报错,默认成功
                        if exec_flag:
                            await self.end_job("SUCCESS")
                        else:
                            await self.error_job(result)
                    except Exception as ex:
                        await self.error_job(traceback.format_exc())
                    finally:
                        await self.update_job()
                else:
                    await asyncio.sleep(10)
            except Exception as e:
                self.print(f"主循环异常: {traceback.format_exc()}")
            finally:
                # 清理当前任务
                self.currentJob = None
                self.current_exec_line = None
                gc.collect()  # 强制垃圾回收，清理内存

    async def async_run_time_out(self, code_block, local_vars, max_exec_time: int):
        """使用单行调用实现RPA安全超时控制"""
        thread_id = f"user_code_{int(time.time() * 1000)}"
        interrupt_event = threading.Event()

        def run_in_thread():
            threading.current_thread().name = thread_id

            # 注入通用中断检查函数
            def should_interrupt(frame, event, arg):
                filename = frame.f_code.co_filename
                if filename != thread_id:
                    return None
                if event == 'line':
                    self.current_exec_line = frame.f_lineno
                    """通用中断检查函数（直接抛出异常）"""
                    if interrupt_event.is_set():
                        raise RuntimeError(f'任务被强制中断 (当前执行行数: {frame.f_lineno})')
                    # 释放GIL，让中断事件能被处理
                    time.sleep(0.001)
                return should_interrupt

            # 执行增强后的代码
            try:
                sys.settrace(should_interrupt)
                exec(compile(code_block, thread_id, "exec"), local_vars, local_vars)
                return True, ""
            except Exception as ex:
                self.print(f"任务 {thread_id} 出错\n{traceback.format_exc()}")
                return False, traceback.format_exc()
            finally:
                sys.settrace(None)

        try:
            # 执行带超时控制
            return await asyncio.wait_for(
                self.loop.run_in_executor(None, run_in_thread),
                timeout=max_exec_time
            )
        except asyncio.TimeoutError:
            interrupt_event.set()
            self.print(f"任务 {thread_id} 超时，触发中断")

            # RPA感知等待
            await self._rpa_aware_wait(thread_id, 8)

            # 检查线程状态
            if any(t.name == thread_id for t in threading.enumerate()):
                self.print(f"警告: 任务 {thread_id} 未能在8秒内退出")
                self._cleanup_rpa_resources()

            return False, f"任务执行超时, 超过最大执行时间: {int(max_exec_time)}秒"

    async def _rpa_aware_wait(self, thread_id: str, max_wait: float):
        """RPA感知的线程等待"""
        start_time = time.time()
        last_check = time.time()

        while time.time() - start_time < max_wait:
            if time.time() - last_check > 0.5:
                self.print(f"等待任务 {thread_id} 退出... ({int(time.time() - start_time)}s)")
                last_check = time.time()

            if not any(t.name == thread_id for t in threading.enumerate()):
                return

            # 短暂等待
            await asyncio.sleep(0.1)

        # 最后一次尝试
        await asyncio.sleep(0.5)

    def _cleanup_rpa_resources(self):
        """强制清理RPA资源（最后手段）"""
        try:
            # 这里可以添加特定于您RPA框架的资源清理逻辑
            # 例如：关闭所有浏览器实例、释放UI资源等
            pass
        except Exception as e:
            self.print(f"强制清理错误: {str(e)}")

    async def update_result_data(self, local_vars: dict):
        """更新任务结果数据"""
        result_data = {}
        for key in local_vars:
            if type(local_vars.get(key)) in [str, int, float, dict, list]:
                result_data[key] = local_vars.get(key)

        if self.currentJob:
            self.currentJob.resultData = json.dumps(result_data, ensure_ascii=False)
            await self.update_job()

    async def log(self, msg: str):
        """记录日志"""
        if self.currentJob:
            self.currentJob.log_list.append(msg)
            self.currentJob.msg = msg
            self.print(msg)
            await self.update_job()

    async def error_log(self, error_msg: str):
        """记录错误日志"""
        if self.currentJob:
            self.currentJob.error_msg_list.append(error_msg)
            self.currentJob.errorCount += 1
            self.print(error_msg)
            await self.update_job()

    async def start_job(self):
        """标记任务开始"""
        if self.currentJob:
            self.currentJob.status = "PROCESS"
            self.currentJob.startDate = int(time.time() * 1000)
            org_task_name = str(self.currentJob.taskName).split("-")[0].strip()
            self.currentJob.taskName = f"{org_task_name}-{self.consumer_name}"
            await self.update_job()

    @staticmethod
    def convert_milliseconds_to_hms(milliseconds: int) -> str:
        """将毫秒转换为小时:分钟:秒格式"""
        seconds = milliseconds / 1000.0
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}小时 {minutes}分钟 {secs}秒"

    async def end_job(self, status: str = "SUCCESS"):
        """结束任务"""
        if self.currentJob:
            self.currentJob.status = status
            self.currentJob.endDate = int(time.time() * 1000)
            self.currentJob.sum_total_time()

            duration_str = self.convert_milliseconds_to_hms(self.currentJob.totalTime)
            if status == "ERROR":
                self.currentJob.msg = f"机器人: {self.consumer_name} {self.currentJob.taskName}-任务执行失败, 耗时{duration_str}"
            else:
                self.currentJob.msg = f"机器人: {self.consumer_name} {self.currentJob.taskName}-任务执行成功, 耗时{duration_str}"
            await self.update_job()

    async def error_job(self, error_msg: str = None):
        """标记任务失败"""
        if error_msg:
            await self.error_log(error_msg)
        await self.end_job("ERROR")

    async def heart_beat_loop(self):
        """心跳循环任务"""
        while self.consumer_running:
            try:
                await self.heart_beat()
                await asyncio.sleep(1)  # 每60秒发送一次心跳
            except asyncio.CancelledError:
                break
            except Exception as ex:
                self.print(f"心跳任务异常: {traceback.format_exc()}")
            finally:
                self.heart_count += 1

    async def heart_beat(self):
        """发送心跳"""
        if self.heart_count % 60 == 0 and self.currentJob and self.currentJob.jobId and self.currentJob.status == "PROCESS":
            await self.api_client.post(
                "/YuanmeiJob/open/sendHeartbeat",
                {"jobId": self.currentJob.jobId}
            )
        new_text_list = [f'时间:{datetime.now().strftime("%H:%M:%S")}']
        if self.currentJob and self.currentJob.jobId:
            new_text_list.append(f"正在执行任务: {self.currentJob.taskName} - {self.currentJob.jobId}")
        if self.current_exec_line:
            new_text_list.append(f"当前执行代码行数: {self.current_exec_line}")
        if not self.currentJob and not self.current_exec_line:
            new_text_list.append("等待新任务.....")

        self.auto_refresh_window.update_content(" | ".join(new_text_list))

    async def get_job(self) -> Optional[YuanmeiJob]:
        """获取一个待处理任务"""
        req_url = "/YuanmeiJob/open/getOneWaitJob"
        if self.queue_name:
            req_url += f"?queueName={self.queue_name}"

        job_result = await self.api_client.get(req_url)
        if job_result:
            self.print(f"获取任务成功:{json.dumps(job_result, ensure_ascii=False)}")
            # 移除不需要的字段
            job_result.pop("id", None)
            job_result.pop("isDel", None)
            self.currentJob = YuanmeiJob(**job_result)
            return self.currentJob
        return None

    async def get_app_code(self) -> (str, int):
        """获取任务关联的应用程序代码"""
        if self.currentJob and self.currentJob.queueName:
            app_data = await self.api_client.get(
                "/YuanmeiYingdaoApp/open/getApp",
                request_params={"queueName": self.currentJob.queueName}
            )
            return app_data.get("pythonCodeBlock", ""), app_data.get("maxExecTime", 60 * 30)
        raise Exception("未知任务队列")

    async def update_job(self):
        """更新任务状态"""
        if self.currentJob:
            job_json = self.currentJob.to_json()
            await self.api_client.post_json(
                "/YuanmeiJob/open/updateJob",
                request_json=job_json
            )

    async def close(self):
        """关闭消费者并清理资源"""
        self.consumer_running = False

        # 取消心跳任务
        if self.heart_beat_task and not self.heart_beat_task.done():
            self.heart_beat_task.cancel()
            try:
                await self.heart_beat_task
            except asyncio.CancelledError:
                pass

        # 关闭API客户端
        await self.api_client.close()
