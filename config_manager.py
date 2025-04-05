# config_manager.py
import json
import os

def load_accounts(config_file="config.json"):
    """
    从配置文件加载账号信息.

    Args:
        config_file: 配置文件路径.

    Returns:
        账号列表 (字典列表).
    """
    config_dir = os.path.dirname(config_file)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir)  # 创建目录如果不存在

    if not os.path.exists(config_file):
        return []

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        return accounts if isinstance(accounts, list) else []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {config_file}: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error loading accounts from {config_file}: {e}")
        return []

def save_accounts(accounts, config_file="config.json"):
    """
    将账号信息保存到配置文件.

    Args:
        accounts: 账号列表 (字典列表).
        config_file: 配置文件路径.
    """
    config_dir = os.path.dirname(config_file)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir)

    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, indent=4, ensure_ascii=False)
        print(f"Accounts saved to {config_file}")
    except Exception as e:
        print(f"Failed to save accounts to {config_file}: {e}")