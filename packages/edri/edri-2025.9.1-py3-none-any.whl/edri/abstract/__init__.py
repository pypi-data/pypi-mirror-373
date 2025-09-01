from .manager.manager_base import ManagerBase
from .manager.manager_priority_base import ManagerPriorityBase


def request(func):
    func.__purpose__ = "request"
    return func


def response(func):
    func.__purpose__ = "response"
    return func


__all__ = ["ManagerBase", "ManagerPriorityBase", "request", "response"]
