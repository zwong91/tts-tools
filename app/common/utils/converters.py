from werkzeug.routing import BaseConverter


class MobileConverter(BaseConverter):
    """
    手机号格式
    """
    regex = r'1[3-9]\d{9}'


class EmailsConverter(BaseConverter):
    """
    邮箱列表格式
    例如: 'recipient1@example.com,recipient2@example.com'
    """
    regex = r'([A-Za-z0-9_\-\.\u4e00-\u9fa5]+@[A-Za-z0-9_\-\.]+\.[A-Za-z]{2,8})(,([A-Za-z0-9_\-\.\u4e00-\u9fa5]+@[A-Za-z0-9_\-\.]+\.[A-Za-z]{2,8}))*'

    def to_python(self, value):
        # 将传入的字符串（多个邮箱）按逗号分割并返回列表
        return value.split(',')
    

def register_converters(app):
    """
    向Flask app中注册转换器
    :param app: Flask app对象
    :return:
    """
    app.url_map.converters['mobile'] = MobileConverter
    app.url_map.converters['emails'] = EmailsConverter
