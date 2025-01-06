import time
import json
from celery.utils.log import get_task_logger

from celery_tasks.main import app
from flask_mail import Mail, Message

from flask import current_app

logger = get_task_logger(__name__)

# 定义任务:
# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff × 2^(n-1))s
# max_retries：异常自动重试次数的上限
@app.task(bind=True, name='email.send_email', retry_backoff=3)
def send_email(self, recipient, subject, body):
    """
    发送邮件
    :param recipient: 收件人邮箱
    :param subject: 邮件主题
    :param body: 邮件内容
    :return:
    """
    try:
        msg = Message(subject=subject, recipients=[recipient], body=body)
        current_app.mail.send(msg)
        logger.info(f"[send_email] 邮件发送成功: 收件人={recipient}, 主题={subject}")
        return {'status': 'success', 'recipient': recipient}
    except Exception as e:
        logger.error(f"[send_email] 邮件发送失败: 收件人={recipient}, 错误={e}")
        # 发生异常自动重试，最多重试 3 次
        raise self.retry(exc=e)

