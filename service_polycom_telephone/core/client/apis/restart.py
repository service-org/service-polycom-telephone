#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com

from __future__ import annotations

import typing as t

from logging import getLogger
from service_client.core.client import BaseClientAPI

logger = getLogger(__name__)


class RestartAPI(BaseClientAPI):
    """ Restart接口类 """

    def post(self, **kwargs: t.Text) -> None:
        """ 重启polycom话机

        :param kwargs: 请求参数

        :return: None
        """
        url = f'{self._base_url}/form-submit/Restart'
        self._post(url, **kwargs)
