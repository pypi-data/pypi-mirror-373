# pip install lark-oapi -U
import json
import os
import uuid
from typing import Optional

import lark_oapi as lark
from lark_oapi.api.im.v1 import *


class FeishuBot:
    """飞书机器人类，封装所有机器人相关功能"""
    
    def __init__(self, config):
        """
        初始化飞书机器人
        
        Args:
            config: 配置对象，包含应用ID、应用密钥和群组信息
        """
        self.config = config
        self._client = None
    
    @property
    def client(self):
        """获取飞书客户端，使用懒加载模式"""
        if self._client is None:
            self._client = lark.Client.builder() \
                .app_id(self.config.feishu_bot.app_id) \
                .app_secret(self.config.feishu_bot.app_secret) \
                .log_level(lark.LogLevel.INFO) \
                .build()
        return self._client
    
    def _get_chat_id(self, bot_name: str) -> Optional[str]:
        """
        根据群组别名获取群组ID
        
        Args:
            bot_name: 群组别名
            
        Returns:
            群组ID，如果别名不存在则返回None
        """
        return self.config.dict_feishu_group.get(bot_name)
    
    def _handle_response_error(self, response, operation_name: str):
        """
        处理API响应错误
        
        Args:
            response: API响应对象
            operation_name: 操作名称，用于错误日志
        """
        if not response.success():
            lark.logger.error(
                f"{operation_name} failed, code: {response.code}, "
                f"msg: {response.msg}, log_id: {response.get_log_id()}, "
                f"resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
            )
            return True
        return False
    
    def send_text(self, content: str, bot_name: str = 'test') -> bool:
        """
        发送文本消息
        
        Args:
            content: 文本内容
            bot_name: 群组别名，默认为'test'
            
        Returns:
            发送是否成功
        """
        chat_id = self._get_chat_id(bot_name)
        if not chat_id:
            lark.logger.error(f"未找到群组别名 '{bot_name}' 对应的群组ID")
            return False
        
        message_content = {"text": content}
        
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(chat_id)
                          .msg_type("text")
                          .content(json.dumps(message_content))
                          .uuid(str(uuid.uuid4()))
                          .build()) \
            .build()
        
        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        
        # 处理失败返回
        if self._handle_response_error(response, "send_text"):
            return False
        
        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return True
    
    def send_image(self, file_path: str, bot_name: str = 'test') -> bool:
        """
        发送图片消息
        
        Args:
            file_path: 图片文件路径
            bot_name: 群组别名，默认为'test'
            
        Returns:
            发送是否成功
        """
        # 先上传图片获取image_key
        image_key = self.upload_image(file_path)
        if not image_key:
            return False
        
        chat_id = self._get_chat_id(bot_name)
        if not chat_id:
            lark.logger.error(f"未找到群组别名 '{bot_name}' 对应的群组ID")
            return False
        
        message_content = {"image_key": image_key}
        
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(chat_id)
                          .msg_type("image")
                          .content(json.dumps(message_content))
                          .uuid(str(uuid.uuid4()))
                          .build()) \
            .build()
        
        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        
        # 处理失败返回
        if self._handle_response_error(response, "send_image"):
            return False
        
        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return True
    
    def send_excel(self, file_path: str, bot_name: str = 'test') -> bool:
        """
        发送Excel文件
        
        Args:
            file_path: Excel文件路径
            bot_name: 群组别名，默认为'test'
            
        Returns:
            发送是否成功
        """
        # 先上传文件获取file_key
        file_key = self.upload_excel(file_path)
        if not file_key:
            return False
        
        chat_id = self._get_chat_id(bot_name)
        if not chat_id:
            lark.logger.error(f"未找到群组别名 '{bot_name}' 对应的群组ID")
            return False
        
        message_content = {"file_key": file_key}
        
        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(chat_id)
                          .msg_type("file")
                          .content(json.dumps(message_content))
                          .uuid(str(uuid.uuid4()))
                          .build()) \
            .build()
        
        # 发起请求
        response: CreateMessageResponse = self.client.im.v1.message.create(request)
        
        # 处理失败返回
        if self._handle_response_error(response, "send_excel"):
            return False
        
        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return True
    
    def upload_excel(self, file_path: str) -> Optional[str]:
        """
        上传Excel文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件key，上传失败返回None
        """
        if not os.path.exists(file_path):
            lark.logger.error(f"文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, "rb") as file:
                file_name = os.path.basename(file_path)
                request: CreateFileRequest = CreateFileRequest.builder() \
                    .request_body(CreateFileRequestBody.builder()
                                  .file_type("xls")
                                  .file_name(file_name)
                                  .file(file)
                                  .build()) \
                    .build()
                
                # 发起请求
                response: CreateFileResponse = self.client.im.v1.file.create(request)
                
                # 处理失败返回
                if self._handle_response_error(response, "upload_excel"):
                    return None
                
                # 处理业务结果
                lark.logger.info(lark.JSON.marshal(response.data, indent=4))
                return response.data.file_key
        except Exception as e:
            lark.logger.error(f"上传Excel文件时发生错误: {e}")
            return None
    
    def upload_image(self, file_path: str) -> Optional[str]:
        """
        上传图片文件
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            图片key，上传失败返回None
        """
        if not os.path.exists(file_path):
            lark.logger.error(f"文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, "rb") as file:
                request: CreateImageRequest = CreateImageRequest.builder() \
                    .request_body(CreateImageRequestBody.builder()
                                  .image_type("message")
                                  .image(file)
                                  .build()) \
                    .build()
                
                # 发起请求
                response: CreateImageResponse = self.client.im.v1.image.create(request)
                
                # 处理失败返回
                if self._handle_response_error(response, "upload_image"):
                    return None
                
                # 处理业务结果
                lark.logger.info(lark.JSON.marshal(response.data, indent=4))
                return response.data.image_key
        except Exception as e:
            lark.logger.error(f"上传图片文件时发生错误: {e}")
            return None