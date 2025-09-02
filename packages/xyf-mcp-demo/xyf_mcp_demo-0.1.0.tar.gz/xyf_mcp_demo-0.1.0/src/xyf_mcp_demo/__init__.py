# 导入 FastMCP 框架，用于创建 MCP 服务器
from mcp.server.fastmcp import FastMCP
# 导入类型注解，用于函数参数和返回值的类型声明
from typing import Dict, List, Optional
# 导入枚举类，用于定义危险等级的常量
from enum import Enum
# 导入 JSON 模块，用于数据序列化（虽然本代码中未直接使用）
import json

# 创建一个名为"危化品安全监测系统"的 MCP 服务器实例
mcp = FastMCP("危化品安全监测系统")

# 定义危险等级枚举类，用于标准化风险分类
class DangerLevel(Enum):
    SAFE = "安全"          # 无健康风险的安全状态
    LOW = "低风险"         # 轻微风险，需要注意
    MEDIUM = "中等风险"    # 中等风险，需要采取防护措施
    HIGH = "高风险"        # 高风险，可能危及生命
    CRITICAL = "极度危险"  # 极度危险，立即威胁生命安全

# 危化品安全标准数据库 - 存储各种危险化学品的安全阈值和健康影响信息
HAZARDOUS_CHEMICALS = {
    # 一氧化碳 - 无色无味的有毒气体
    "一氧化碳": {
        "name": "一氧化碳",           # 化学品中文名称
        "cas": "630-08-0",          # CAS登记号（化学文摘社编号）
        "unit": "ppm",              # 浓度测量单位（百万分之一）
        "thresholds": {             # 各危险等级的浓度阈值（单位：ppm）
            "safe": 35,      # 安全阈值：8小时时间加权平均值
            "low": 50,       # 低风险阈值：短期接触限值
            "medium": 200,   # 中等风险阈值：立即危险浓度
            "high": 1200,    # 高风险阈值：生命危险浓度
            "critical": 2000 # 极度危险阈值：致命浓度
        },
        "effects": {                # 各浓度水平对健康的影响描述
            "safe": "正常环境，无健康风险",
            "low": "轻微头痛，需要通风",
            "medium": "头晕、恶心，立即撤离",
            "high": "意识模糊，生命危险",
            "critical": "昏迷、死亡风险极高"
        }
    },
    # 硫化氢 - 具有臭鸡蛋味的有毒气体
    "硫化氢": {
        "name": "硫化氢",           # 化学品中文名称
        "cas": "7783-06-4",        # CAS登记号
        "unit": "ppm",             # 浓度测量单位
        "thresholds": {            # 各危险等级的浓度阈值
            "safe": 10,     # 安全阈值
            "low": 20,      # 低风险阈值
            "medium": 50,   # 中等风险阈值
            "high": 100,    # 高风险阈值
            "critical": 500 # 极度危险阈值
        },
        "effects": {               # 各浓度水平的健康影响
            "safe": "正常环境，无健康风险",
            "low": "轻微眼部刺激",
            "medium": "强烈刺激，呼吸困难",
            "high": "肺水肿，生命危险",
            "critical": "呼吸麻痹，致命"
        }
    },
    # 氨气 - 具有强烈刺激性气味的碱性气体
    "氨气": {
        "name": "氨气",            # 化学品中文名称
        "cas": "7664-41-7",       # CAS登记号
        "unit": "ppm",            # 浓度测量单位
        "thresholds": {           # 各危险等级的浓度阈值
            "safe": 25,     # 安全阈值
            "low": 35,      # 低风险阈值
            "medium": 300,  # 中等风险阈值
            "high": 500,    # 高风险阈值
            "critical": 2500 # 极度危险阈值
        },
        "effects": {              # 各浓度水平的健康影响
            "safe": "正常环境，无健康风险",
            "low": "轻微刺激",
            "medium": "强烈刺激，流泪",
            "high": "化学烧伤，呼吸困难",
            "critical": "肺水肿，生命危险"
        }
    },
    # 氯气 - 黄绿色有毒气体，具有强烈刺激性
    "氯气": {
        "name": "氯气",           # 化学品中文名称
        "cas": "7782-50-5",      # CAS登记号
        "unit": "ppm",           # 浓度测量单位
        "thresholds": {          # 各危险等级的浓度阈值
            "safe": 0.5,   # 安全阈值（氯气毒性很强，安全阈值很低）
            "low": 1,      # 低风险阈值
            "medium": 3,   # 中等风险阈值
            "high": 30,    # 高风险阈值
            "critical": 100 # 极度危险阈值
        },
        "effects": {             # 各浓度水平的健康影响
            "safe": "正常环境，无健康风险",
            "low": "轻微刺激",
            "medium": "呼吸道刺激",
            "high": "肺水肿，生命危险",
            "critical": "致命"
        }
    },
    # 甲烷 - 可燃气体，主要关注爆炸风险而非毒性
    "甲烷": {
        "name": "甲烷",           # 化学品中文名称
        "cas": "74-82-8",        # CAS登记号
        "unit": "%LEL",          # 浓度测量单位：爆炸下限百分比
        "thresholds": {          # 各危险等级的浓度阈值（以爆炸下限百分比表示）
            "safe": 10,    # 安全阈值：10%LEL
            "low": 25,     # 低风险阈值：25%LEL
            "medium": 50,  # 中等风险阈值：50%LEL
            "high": 75,    # 高风险阈值：75%LEL
            "critical": 100 # 极度危险阈值：100%LEL (相当于5%体积浓度)
        },
        "effects": {             # 各浓度水平的风险描述（主要是爆炸风险）
            "safe": "正常环境，无爆炸风险",
            "low": "需要监控，注意通风",
            "medium": "存在爆炸风险，立即通风",
            "high": "高爆炸风险，撤离人员",
            "critical": "极度危险，立即撤离"
        }
    }
}

