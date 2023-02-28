#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @FileName  :ui_state.py
# @Time      :08/02/2023
# @Author    :russionbear
# @Function  :function
from typing import Generic, Dict
from qins_moon.core.utils.data_structure import RegistryBase, AnyT, Any


class IUIStateInterface:
    def event(self, e0):
        pass

    def active(self):
        pass

    def inactive(self):
        pass


class UIStateManagerBase(RegistryBase[AnyT]):
    """
    不适用stack是因为它没dict+currentUiStateMngr灵活
    """
    def __init__(self):
        super().__init__()
        self._storage: Dict[Any, AnyT] = {}
        # 运行时不能为空
        self.currentUIState: None | IUIStateInterface = None

    def switch_ui_state(self, key):
        if self.currentUIState is not None:
            self.currentUIState.inactive()
        self.currentUIState = self[key]
        self.currentUIState.active()

    def active(self):
        self.currentUIState.active()

    def inactive(self):
        self.currentUIState.inactive()

    def event(self, e0):
        self.currentUIState.event(e0)


class UIStateMngManager(RegistryBase[UIStateManagerBase]):
    """
    不适用stack是因为它没dict+currentUiStateMngr灵活
    """
    _instance = None

    def __init__(self):
        if self.__class__._instance is not None:
            return
        self.__class__._instance = self
        super().__init__()
        # 运行时不能为空
        self.currentUiStateMngr: UIStateManagerBase | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            return cls._instance
        return super().__new__(cls)

    def switch_ui_state_mngr(self, key):
        if self.currentUiStateMngr is not None:
            self.currentUiStateMngr.inactive()
        self.currentUiStateMngr = self[key]
        self.currentUiStateMngr.active()
