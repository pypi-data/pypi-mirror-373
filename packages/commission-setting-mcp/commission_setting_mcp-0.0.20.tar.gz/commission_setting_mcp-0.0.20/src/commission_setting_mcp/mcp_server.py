import asyncio
import os
from mcp.server.fastmcp import FastMCP

from commission_setting_mcp import playwright_commission
from commission_setting_mcp.feishu_util import YXXFeishuSheetUtil
from shared.error_handler import format_exception_message
from shared.log_util import log_info

mcp = FastMCP("commission_setting_mcp_server", port=8089)


async def server_log_info(msg: str):
    """发送信息级别的日志消息"""
    log_info(msg)
    await mcp.get_context().session.send_log_message(
        level="info",
        data=msg,
    )


def get_batch_sleep_time() -> float:
    """从环境变量获取批量操作间隔时间，如果未配置则返回0（不sleep）"""
    try:
        sleep_time = os.getenv("sleep_seconds", '0')
        return float(sleep_time)
    except (ValueError, TypeError):
        return 0.0


# @mcp.tool()
# async def query_unconfigured_commission_plan_products() -> str:
#     """查询未配置分润方案的商品"""
#     try:
#         await server_log_info("正在查询未配置分润方案的商品...")
#
#         feishu_util = YXXFeishuSheetUtil()
#         filtered_rows = await feishu_util.get_filtered_rows()
#
#         if not filtered_rows:
#             result = "当前没有未配置分润方案的商品。"
#         else:
#             result_lines = ["未配置分润方案的商品列表："]
#             for row in filtered_rows:
#                 product_id = row.get("聚宝赞商品id", "未知")
#                 system_config = row.get("系统配置模版", "未知")
#                 result_lines.append(f"聚宝赞商品id:{product_id}，分润系统配置模版：\"{system_config}\"。")
#
#             result = "\n".join(result_lines)
#
#         await server_log_info(f"查询到 {len(filtered_rows)} 个未配置商品")
#         return result
#
#     except Exception as e:
#         await server_log_info(f"【E】查询未配置商品时出错: {str(e)}")
#         return format_exception_message("查询未配置商品时出错", e)

# @mcp.tool()
# async def open_product_settlement_page() -> str:
#     """商品配置分润方案第一步，打开商品结算设置页面，打开成功才能执行后续步骤"""
#     try:
#         await server_log_info("正在打开商品结算页面...")
#         _, result = await playwright_commission.open_commission_setting_page()
#         await server_log_info(f"打开商品结算页面结果: {result}")
#         return result
#     except Exception as e:
#         await server_log_info(f"【E】打开商品结算页面时出错: {str(e)}")
#         return format_exception_message("打开商品结算页面时出错", e)


@mcp.tool()
async def complete_product_reward_config_workflow(product_ids: list[str]) -> str:
    """为指定推客商品ID列表进行【奖励配置】，支持批量配置多个商品。
    内部会打开聚宝赞浏览器页面，如果浏览器已打开，会自动在新标签页中执行任务；如果浏览器未打开，会先打开浏览器再执行任务。

    Args:
        product_ids: 推客商品ID列表

    Returns:
        result: 配置结果（换行符分隔），如果中间有异常则中断后返回。
    """
    try:
        log_info(f"complete_product_reward_config_workflow start {product_ids}")
        await server_log_info(f"开始商品列表 {product_ids} 的完整结算配置流程...")

        # 批量配置商品分润方案
        results = []
        sleep_time = get_batch_sleep_time()
        
        for i, product_id in enumerate(product_ids):
            log_info(f"配置商品ID: {product_id}")
            await server_log_info(f"正在配置商品 {product_id}...")
            
            result = await playwright_commission.smart_set_product_commission_plan(
                product_id
            )
            
            # 检查是否有异常信息
            if "异常" in result or "失败" in result or "登录" in result or "错误" in result:
                log_info(f"配置商品 {product_id} 时发生异常: {result}")
                await server_log_info(f"【E】配置商品 {product_id} 时发生异常，中断后续配置: {result}")
                return result  # 返回异常信息，不继续处理
            
            results.append(result)
            log_info(f"商品 {product_id} 配置结果: {result}")
            await server_log_info(f"商品 {product_id} 配置完成: {result}")
            
            # 配置完成后sleep，除了最后一个商品
            if sleep_time > 0 and i < len(product_ids) - 1:
                await server_log_info(f"等待 {sleep_time} 秒后继续配置下一个商品...")
                await asyncio.sleep(sleep_time)

        final_result = "\n".join(results)
        await server_log_info(f"批量配置完成: {final_result}")
        return final_result

    except Exception as e:
        await server_log_info(f"【E】完整工作流程执行时出错: {str(e)}")
        return format_exception_message("完整工作流程执行时出错", e)


