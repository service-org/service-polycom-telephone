#! -*- coding: utf-8 -*-
#
# author: forcemain@163.com


from service_core.exception import RemoteError


class PolycomTelephoneError(RemoteError):
    """ PolycomTelephone异常 """
    pass


class PolycomTelephoneInvalidLoginError(RemoteError):
    """ PolycomTelephone首次帐号密码错误异常 """
    pass


class PolycomTelephoneInvalidLoginThatOneAttemptLeftError(RemoteError):
    """ PolycomTelephone多次帐号密码错误还剩一次异常 """
    pass


class PolycomTelephoneInvalidLoginThatLockedForError(RemoteError):
    """ PolycomTelephone多次帐号密码错误已被锁定异常 """
    pass


class PolycomTelephoneInvalidLoginThatLockedError(RemoteError):
    """ PolycomTelephone多次帐号密码错误在锁定中异常 """
    pass
