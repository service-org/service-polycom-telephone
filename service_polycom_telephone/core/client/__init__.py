#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from bs4 import BeautifulSoup
from logging import getLogger
from urllib3.util import make_headers
from service_client.core.client import BaseClient
from service_polycom_telephone.exception import PolycomTelephoneError
from service_polycom_telephone.exception import PolycomTelephoneInvalidLoginError
from service_polycom_telephone.exception import PolycomTelephoneInvalidLoginThatLockedError
from service_polycom_telephone.exception import PolycomTelephoneInvalidLoginThatLockedForError
from service_polycom_telephone.exception import PolycomTelephoneInvalidLoginThatOneAttemptLeftError

from .apis.restart import RestartAPI

logger = getLogger(__name__)


class PolycomTelephoneClient(BaseClient):
    """ PolycomTelephone通用连接类 """

    restart = RestartAPI()

    def __init__(
            self,
            username: t.Optional[t.Text] = None,
            password: t.Optional[t.Text] = None,
            verify_ssl: t.Optional[bool] = None,
            **kwargs: t.Any
    ) -> None:
        """ 初始化实例

        :param username: 登录帐号
            1. 默认值为Polycom
        :param password: 登录密码
            1. 默认密码为123456或456
        :param verify_ssl: 验证ssl?
            1. 默认不验证SSL证书
        :param kwargs: 其它参数
        """
        self.username = 'Polycom' if username is None else username
        self.password = '123456' if password is None else password
        not verify_ssl and kwargs.setdefault('pool_options', {}).update(
            {'cert_reqs': 'CERT_NONE', 'assert_hostname': False}
        )
        # 密码验证通过后的cookie
        self._pwd_auth_cookie = None
        # 管理后台页面csrf-token
        self._anti_csrf_token = None
        super(PolycomTelephoneClient, self).__init__(**kwargs)

    def set_pwd_auth_cookie(self) -> None:
        """ 设置密码验证会话凭证

        :return: None
        """
        if self._pwd_auth_cookie: return
        url = f'{self.base_url}/form-submit/auth.htm'
        headers = make_headers(basic_auth=f'{self.username}:{self.password}')
        rsp = super(PolycomTelephoneClient, self).request('POST', url, headers=headers)
        rsp_data = rsp.data.decode('utf-8')
        lock_params, login_state, locked_time = rsp_data.split('|')
        if login_state == 'INVALID_LOGIN':
            raise PolycomTelephoneInvalidLoginError('invalid password, try again')
        if login_state == 'ONE_ATTEMPT_LEFT':
            raise PolycomTelephoneInvalidLoginThatOneAttemptLeftError('invalid password, one login attempt left')
        if login_state == 'LOCKEDFOR':
            raise PolycomTelephoneInvalidLoginThatLockedForError(f'account is locked for {locked_time}')
        if login_state == 'LOCKED':
            raise PolycomTelephoneInvalidLoginThatLockedError('account is locked, try again after sometime')
        if login_state != 'SUCCESS':
            raise PolycomTelephoneError(rsp_data)
        logger.debug(f'rsp headers={rsp.headers}')
        self._pwd_auth_cookie = rsp.headers.get('Set-Cookie')

    def set_anti_csrf_token(self) -> None:
        """ 设置后台页面csrf-token

        :return: None
        """
        if self._anti_csrf_token: return
        url = f'{self.base_url}/index.htm'
        self.set_pwd_auth_cookie()
        headers = {'Cookie': self._pwd_auth_cookie}
        rsp = super(PolycomTelephoneClient, self).request('GET', url, headers=headers)
        rsp_data = rsp.data.decode('utf-8')
        bs4 = BeautifulSoup(rsp_data, 'html.parser')
        ele = bs4.find('meta', {'name': 'csrf-token'})
        self._anti_csrf_token = ele['content']

    def request(self, method: t.Text, url: t.Text, **kwargs: t.Any) -> t.Any:
        """ 请求处理方法

        :param method: 请求方法
        :param url: 请求地址
        :param kwargs: 请求参数
        :return: t.Any
        """
        self.set_pwd_auth_cookie()
        self.set_anti_csrf_token()
        headers = kwargs.setdefault('headers', {})
        self._pwd_auth_cookie and headers.update({'Cookie': self._pwd_auth_cookie})
        self._anti_csrf_token and headers.update({'anti-csrf-token': self._anti_csrf_token})
        return super(PolycomTelephoneClient, self).request(method, url, **kwargs)
