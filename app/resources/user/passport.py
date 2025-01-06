from flask_restful import Resource
from flask_limiter.util import get_remote_address
from flask import request, current_app, g
from flask_restful.reqparse import RequestParser
import random
from datetime import datetime, timedelta
from redis.exceptions import ConnectionError

from celery_tasks.email.tasks import send_email
from utils import constants
from utils import validate

from utils.jwt_util import generate_jwt
# from cache import user as cache_user
from utils.limiter import limiter as lmt

class EmailResource(Resource):
    """
    发邮件
    """
    error_message = 'Too many requests.'

    decorators = [
        lmt.limit(constants.LIMIT_EMAIL_SNED_BY_RECIPENT,
                  key_func=lambda: request.view_args['recipient'],
                  error_message=error_message),
        lmt.limit(constants.LIMIT_EMAIL_VERIFICATION_CODE_BY_IP,
                  key_func=get_remote_address,
                  error_message=error_message)
    ]

    def get(self, recipients, subject, body):
        # 为每个收件人生成验证码并发送邮件
        for recipient in recipients:
            code = '{:0>6d}'.format(random.randint(0, 999999))
            # 存储每个收件人的验证码
            current_app.redis_master.setex(f'app:code:{recipient}', constants.EMAIL_VERIFICATION_CODE_EXPIRES, code)
            
            # 异步发送邮件
            send_email.delay(recipient, subject, body)
        
        # 返回所有的收件人
        return {'recipients': recipients}


class AuthorizationResource(Resource):
    """
    认证
    """
    def _generate_tokens(self, user_id, refresh=True):
        """
        生成token 和refresh_token
        :param user_id: 用户id
        :return: token, refresh_token
        """
        # 颁发JWT
        secret = current_app.config['JWT_SECRET']
        # 生成调用token， refresh_token
        expiry = datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])

        token = generate_jwt({'user_id': user_id}, expiry, secret)

        if refresh:
            exipry = datetime.utcnow() + timedelta(days=current_app.config['JWT_REFRESH_DAYS'])
            refresh_token = generate_jwt({'user_id': user_id, 'is_refresh': True}, exipry, secret)
        else:
            refresh_token = None

        return token, refresh_token

    def post(self):
        """
        登录创建token
        """
        json_parser = RequestParser()
        json_parser.add_argument('recipient', type=validate.recipient, required=True, location='json')
        json_parser.add_argument('code', type=validate.regex(r'^\d{6}$'), required=True, location='json')
        args = json_parser.parse_args()
        recipient = args.recipient
        code = args.code

        # 从redis中获取验证码
        key = 'app:code:{}'.format(recipient)
        try:
            real_code = current_app.redis_master.get(key)
        except ConnectionError as e:
            current_app.logger.error(e)
            real_code = current_app.redis_slave.get(key)

        try:
            current_app.redis_master.delete(key)
        except ConnectionError as e:
            current_app.logger.error(e)

        if not real_code or real_code.decode() != code:
            return {'message': 'Invalid code.'}, 400

        # 生成用户的jwt token
        # 在payload 保存用户的什么信息
        # user_id  一定

        token, refresh_token = self._generate_tokens(user.id)

        return {'token': token, 'refresh_token': refresh_token}, 201

    def put(self):
        """
        刷新token
        :return:
        """
        if g.user_id is not None and g.is_refresh is True:
            token, refresh_token = self._generate_tokens(g.user_id, refresh=False)
            return {'token': token}
        else:
            return {'message': 'Invalid refresh token'}, 403
