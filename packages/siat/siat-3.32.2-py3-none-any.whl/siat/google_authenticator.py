# -*- coding: utf-8 -*-
"""
本模块功能：模拟谷歌验证器，Google Authenticator
基于电脑时间，以密钥为基准，生成6位数字动态口令
"""

import hmac, base64, struct, hashlib, time

class CalGoogleCode():
    """计算谷歌验证码（秘钥，生成6位验证码）"""

    # 使用静态方法，调用这个方法时，不必对类进行实例化
    @staticmethod
    def cal_google_code(secret, current_time=int(time.time()) // 30):
        """
        :param secret:   16位谷歌秘钥
        :param current_time:   时间（谷歌验证码是30s更新一次）
        :return:  返回6位谷歌验证码
        """
        key = base64.b32decode(secret)
        msg = struct.pack(">Q", current_time)
        google_code = hmac.new(key, msg, hashlib.sha1).digest()
        o = ord(chr(google_code[19])) & 15  # python3时，ord的参数必须为chr类型
        google_code = (struct.unpack(">I", google_code[o:o + 4])[0] & 0x7fffffff) % 1000000
        
        return '%06d' % google_code  # 不足6位时，在前面补0

def signin_binance():
    secret_key = "HLAT4FZ6IDW53AYD"
    print(CalGoogleCode.cal_google_code(secret_key))
    
    return

def signin_pypi():
    secret_key = "CYKOJC2LMKOKPD6VGI7CAHDWBP2AVB23"
    print(CalGoogleCode.cal_google_code(secret_key))

    return

if __name__ == '__main__':
    # For Binance
    secret_key = "HLAT4FZ6IDW53AYD"
    print(CalGoogleCode.cal_google_code(secret_key))
    
    # for PyPi
    secret_key = "CYKOJC2LMKOKPD6VGI7CAHDWBP2AVB23"
    print(CalGoogleCode.cal_google_code(secret_key))
