import logging
import os
from pathlib import Path

import toml

ROOT_PATH: Path = Path(__file__ + '/../..').resolve()


class BaseConfig:
    """
    配置管理的基类。
    """
    
    @classmethod
    def update_from_toml(cls, path: str, section: str = None):
        try:
            config = toml.load(path)
            items = config.get(section, {}) if section else config
            for key, value in items.items():
                if hasattr(cls, key.upper()):
                    setattr(cls, key.upper(), value)
        except Exception as err:
            logging.error(f'Loading config error: {err}')


class Config(BaseConfig):
    """
    全局配置
    """
    DATABASES_DIR: Path = ROOT_PATH / 'database'  # 数据库路径
    LOG_LEVE: int = 20  # 日志等级
    SQLALCHEMY_LOG: bool = False  # sqlalchemy 日志
    BOT_TOKEN: str = ""  # 机器人 Token


class SubmitConfig(BaseConfig):
    """
    投稿配置
    """
    SUBMITTER_LIMIT: bool = False  # 投稿限制
    SUBMITTER_LIMIT_BAN: bool = True  # 投稿限制封禁
    SUBMITTER_LIMIT_MINUTE: int = 6  # 投稿限制频率/分钟 表示每分钟最多投6份稿件
    SUBMITTER_LIMIT_DAY: int = 100  # 投稿限制频率/分钟 表示每天最多投100份稿件
    
    # 投稿类型
    SUBMITTER_TYPE_LIMIT: bool = True  # 投稿类型限制
    SUBMITTER_TYPE: list = ["TEXT", "PHOTO", "VIDEO", "DOCUMENT"]  # 允许的投稿类型 TEXT,PHOTO,VIDEO,STICKER,ANIMATION,DOCUMENT


class ReviewConfig(BaseConfig):
    """
    审核配置
    """
    REJECTED_CHANNEL: int = 0  # 拒稿频道
    PUBLISH_CHANNEL: int = 0  # 发布频道
    REVIEWER_GROUP: int = 0  # 审核群组
    REJECTION_REASON: str = "内容不够有趣:内容不适当:重复投稿"  # 拒稿理由
    REJECT_NUMBER_REQUIRED: int = 2  # 拒稿所需的最小审核人数
    APPROVE_NUMBER_REQUIRED: int = 2  # 通过所需的最小审核人数
    REJECT_REASON_USER_LIMIT: bool = True  # 是否限制只能由原拒稿人选择拒稿理由
    RETRACT_NOTIFY: bool = True  # 是否通知投稿者稿件被撤回
    BANNED_NOTIFY: bool = True  # 是否通知投稿者已被屏蔽


if os.path.exists(os.path.join(ROOT_PATH, 'config.toml')):
    _toml_file_path = os.path.join(ROOT_PATH, 'config.toml')
    Config.update_from_toml(_toml_file_path)
    ReviewConfig.update_from_toml(_toml_file_path, 'Review')
    SubmitConfig.update_from_toml(_toml_file_path, 'Submit')
