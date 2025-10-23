"""
业务工具模块
定义实际业务场景中的工具函数
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import random
from src.utils import log


def query_order(order_id: str) -> Dict[str, Any]:
    """
    查询订单信息
    
    Args:
        order_id: 订单号
    
    Returns:
        订单详细信息
    """
    log.info(f"查询订单: {order_id}")
    
    # 模拟订单数据（生产环境中应该查询数据库）
    mock_orders = {
        "ORD001": {
            "order_id": "ORD001",
            "status": "已发货",
            "product": "iPhone 15 Pro",
            "quantity": 1,
            "price": 7999.00,
            "order_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "shipping_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "expected_delivery": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "tracking_number": "SF1234567890"
        },
        "ORD002": {
            "order_id": "ORD002",
            "status": "处理中",
            "product": "MacBook Pro 14寸",
            "quantity": 1,
            "price": 15999.00,
            "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "shipping_date": None,
            "expected_delivery": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "tracking_number": None
        }
    }
    
    if order_id in mock_orders:
        return {
            "success": True,
            "data": mock_orders[order_id],
            "message": "订单查询成功"
        }
    else:
        return {
            "success": False,
            "data": None,
            "message": f"未找到订单号为 {order_id} 的订单"
        }


def process_refund(order_id: str, reason: str, amount: Optional[float] = None) -> Dict[str, Any]:
    """
    处理退款请求
    
    Args:
        order_id: 订单号
        reason: 退款原因
        amount: 退款金额（可选，默认全额退款）
    
    Returns:
        退款处理结果
    """
    log.info(f"处理退款: order_id={order_id}, reason={reason}, amount={amount}")
    
    # 先查询订单
    order_result = query_order(order_id)
    
    if not order_result["success"]:
        return {
            "success": False,
            "refund_id": None,
            "message": "订单不存在，无法申请退款"
        }
    
    order = order_result["data"]
    refund_amount = amount or order["price"]
    
    # 模拟退款处理
    refund_id = f"RFD{random.randint(10000, 99999)}"
    
    return {
        "success": True,
        "refund_id": refund_id,
        "order_id": order_id,
        "refund_amount": refund_amount,
        "reason": reason,
        "status": "审核中",
        "estimated_days": "3-5个工作日",
        "message": f"退款申请已提交，退款单号：{refund_id}，预计3-5个工作日内完成审核"
    }


def check_inventory(product_name: str) -> Dict[str, Any]:
    """
    查询商品库存
    
    Args:
        product_name: 商品名称
    
    Returns:
        库存信息
    """
    log.info(f"查询库存: {product_name}")
    
    # 模拟库存数据
    mock_inventory = {
        "iPhone 15 Pro": {
            "product_name": "iPhone 15 Pro",
            "sku": "IP15P-256-BLK",
            "stock": 156,
            "status": "有货",
            "price": 7999.00,
            "warehouse": "华东仓"
        },
        "MacBook Pro": {
            "product_name": "MacBook Pro 14寸",
            "sku": "MBP14-512-SLV",
            "stock": 23,
            "status": "有货",
            "price": 15999.00,
            "warehouse": "华北仓"
        },
        "AirPods Pro": {
            "product_name": "AirPods Pro 2",
            "sku": "APP2-WHT",
            "stock": 0,
            "status": "缺货",
            "price": 1899.00,
            "warehouse": "华南仓",
            "expected_restock": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        }
    }
    
    # 模糊匹配商品名称
    for key, value in mock_inventory.items():
        if product_name.lower() in key.lower():
            return {
                "success": True,
                "data": value,
                "message": "库存查询成功"
            }
    
    return {
        "success": False,
        "data": None,
        "message": f"未找到商品：{product_name}"
    }


def get_logistics_info(tracking_number: str) -> Dict[str, Any]:
    """
    查询物流信息
    
    Args:
        tracking_number: 物流单号
    
    Returns:
        物流跟踪信息
    """
    log.info(f"查询物流: {tracking_number}")
    
    # 模拟物流数据
    mock_logistics = {
        "SF1234567890": {
            "tracking_number": "SF1234567890",
            "carrier": "顺丰速运",
            "status": "运输中",
            "current_location": "上海分拨中心",
            "destination": "北京市朝阳区",
            "traces": [
                {
                    "time": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                    "location": "上海分拨中心",
                    "status": "已到达上海分拨中心"
                },
                {
                    "time": (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
                    "location": "深圳集散中心",
                    "status": "已离开深圳集散中心"
                },
                {
                    "time": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                    "location": "深圳华强北营业点",
                    "status": "已揽收"
                }
            ]
        }
    }
    
    if tracking_number in mock_logistics:
        return {
            "success": True,
            "data": mock_logistics[tracking_number],
            "message": "物流查询成功"
        }
    else:
        return {
            "success": False,
            "data": None,
            "message": f"未找到物流单号：{tracking_number}"
        }

