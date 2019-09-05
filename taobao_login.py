import re
import os
import json

import requests

"""
获取详细教程、获取代码帮助、提出意见建议
关注微信公众号「裸睡的猪」与猪哥联系

@Author  :   猪哥,
@Version :   2.0"
"""

s = requests.Session()
# cookies序列化文件
COOKIES_FILE_PATH = 'taobao_login_cookies.txt'


class TaoBaoLogin:

    def __init__(self, session):
        """
        账号登录对象
        :param username: 用户名
        :param ua: 淘宝的ua参数
        :param TPL_password2: 加密后的密码
        """
        # 检测是否需要验证码的URL
        self.user_check_url = 'https://login.taobao.com/member/request_nick_check.do?_input_charset=utf-8'
        # 验证淘宝用户名密码URL
        self.verify_password_url = "https://login.taobao.com/member/login.jhtml"
        # 访问st码URL
        self.vst_url = 'https://login.taobao.com/member/vst.htm?st={}'
        # 淘宝个人 主页
        self.my_taobao_url = 'http://i.taobao.com/my_taobao.htm'

        # 淘宝用户名
        self.username = ''
        # 淘宝重要参数，从浏览器或抓包工具中复制，可重复使用
        self.ua = '120#bX1bSEvjRMp2ze/4jvYZMs/fbcomv9OI3Z7HiwbBdwWe5C9weI+bNAODPeK7mAeX74EwzlBOp79GXyKATeKcH+75j64avOVN+mTcF2I59mFf5dA2vLLFVoFN/YwwDHtkmlIDnhIwRNBOWCSF2P+ELE+DfWY2DSWnbD0BdSzH2eb9ifkk/woTLHo04BUZww5HlHCfbcsYsJfeekLliXIXSERUyn+medmJbccH0zTz7+4upEgVj2eDUH7NwCY5C2eozwi7gMqBjbAGHsN9vh/roEcPbE/ejUMPEIhSO5O3E/h5y12b7UHgWMfbLvv2VlMPDC0Zv5HHyB8/yvYS7U4RNWt/EDht7CoRyEuSb5htujPMybYb75UyNPc8CoYyMbgcVOKib1G74JiugnfIv/0j8aFMqOvxt9oioQpO6FjFXN9n40fS/WCFEEXLqD+sb/1VBb0aIxpmaKnIkALWg5PbFYSSBX2K+1tc07NOiWG6jjuzl6P7/QiNidfvmALZ+aR/LwuURI9PJWGV3ssr+U2Mtpw48o3JARdyZwAEzwrUrc4Vuz6aCYMQ8uPDSgja1tpLtbv7WULp3L3U7ymExWRqZ9Ghr0drjSupU7WqtWU+2LTvq1mphGnKHUFLN7EA4333WL6ufy9j5A0kIt1dNO7QzncwUpeUKmk2ElvvzjY+V2C6G0bKFE9QAcPa8oeLXZ/69DN10q8/hWX5BHmaM8acZ20kxRJlAypphFaR6UJ/8Nf3ldkUJVURw2fUa08hVSb0O6x6Ya2Jmxtg+VlZ3jxSK2lajQJgrGvsiXHejhaiC3Wb+gPoo/lZLRXH3bp/XkW4dFoqAy3vFCXLAFHuphEZ0YQVyjfJd43pZJe/Ead7F3QDsSILQRCN5qBKXcI5CWFZjvDZLDJQAfy+eOqB4Ebrmu2HYondSHTUFE6ihDoQlJzzUPZNDJU/YF/tYU8HLZFrMb5pP5XaBFTAgLbfOBtFLVJuZgmZYJwjK7Ybe6qWbSTld9TPaGyWhS+1hXud1iiquzDPxQ8AyMBGp179yPvwyNmp3jJH6sH6/Ug4i2nRFBnMkEHwHMyug1+YfnCqx/R1bnS5OJLOQUHD6hiySAkEg8p6ctwjPtkZnaHLPSBpQKh/I9dB6Vr84/fLI2O3le1se/DA6drRuZKE6s2lTYX3pRz+ZIYrpjKCCkIwKvcMUwJ6QLvG8LFjmA3/B+QI5Mrf6LEq3KZBB344KceXdzekSnno+XQ0lr7ZSVzSP5S/t/tb1PUb+ThSyg0GAORLEky4dGYsBxUtWuqThI9XDocYFxJhfW0zLF1WeIHQ7TnDx0EY0QE2VzfDkvO2ZEN/6i5IsBaMtmBDWGEceNktMG4w5hkITuTKt2fIJqHcc8qbNGFjJXxhCq1MvyFInY//asgUSqcpTSJ3q30E6P0HfnMSq2qx4dbBjsf82WJhA8OvjYmkNA9mM6COw0uL2ViR1vgYMFoB3vJXBvp4jeF4QU35ICEaxo+hT4LiEplhwRbPF2A0QWu+i7WoVABGta1u01e3JWiVr871aQ9JCw+pgTOU+EBUceLR7whdC9FFXXIcWuNoqAwib5BbTN3q34EvPbJ6Zx2wD9NsUTHuHqz78/voSKfkzH61Ba56L9eeXuzxNKGg8gLPk5AUdSIBLZejsRwg2lsZh6rdiEUtgbuBb/JscO//vVi/WkmrB424s+SlfJxnFYRiR8qiZi1+yY3HBuLFOYktMxhN7u0P8TPUT8UGQr4WPi8a+3qrIk4oOgFd+IY3d7DnFQtbeJ7lMyrMnvfWgEuuZnMhSAPEtyfu6sypunUH5ouwCcB+AJ0VRgG63ewKh7juRT2jOb89YqhGJ92n4RwMr8RSaBrol9nAvSUVAXZHZQkUBum32YAsTXaDDX1lKT3ATcQc'
        # 加密后的密码，从浏览器或抓包工具中复制，可重复使用
        self.TPL_password2 = '48b989ba5227430fde9317aab6d9f01c751b70ab66f716b205277add6d34e5d59386af23b970c76a3a95a7c42ff6e38b53d9c6b62c4cb94ad65db52b0733f5ef1e5682385daf204057f989b59c694ecd8912d6912696f2f94a63e9457b32b4c462afab6e503853c54a7fab236728404f52dd87c93e8de60ee0086789a1b1710e'

        # 请求超时时间
        self.timeout = 3
        # session对象，用于共享cookies
        self.session = session

        if not self.username:
            raise RuntimeError('请填写你的淘宝用户名')

    def _user_check(self):
        """
        检测账号是否需要验证码
        :return:
        """
        data = {
            'username': self.username,
            'ua': self.ua
        }
        try:
            response = self.session.post(self.user_check_url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('检测是否需要验证码请求失败，原因：')
            raise e
        needcode = response.json()['needcode']
        print('是否需要滑块验证：{}'.format(needcode))
        return needcode

    def _verify_password(self):
        """
        验证用户名密码，并获取st码申请URL
        :return: 验证成功返回st码申请地址
        """
        verify_password_headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://login.taobao.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://login.taobao.com/member/login.jhtml?from=taobaoindex&f=top&style=&sub=true&redirect_url=https%3A%2F%2Fi.taobao.com%2Fmy_taobao.htm',
        }
        # 登录toabao.com提交的数据，如果登录失败，可以从浏览器复制你的form data
        verify_password_data = {
            'TPL_username': self.username,
            'ncoToken': '78401cd0eb1602fc1bbf9b423a57e91953e735a5',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': 0,
            'newlogin': 0,
            'TPL_redirect_url': 'https://s.taobao.com/search?q=%E9%80%9F%E5%BA%A6%E9%80%9F%E5%BA%A6&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306',
            'from': 'tb',
            'fc': 'default',
            'style': 'default',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'loginType': '3',
            'gvfdcname': '10',
            # 'gvfdcre': '68747470733A2F2F6C6F67696E2E74616F62616F2E636F6D2F6D656D6265722F6C6F676F75742E6A68746D6C3F73706D3D61323330722E312E3735343839343433372E372E33353836363032633279704A767526663D746F70266F75743D7472756526726564697265637455524C3D6874747073253341253246253246732E74616F62616F2E636F6D25324673656172636825334671253344253235453925323538302532353946253235453525323542412532354136253235453925323538302532353946253235453525323542412532354136253236696D6766696C65253344253236636F6D6D656E64253344616C6C2532367373696425334473352D652532367365617263685F747970652533446974656D253236736F75726365496425334474622E696E64657825323673706D253344613231626F2E323031372E3230313835362D74616F62616F2D6974656D2E31253236696525334475746638253236696E69746961746976655F69642533447462696E6465787A5F3230313730333036',
            'TPL_password_2': self.TPL_password2,
            'loginASR': '1',
            'loginASRSuc': '1',
            'oslanguage': 'zh-CN',
            'sr': '1440*900',
            'osVer': 'macos|10.145',
            'naviVer': 'chrome|76.038091',
            'osACN': 'Mozilla',
            'osAV': '5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'osPF': 'MacIntel',
            'appkey': '00000000',
            'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?redirectURL=https://s.taobao.com/search?q=%E9%80%9F%E5%BA%A6%E9%80%9F%E5%BA%A6&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306&useMobile=true',
            'showAssistantLink': '',
            'um_token': 'TD0789BC99BFBBF893B3C8C0E1729CCA3CB0469EA11FF6D196BA826C8EB',
            'ua': self.ua
        }
        try:
            response = self.session.post(self.verify_password_url, headers=verify_password_headers, data=verify_password_data,
                              timeout=self.timeout)
            response.raise_for_status()
            # 从返回的页面中提取申请st码地址
        except Exception as e:
            print('验证用户名和密码请求失败，原因：')
            raise e
        # 提取申请st码url
        apply_st_url_match = re.search(r'<script src="(.*?)"></script>', response.text)
        # 存在则返回
        if apply_st_url_match:
            print('验证用户名密码成功，st码申请地址：{}'.format(apply_st_url_match.group(1)))
            return apply_st_url_match.group(1)
        else:
            raise RuntimeError('用户名密码验证失败！response：{}'.format(response.text))

    def _apply_st(self):
        """
        申请st码
        :return: st码
        """
        apply_st_url = self._verify_password()
        try:
            response = self.session.get(apply_st_url)
            response.raise_for_status()
        except Exception as e:
            print('申请st码请求失败，原因：')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', response.text)
        if st_match:
            print('获取st码成功，st码：{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败！response：{}'.format(response.text))

    def login(self):
        """
        使用st码登录
        :return:
        """
        # 加载cookies文件
        if self._load_cookies():
            return True
        # 判断是否需要滑块验证
        self._user_check()
        st = self._apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = self.session.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登录请求，原因：')
            raise e
        # 登录成功，提取跳转淘宝用户主页url
        my_taobao_match = re.search(r'top.location.href = "(.*?)"', response.text)
        if my_taobao_match:
            print('登录淘宝成功，跳转链接：{}'.format(my_taobao_match.group(1)))
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登录失败！response：{}'.format(response.text))

    def _load_cookies(self):
        # 1、判断cookies序列化文件是否存在
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        # 2、加载cookies
        self.session.cookies = self._deserialization_cookies()
        # 3、判断cookies是否过期
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies过期，删除cookies文件！')
            return False
        print('加载淘宝登录cookies成功!!!')
        return True

    def _serialization_cookies(self):
        """
        序列化cookies
        :return:
        """
        cookies_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def _deserialization_cookies(self):
        """
        反序列化cookies
        :return:
        """
        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_taobao_nick_name(self):
        """
        获取淘宝昵称
        :return: 淘宝昵称
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = self.session.get(self.my_taobao_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('获取淘宝主页请求失败！原因：')
            raise e
        # 提取淘宝昵称
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('登录淘宝成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('获取淘宝昵称失败！response：{}'.format(response.text))


if __name__ == '__main__':
    ul = TaoBaoLogin(s)
    ul.login()
    ul.get_taobao_nick_name()