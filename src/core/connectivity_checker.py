"""DeepSeek API连通性检查器"""

import requests
from PyQt6.QtCore import QThread, pyqtSignal
from config.core import AppConstants


class ConnectivityChecker(QThread):
    """API连通性检查工作线程"""

    check_completed = pyqtSignal()
    check_failed = pyqtSignal(str)

    def __init__(self, api_key: str, api_url: str = None):
        super().__init__()
        self.api_key = api_key
        self.api_url = api_url or AppConstants.DEEPSEEK_API_URL

    def run(self):
        """执行连通性检查"""
        try:
            # 构建请求头
            headers = {
                AppConstants.DEEPSEEK_HEADER_CONTENT_TYPE: AppConstants.DEEPSEEK_CONTENT_TYPE_JSON,
                AppConstants.DEEPSEEK_HEADER_AUTHORIZATION: f"{AppConstants.DEEPSEEK_AUTH_PREFIX}{self.api_key}",
            }

            # 构建一个简单的测试请求
            payload = {
                AppConstants.DEEPSEEK_PARAM_MODEL: AppConstants.DEEPSEEK_DEFAULT_MODEL,
                AppConstants.DEEPSEEK_PARAM_MESSAGES: [
                    {
                        AppConstants.DEEPSEEK_MESSAGE_ROLE: AppConstants.DEEPSEEK_ROLE_USER,
                        AppConstants.DEEPSEEK_MESSAGE_CONTENT: "测试连接",
                    }
                ],
                AppConstants.DEEPSEEK_PARAM_TEMPERATURE: 0.1,
                AppConstants.DEEPSEEK_PARAM_MAX_TOKENS: 10,
            }

            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10,  # 较短的超时时间用于连通性检查
            )

            if response.status_code == AppConstants.DEEPSEEK_SUCCESS_STATUS_CODE:
                # 检查响应格式是否正确
                result = response.json()
                if (
                    AppConstants.DEEPSEEK_RESPONSE_CHOICES in result
                    and len(result[AppConstants.DEEPSEEK_RESPONSE_CHOICES]) > 0
                ):
                    self.check_completed.emit()
                else:
                    self.check_failed.emit("API响应格式异常")
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json().get("error", {}).get("message", "")
                    if error_detail:
                        error_msg += f": {error_detail}"
                except:
                    pass
                self.check_failed.emit(error_msg)

        except requests.exceptions.Timeout:
            self.check_failed.emit("请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            self.check_failed.emit("网络连接失败，请检查网络设置")
        except requests.exceptions.RequestException as e:
            self.check_failed.emit(f"请求异常: {str(e)}")
        except Exception as e:
            self.check_failed.emit(f"未知错误: {str(e)}")
