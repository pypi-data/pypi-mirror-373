import os
import logging
import requests
import inspect
from typing import List, Optional, Union, Dict, Any


class WeChatWorkSender:
    """企业微信API封装类，实现消息发送及相关功能"""

    def __init__(self, corpid: str, corpsecret: str, agentid: int):
        """
        初始化企业微信客户端
        :param corpid: 企业ID
        :param corpsecret: 应用密钥
        :param agentid: 应用编号
        """
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.access_token = self._fetch_access_token()

    def _fetch_access_token(self) -> str:
        """获取企业微信访问令牌"""
        endpoint = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        params = {
            "corpid": self.corpid,
            "corpsecret": self.corpsecret
        }
        response = requests.get(endpoint, params=params)
        result = response.json()

        if "access_token" not in result:
            raise SystemError(f"获取token失败: {result}")
        return result["access_token"]

    def upload_media(self, media_type: str, file_path: str) -> str:
        """
        上传多媒体文件到企业微信服务器
        :param media_type: 媒体类型 (image/file等)
        :param file_path: 本地文件路径
        :return: 媒体ID
        """
        upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.access_token}&type={media_type}"

        with open(file_path, "rb") as fh:
            files = {"media": fh}
            response = requests.post(upload_url, files=files)

        data = response.json()
        if "media_id" not in data:
            raise SystemError(f"文件上传失败: {data}")
        return data["media_id"]

    def send_text_message(self, user_ids: List[str], content: str) -> Dict[str, Any]:
        """
        发送文本消息给指定成员
        :param user_ids: 接收用户列表
        :param content: 消息内容
        :return: API响应原始数据
        """
        payload = {
            "touser": "|".join(user_ids),
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {"content": content},
            "safe": 0  # 不校验安全等级
        }
        return self._post_message("message/send", payload)

    def send_image_message(self, user_ids: List[str], image_path: str) -> Dict[str, Any]:
        """
        发送图片消息
        :param user_ids: 接收用户列表
        :param image_path: 图片文件路径
        :return: API响应原始数据
        """
        media_id = self.upload_media("image", image_path)
        payload = {
            "touser": "|".join(user_ids),
            "msgtype": "image",
            "agentid": self.agentid,
            "image": {"media_id": media_id},
            "safe": 0
        }
        return self._post_message("message/send", payload)

    def send_file_message(self, user_ids: List[str], file_path: str) -> Dict[str, Any]:
        """
        发送文件消息
        :param user_ids: 接收用户列表
        :param file_path: 文件路径
        :return: API响应原始数据
        """
        media_id = self.upload_media("file", file_path)
        payload = {
            "touser": "|".join(user_ids),
            "msgtype": "file",
            "agentid": self.agentid,
            "file": {"media_id": media_id},
            "safe": 0
        }
        return self._post_message("message/send", payload)

    def upload_group_file(self, webhook_url: str, file_path: str) -> str:
        """
        上传群聊文件
        :param webhook_url: 群机器人Webhook地址
        :param file_path: 要上传的文件路径
        :return: 媒体ID
        """
        key = webhook_url.split("key=")[1]
        upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file"

        with open(file_path, "rb") as fh:
            files = {"media": fh}
            response = requests.post(upload_url, files=files)

        data = response.json()
        if data["errcode"] != 0:
            raise SystemError(f"群文件上传失败: {data}")
        return data["media_id"]

    def send_group_text(self, webhook_url: str, text: str, mentioned_list: List[str] = None) -> Dict[str, Any]:
        """
        发送群聊文本消息
        :param webhook_url: 群机器人Webhook地址
        :param text: 文本内容
        :param mentioned_list: @提及的用户列表，默认为['@all']
        :return: API响应原始数据
        """
        if mentioned_list is None:
            mentioned_list = ["@all"]

        payload = {
            "msgtype": "text",
            "text": {
                "content": text,
                "mentioned_list": mentioned_list
            }
        }
        return requests.post(webhook_url, json=payload).json()

    def send_group_file(self, webhook_url: str, file_path: str) -> Dict[str, Any]:
        """
        发送群聊文件消息
        :param webhook_url: 群机器人Webhook地址
        :param file_path: 文件路径
        :return: API响应原始数据
        """
        media_id = self.upload_group_file(webhook_url, file_path)
        payload = {
            "msgtype": "file",
            "file": {"media_id": media_id}
        }
        return requests.post(webhook_url, json=payload).json()

    def recall_message(self, msgid: str) -> Dict[str, Any]:
        """
        撤回已发送的消息
        :param msgid: 要撤回的消息ID
        :return: API响应原始数据
        """
        if not msgid:
            raise ValueError("消息ID不能为空")

        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/recall?access_token={self.access_token}"
        payload = {"msgid": msgid}

        try:
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            raise SystemError(f"消息撤回失败: {str(e)}")

    def _post_message(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """通用消息发送方法"""
        url = f"https://qyapi.weixin.qq.com/cgi-bin/{endpoint}?access_token={self.access_token}"
        return requests.post(url, json=data).json()


class WeComMessageHandler:
    """企业微信消息处理器，支持多种消息类型和模式切换"""

    MODE_ENTERPRISE = "enterprise"  # 企业应用模式
    MODE_GROUP_WEBHOOK = "group_webhook"  # 群聊Webhook模式

    def __init__(self, *args, **kwargs):
        """
        初始化消息处理器，支持两种模式：
        1. 企业模式：需要提供(corpid, corpsecret, agentid)
        2. Webhook模式：需要提供group_webhook
        """
        self.mode = None
        self.logger = self._setup_logger()

        # 解析参数确定工作模式
        if 'group_webhook' in kwargs and kwargs['group_webhook']:
            self._init_webhook_mode(kwargs['group_webhook'])
        elif len(args) == 3:  # corpid, corpsecret, agentid
            self._init_enterprise_mode(*args)
        else:
            raise ValueError("无效的初始化参数组合")

    def _setup_logger(self) -> logging.Logger:
        """配置日志系统，确保中文无乱码"""
        caller_frame = inspect.stack()[2]
        caller_filepath = caller_frame.filename
        caller_filename = os.path.basename(caller_filepath)
        log_filename = f"{os.path.splitext(caller_filename)[0]}.log"
        log_dir = os.path.dirname(caller_filepath)
        log_filepath = os.path.join(log_dir, log_filename)

        # 确保目录存在
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except PermissionError:
                log_dir = os.path.expanduser("~")
                log_filepath = os.path.join(log_dir, log_filename)
                print(f"警告：无权限创建日志目录，使用默认目录 {log_dir}")
            except Exception as e:
                print(f"警告：无法创建日志目录，仅输出控制台日志：{str(e)}")
                log_filepath = None

        # 独立日志器（避免冲突）
        logger = logging.getLogger("WeComMessageHandler")
        logger.setLevel(logging.INFO)
        logger.propagate = False  # 不传递给根日志器，避免重复

        # 清除旧处理器
        if logger.handlers:
            logger.handlers.clear()

        # 日志格式（包含模块行号，便于调试）
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台处理器（无需编码，输出到终端）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器（强制 utf-8 编码，解决中文乱码）
        if log_filepath:
            try:
                # 关键：必须显式指定 encoding='utf-8'
                file_handler = logging.FileHandler(log_filepath, mode="a", encoding="utf-8")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                logger.info(f"日志系统初始化完成，日志文件：{log_filepath}")
                logger.info("中文日志测试：日志初始化成功（中文正常显示）")  # 测试中文
            except Exception as e:
                logger.warning(f"无法创建日志文件，仅输出到控制台：{str(e)}")
        else:
            logger.info("日志系统初始化完成，仅输出控制台日志")

        return logger

    def _init_enterprise_mode(self, corpid: str, corpsecret: str, agentid: int):
        """初始化企业模式"""
        self.mode = self.MODE_ENTERPRISE
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.group_webhook = None
        self.sender = WeChatWorkSender(corpid, corpsecret, agentid)

    def _init_webhook_mode(self, webhook_url: str):
        """初始化Webhook模式"""
        self.mode = self.MODE_GROUP_WEBHOOK
        self.group_webhook = webhook_url
        self.corpid = None
        self.corpsecret = None
        self.agentid = None
        self.sender = WeChatWorkSender("", "", "")  # Dummy sender for webhook mode

    def send_message(self, target: Union[str, List[str]], message: Union[str, bytes], mentioned_list: List[str] = None):
        """
        发送消息入口方法
        :param target: 接收目标（企业模式下为用户ID，Webhook模式下忽略）
        :param message: 消息内容或文件路径
        :param mentioned_list: @提及的用户列表（仅群聊有效）
        """
        try:
            if self.mode == self.MODE_ENTERPRISE:
                self._send_enterprise_message(target, message, mentioned_list)
            elif self.mode == self.MODE_GROUP_WEBHOOK:
                self._send_webhook_message(message, mentioned_list)
        except Exception as e:
            self.logger.error(f"消息发送失败: {str(e)}", exc_info=True)
            raise

    def _send_enterprise_message(self, user_id: str, message: Union[str, bytes], mentioned_list: List[str]):
        """企业模式下的消息发送逻辑"""
        self.logger.info(f"向企业用户[{user_id}]发送消息")

        if isinstance(message, str):
            if message.endswith(('.jpg', '.png', '.gif')):
                result = self.sender.send_image_message([user_id], message)
            elif os.path.isfile(message):
                ext = os.path.splitext(message)[1].lower()
                if ext in ['.xlsx', '.docx', '.pdf', '.txt', '.ppt', '.pptx']:
                    result = self.sender.send_file_message([user_id], message)
                else:
                    result = self.sender.send_text_message([user_id], open(message, 'r').read())
            else:
                result = self.sender.send_text_message([user_id], message)
        else:
            raise TypeError("不支持的消息类型")

        self._handle_result(result, f"发给[{user_id}]的消息")

    def _send_webhook_message(self, message: Union[str, bytes], mentioned_list: List[str]):
        """Webhook模式下的消息发送逻辑"""
        self.logger.info("向群聊发送Webhook消息")

        if isinstance(message, str):
            if os.path.isfile(message):
                result = self.sender.send_group_file(self.group_webhook, message)
            else:
                result = self.sender.send_group_text(self.group_webhook, message, mentioned_list)
        else:
            raise TypeError("不支持的消息类型")

        self._handle_result(result, "群聊消息")

    def _handle_result(self, result: Dict, message_prefix: str):
        """处理API调用结果"""
        msgid = result.get('msgid', '未知')
        success = result.get('errcode', -1) == 0

        log_msg = f"{message_prefix}发送结果: {'成功' if success else '失败'}, " \
                  f"错误码: {result.get('errcode')}, 消息ID: {msgid}"

        if success:
            self.logger.info(log_msg)
            print(f"&#9989; 消息发送成功，ID: {msgid}")
        else:
            self.logger.error(log_msg)
            print(f"&#10060; 消息发送失败，错误: {result.get('errmsg')}")

    def recall_message(self, msgid: str) -> bool:
        """撤回消息（仅企业模式支持）"""
        if self.mode != self.MODE_ENTERPRISE:
            self.logger.warning("当前模式不支持消息撤回")
            return False

        self.logger.info(f"尝试撤回消息 [{msgid}]")
        try:
            result = self.sender.recall_message(msgid)
            if result.get('errcode') == 0:
                self.logger.info(f"消息撤回成功: {msgid}")
                return True
            else:
                self.logger.warning(f"消息撤回失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            self.logger.error(f"撤回异常: {str(e)}")
            return False