# 使用@mcp.tool()装饰器将函数注册为MCP工具，可被外部调用
@mcp.tool()
def check_chemical_concentration(chemical_name: str, concentration: float, unit: str = "ppm") -> Dict:
    """
    检测危化品浓度并评估安全风险
    
    Args:
        chemical_name: 化学品名称（必须是数据库中已定义的化学品）
        concentration: 检测到的浓度值（数值）
        unit: 浓度单位（默认为ppm，部分化学品可能使用其他单位）
    
    Returns:
        包含完整风险评估结果的字典，包括危险等级、健康影响、安全建议等
    """
    
    # 检查输入的化学品名称是否存在于数据库中
    if chemical_name not in HAZARDOUS_CHEMICALS:
        # 如果化学品不在数据库中，获取所有可用化学品列表
        available_chemicals = list(HAZARDOUS_CHEMICALS.keys())
        # 返回错误信息和可用化学品列表
        return {
            "error": f"未找到化学品 '{chemical_name}'",
            "available_chemicals": available_chemicals,
            "suggestion": "请检查化学品名称是否正确"
        }
    
    # 从数据库中获取指定化学品的完整信息
    chemical_data = HAZARDOUS_CHEMICALS[chemical_name]
    # 提取安全阈值字典
    thresholds = chemical_data["thresholds"]
    # 提取健康影响描述字典
    effects = chemical_data["effects"]
    
    # 根据浓度值确定危险等级（使用阶梯式判断）
    if concentration <= thresholds["safe"]:
        # 浓度在安全范围内
        danger_level = DangerLevel.SAFE
        level_key = "safe"
    elif concentration <= thresholds["low"]:
        # 浓度在低风险范围内
        danger_level = DangerLevel.LOW
        level_key = "low"
    elif concentration <= thresholds["medium"]:
        # 浓度在中等风险范围内
        danger_level = DangerLevel.MEDIUM
        level_key = "medium"
    elif concentration <= thresholds["high"]:
        # 浓度在高风险范围内
        danger_level = DangerLevel.HIGH
        level_key = "high"
    else:
        # 浓度超过高风险阈值，属于极度危险
        danger_level = DangerLevel.CRITICAL
        level_key = "critical"
    
    # 根据危险等级生成相应的安全建议
    recommendations = _get_safety_recommendations(danger_level, chemical_name)
    
    # 返回完整的检测结果字典
    return {
        "chemical_name": chemical_name,                    # 化学品名称
        "concentration": concentration,                     # 检测浓度值
        "unit": unit,                                      # 浓度单位
        "cas_number": chemical_data["cas"],                # CAS登记号
        "danger_level": danger_level.value,               # 危险等级（字符串值）
        "health_effects": effects[level_key],             # 当前浓度的健康影响描述
        "safety_thresholds": thresholds,                  # 完整的安全阈值信息
        "recommendations": recommendations,                # 安全建议列表
        "emergency_actions": _get_emergency_actions(danger_level)  # 应急措施列表
    }

