"""
LinkedIn浏览器管理器 - 独立模块
专门负责LinkedIn浏览器的自动化操作
"""

import sys
import os
import time
import win32gui
import win32process
import win32con
import win32api
import win32clipboard
import subprocess
import ctypes
import ctypes.wintypes
import psutil
import re
from typing import List, Dict, Optional, Tuple


class WindowInfo:
    """窗口信息类"""
    def __init__(self, hwnd: int, title: str, class_name: str, pid: int, process_name: str):
        self.hwnd = hwnd
        self.title = title
        self.class_name = class_name
        self.pid = pid
        self.process_name = process_name
        
    def __str__(self):
        return f"窗口: {self.title} | 进程: {self.process_name} | PID: {self.pid}"


class WindowManager:
    """Windows窗口管理器"""
    
    def __init__(self):
        self.windows: List[WindowInfo] = []
        
    def refresh_windows(self) -> List[WindowInfo]:
        """刷新并获取所有可见窗口"""
        self.windows = []
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # 只获取有标题的窗口
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        class_name = win32gui.GetClassName(hwnd)
                        
                        window_info = WindowInfo(
                            hwnd=hwnd,
                            title=title,
                            class_name=class_name,
                            pid=pid,
                            process_name=process.name()
                        )
                        windows.append(window_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            return True
        
        win32gui.EnumWindows(enum_windows_callback, self.windows)
        return self.windows
    
    def find_window_by_process(self, process_name: str) -> List[WindowInfo]:
        """根据进程名查找窗口"""
        self.refresh_windows()
        matches = []
        
        for window in self.windows:
            if process_name.lower() in window.process_name.lower():
                matches.append(window)
        
        return matches
    
    def switch_to_window(self, window_info: WindowInfo) -> bool:
        """切换到指定窗口"""
        try:
            hwnd = window_info.hwnd
            
            # 如果窗口最小化，先恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 将窗口置于前台
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            
            return True
        except Exception as e:
            print(f"切换窗口失败: {e}")
            return False


class BrowserManager:
    """通用浏览器管理器基类"""
    
    def __init__(self, target_url: str = "linkedin.com", title_keywords: List[str] = None):
        self.wm = WindowManager()
        self.target_url = target_url
        self.title_keywords = title_keywords or ["LinkedIn", "linkedin"]
        
        # 根据URL生成可能的域名列表
        self.domains = self._generate_domain_list(target_url)
    
    def _generate_domain_list(self, url: str) -> List[str]:
        """根据URL生成可能的域名列表"""
        base_domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
        return [
            base_domain,
            f"www.{base_domain}",
            f"m.{base_domain}",
            f"cn.{base_domain}"
        ]


    def find_edge_windows(self) -> List:
        """查找所有Edge浏览器窗口"""
        return self.wm.find_window_by_process("msedge")
    
    def maximize_window(self, window_info):
        """最大化指定窗口"""
        try:
            hwnd = window_info.hwnd
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            print(f"最大化窗口失败: {e}")
            return False
    
    def focus_edge_window(self) -> Optional[object]:
        """聚焦到Edge窗口并最大化"""
        edge_windows = self.find_edge_windows()
        
        if not edge_windows:
            print("未找到Edge浏览器窗口")
            return None
        
        # 选择第一个Edge窗口
        target_window = edge_windows[0]
        print(f"找到Edge窗口: {target_window.title}")
        
        # 切换到窗口
        if self.wm.switch_to_window(target_window):
            print("成功切换到Edge窗口")
            time.sleep(0.5)  # 等待窗口切换完成
            
            # 最大化窗口
            if self.maximize_window(target_window):
                print("窗口已最大化")
            
            return target_window
        else:
            print("切换到Edge窗口失败")
            return None
    
    def launch_edge_with_website(self) -> bool:
        """启动Edge浏览器并直接打开目标网站"""
        try:
            print(f"启动Edge浏览器并打开{self.target_url}...")
            # 直接启动Edge并访问目标网站
            subprocess.Popen([
                "start", "msedge", self.target_url
            ], shell=True)
            
            # 等待浏览器启动
            time.sleep(3)
            
            # 查找新启动的Edge窗口并最大化
            edge_windows = self.find_edge_windows()
            if edge_windows:
                target_window = edge_windows[0]
                self.wm.switch_to_window(target_window)
                time.sleep(0.5)
                self.maximize_window(target_window)
                print(f"Edge浏览器启动成功，已打开{self.target_url}")
                return True
            
            return False
        except Exception as e:
            print(f"启动Edge浏览器失败: {e}")
            return False
    
    def send_key_combination(self, *keys):
        """发送组合键"""
        try:
            # 按下所有键
            for key in keys:
                if isinstance(key, str):
                    win32api.keybd_event(ord(key.upper()), 0, 0, 0)
                else:
                    win32api.keybd_event(key, 0, 0, 0)
            
            time.sleep(0.05)
            
            # 释放所有键（逆序）
            for key in reversed(keys):
                if isinstance(key, str):
                    win32api.keybd_event(ord(key.upper()), 0, win32con.KEYEVENTF_KEYUP, 0)
                else:
                    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
            
            time.sleep(0.1)
        except Exception as e:
            print(f"发送按键失败: {e}")
            return False
        return True
    
    def type_text_via_clipboard(self, text):
        """剪贴板输入"""
        try:
            print(f"使用剪贴板输入: {text}")
            
            # 保存当前剪贴板内容
            old_clipboard = None
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                    old_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
            except:
                pass
            
            # 设置新内容到剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            
            time.sleep(0.1)
            
            # 粘贴内容
            self.send_key_combination(win32con.VK_CONTROL, 'V')
            time.sleep(0.2)
            
            # 恢复原剪贴板内容
            if old_clipboard:
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(old_clipboard, win32clipboard.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                except:
                    pass
            
            print(f"✓ 剪贴板输入完成: {text}")
            return True
            
        except Exception as e:
            print(f"剪贴板输入失败: {e}")
            return False
    
    def get_current_url(self) -> str:
        """获取当前Edge浏览器页面的URL"""
        try:
            print("获取当前页面URL...")
            
            # 保存当前剪贴板内容
            old_clipboard = None
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                    old_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
            except:
                pass
            
            # 获取地址栏内容
            # 1. Ctrl+L 选中地址栏
            self.send_key_combination(win32con.VK_CONTROL, 'L')
            time.sleep(0.2)
            
            # 2. Ctrl+C 复制地址栏内容
            self.send_key_combination(win32con.VK_CONTROL, 'C')
            time.sleep(0.2)
            
            # 3. 获取剪贴板内容
            current_url = ""
            try:
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                    current_url = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
            except:
                pass
            
            # 恢复剪贴板内容
            if old_clipboard:
                try:
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(old_clipboard, win32clipboard.CF_UNICODETEXT)
                    win32clipboard.CloseClipboard()
                except:
                    pass
            
            # 按ESC退出地址栏选中状态
            win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
            time.sleep(0.02)
            win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            if current_url:
                print(f"✓ 获取到URL: {current_url}")
                return current_url.strip()
            else:
                print("✗ 无法获取URL")
                return ""
                
        except Exception as e:
            print(f"获取URL失败: {e}")
            return ""
    
    def is_target_url(self, url: str) -> bool:
        """判断URL是否为目标网站相关页面"""
        if not url:
            return False
        
        url_lower = url.lower()
        
        for domain in self.domains:
            if domain in url_lower:
                return True
        
        return False
    
    def check_target_tab_exists(self) -> bool:
        """检查是否存在目标网站标签页"""
        edge_windows = self.find_edge_windows()
        if not edge_windows:
            return False
        
        current_window = edge_windows[0]
        window_title = current_window.title
        
        # 检查标题是否包含目标网站相关关键字
        for keyword in self.title_keywords:
            if keyword.lower() in window_title.lower():
                print(f"✓ 标题检查通过: {window_title}")
                # 进一步检查URL
                current_url = self.get_current_url()
                if self.is_target_url(current_url):
                    print(f"✓ URL检查通过: {current_url}")
                    return True
        
        return False
    
    def open_website_tab_in_existing_edge(self) -> bool:
        """在现有Edge窗口中打开目标网站标签页"""
        try:
            print(f"在现有Edge窗口中打开{self.target_url}...")
            
            # 新建标签页
            print("使用Ctrl+T新建标签页...")
            self.send_key_combination(win32con.VK_CONTROL, 'T')
            time.sleep(1.0)
            
            # 确保光标在地址栏
            print("确保焦点在地址栏...")
            self.send_key_combination(win32con.VK_CONTROL, 'L')
            time.sleep(0.3)
            
            # 清空地址栏内容
            print("清空地址栏...")
            self.send_key_combination(win32con.VK_CONTROL, 'A')
            time.sleep(0.1)
            win32api.keybd_event(win32con.VK_DELETE, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(win32con.VK_DELETE, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            
            # 输入目标网址
            print(f"输入网址: {self.target_url}")
            if self.type_text_via_clipboard(self.target_url):
                print("✓ 网址输入成功")
                
                # 按回车访问
                print("按回车访问网站...")
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                time.sleep(0.1)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                print(f"✓ 成功打开{self.target_url}网站！")
                return True
            else:
                print("✗ 网址输入失败")
                return False
            
        except Exception as e:
            print(f"在现有Edge中打开{self.target_url}失败: {e}")
            return False
    
    def switch_edge_tabs(self) -> bool:
        """使用Ctrl+Tab切换Edge标签页来查找目标网站"""
        try:
            print(f"使用Ctrl+Tab切换标签页查找{self.target_url}...")
            
            # 记录初始状态
            initial_windows = self.find_edge_windows()
            if not initial_windows:
                return False
            
            initial_title = initial_windows[0].title
            
            # 尝试切换几个标签页
            for i in range(10):  # 最多切换10个标签页
                self.send_key_combination(win32con.VK_CONTROL, win32con.VK_TAB)
                time.sleep(0.5)
                
                # 检查当前标签页
                print(f"检查第{i+1}个标签页...")
                if self.check_target_tab_exists():
                    print(f"✓ 在第{i+1}个标签页找到{self.target_url}")
                    return True
                
                # 检查是否回到了初始标签页（避免无限循环）
                current_windows = self.find_edge_windows()
                if current_windows:
                    current_title = current_windows[0].title
                    if current_title == initial_title and i > 0:
                        print(f"已遍历所有标签页，未找到{self.target_url}")
                        break
            
            return False
            
        except Exception as e:
            print(f"切换标签页失败: {e}")
            return False
    
    def reset_page_zoom(self) -> bool:
        """重置页面缩放到100%"""
        try:
            print("重置页面缩放到100%...")
            # 使用Ctrl+0重置缩放
            self.send_key_combination(win32con.VK_CONTROL, '0')
            time.sleep(0.3)  # 等待缩放重置生效
            print("✓ 页面缩放已重置为100%")
            return True
        except Exception as e:
            print(f"重置缩放失败: {e}")
            return False
    
    def run_browser_automation(self):
        """执行网站浏览器自动化主流程"""
        print(f"=== {self.target_url}自动化脚本启动 ===\n")
        
        try:
            # 步骤1: 查找Edge浏览器
            print("1. 查找Edge浏览器...")
            edge_window = self.focus_edge_window()
            
            if edge_window:
                print("✓ 找到Edge浏览器，已聚焦并最大化\n")
                
                # 步骤2: 检查是否已有目标网站标签页
                print(f"2. 检查是否存在{self.target_url}标签页...")
                if self.check_target_tab_exists():
                    print(f"✓ 已存在{self.target_url}标签页")
                    self.reset_page_zoom()  # 重置页面缩放
                    print("任务完成！\n")
                    return True
                
                # 步骤3: 切换标签页查找目标网站
                print(f"3. 切换标签页查找{self.target_url}...")
                if self.switch_edge_tabs():
                    print(f"✓ 在现有标签页中找到{self.target_url}")
                    self.reset_page_zoom()  # 重置页面缩放
                    print("任务完成！\n")
                    return True
                
                # 步骤4: 在现有Edge中打开目标网站
                print(f"4. 在现有Edge中新建{self.target_url}标签页...")
                if self.open_website_tab_in_existing_edge():
                    print(f"✓ 成功在现有Edge中打开{self.target_url}")
                    time.sleep(1.0)  # 等待页面加载
                    self.reset_page_zoom()  # 重置页面缩放
                    print("任务完成！\n")
                    return True
                else:
                    # 如果现有Edge失败，尝试新启动
                    print("现有Edge操作失败，尝试启动新实例...")
                    if self.launch_edge_with_website():
                        print("✓ 新Edge实例启动成功")
                        time.sleep(2.0)  # 等待页面加载
                        self.reset_page_zoom()  # 重置页面缩放
                        print("任务完成！\n")
                        return True
            
            else:
                print("✗ 未找到Edge浏览器\n")
                
                # 步骤5: 启动新的Edge并打开目标网站
                print("5. 启动新的Edge浏览器...")
                if self.launch_edge_with_website():
                    print(f"✓ 新Edge浏览器启动成功，已打开{self.target_url}")
                    time.sleep(2.0)  # 等待页面加载
                    self.reset_page_zoom()  # 重置页面缩放
                    print("任务完成！\n")
                    return True
            
            print(f"✗ 所有方案均失败，{self.target_url}自动化未能完成")
            return False
            
        except Exception as e:
            print(f"✗ 自动化过程出现异常: {e}")
            import traceback
            traceback.print_exc()
            return False


class LinkedInBrowserManager(BrowserManager):
    """LinkedIn浏览器管理器"""
    
    def __init__(self):
        # 使用LinkedIn默认值调用父类构造函数
        super().__init__(target_url="linkedin.com", title_keywords=["LinkedIn", "linkedin"])
    
    def run_linkedin_automation(self):
        """保持原有的LinkedIn方法名以确保向后兼容"""
        return self.run_browser_automation()


def open_website(target_url: str = "linkedin.com", title_keywords: Optional[List[str]] = None) -> bool:
    """
    通用的网站自动打开函数
    
    Args:
        target_url: 目标网站域名，如 "github.com", "linkedin.com"
        title_keywords: 标签页标题关键字列表，用于识别目标网站
                       如果为None，将自动根据域名生成关键字
    
    Returns:
        bool: 是否成功打开目标网站
    
    Examples:
        # 使用默认LinkedIn设置
        open_website()
        
        # 打开GitHub
        open_website("github.com", ["GitHub", "github"])
        
        # 打开百度
        open_website("baidu.com", ["百度", "baidu"])
    """
    try:
        # 如果没有提供关键字，尝试自动生成
        if title_keywords is None:
            domain_name = target_url.replace("www.", "").replace(".com", "").replace(".cn", "")
            title_keywords = [domain_name, domain_name.lower(), domain_name.upper(), domain_name.capitalize()]
        
        print(f"=== 自动打开 {target_url} ===")
        print(f"使用标题关键字: {title_keywords}")
        
        manager = BrowserManager(target_url=target_url, title_keywords=title_keywords)
        success = manager.run_browser_automation()
        
        if success:
            print(f"=== {target_url} 自动化完成 ===")
            print(f"现在您可以开始使用 {target_url} 了！")
        else:
            print(f"=== {target_url} 自动化失败 ===")
            print("请手动检查Edge浏览器和网络连接")
        
        return success
        
    except Exception as e:
        print(f"自动化过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数 - 默认打开LinkedIn以保持向后兼容"""
    try:
        # 为了保持向后兼容，默认仍然打开LinkedIn
        success = open_website("baidu.com", ["百度", "baidu"])
        
    except KeyboardInterrupt:
        print("\n用户中断了程序")
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
