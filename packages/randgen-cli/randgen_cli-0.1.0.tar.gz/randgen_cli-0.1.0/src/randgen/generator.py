import random
import string
from faker import Faker

class DataGenerator:
    def __init__(self, locale='en_US'):
        # 可以指定语言区域，例如 'zh_CN' 生成中文数据
        self.fake = Faker(locale)
    
    def generate_name(self):
        """生成随机姓名"""
        return self.fake.name()
    
    def generate_email(self):
        """生成随机邮箱"""
        return self.fake.email()
    
    def generate_date(self, start_date="-30y", end_date="today"):
        """
        生成随机日期
        start_date: 开始日期（默认30年前）
        end_date: 结束日期（默认今天）
        """
        return self.fake.date_between(start_date=start_date, end_date=end_date).isoformat()
    
    def generate_int(self, min_val=0, max_val=100):
        """生成指定范围内的随机整数"""
        return random.randint(min_val, max_val)
    
    def generate_float(self, min_val=0, max_val=100, precision=2):
        """生成指定范围内的随机浮点数"""
        value = random.uniform(min_val, max_val)
        return round(value, precision)
    
    def generate_string(self, length=10):
        """生成指定长度的随机字符串"""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))
    
    def generate_phone(self):
        """生成随机手机号"""
        return self.fake.phone_number()
    
    def generate_address(self):
        """生成随机地址"""
        return self.fake.address().replace('\n', ', ')