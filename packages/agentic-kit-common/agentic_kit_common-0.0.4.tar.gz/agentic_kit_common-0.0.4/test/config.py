import os
import yaml
import json
import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)

def load_config(config_path: str = None) -> Dict[str, Any]:
    """从配置文件加载配置信息，支持多重路径查找"""
    
    if config_path is not None:
        # 如果指定了配置路径，直接使用
        return _load_single_config(config_path)
    
    # 多重路径查找策略
    search_paths = _get_config_search_paths()
    
    for path in search_paths:
        if os.path.exists(path):
            logger.info(f"找到配置文件: {path}")
            return _load_single_config(path)
    
    logger.warning(f"在以下路径中都未找到配置文件: {search_paths}")
    return {}

def _get_config_search_paths() -> List[str]:
    """获取配置文件的搜索路径列表"""
    current_file = os.path.abspath(__file__)
    paths = []
    
    # 1. 包根目录 (agentic_kit_common/)
    package_root = os.path.dirname(os.path.dirname(current_file))
    paths.extend([
        os.path.join(package_root, 'conf.yaml'),
        os.path.join(package_root, 'config.yaml'),
        os.path.join(package_root, 'config.json')
    ])
    
    # 2. 项目根目录的上一层（如果包在子目录中）
    project_parent = os.path.dirname(package_root)
    paths.extend([
        os.path.join(project_parent, 'conf.yaml'),
        os.path.join(project_parent, 'config.yaml'), 
        os.path.join(project_parent, 'config.json')
    ])
    
    # 3. 当前工作目录
    cwd = os.getcwd()
    paths.extend([
        os.path.join(cwd, 'conf.yaml'),
        os.path.join(cwd, 'config.yaml'),
        os.path.join(cwd, 'config.json')
    ])
    
    # 4. 用户主目录
    home_dir = os.path.expanduser('~')
    paths.extend([
        os.path.join(home_dir, '.agentic_kit_common', 'conf.yaml'),
        os.path.join(home_dir, '.agentic_kit_common', 'config.yaml'),
        os.path.join(home_dir, '.agentic_kit_common', 'config.json')
    ])
    
    # 5. 环境变量指定的路径
    env_config_path = os.environ.get('AGENTIC_KIT_CONFIG')
    if env_config_path:
        paths.insert(0, env_config_path)  # 环境变量路径优先级最高
    
    # 6. /etc 系统配置目录 (Linux/Mac)
    if os.name != 'nt':  # 非Windows系统
        paths.extend([
            '/etc/agentic_kit_common/conf.yaml',
            '/etc/agentic_kit_common/config.yaml',
            '/etc/agentic_kit_common/config.json'
        ])
    
    return paths

def _load_single_config(config_path: str) -> Dict[str, Any]:
    """加载单个配置文件"""
    if not os.path.exists(config_path):
        logger.warning(f"配置文件不存在: {config_path}")
        return {}
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config = yaml.safe_load(f)
            elif config_path.endswith('.json'):
                config = json.load(f)
            else:
                logger.error(f"不支持的配置文件格式: {config_path}")
                return {}
        
        logger.info(f"成功加载配置文件: {config_path}")
        return config or {}
        
    except Exception as e:
        logger.error(f"读取配置文件失败: {config_path}, 错误: {str(e)}")
        return {}

def get_config_info() -> Dict[str, Any]:
    """获取配置加载信息，用于调试"""
    search_paths = _get_config_search_paths()
    info = {
        'search_paths': search_paths,
        'existing_paths': [path for path in search_paths if os.path.exists(path)],
        'current_file': __file__,
        'working_directory': os.getcwd(),
        'env_config_path': os.environ.get('AGENTIC_KIT_CONFIG')
    }
    return info