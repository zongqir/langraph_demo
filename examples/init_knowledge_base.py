"""
初始化知识库
添加常见问题和产品信息到向量数据库
"""
import sys
from pathlib import Path

# 开发调试：添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from langraph_customer_service.knowledge_base import KnowledgeBase
from langraph_customer_service.utils import log


def main():
    """初始化知识库"""
    
    log.info("开始初始化知识�?..")
    
    # 创建知识库实�?
    kb = KnowledgeBase()
    
    # 产品信息知识
    product_docs = [
        # iPhone系列
        """iPhone 15 Pro产品信息�?
        - 屏幕�?.1英寸超视网膜XDR显示�?
        - 处理器：A17 Pro芯片
        - 摄像头：4800万像素主摄，支持2倍光学变�?
        - 存储�?28GB/256GB/512GB/1TB可�?
        - 价格�?999元起
        - 特色：钛金属设计，动作按钮，USB-C接口
        """,
        
        """iPhone 15产品信息�?
        - 屏幕�?.1英寸超视网膜XDR显示�?
        - 处理器：A16仿生芯片
        - 摄像头：4800万像素主�?
        - 存储�?28GB/256GB/512GB可�?
        - 价格�?999元起
        - 特色：动态岛，USB-C接口，双摄系�?
        """,
        
        # MacBook系列
        """MacBook Pro 14寸产品信息：
        - 处理器：M3/M3 Pro/M3 Max芯片可�?
        - 屏幕�?4.2英寸Liquid视网膜XDR显示�?
        - 内存�?GB起，最�?28GB
        - 存储�?12GB起，最�?TB
        - 价格�?5999元起
        - 特色：ProMotion技术，续航最�?2小时，多接口支持
        """,
        
        """MacBook Air 15寸产品信息：
        - 处理器：M3芯片
        - 屏幕�?5.3英寸Liquid视网膜显示屏
        - 内存�?GB/16GB/24GB可�?
        - 存储�?56GB起，最�?TB
        - 价格�?0499元起
        - 特色：轻薄便携，无风扇设计，续航最�?8小时
        """,
        
        # AirPods系列
        """AirPods Pro 2产品信息�?
        - 降噪：自适应主动降噪
        - 芯片：H2芯片
        - 续航：单次使用最�?小时，配合充电盒最�?0小时
        - 价格�?899�?
        - 特色：空间音频，自适应通透模式，精准查找
        """,
        
        """AirPods 3产品信息�?
        - 芯片：H1芯片
        - 续航：单次使用最�?小时，配合充电盒最�?0小时
        - 价格�?399�?
        - 特色：空间音频，抗汗抗水，MagSafe充电�?
        """
    ]
    
    # 常见问题知识
    faq_docs = [
        """退换货政策�?
        1. 自收货之日起7天内，商品未使用且包装完好，可申请无理由退�?
        2. 非人为损坏的质量问题，自购买之日�?5天内可换�?
        3. 产品享有1年保修服�?
        4. 退货运费：质量问题由商家承担，个人原因由买家承�?
        5. 退款时效：商品签收�?-5个工作日内完成退款审�?
        """,
        
        """配送说明：
        1. 正常配送时效：下单�?-3个工作日发货�?-7天送达
        2. 偏远地区可能需要额�?-2�?
        3. 支持顺丰速运、京东物流等多家快�?
        4. 部分商品支持当日�?次日达服�?
        5. 可在订单详情中查看物流信�?
        """,
        
        """支付方式�?
        支持以下支付方式�?
        1. 微信支付
        2. 支付�?
        3. 银联支付
        4. 花呗分期�?�?6�?12期免息）
        5. 信用卡支�?
        6. Apple Pay
        """,
        
        """售后服务�?
        1. 产品享有1年免费保�?
        2. 可购买AppleCare+延保服务
        3. 全国Apple授权服务点支�?
        4. 7x24小时在线客服
        5. 非人为损坏免费维�?
        6. 人为损坏提供付费维修服务
        """,
        
        """发票说明�?
        1. 支持开具电子发票和纸质发票
        2. 发票类型：增值税普通发票、增值税专用发票
        3. 发票内容：商品明细、办公用品、电子产品等
        4. 开票时效：订单完成后即可申请开�?
        5. 电子发票会发送到预留邮箱
        """,
        
        """会员权益�?
        1. 新用户注册即�?00积分
        2. 每消�?元积1�?
        3. 积分可抵扣现金（100积分=1元）
        4. 会员专享优惠�?
        5. 生日月双倍积�?
        6. 优先客服通道
        """,
        
        """订单修改�?
        1. 订单未发货前可以修改收货地址
        2. 订单支付�?0分钟内可以取�?
        3. 如需修改商品，需取消重新下单
        4. 联系客服可协助处理订单问�?
        """
    ]
    
    # 技术支持知�?
    tech_docs = [
        """iPhone激活教程：
        1. 长按电源键开�?
        2. 选择语言和地�?
        3. 连接Wi-Fi网络
        4. 设置面容ID或触控ID
        5. 创建或登录Apple ID
        6. 同意条款与条�?
        7. 设置Siri和其他服�?
        8. 完成设置，开始使�?
        """,
        
        """MacBook首次使用指南�?
        1. 连接电源适配�?
        2. 按下电源键开�?
        3. 选择国家或地�?
        4. 连接Wi-Fi
        5. 数据迁移（如需要）
        6. 登录或创建Apple ID
        7. 创建电脑账户
        8. 设置触控ID
        9. 选择主题（浅�?深色�?
        10. 完成设置
        """,
        
        """AirPods配对方法�?
        1. 打开充电盒盖�?
        2. 长按充电盒背面按钮直到状态灯闪烁白色
        3. 在iPhone设置中选择蓝牙
        4. 在可用设备中点击您的AirPods
        5. 配对成功后即可使�?
        注：首次配对后，打开盒盖即可自动连接
        """,
        
        """常见问题排查�?
        问题1：设备无法开�?
        解决：长按电源键10秒强制重启，检查电量是否充�?
        
        问题2：Wi-Fi连接不稳�?
        解决：重启路由器，忘记网络后重新连接，检查系统更�?
        
        问题3：电池续航短
        解决：检查后台应用，关闭不必要的定位服务，降低屏幕亮�?
        
        问题4：无法下载应�?
        解决：检查Apple ID登录状态，确认网络连接，查看存储空�?
        """
    ]
    
    # 合并所有文�?
    all_docs = product_docs + faq_docs + tech_docs
    
    # 创建元数�?
    metadata = []
    metadata.extend([{"category": "product", "type": "iPhone"}] * 2)
    metadata.extend([{"category": "product", "type": "MacBook"}] * 2)
    metadata.extend([{"category": "product", "type": "AirPods"}] * 2)
    metadata.extend([{"category": "faq", "type": "policy"}] * 7)
    metadata.extend([{"category": "tech", "type": "tutorial"}] * 4)
    
    # 添加到知识库
    kb.add_documents(all_docs, metadata)
    
    # 保存知识�?
    kb.save()
    
    log.info(f"知识库初始化完成！共添加 {len(all_docs)} 条文�?)
    
    # 测试检�?
    log.info("\n测试知识库检�?..")
    test_queries = [
        "iPhone 15 Pro多少钱？",
        "如何退货？",
        "AirPods怎么配对�?
    ]
    
    for query in test_queries:
        log.info(f"\n查询: {query}")
        results = kb.search(query, top_k=2)
        for i, result in enumerate(results, 1):
            log.info(f"结果{i} (相似�? {result['score']:.4f}):")
            log.info(f"{result['document'][:100]}...")


if __name__ == "__main__":
    main()