# 内部辅助函数：根据危险等级和化学品类型生成安全建议
def _get_safety_recommendations(danger_level: DangerLevel, chemical_name: str) -> List[str]:
    """
    根据危险等级提供相应的安全建议
    
    Args:
        danger_level: 危险等级枚举值
        chemical_name: 化学品名称（预留参数，可用于特定化学品的特殊建议）
    
    Returns:
        安全建议字符串列表
    """
    # 定义不同危险等级对应的基础安全建议
    base_recommendations = {
        # 安全等级：日常维护性建议
        DangerLevel.SAFE: [
            "继续正常监测",           # 保持常规监测频率
            "保持良好通风",           # 维持基本通风条件
            "定期校准检测设备"        # 确保监测设备准确性
        ],
        # 低风险等级：预防性措施
        DangerLevel.LOW: [
            "加强通风措施",           # 增加通风量
            "增加监测频率",           # 提高检测频次
            "准备个人防护设备",       # 准备必要的防护用品
            "通知相关人员注意"        # 向工作人员发出提醒
        ],
        # 中等风险等级：积极防护措施
        DangerLevel.MEDIUM: [
            "立即加强通风",           # 马上增强通风系统
            "穿戴适当防护设备",       # 佩戴防护用品
            "减少暴露时间",           # 限制人员在该区域的时间
            "准备应急措施",           # 准备应急响应方案
            "通知安全负责人"          # 向安全管理人员报告
        ],
        # 高风险等级：紧急防护措施
        DangerLevel.HIGH: [
            "立即撤离非必要人员",     # 疏散不必要的工作人员
            "穿戴全套防护设备",       # 使用完整的个人防护装备
            "启动应急通风系统",       # 开启紧急通风设备
            "联系应急响应小组",       # 通知专业应急团队
            "准备医疗救护"            # 准备医疗急救资源
        ],
        # 极度危险等级：紧急撤离措施
        DangerLevel.CRITICAL: [
            "立即撤离所有人员",       # 全员紧急撤离
            "启动紧急应急预案",       # 启动最高级别应急响应
            "联系消防和医疗部门",     # 联系外部救援力量
            "切断污染源",             # 停止或隔离污染源
            "建立安全隔离区"          # 设置安全警戒区域
        ]
    }
    
    # 根据危险等级返回相应的建议，如果等级未定义则返回空列表
    return base_recommendations.get(danger_level, [])

# 内部辅助函数：根据危险等级生成应急措施
def _get_emergency_actions(danger_level: DangerLevel) -> List[str]:
    """
    根据危险等级提供相应的应急措施
    
    Args:
        danger_level: 危险等级枚举值
    
    Returns:
        应急措施字符串列表
    """
    
    # 定义不同危险等级对应的应急行动
    emergency_actions = {
        # 安全等级：无需特殊应急措施
        DangerLevel.SAFE: ["无需特殊措施"],
        # 低风险等级：基础应急准备
        DangerLevel.LOW: ["准备应急设备", "通知班组长"],
        # 中等风险等级：启动二级应急响应
        DangerLevel.MEDIUM: ["启动二级应急响应", "通知安全部门"],
        # 高风险等级：启动一级应急响应
        DangerLevel.HIGH: ["启动一级应急响应", "联系医疗部门"],
        # 极度危险等级：启动最高级应急响应
        DangerLevel.CRITICAL: ["启动最高级应急响应", "立即报告政府部门"]
    }
    
    # 根据危险等级返回相应的应急措施，如果等级未定义则返回空列表
    return emergency_actions.get(danger_level, [])

# 使用@mcp.tool()装饰器注册批量检测工具
@mcp.tool()
def batch_check_concentrations(measurements: List[Dict]) -> List[Dict]:
    """
    批量检测多种化学品浓度，提高检测效率
    
    Args:
        measurements: 测量数据列表，每个元素是包含化学品信息的字典
                     每个字典应包含: chemical_name, concentration, unit(可选)
    
    Returns:
        检测结果列表，每个元素对应一个化学品的完整检测结果
    """
    
    # 初始化结果列表
    results = []
    # 遍历每个测量数据
    for measurement in measurements:
        try:
            # 调用单个化学品检测函数进行检测
            result = check_chemical_concentration(
                measurement["chemical_name"],           # 化学品名称
                measurement["concentration"],           # 浓度值
                measurement.get("unit", "ppm")         # 单位（默认ppm）
            )
            # 将检测结果添加到结果列表
            results.append(result)
        except Exception as e:
            # 如果检测过程中出现异常，记录错误信息
            results.append({
                "error": f"检测失败: {str(e)}",        # 错误描述
                "measurement": measurement              # 原始测量数据
            })
    
    # 返回所有检测结果
    return results