# @mcp.tool()
# async def open_rebate_set_page() -> str:
#     """服务商返点关联商品或检查商品返点方案的第一步，打开服务商返点关联页，打开成功才能执行后续步骤"""
#     try:
#         await server_log_info("正在打开服务商返点关联页...")
#         _, result = await playwright_commission.open_rebate_set_page()
#         await server_log_info(f"打开服务商返点关联页结果: {result}")
#         return result
#     except Exception as e:
#         await server_log_info(f"【E】打开服务商返点关联页时出错: {str(e)}")
#         return format_exception_message("打开服务商返点关联页时出错", e)


@mcp.tool()
async def complete_product_rebate_config_workflow(product_ids: list[str]) -> str:
    """为指定聚宝赞商品ID列表进行【返点配置】，支持批量配置多个商品。
    内部会打开聚宝赞浏览器页面，如果浏览器已打开，会自动在新标签页中执行任务；如果浏览器未打开，会先打开浏览器再执行任务。

    Args:
        product_ids: 聚宝赞商品ID列表

    Returns:
        result: 配置结果（换行符分隔），如果中间有异常则中断后返回。
    """
    try:
        log_info(f"complete_product_rebate_config_workflow start {product_ids}")
        await server_log_info(f"开始商品列表 {product_ids} 的完整返点配置流程...")

        # 批量配置商品返点方案
        results = []
        sleep_time = get_batch_sleep_time()
        
        for i, product_id in enumerate(product_ids):
            log_info(f"配置商品ID: {product_id}")
            await server_log_info(f"正在配置商品 {product_id}...")
            
            result = await playwright_commission.smart_set_product_rebate(
                product_id
            )
            
            # 检查是否有异常信息
            if "异常" in result or "失败" in result or "登录" in result or "错误" in result:
                log_info(f"配置商品 {product_id} 时发生异常: {result}")
                await server_log_info(f"【E】配置商品 {product_id} 时发生异常，中断后续配置: {result}")
                return result  # 返回异常信息，不继续处理
            
            results.append(result)
            log_info(f"商品 {product_id} 配置结果: {result}")
            await server_log_info(f"商品 {product_id} 配置完成: {result}")
            
            # 配置完成后sleep，除了最后一个商品
            if sleep_time > 0 and i < len(product_ids) - 1:
                await server_log_info(f"等待 {sleep_time} 秒后继续配置下一个商品...")
                await asyncio.sleep(sleep_time)

        final_result = "\n".join(results)
        await server_log_info(f"批量返点配置完成: {final_result}")
        return final_result

    except Exception as e:
        await server_log_info(f"【E】完整返点配置工作流程执行时出错: {str(e)}")
        return format_exception_message("完整返点配置工作流程执行时出错", e)


# @mcp.tool()
# async def get_current_time() -> str:
#     """获取当前时间字符串，格式为YYYY-MM-DD HH:MM:SS"""
#     try:
#         from datetime import datetime
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         return f"当前时间: {current_time}"
#     except Exception as e:
#         await server_log_info(f"【E】获取当前时间时出错: {str(e)}")
#         return format_exception_message("获取当前时间时出错", e)


