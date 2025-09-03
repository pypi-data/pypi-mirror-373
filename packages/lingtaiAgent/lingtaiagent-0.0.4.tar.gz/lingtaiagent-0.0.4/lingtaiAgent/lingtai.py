import logging, sys, requests, base64, threading, time, queue, hashlib
from typing import Dict, Any, Optional

def _get_logger(logname):
    log = logging.getLogger(logname)
    log.setLevel(logging.INFO)
    console_handle = logging.StreamHandler(sys.stdout)
    console_handle.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s',
                                                  datefmt='%Y-%m-%d %H:%M:%S'))
    log.addHandler(console_handle)
    return log

lingtaiAgent_logger = _get_logger("lingtai-agent")

# pass
class LingtaiBot(object):
    # 信息初始化，需要传入 bot 的 bot_identity
    def __init__(
        self,
        bot_identity: str = "",
        base_url: str = "http://127.0.0.1:8000",
        bot_type: str = "dingding2",
        bot_info: Optional[Dict[str, Any]] = None,
        bot_config: Optional[Dict[str, Any]] = None,
        bot_desc: str = "灵台机器人",
    ):
        self.bot_identity = bot_identity
        self.base_url = base_url
        self.bot_type = bot_type
        self.bot_info = bot_info if bot_info is not None else {}
        self.bot_config = bot_config if bot_config is not None else {}
        self.bot_desc = bot_desc

        self.receivingInterval = 5
        self.msgList = queue.Queue()
        self.functionDict = {'Msg': {}}

    # 启动进程
    def run(self):
        lingtaiAgent_logger.info("进程已启动")

        # 启动消息监听
        self.start_receiving()

        # 注册机器人信息
        self.register_bot()

        # 配置消息处理方法
        def reply_fn():
            lingtaiAgent_logger.info("开始配置消息处理函数")

            while True:
                try:
                    msg = self.msgList.get()
                    print("收到消息xxx：",msg)

                except queue.Empty:
                    pass
                else:
                    replyFn = self.functionDict['Msg'].get("handler_msg")

                    if replyFn is None:
                        lingtaiAgent_logger.warning("消息处理函数缺失")
                    else:
                        try:
                            replyFn(msg)
                        except Exception as e:
                            lingtaiAgent_logger.warning("消息处理函数异常")
                            lingtaiAgent_logger.warning(e)

        # 启动消息处理
        replyThread = threading.Thread(target=reply_fn)
        replyThread.start()

    # 注册机器人
    def register_bot(self):
        try:
            requests.request(
                method="POST",
                url="{}/api/v1/bot/registerRobot".format(self.base_url),
                json={
                    "bot_type": self.bot_type,
                    "bot_identity": self.bot_identity,
                    "bot_info": self.bot_info,
                    "bot_config": self.bot_config,
                    "bot_desc": self.bot_desc,
                },
            )
            lingtaiAgent_logger.info("机器人已注册".format(id))
        except:
            lingtaiAgent_logger.error("将消息「{}」状态置为已处理失败".format(id))

    # 消息处理
    def handler_msg(self):
        def _handler_msg(fn):
            self.functionDict['Msg']['handler_msg'] = fn
            return fn
        return _handler_msg

    # 接收消息
    def start_receiving(self):
        # 启动消息接收
        lingtaiAgent_logger.info("start_receiving")
        def maintain_loop():
            # 循环获取消息
            while True:
                lingtaiAgent_logger.info("每 {} 秒获取一次消息".format(self.receivingInterval))
                # 获取消息
                try:
                    received_msg_list = requests.request(
                        method="POST",
                        url="{}/api/v1/bot/getRobotMessage".format(self.base_url),
                        json={
                            "bot_identity":self.bot_identity,
                            "msg_status":"init"
                        },
                    ).json()["data"]
                except:
                    received_msg_list = []
                # received_msg_list = [{"text": "测试的文本消息1"}, {"text": "测试的文本消息2"}]
                lingtaiAgent_logger.info("消息内容为：{}".format(received_msg_list))
                # 如果时间线消息的数据不为空，则更新 lastId
                if len(received_msg_list) == 0:
                    pass
                else:
                    for msg in received_msg_list:
                        self.msgList.put(msg)
                time.sleep(self.receivingInterval)

        maintainThread = threading.Thread(target=maintain_loop)
        maintainThread.start()

    # 更改消息状态为已处理 并 执行机器人行为
    def set_robot_message_done(self, id):
        try:
            requests.request(
                method="POST",
                url="{}/api/v1/bot/updateRobotMessage".format(self.base_url),
                json={
                    "id": id,
                    "msg_status": "done"
                },
            )
            lingtaiAgent_logger.info("将消息「{}」状态置为已处理".format(id))
            requests.request(
                method="POST",
                url="{}/api/v1/bot/handleRobotActions".format(self.base_url),
                json={
                    "bot_identity": self.bot_identity,
                },
            )
            lingtaiAgent_logger.info("机器人行为已执行")
        except:
            lingtaiAgent_logger.error("将消息「{}」状态置为已处理失败".format(id))

    # 发送文本消息
    def send_text(self, text):
        try:
            requests.request(
                method="POST",
                url="{}/api/v1/bot/addRobotAction".format(self.base_url),
                json={
                    "bot_identity":self.bot_identity,
                    "action_name": "send_text",
                    "action_params": text
                },
            )
            lingtaiAgent_logger.info("发送消息[{}]成功".format(text))
        except:
            lingtaiAgent_logger.error("发送消息[{}]失败".format(text))

    # AI 回复消息
    def send_ai_text(self, text):
        try:
            my_gpt = ChatGPT(
                base_url=self.bot_config["gpt_config"]["base_url"],
                api_key=self.bot_config["gpt_config"]["api_key"],
                type="dify"
            )

            requests.request(
                method="POST",
                url="{}/api/v1/bot/addRobotAction".format(self.base_url),
                json={
                    "bot_identity":self.bot_identity,
                    "action_name": "send_text",
                    "action_params": my_gpt.chat({"role": "user", "content": str(text)})
                },
            )
            lingtaiAgent_logger.info("使用AI发送消息[{}]成功".format(text))
        except Exception as e:
            lingtaiAgent_logger.warning(e)
            lingtaiAgent_logger.error("使用AI发送消息[{}]失败".format(text))

