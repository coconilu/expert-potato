"""文案修复工作线程模块"""

import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from config.core import AppConstants


class TextRefineWorker(QThread):
    """文案修复工作线程"""

    progress_updated = pyqtSignal(int)
    text_refined = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    domain_detected = pyqtSignal(str)

    def __init__(self, text: str, api_key: str, api_url: str = None):
        super().__init__()
        self.text = text
        self.api_key = api_key
        self.api_url = api_url or AppConstants.DEEPSEEK_API_URL

    def detect_domain_and_refine(self, text: str) -> tuple[str, str]:
        """检测文案领域并修复文案"""
        try:
            headers = {
                AppConstants.DEEPSEEK_HEADER_CONTENT_TYPE: AppConstants.DEEPSEEK_CONTENT_TYPE_JSON,
                AppConstants.DEEPSEEK_HEADER_AUTHORIZATION: f"{AppConstants.DEEPSEEK_AUTH_PREFIX}{self.api_key}",
            }

            # 构建提示词
            prompt = AppConstants.DEEPSEEK_PROMPT_TEMPLATE.format(text=text)

            payload = {
                AppConstants.DEEPSEEK_PARAM_MODEL: AppConstants.DEEPSEEK_DEFAULT_MODEL,
                AppConstants.DEEPSEEK_PARAM_MESSAGES: [
                    {
                        AppConstants.DEEPSEEK_MESSAGE_ROLE: AppConstants.DEEPSEEK_ROLE_USER,
                        AppConstants.DEEPSEEK_MESSAGE_CONTENT: prompt,
                    }
                ],
                AppConstants.DEEPSEEK_PARAM_TEMPERATURE: AppConstants.DEEPSEEK_DEFAULT_TEMPERATURE,
                AppConstants.DEEPSEEK_PARAM_MAX_TOKENS: AppConstants.DEEPSEEK_DEFAULT_MAX_TOKENS,
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=AppConstants.DEEPSEEK_REQUEST_TIMEOUT,
            )

            if response.status_code == AppConstants.DEEPSEEK_SUCCESS_STATUS_CODE:
                result = response.json()
                content = result[AppConstants.DEEPSEEK_RESPONSE_CHOICES][0][
                    AppConstants.DEEPSEEK_RESPONSE_MESSAGE
                ][AppConstants.DEEPSEEK_RESPONSE_CONTENT]

                # 解析返回的JSON格式结果
                try:
                    parsed_result = json.loads(content)
                    domain = parsed_result.get(
                        AppConstants.DEEPSEEK_RESULT_DOMAIN,
                        AppConstants.DEEPSEEK_DEFAULT_DOMAIN,
                    )
                    refined_text = parsed_result.get(
                        AppConstants.DEEPSEEK_RESULT_REFINED_TEXT, text
                    )
                    return domain, refined_text
                except json.JSONDecodeError:
                    # 如果返回的不是JSON格式，直接返回内容
                    return AppConstants.DEEPSEEK_DEFAULT_DOMAIN, content
            else:
                raise Exception(
                    AppConstants.DEEPSEEK_ERROR_API_REQUEST.format(
                        status_code=response.status_code, error=response.text
                    )
                )

        except requests.exceptions.Timeout:
            raise Exception(AppConstants.DEEPSEEK_ERROR_TIMEOUT)
        except requests.exceptions.ConnectionError:
            raise Exception(AppConstants.DEEPSEEK_ERROR_CONNECTION)
        except Exception as e:
            raise Exception(AppConstants.DEEPSEEK_ERROR_GENERAL.format(error=str(e)))

    def run(self):
        """执行文案修复任务"""
        try:
            # 更新进度
            self.progress_updated.emit(AppConstants.DEEPSEEK_PROGRESS_START)

            # 检查输入文本
            if not self.text or not self.text.strip():
                raise ValueError(AppConstants.DEEPSEEK_ERROR_EMPTY_TEXT)

            # 检查API密钥
            if not self.api_key or not self.api_key.strip():
                raise ValueError(AppConstants.DEEPSEEK_ERROR_EMPTY_API_KEY)

            self.progress_updated.emit(AppConstants.DEEPSEEK_PROGRESS_VALIDATING)

            print(
                AppConstants.DEEPSEEK_LOG_START_REFINING,
                self.text[:50] + AppConstants.DEEPSEEK_LOG_TEXT_TRUNCATE,
            )

            # 调用API进行领域检测和文案修复
            domain, refined_text = self.detect_domain_and_refine(self.text)

            self.progress_updated.emit(AppConstants.DEEPSEEK_PROGRESS_PROCESSING)

            # 发送检测到的领域
            self.domain_detected.emit(domain)

            self.progress_updated.emit(AppConstants.DEEPSEEK_PROGRESS_COMPLETE)

            # 发送修复后的文案
            self.text_refined.emit(refined_text)

            print(AppConstants.DEEPSEEK_LOG_REFINING_SUCCESS)

        except ValueError as e:
            print(AppConstants.DEEPSEEK_LOG_VALIDATION_ERROR, e)
            self.error_occurred.emit(str(e))
        except Exception as e:
            print(AppConstants.DEEPSEEK_LOG_EXCEPTION, e)
            self.error_occurred.emit(str(e))
