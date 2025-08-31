# -*- coding: utf-8 -*-
# @Project: 芒果测试平台# @Description: 随机数据封装
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import random
import string
import uuid

from faker import Faker

from ..exceptions import MangoToolsError
from ..exceptions.error_msg import ERROR_MSG_0006


class RandomStringData:
    """ 随机的字符类型测试数据 """
    faker = Faker(locale='zh_CN')

    @classmethod
    def str_uuid(cls):
        """随机的UUID，长度36"""
        return str(uuid.uuid4())

    @classmethod
    def str_city(cls):
        """获取城市"""
        return cls.faker.city()

    @classmethod
    def str_country(cls):
        """获取国家"""
        return cls.faker.country()

    @classmethod
    def str_province(cls):
        """获取省份"""
        return cls.faker.province()

    @classmethod
    def str_pystr(cls):
        """生成英文的字符串"""
        return cls.faker.pystr()

    @classmethod
    def str_word(cls):
        """生成词语"""
        return cls.faker.word()

    @classmethod
    def str_text(cls):
        """生成一篇文章"""
        return cls.faker.text()

    @classmethod
    def str_random_string(cls, length=10):
        """随机字母数字,参数：length（默认10）"""
        try:
            length = int(length)
        except ValueError:
            raise MangoToolsError(*ERROR_MSG_0006)
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    @classmethod
    def str_lowercase(cls, length=10):
        """生成指定长度的纯小写字母字符串,参数：length（默认10）"""
        return ''.join(random.choices(string.ascii_lowercase, k=int(length)))

    @classmethod
    def str_uppercase(cls, length=10):
        """生成指定长度的纯大写字母字符串,参数：length（默认10）"""
        return ''.join(random.choices(string.ascii_uppercase, k=int(length)))

    @classmethod
    def str_special_chars(cls, length=10):
        """生成指定长度的特殊字符字符串,参数：length（默认10）"""
        special_chars = '!@#$%^&*()-_=+[]{}|;:,.<>?/'
        return ''.join(random.choices(special_chars, k=int(length)))

    @classmethod
    def str_email(cls):
        """生成随机邮箱"""
        return cls.faker.email()

    @classmethod
    def str_phone_number(cls):
        """生成随机手机号"""
        return cls.faker.phone_number()

    @classmethod
    def str_url(cls):
        """生成随机URL"""
        return cls.faker.url()

    @classmethod
    def str_ipv4(cls):
        """生成随机IPv4地址"""
        return cls.faker.ipv4()

    @classmethod
    def str_mac_address(cls):
        """生成随机MAC地址"""
        return cls.faker.mac_address()

    @classmethod
    def str_ipv6(cls):
        """生成随机IPv6地址"""
        return cls.faker.ipv6()

    @classmethod
    def str_date(cls):
        """生成随机日期字符串（YYYY-MM-DD）"""
        return cls.faker.date()

    @classmethod
    def str_time(cls):
        """生成随机时间字符串（HH:MM:SS）"""
        return cls.faker.time()

    @classmethod
    def str_datetime(cls):
        """生成随机日期时间字符串（YYYY-MM-DD HH:MM:SS）"""
        return cls.faker.date_time().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def str_company(cls):
        """生成随机公司名"""
        return cls.faker.company()

    @classmethod
    def str_name(cls):
        """生成随机人名"""
        return cls.faker.name()

    @classmethod
    def str_credit_card(cls):
        """生成随机银行卡号"""
        return cls.faker.credit_card_number()

    @classmethod
    def str_ssn(cls):
        """生成随机身份证号（中国大陆18位）"""
        return cls.faker.ssn()

    @classmethod
    def str_license_plate(cls):
        """生成随机车牌号"""
        return cls.faker.license_plate()

    @classmethod
    def str_url_path(cls):
        """生成随机URL路径"""
        return cls.faker.uri_path()

    @classmethod
    def str_hex_color(cls):
        """生成随机HEX颜色"""
        return cls.faker.hex_color()

    @classmethod
    def str_uuid_no_dash(cls):
        """生成无短横线的UUID字符串"""
        return uuid.uuid4().hex

    @classmethod
    def str_en_sentence(cls):
        """生成随机英文句子"""
        return cls.faker.sentence()

    @classmethod
    def str_en_paragraph(cls):
        """生成随机英文段落"""
        return cls.faker.paragraph()

    @classmethod
    def str_cn_name(cls):
        """生成随机中文姓名"""
        return cls.faker.name()

    @classmethod
    def str_cn_address(cls):
        """生成随机中文地址"""
        return cls.faker.address()

    @classmethod
    def str_postcode(cls):
        """生成随机邮政编码"""
        return cls.faker.postcode()

    @classmethod
    def str_company_email(cls):
        """生成随机公司邮箱"""
        return cls.faker.company_email()

    @classmethod
    def str_domain(cls):
        """生成随机域名"""
        return cls.faker.domain_name()

    @classmethod
    def str_filename(cls, extension='txt'):
        """生成随机文件名，可指定扩展名,参数：（默认txt）"""
        name = cls.faker.file_name()
        if extension:
            name = name.split('.')[0] + '.' + extension.lstrip('.')
        return name

    @classmethod
    def str_file_path(cls):
        """生成随机文件路径"""
        return cls.faker.file_path()

    @classmethod
    def str_image_url(cls):
        """生成随机图片URL"""
        return cls.faker.image_url()

    @classmethod
    def str_latlng(cls):
        """生成随机经纬度字符串"""
        return f"{cls.faker.latitude()},{cls.faker.longitude()}"

    @classmethod
    def str_html_tag(cls):
        """生成随机HTML标签字符串"""
        tag = random.choice(['div', 'span', 'a', 'p', 'img', 'ul', 'li', 'table', 'tr', 'td'])
        return f"<{tag}>{cls.faker.word()}</{tag}>"

    @classmethod
    def str_json(cls):
        """生成随机JSON字符串"""
        import json
        data = {cls.faker.word(): cls.faker.word() for _ in range(3)}
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def str_base64(cls, length=10):
        """生成随机Base64字符串,参数：length（默认10）"""
        import base64
        raw = cls.str_random_string(length=int(length))
        return base64.b64encode(raw.encode()).decode()

    @classmethod
    def str_emoji(cls):
        """生成随机Emoji表情"""
        emojis = ['😀', '😂', '🥰', '😎', '🤔', '😭', '👍', '🎉', '🔥', '🌈', '🍉', '🚀']
        return random.choice(emojis)

    @classmethod
    def str_color_name(cls):
        """生成随机颜色名"""
        return cls.faker.color_name()

    @classmethod
    def str_job(cls):
        """生成随机职业"""
        return cls.faker.job()

    @classmethod
    def str_university(cls):
        """生成随机大学名"""
        return cls.faker.university()

    @classmethod
    def str_company_job(cls):
        """生成随机公司职位"""
        return cls.faker.job()

    @classmethod
    def str_html_fragment(cls):
        """生成随机HTML片段字符串"""
        tag = random.choice(['div', 'span', 'a', 'p', 'img'])
        attr = f'id="{cls.faker.word()}" class="{cls.faker.word()}"'
        return f'<{tag} {attr}>{cls.faker.sentence()}</{tag}>'

    @classmethod
    def str_markdown(cls):
        """生成随机Markdown文本"""
        return f'# {cls.faker.word()}\n\n- {cls.faker.sentence()}\n- {cls.faker.sentence()}'

    @classmethod
    def str_sql(cls):
        """生成随机SQL语句字符串"""
        table = cls.faker.word()
        col = cls.faker.word()
        val = cls.faker.word()
        return f"SELECT * FROM {table} WHERE {col}='{val}';"

    @classmethod
    def str_xml_fragment(cls):
        """生成随机XML片段字符串"""
        tag = cls.faker.word()
        return f'<{tag}>{cls.faker.word()}</{tag}>'

    @classmethod
    def str_url_params(cls, count=3):
        """生成随机URL参数字符串,参数：count（默认3）"""
        params = [f'{cls.faker.word()}={cls.faker.word()}' for _ in range(int(count))]
        return '&'.join(params)

    @classmethod
    def str_intl_phone(cls):
        """生成随机国际电话号码字符串"""
        return cls.faker.phone_number().replace('-', ' ')

    @classmethod
    def str_card_number_split(cls):
        """生成带空格分隔的银行卡号字符串"""
        card = cls.faker.credit_card_number()
        return ' '.join([card[i:i + 4] for i in range(0, len(card), 4)])

    @classmethod
    def str_isbn(cls):
        """生成随机ISBN号字符串"""
        return cls.faker.isbn13(separator='-')

    @classmethod
    def str_vin(cls):
        """生成随机车架号（VIN）字符串"""
        return cls.faker.unique.bothify(text='?#?#?#?#?#?#?#?#?#?#?#?#?#?#?#')

    @classmethod
    def str_wechat_id(cls):
        """生成随机微信号字符串"""
        return cls.faker.user_name() + str(random.randint(100, 9999))

    @classmethod
    def str_qq(cls):
        """生成随机QQ号字符串"""
        return str(random.randint(10000, 999999999))

    @classmethod
    def str_short_url(cls):
        """生成随机短链字符串"""
        return f'https://bit.ly/{cls.str_random_string(length=7)}'

    @classmethod
    def str_special_mix(cls, length=10):
        """生成随机特殊符号混合字符串,参数：length（默认3）"""
        specials = '!@#$%^&*()_+-=~`[]{}|;:,.<>?/\\"\''
        return ''.join(random.choices(specials, k=length))

    @classmethod
    def str_whitespace(cls, length=10):
        """生成大段空白/制表符/换行符字符串,参数：length（默认3）"""
        chars = [' ', '\t', '\n']
        return ''.join(random.choices(chars, k=length))

    @classmethod
    def str_url_encoded(cls, length=10):
        """生成随机URL编码字符串,参数：length（默认3）"""
        import urllib.parse
        raw = cls.str_random_string(length=int(length))
        return urllib.parse.quote(raw)

    @classmethod
    def str_json_nested(cls):
        """生成随机嵌套JSON字符串"""
        import json
        data = {cls.faker.word(): {cls.faker.word(): cls.faker.word()} for _ in range(2)}
        return json.dumps(data, ensure_ascii=False)

    @classmethod
    def str_html_escape(cls):
        """生成随机HTML转义字符串"""
        import html
        raw = cls.faker.sentence()
        return html.escape(raw)

    @classmethod
    def str_with_emoji(cls):
        """生成带emoji的随机文本字符串"""
        base = cls.faker.sentence()
        emoji = random.choice(['😀', '😂', '🥰', '😎', '🤔', '😭', '👍', '🎉', '🔥', '🌈', '🍉', '🚀'])
        return base + emoji
