from lingtaiAgent.lingtai import LingtaiBot,lingtaiAgent_logger

lingtaiBot = LingtaiBot(
    bot_identity="",
    base_url = "http://127.0.0.1:8001",
    bot_type = "dingding2",
    bot_info = {},
    bot_config = {
        "webhook": "https://oapi.dingtalk.com/robot/send?access_token=",
        "secret": "",
        "token": "demo_robot"
    },
    bot_desc = "机器人功能测试群的自定义机器人"
)


@lingtaiBot.handler_msg()
def msg_register(msg):
    lingtaiAgent_logger.info("收到消息：", msg)
    # 此处编写各种处理逻辑
    lingtaiBot.send_text("你好，世界")
    lingtaiBot.set_robot_message_done(msg["id"])

if __name__ == '__main__':
    lingtaiBot.run()