# 使用@mcp.resource()装饰器注册资源，支持动态URI参数
@mcp.resource("chemical://{chemical_name}")
def get_chemical_info(chemical_name: str) -> str:
    """
    获取指定化学品的详细安全信息资源
    
    Args:
        chemical_name: 要查询的化学品名称
    
    Returns:
        格式化的化学品安全信息字符串
    """
    
    # 检查化学品是否存在于数据库中
    if chemical_name not in HAZARDOUS_CHEMICALS:
        # 获取所有可用化学品名称列表
        available = ", ".join(HAZARDOUS_CHEMICALS.keys())
        # 返回未找到的提示信息
        return f"未找到化学品 '{chemical_name}'。\n可用化学品: {available}"
    
    # 获取指定化学品的完整数据
    chemical = HAZARDOUS_CHEMICALS[chemical_name]
    
    # 格式化输出化学品的详细信息
    info = f"""
化学品名称: {chemical['name']}                    # 化学品中文名称
CAS号: {chemical['cas']}                          # 化学文摘社登记号
测量单位: {chemical['unit']}                      # 浓度测量单位

安全阈值:                                         # 各危险等级的浓度界限
- 安全范围: ≤ {chemical['thresholds']['safe']} {chemical['unit']}
- 低风险: ≤ {chemical['thresholds']['low']} {chemical['unit']}
- 中等风险: ≤ {chemical['thresholds']['medium']} {chemical['unit']}
- 高风险: ≤ {chemical['thresholds']['high']} {chemical['unit']}
- 极度危险: > {chemical['thresholds']['critical']} {chemical['unit']}

健康影响:                                         # 各浓度水平的健康后果
- 安全水平: {chemical['effects']['safe']}
- 低风险: {chemical['effects']['low']}
- 中等风险: {chemical['effects']['medium']}
- 高风险: {chemical['effects']['high']}
- 极度危险: {chemical['effects']['critical']}
"""
    # 返回格式化的信息字符串
    return info

# 使用@mcp.prompt()装饰器注册提示词生成器
@mcp.prompt()
def generate_safety_report(site_name: str, measurements: str, incident_type: str = "routine") -> str:
    """
    生成危化品安全监测报告的AI提示词
    
    Args:
        site_name: 监测地点的名称（如工厂名、车间名等）
        measurements: 测量数据的描述（可以是文本描述或数据）
        incident_type: 事件类型，决定报告的性质和紧急程度
                      - "routine": 例行监测报告
                      - "emergency": 紧急事件报告
                      - "investigation": 事故调查报告
    
    Returns:
        用于AI生成专业安全报告的结构化提示词
    """
    
    # 定义不同事件类型对应的报告模板描述
    report_templates = {
        "routine": "请生成一份例行危化品安全监测报告",      # 日常监测报告
        "emergency": "请生成一份紧急事件危化品安全报告",   # 应急事件报告
        "investigation": "请生成一份事故调查危化品安全报告" # 事故调查报告
    }
    
    # 根据事件类型选择合适的模板，如果类型不存在则使用默认的例行报告模板
    template = report_templates.get(incident_type, report_templates["routine"])
    
    # 构建结构化的AI提示词
    prompt = f"""
{template}，包含以下信息：

监测地点: {site_name}                              # 事件发生的具体位置
测量数据: {measurements}                           # 相关的监测数据和测量结果
事件类型: {incident_type}                         # 事件的分类和性质

报告应包括：                                       # 报告必须包含的标准章节
1. 执行摘要                                       # 关键信息的简要概述
2. 监测数据分析                                   # 详细的数据分析和解读
3. 风险评估结果                                   # 基于数据的风险等级判断
4. 安全建议和改进措施                             # 具体的安全改进建议
5. 应急响应计划（如适用）                         # 针对紧急情况的响应方案
6. 结论和建议                                     # 总结性的结论和后续建议

请确保报告专业、详细且符合安全规范。              # 对报告质量和格式的要求
"""
    
    # 返回构建好的提示词
    return prompt

def main() -> None:
    mcp.run(transport='stdio')
