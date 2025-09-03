#!/usr/bin/env python3
"""
🚀 工作性价比计算器MCP工具
基于Zippland/worth-calculator项目的Python实现

这个工具可以帮助你评估工作的真实价值，综合考虑薪资、工时、通勤、工作环境等多个因素。
"""

import json
import logging
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# ================================
# 🔧 配置区域 - 请填写以下信息
# ================================

# 基本信息（用于生成setup.py）
PACKAGE_NAME = "worth-calculator-mcp"
TOOL_NAME = "工作性价比计算器"
VERSION = "0.1.0"
AUTHOR = "Alvin"
AUTHOR_EMAIL = "alvin@example.com"
DESCRIPTION = "一个基于Zippland/worth-calculator的工作性价比计算工具，综合评估工作真实价值"
URL = "https://github.com/Zippland/worth-calculator"
LICENSE = "MIT"

# 依赖包列表
REQUIREMENTS = [
    "mcp>=1.0.0",
    "fastmcp>=0.1.0",
]

# ================================
# 🛠️ MCP工具核心代码
# ================================

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建MCP服务器，显式指定端口
mcp = FastMCP(TOOL_NAME, port=9000)

# PPP转换因子映射表 (部分国家/地区)
PPP_CONVERSION_FACTORS = {
    "中国": 4.19,
    "美国": 1.0,
    "日本": 105.0,
    "韩国": 1100.0,
    "德国": 0.9,
    "英国": 0.78,
    "法国": 0.85,
    "加拿大": 1.3,
    "澳大利亚": 1.4,
    "新加坡": 1.35,
    "香港": 0.78,
    "台湾": 28.0,
    "澳门": 0.78
}

# 城市生活成本系数
CITY_LIVING_COST = {
    "一线城市": 1.0,
    "新一线": 0.8,
    "二线城市": 0.65,
    "三线城市": 0.55,
    "四线城市": 0.45,
    "县城": 0.38,
    "乡镇": 0.3
}

# 工作环境评分
WORK_ENVIRONMENT_SCORE = {
    "偏僻的工厂/工地/户外": 30,
    "工厂/工地/户外": 40,
    "普通环境": 60,
    "CBD": 80
}

# 领导关系评分
LEADER_RELATION_SCORE = {
    "对我不爽": 20,
    "管理严格": 40,
    "中规中矩": 60,
    "善解人意": 80,
    "我是嫡系": 90
}

# 职业稳定度评分
JOB_STABILITY_SCORE = {
    "政府/事业单位": 90,
    "国企/大型企业": 80,
    "外企/守法企业": 70,
    "私企/狼性文化": 50,
    "劳务派遣/OD": 30,
    "自由职业": 40
}

# ================================
# 🔧 工具函数
# ================================

