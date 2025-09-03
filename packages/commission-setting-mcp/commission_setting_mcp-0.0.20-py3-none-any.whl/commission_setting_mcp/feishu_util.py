import os
import httpx
import asyncio
from typing import Optional, List, Dict, Any
from enum import Enum

from dotenv import load_dotenv

from shared.log_util import log_debug, log_info, log_error

load_dotenv()

class SheetName(Enum):
    """飞书表格名称枚举"""
    PROFIT_TEMPLATE = "分润模板表"
    REWARD_CONFIG = "奖励配置表" 
    REBATE_CONFIG = "返点配置表"


# 为了向后兼容，也提供常量形式
class SheetNames:
    """飞书表格名称常量"""
    PROFIT_TEMPLATE: str = SheetName.PROFIT_TEMPLATE.value
    REWARD_CONFIG: str = SheetName.REWARD_CONFIG.value
    REBATE_CONFIG: str = SheetName.REBATE_CONFIG.value
    
    @classmethod
    def all(cls) -> List[str]:
        """获取所有表名"""
        return [cls.PROFIT_TEMPLATE, cls.REWARD_CONFIG, cls.REBATE_CONFIG]


class YXXFeishuSheetUtil:
    """云选象飞书表格操作工具类"""
    
    def __init__(self):
        self.app_id = os.getenv("feishu-app-id")
        self.app_secret = os.getenv("feishu-app-secret")
        self.tenant_access_token: Optional[str] = None
        self.token_expires_at: float = 0
        
        # 表格ID
        self.spreadsheet_id = "EjMLsOBqXhYiKTt0WDwcOjngnqg"
        
        # 三个表的配置
        self.sheet_configs = {
            SheetNames.PROFIT_TEMPLATE: {
                "sheet_id": "jOMYW6",
                "data_range": "A:M",
                "product_id_column": "聚宝赞商品id"
            },
            SheetNames.REWARD_CONFIG: {
                "sheet_id": "M3bAQd", 
                "data_range": "A:H",
                "product_id_column": "聚宝赞推客商品ID"
            },
            SheetNames.REBATE_CONFIG: {
                "sheet_id": "xx5CRt",
                "data_range": "A:K", 
                "product_id_column": "聚宝赞推客商品ID"
            }
        }
        
        if not self.app_id or not self.app_secret:
            raise ValueError("需要设置环境变量 feishu-app-id 和 feishu-app-secret")
    
    async def get_tenant_access_token(self) -> str:
        """获取tenant_access_token，如果token未过期则直接返回缓存的token"""
        import time
        
        # 检查token是否还有效（提前5分钟刷新）
        if self.tenant_access_token and time.time() < (self.token_expires_at - 300):
            return self.tenant_access_token
        
        log_info("获取飞书租户访问令牌...")
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"获取token失败: {result.get('msg', '未知错误')}")
            
            self.tenant_access_token = result.get("tenant_access_token")
            expires_in = result.get("expire", 7200)  # 默认2小时
            self.token_expires_at = time.time() + expires_in
            
            log_info(f"成功获取token，有效期: {expires_in} 秒")
            return self.tenant_access_token
    
    async def read_sheet_data(self, sheet_name: str) -> List[List[str]]:
        """读取飞书表格数据
        
        Args:
            sheet_name: 表名称，支持 SheetNames.PROFIT_TEMPLATE, SheetNames.REWARD_CONFIG, SheetNames.REBATE_CONFIG
        """
        if sheet_name not in self.sheet_configs:
            raise ValueError(f"不支持的表名: {sheet_name}，支持的表名: {list(self.sheet_configs.keys())}")
        
        config = self.sheet_configs[sheet_name]
        token = await self.get_tenant_access_token()
        
        url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_id}/values/{config['sheet_id']}!{config['data_range']}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        log_info(f"读取表格数据: {sheet_name} ({config['sheet_id']}!{config['data_range']})")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"读取表格数据失败: {result.get('msg', '未知错误')}")
            
            values = result.get("data", {}).get("valueRange", {}).get("values", [])
            log_info(f"成功读取到 {len(values)} 行数据")
            log_debug(f"读取到的数据: {values[:5]}...")
            return values
    
    def _convert_row_to_dict(self, headers: List[str], row: List[Any], row_index: int) -> Dict[str, Any]:
        """将行数据转换为字典格式，使用表头作为key"""
        row_dict = {"row_index": row_index}
        
        # 确保行数据长度不超过表头长度
        max_len = min(len(headers), len(row))
        
        for i in range(max_len):
            header = str(headers[i]).strip()
            value = row[i] if row[i] is not None else ""
            # 对于数字类型，保持原类型；对于字符串类型，转换为字符串并去除空格
            if isinstance(value, (int, float)):
                row_dict[header] = value
            else:
                row_dict[header] = str(value).strip()
        
        return row_dict

    async def get_all_data(self, sheet_name: str) -> List[Dict[str, Any]]:
        """获取指定表的所有数据，转换为字典格式
        
        Args:
            sheet_name: 表名称，支持 SheetNames.PROFIT_TEMPLATE, SheetNames.REWARD_CONFIG, SheetNames.REBATE_CONFIG
            
        Returns:
            List[Dict[str, Any]]: 表格数据列表，每行为一个字典
        """
        values = await self.read_sheet_data(sheet_name)
        
        if not values:
            log_info(f"{sheet_name} 为空，没有找到任何数据")
            return []
        
        # 假设第一行是标题行
        headers = values[0] if values else []
        if not headers:
            log_info(f"{sheet_name} 没有表头")
            return []
        
        all_rows = []
        
        for row_index, row in enumerate(values[1:], start=2):  # 从第2行开始（跳过标题行）
            # 确保行有足够的列
            if len(row) < len(headers):
                # 补充空值到与表头长度一致
                row = row + [None] * (len(headers) - len(row))
            
            # 转换为字典格式
            row_dict = self._convert_row_to_dict(headers, row, row_index)
            all_rows.append(row_dict)
        
        log_info(f"{sheet_name} 总共获取到 {len(all_rows)} 行数据")
        return all_rows
    
    async def find_by_product_id(self, sheet_name: str, product_id: str) -> Optional[Dict[str, Any]]:
        """根据商品ID查找指定表中的行数据
        
        Args:
            sheet_name: 表名称，支持 SheetNames.PROFIT_TEMPLATE, SheetNames.REWARD_CONFIG, SheetNames.REBATE_CONFIG
            product_id: 商品ID
            
        Returns:
            Optional[Dict[str, Any]]: 找到的行数据字典，未找到返回None
        """
        if sheet_name not in self.sheet_configs:
            raise ValueError(f"不支持的表名: {sheet_name}")
        
        config = self.sheet_configs[sheet_name]
        product_id_column = config["product_id_column"]
        
        values = await self.read_sheet_data(sheet_name)
        
        if not values:
            log_info(f"{sheet_name} 为空")
            return None
        
        # 使用表头来找商品ID列
        headers = values[0] if values else []
        
        for row_index, row in enumerate(values[1:], start=2):  # 从第2行开始（跳过标题行）
            # 确保行有足够的列
            if len(row) < len(headers):
                row = row + [None] * (len(headers) - len(row))
            
            # 转换为字典格式
            row_dict = self._convert_row_to_dict(headers, row, row_index)
            
            # 获取商品ID值
            row_product_id = str(row_dict.get(product_id_column, "")).strip()
            if row_product_id == str(product_id):
                log_info(f"在{sheet_name}中找到商品ID {product_id} 对应的行号: {row_index}")
                return row_dict
        
        log_info(f"在{sheet_name}中未找到商品ID {product_id} 对应的行")
        return None
    
    async def get_filtered_rows(self) -> List[Dict[str, Any]]:
        """获取分润模板表中符合条件的行数据：系统配置模版列不为空，且已配置列为空（向后兼容）"""
        values = await self.read_sheet_data(SheetNames.PROFIT_TEMPLATE)
        
        if not values:
            log_info("分润模板表为空，没有找到任何数据")
            return []
        
        # 假设第一行是标题行
        headers = values[0] if values else []
        if len(headers) < 12:
            raise Exception(f"分润模板表列数不足，预期至少12列，实际只有{len(headers)}列")
        
        # 系统配置模版和已配置列的名称
        system_config_header = "系统配置模版"
        configured_header = "已配置分润方案"
        
        filtered_rows = []
        
        for row_index, row in enumerate(values[1:], start=2):  # 从第2行开始（跳过标题行）
            # 确保行有足够的列
            if len(row) < len(headers):
                # 补充空值到与表头长度一致
                row = row + [None] * (len(headers) - len(row))
            
            # 转换为字典格式
            row_dict = self._convert_row_to_dict(headers, row, row_index)
            
            # 获取系统配置模版和已配置的值
            system_config_value = row_dict.get(system_config_header, "")
            configured_value = row_dict.get(configured_header, "")
            
            # 系统配置模版不为空，且已配置为空
            if system_config_value and not configured_value:
                filtered_rows.append(row_dict)
        
        log_info(f"找到 {len(filtered_rows)} 行符合条件的数据")
        return filtered_rows
    
    async def find_row_by_product_id(self, product_id: str) -> Optional[int]:
        """根据商品ID查找对应的行号（向后兼容方法，仅适用于分润模板表）
        
        Args:
            product_id: 商品ID
            
        Returns:
            Optional[int]: 找到的行号（Excel中的行号），未找到返回None
        """
        row_data = await self.find_by_product_id(SheetNames.PROFIT_TEMPLATE, product_id)
        if row_data:
            return row_data["row_index"]
        return None
    
    # async def update_cell_by_row_and_column(self, row_index: int, col_name: str = "已配置分润方案", value: str = "Y") -> bool:
    #     """更新指定行和列的单元格值
    #     
    #     Args:
    #         row_index: Excel中的行号（从1开始）
    #         col_name: 列名，默认为"已配置分润方案"
    #         value: 要设置的值，默认为"Y"
    #         
    #     Returns:
    #         bool: 更新是否成功
    #     """
    #     token = await self.get_tenant_access_token()
    #     
    #     # 获取列字母
    #     col_letter = self.get_column_letter(col_name)
    #     cell_range = f"{self.sheet_name}!{col_letter}{row_index}:{col_letter}{row_index}"
    #     
    #     url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{self.spreadsheet_id}/values"
    #     headers = {
    #         "Authorization": f"Bearer {token}",
    #         "Content-Type": "application/json"
    #     }
    #     
    #     data = {
    #         "valueRange": {
    #             "range": cell_range,
    #             "values": [[value]]
    #         }
    #     }
    #     
    #     log_info(f"更新单元格 {cell_range} ({col_name}列) 的值为: {value}")
    #     
    #     async with httpx.AsyncClient() as client:
    #         response = await client.put(url, headers=headers, json=data)
    #         response.raise_for_status()
    #         
    #         result = response.json()
    #         if result.get("code") != 0:
    #             log_error(f"更新单元格失败: {result.get('msg', '未知错误')}")
    #             return False
    #         
    #         log_info(f"成功更新单元格 {cell_range}")
    #         return True
    
    # async def update_configured_status(self, row_index: int, value: str = "Y") -> bool:
    #     """更新指定行的已配置状态（兼容性方法）
    #     
    #     Args:
    #         row_index: Excel中的行号（从1开始）
    #         value: 要设置的值，默认为"Y"
    #         
    #     Returns:
    #         bool: 更新是否成功
    #     """
    #     return await self.update_cell_by_row_and_column(row_index, "已配置分润方案", value)
    
    # async def update_by_product_id(self, product_id: str, col_name: str = "已配置分润方案", value: str = "Y") -> bool:
    #     """根据商品ID更新指定列的值
    #     
    #     Args:
    #         product_id: 商品ID
    #         col_name: 要更新的列名，默认为"已配置分润方案"
    #         value: 要设置的值，默认为"Y"
    #         
    #     Returns:
    #         bool: 更新是否成功
    #     """
    #     log_debug(f"开始根据商品ID {product_id} 更新列 {col_name} 的值为: {value}")
    #     # 先根据商品ID找到行号
    #     row_index = await self.find_row_by_product_id(product_id)
    #     
    #     if row_index is None:
    #         log_error(f"未找到商品ID {product_id} 对应的行，无法更新")
    #         return False
    #     
    #     # 更新指定行和列的值
    #     return await self.update_cell_by_row_and_column(row_index, col_name, value)
    
    # async def batch_update_configured_status(self, row_indices: List[int], value: str = "Y") -> Dict[int, bool]:
    #     """批量更新多行的已配置状态
    #     
    #     Args:
    #         row_indices: 要更新的行号列表
    #         value: 要设置的值，默认为"Y"
    #         
    #     Returns:
    #         Dict[int, bool]: 每行的更新结果
    #     """
    #     results = {}
    #     
    #     for row_index in row_indices:
    #         try:
    #             success = await self.update_configured_status(row_index, value)
    #             results[row_index] = success
    #             # 添加小延时避免请求过快
    #             await asyncio.sleep(0.1)
    #         except Exception as e:
    #             log_error(f"更新行 {row_index} 失败: {str(e)}")
    #             results[row_index] = False
    #     
    #     return results