#!/usr/bin/env python
# -- coding: utf-8 --
# author: albert time:2023/5/7
from typing import Text

from pydantic import BaseModel


class Config(BaseModel):
    """存储项目的配置信息"""
    # 项目名称
    project_name: Text
    # 项目环境
    env: Text
    # 测试人
    tester_name: Text
    # 是否信息通知
    notification_type: Text = '0'
    # 是否生成excel报告
    excel_report: bool
    # 是否实时更新测试用例
    real_time_update_test_cases: bool = False
    # 测试url
    host: Text