@mcp.tool()
def calculate_job_worth(
    annual_salary: float,  # 年薪总包（元）
    country: str = "中国",  # 工作国家/地区
    work_days_per_week: int = 5,  # 每周工作天数
    wfh_days_per_week: int = 0,  # 每周WFH天数
    annual_leave_days: int = 5,  # 年假天数
    public_holiday_days: int = 13,  # 法定假日天数
    paid_sick_leave_days: int = 3,  # 带薪病假天数
    daily_work_hours: float = 10,  # 每日工时（小时）
    commute_time: float = 2,  # 每日通勤时间（小时）
    rest_fishing_time: float = 2,  # 每日休息和摸鱼时间（小时）
    city_type: str = "一线城市",  # 所在城市类型
    is_hometown: bool = False,  # 是否在家乡工作
    leader_relation: str = "中规中矩",  # 领导关系
    job_stability: str = "私企/狼性文化",  # 职业稳定度
    work_environment: str = "普通环境"  # 工作环境
) -> dict:
    """
    计算工作性价比
    
    Args:
        annual_salary: 年薪总包（元）
        country: 工作国家/地区
        work_days_per_week: 每周工作天数
        wfh_days_per_week: 每周WFH天数
        annual_leave_days: 年假天数
        public_holiday_days: 法定假日天数
        paid_sick_leave_days: 带薪病假天数
        daily_work_hours: 每日工时（小时）
        commute_time: 每日通勤时间（小时）
        rest_fishing_time: 每日休息和摸鱼时间（小时）
        city_type: 所在城市类型
        is_hometown: 是否在家乡工作
        leader_relation: 领导关系
        job_stability: 职业稳定度
        work_environment: 工作环境
    
    Returns:
        包含计算结果的字典，包括标准化日薪、综合满意度评分等
    """
    try:
        # 计算实际工作天数
        total_work_days = 52 * work_days_per_week - annual_leave_days - public_holiday_days - paid_sick_leave_days
        
        # 计算有效工时（扣除休息和摸鱼时间）
        effective_work_hours_per_day = daily_work_hours - rest_fishing_time
        
        # 计算年有效工作小时
        annual_effective_work_hours = total_work_days * effective_work_hours_per_day
        
        # 计算小时工资
        hourly_salary = annual_salary / annual_effective_work_hours if annual_effective_work_hours > 0 else 0
        
        # 计算日薪（考虑通勤时间的真实日薪）
        # 通勤时间被视为额外的工作成本
        total_day_time = daily_work_hours + commute_time
        real_daily_salary = (annual_salary / total_work_days) if total_work_days > 0 else 0
        
        # PPP调整（购买力平价）
        ppp_factor = PPP_CONVERSION_FACTORS.get(country, 1.0)
        ppp_adjusted_daily_salary = real_daily_salary / ppp_factor
        
        # 城市生活成本调整
        city_factor = CITY_LIVING_COST.get(city_type, 1.0)
        standardized_daily_salary = ppp_adjusted_daily_salary * city_factor
        
        # 在家乡工作的加成（减少生活成本和增加幸福感）
        hometown_bonus = 1.15 if is_hometown else 1.0
        standardized_daily_salary *= hometown_bonus
        
        # 计算综合满意度评分
        # 1. 基础分（基于薪资和时间投入的平衡）
        base_score = min(100, (hourly_salary / 50) * 20)  # 假设50元/小时为中等水平
        
        # 2. WFH加成（减少通勤压力）
        wfh_score = (wfh_days_per_week / work_days_per_week) * 10 if work_days_per_week > 0 else 0
        
        # 3. 工作环境评分
        environment_score = WORK_ENVIRONMENT_SCORE.get(work_environment, 60) * 0.3
        
        # 4. 领导关系评分
        leader_score = LEADER_RELATION_SCORE.get(leader_relation, 60) * 0.25
        
        # 5. 职业稳定度评分
        stability_score = JOB_STABILITY_SCORE.get(job_stability, 50) * 0.25
        
        # 综合评分
        total_score = base_score + wfh_score + environment_score + leader_score + stability_score
        total_score = min(100, max(0, total_score))
        
        # 评估结论
        if total_score >= 80:
            conclusion = "工作很值得，继续保持！"
        elif total_score >= 60:
            conclusion = "工作还可以，有提升空间。"
        elif total_score >= 40:
            conclusion = "工作一般般，考虑优化或寻找更好机会。"
        else:
            conclusion = "工作不太值得，建议寻找更好的机会。"
        
        # 返回计算结果
        return {
            "annual_salary": annual_salary,
            "total_work_days": total_work_days,
            "hourly_salary": round(hourly_salary, 2),
            "real_daily_salary": round(real_daily_salary, 2),
            "standardized_daily_salary": round(standardized_daily_salary, 2),
            "total_score": round(total_score, 2),
            "conclusion": conclusion,
            "details": {
                "base_score": round(base_score, 2),
                "wfh_score": round(wfh_score, 2),
                "environment_score": round(environment_score, 2),
                "leader_score": round(leader_score, 2),
                "stability_score": round(stability_score, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"计算过程中发生错误: {str(e)}")
        return {
            "error": f"计算失败: {str(e)}"
        }

@mcp.tool()
def compare_jobs(job1: dict, job2: dict) -> dict:
    """
    比较两份工作的性价比
    
    Args:
        job1: 第一份工作的参数，包含calculate_job_worth所需的所有参数
        job2: 第二份工作的参数，包含calculate_job_worth所需的所有参数
    
    Returns:
        两份工作的比较结果
    """
    try:
        # 计算两份工作的性价比
        result1 = calculate_job_worth(**job1)
        result2 = calculate_job_worth(**job2)
        
        # 比较结果
        comparison = {
            "job1": result1,
            "job2": result2,
            "recommendation": "第一份工作更值得" if result1["total_score"] > result2["total_score"] else "第二份工作更值得"
        }
        
        return comparison
        
    except Exception as e:
        logger.error(f"比较过程中发生错误: {str(e)}")
        return {
            "error": f"比较失败: {str(e)}"
        }

@mcp.tool()
def get_supported_countries() -> list:
    """
    获取支持的国家/地区列表
    
    Returns:
        支持的国家/地区列表
    """
    return list(PPP_CONVERSION_FACTORS.keys())

@mcp.tool()
def get_current_version() -> str:
    """
    获取当前工具版本
    
    Returns:
        版本号字符串
    """
    return VERSION

# 添加一个简单的调试工具函数
def test_calculation():
    """测试计算逻辑是否正确"""
    # 模拟一些基本参数
    params = {
        "annual_salary": 200000,
        "country": "中国",
        "work_days_per_week": 5,
        "wfh_days_per_week": 1,
        "annual_leave_days": 10,
        "public_holiday_days": 13,
        "paid_sick_leave_days": 5,
        "daily_work_hours": 9,
        "commute_time": 1.5,
        "rest_fishing_time": 1.5,
        "city_type": "新一线",
        "is_hometown": False,
        "leader_relation": "中规中矩",
        "job_stability": "外企/守法企业",
        "work_environment": "普通环境"
    }
    
    # 直接调用计算函数进行测试
    result = calculate_job_worth(**params)
    print("\n===== 直接计算测试结果 =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

# ================================
# 🚀 主函数
# ================================

def main():
    """启动MCP服务器"""
    logger.info(f"启动 {TOOL_NAME}...")
    logger.info(f"版本: {VERSION}")
    logger.info(f"作者: {AUTHOR}")
    logger.info("这个工具可以帮助你评估工作的真实价值，综合考虑薪资、工时、通勤、工作环境等多个因素。")
    
    # 先进行本地计算测试，确保计算逻辑正确
    print("\n===== 开始本地计算测试 =====")
    test_calculation()
    print("\n===== 本地计算测试完成 =====")
    
    # 显示工具信息
    print(f"\n工具名称: {TOOL_NAME}")
    print(f"版本: {VERSION}")
    print(f"作者: {AUTHOR}")
    print(f"描述: {DESCRIPTION}")
    print(f"支持的国家/地区数量: {len(PPP_CONVERSION_FACTORS)}")
    print(f"支持的城市类型数量: {len(CITY_LIVING_COST)}")
    
    # 列出所有可用的工具函数名称（不尝试访问不存在的属性）
    print("\n可用的工具函数:")
    print("- calculate_job_worth: 计算工作性价比")
    print("- compare_jobs: 比较两份工作的性价比")
    print("- get_supported_countries: 获取支持的国家/地区列表")
    print("- get_current_version: 获取当前工具版本")
    
    print("\n准备启动MCP服务器...")
    print("服务器将在端口 9000 上运行")
    print("请注意，由于MCP框架的工作方式，可能无法通过HTTP请求直接访问，但可以通过MCP客户端连接使用")
    
    # 启动MCP服务器
    try:
        logger.info("开始启动MCP服务器...")
        print("正在启动MCP服务器，请稍候...")
        # 添加更多的日志记录
        logger.info(f"服务器配置: 端口={9000}, 工具名称={TOOL_NAME}")
        
        # 启动服务器并保持运行
        print("MCP服务器已启动！按Ctrl+C停止服务器")
        mcp.run()
        
        # 如果run()方法返回，打印日志
        logger.info("MCP服务器已停止")
        print("\nMCP服务器已停止")
    except KeyboardInterrupt:
        logger.info("用户中断，停止MCP服务器")
        print("\n用户中断，MCP服务器已停止")
    except Exception as e:
        logger.error(f"MCP服务器启动失败: {str(e)}")
        print(f"\n服务器启动失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()