@mcp.tool()
async def check_product_setting(product_ids: list[str]) -> str:
    """【检查】指定推客商品ID列表的奖励配置和返点配置设置是否正确，支持批量检查多个商品。
    内部会打开聚宝赞浏览器页面，如果浏览器已打开，会自动在新标签页中执行任务；如果浏览器未打开，会先打开浏览器再执行任务。

    Args:
        product_ids: 推客商品ID列表

    Returns:
        result: 检查结果（换行符分隔），如果中间有异常则中断后返回。
    """
    try:
        log_info(f"check_product_setting start {product_ids}")
        await server_log_info(f"开始商品列表 {product_ids} 的完整配置检查流程...")

        # 批量检查商品配置
        results = []
        sleep_time = get_batch_sleep_time()
        
        for i, product_id in enumerate(product_ids):
            log_info(f"检查商品ID: {product_id}")
            await server_log_info(f"正在检查商品 {product_id}...")
            
            result = await playwright_commission.smart_check_product_commission_setting(
                product_id
            )
            
            # 检查是否有严重异常信息（只有真正的系统异常才中断流程）
            if "登录" in result or "浏览器" in result or "检查异常" in result:
                log_info(f"检查商品 {product_id} 时发生系统异常: {result}")
                await server_log_info(f"【E】检查商品 {product_id} 时发生系统异常，中断后续检查: {result}")
                return result  # 返回异常信息，不继续处理
            
            results.append(result)
            log_info(f"商品 {product_id} 检查结果: {result}")
            await server_log_info(f"商品 {product_id} 检查完成: {result}")
            
            # 检查完成后sleep，除了最后一个商品
            if sleep_time > 0 and i < len(product_ids) - 1:
                await server_log_info(f"等待 {sleep_time} 秒后继续检查下一个商品...")
                await asyncio.sleep(sleep_time)

        # 格式化拼接结果，为每个商品的结果添加分隔
        formatted_results = []
        for i, result in enumerate(results):
            if i > 0:  # 除了第一个商品，其他商品前面加分隔线
                formatted_results.append("\n" + "="*50)
            formatted_results.append(result)
        
        final_result = "\n".join(formatted_results)
        await server_log_info(f"批量配置检查完成，共检查 {len(results)} 个商品")
        return final_result

    except Exception as e:
        await server_log_info(f"【E】完整配置检查工作流程执行时出错: {str(e)}")
        return format_exception_message("完整配置检查工作流程执行时出错", e)


@mcp.tool()
async def query_promoter_product_ids(wechat_product_ids: list[str]) -> str:
    """从飞书表格根据微信商品ID查询推客商品ID，然后返回查询到的推客商品ID列表。
    
    Args:
        wechat_product_ids: 微信商品ID列表
        
    Returns:
        推客商品ID列表（换行符分隔），每个商品对应一行，如果不存在则对应位置返回 "/"。
        如果发生异常（如未登录），则只返回一个异常信息。
        
    Examples:
        正常情况返回：
        6162916
        /
        6162869
        
        异常情况返回：
        请用户先手动登录，再重新打开原网址进行后续操作！
    """
    try:
        await server_log_info(f"正在批量查询微信商品ID列表 {wechat_product_ids} 对应的推客商品ID...")

        result = await playwright_commission.smart_query_promoter_product_id(wechat_product_ids)

        await server_log_info(f"批量查询完成，结果: {result}")
        return result
        
    except Exception as e:
        await server_log_info(f"【E】批量查询推客商品ID时出错: {str(e)}")
        return format_exception_message("批量查询推客商品ID时出错", e)


@mcp.tool()
async def get_current_version() -> str:
    """获取当前工具的版本号"""
    try:
        import importlib.metadata
        version = importlib.metadata.version("commission-setting-mcp")
        return f"当前版本号: {version}"
    except Exception as e:
        await server_log_info(f"【E】获取版本号时出错: {str(e)}")
        return format_exception_message("获取版本号时出错", e)

def main():
    """佣金设置MCP服务入口函数"""
    log_info(f"佣金设置MCP服务启动")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()