from lingtaiAgent.lingtai import LingtaiBot,lingtaiAgent_logger

lingtaiBot = LingtaiBot(
    bot_identity="SEC2d8ca7a0b492d3ad8e7cf0a4643960cd0bc931cd471c55604c659781473e1aa2",
    base_url = "http://127.0.0.1:8001",
    bot_type = "dingding2",
    bot_info = {},
    bot_config = {
        "webhook": "https://oapi.dingtalk.com/robot/send?access_token=8a946fe4882ad55dbd0be73fbdbe685f7778c0910a9658d5f125ae14b2d259aa",
        "secret": "SEC2d8ca7a0b492d3ad8e7cf0a4643960cd0bc931cd471c55604c659781473e1aa2",
        "token": "demo_robot",
        "gpt_config": {
            "base_url": "http://ack-bi2.inner.yueyuechuxing.test/v1",
            "api_key": "app-nUZMQQMknxINvsrcUhQUbEaT"
        }
    },
    bot_desc = "机器人功能测试群的自定义机器人"
)


@lingtaiBot.handler_msg()
def msg_register(msg):
    lingtaiAgent_logger.info("收到消息：", msg["origin_msg"]["text"]["content"])
    # 此处编写各种处理逻辑
    lingtaiBot.send_ai_text(msg["origin_msg"]["text"]["content"])
    lingtaiBot.set_robot_message_done(msg["id"])

if __name__ == '__main__':
    lingtaiBot.run()