# gpt 工具
class ChatGPT():
    def __init__(self, base_url, api_key, system_message=None, open_history=False, model="gpt-4o-mini", type=None, bot_id=None):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.messages = []
        self.system_message = system_message
        if system_message is None:
            self.system_message = {"role": "system", "content": ""}
        self.messages.append(system_message)
        self.open_history = open_history

        # 适配 dify
        self.type = type
        self.conversation = ""
        # 适配 coze
        self.bot_id = bot_id

    # 传入格式：{"role": "user", "content": "你叫什么名字？"}
    def chat(self, message):
        if self.type == "dify":
            # 适配 dify
            if self.open_history:
                res = requests.request(
                    method="POST",
                    url="{}/chat-messages".format(self.base_url),
                    headers={"Authorization": "Bearer {}".format(self.api_key), "Content-Type": "application/json"},
                    json={
                        "inputs": {},
                        "query": self.system_message["content"] + message["content"],
                        "response_mode": "blocking",
                        "conversation_id": self.conversation,
                        "user": message["role"]
                    }
                )
                print(res.text)
                self.conversation = res.json()["conversation_id"]
                return res.json()["answer"]
            else:
                res = requests.request(
                    method="POST",
                    url="{}/chat-messages".format(self.base_url),
                    headers={"Authorization": "Bearer {}".format(self.api_key), "Content-Type": "application/json"},
                    json={
                        "inputs": {},
                        "query": self.system_message["content"] + message["content"],
                        "response_mode": "blocking",
                        "user": message["role"]
                    }
                )
                print(res.text)
                return res.json()["answer"]
        elif self.type == "coze":
            # 适配扣子
            if self.open_history:
                res = requests.request(
                    method="POST",
                    url="{}/open_api/v2/chat".format(self.base_url),
                    headers={"Authorization": "Bearer {}".format(self.api_key), "Content-Type": "application/json"},
                    json={
                        "conversation_id": self.conversation,
                        "bot_id": self.bot_id,
                        "user": message["role"],
                        "query": self.system_message["content"] + message["content"],
                        "stream": False
                    }
                )
                self.conversation = res.json()["conversation_id"]
                for message in res.json()["messages"]:
                    if message["role"] == "assistant" and message["type"] == "answer":
                        return message["content"]
            else:
                res = requests.request(
                    method="POST",
                    url="{}/open_api/v2/chat".format(self.base_url),
                    headers={"Authorization": "Bearer {}".format(self.api_key), "Content-Type": "application/json"},
                    json={
                        "conversation_id": self.conversation,
                        "bot_id": self.bot_id,
                        "user": message["role"],
                        "query": self.system_message["content"] + message["content"],
                        "stream": False
                    }
                )
                for message in res.json()["messages"]:
                    if message["role"] == "assistant" and message["type"] == "answer":
                        return message["content"]
        else:
            # 原生 gpt
            if self.open_history:
                if len(self.messages) > 10:
                    del self.messages[1]
                self.messages.append(message)
                res = requests.request(
                    method="POST",
                    url="{}/v1/chat/completions".format(self.base_url),
                    headers={"Authorization": "Bearer {}".format(self.api_key), "Content-Type": "application/json"},
                    json={
                        "model": self.model,
                        "messages": self.messages
                    }
                )
                self.messages.append(res.json()["choices"][0]["message"])
                return res.json()["choices"][0]["message"]["content"]
            else:
                self.messages.append(message)
                res = requests.request(
                    method="POST",
                    url="{}/v1/chat/completions".format(self.base_url),
                    headers={"Authorization": "Bearer {}".format(self.api_key), "Content-Type": "application/json"},
                    json={
                        "model": self.model,
                        "messages": self.messages
                    }
                )
                self.messages.remove(message)
                return res.json()["choices"][0]["message"]["content"]
