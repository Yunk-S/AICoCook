#!/usr/bin/env python3
"""
数据导入命令行工具

提供命令行接口来导入CSV数据和管理向量嵌入。
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.data_import_service import DataImportService
from app.database import init_db
from app.core.logging import setup_logging
import structlog

# 设置日志
setup_logging()
logger = structlog.get_logger()


async def import_epicurious_data(args):
    """导入Epicurious数据"""
    print("🚀 开始导入 Epicurious 数据...")
    
    # 初始化数据库
    init_db()
    
    # 创建导入服务
    import_service = DataImportService()
    
    try:
        # 执行导入
        result = await import_service.import_epicurious_csv(
            csv_path=args.csv_path,
            start_from=args.start_from,
            limit=args.limit,
            generate_embeddings=args.embeddings
        )
        
        print("\n✅ 导入完成！")
        print(f"📊 统计信息:")
        print(f"   - 处理记录: {result['total_processed']}")
        print(f"   - 成功导入: {result['successful_imports']}")
        print(f"   - 导入失败: {result['failed_imports']}")
        print(f"   - 生成嵌入: {result['embeddings_generated']}")
        
        if result['errors']:
            print(f"\n⚠️  错误信息:")
            for error in result['errors'][:5]:  # 只显示前5个错误
                print(f"   - {error}")
            if len(result['errors']) > 5:
                print(f"   - ... 还有 {len(result['errors']) - 5} 个错误")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        sys.exit(1)


async def rebuild_embeddings(args):
    """重建向量嵌入"""
    print("🔄 开始重建向量嵌入...")
    
    # 初始化数据库
    init_db()
    
    # 创建导入服务
    import_service = DataImportService()
    
    try:
        # 执行重建
        result = await import_service.rebuild_embeddings(
            batch_size=args.batch_size
        )
        
        print("\n✅ 重建完成！")
        print(f"📊 统计信息:")
        print(f"   - 处理数量: {result['total_processed']}")
        
    except Exception as e:
        print(f"❌ 重建失败: {e}")
        sys.exit(1)


async def show_status(args):
    """显示导入状态"""
    print("📊 检查数据状态...")
    
    # 创建导入服务
    import_service = DataImportService()
    
    try:
        # 获取状态
        status = await import_service.get_import_status()
        
        print("\n📈 数据状态:")
        print(f"   - 总食谱数: {status['total_recipes']}")
        print(f"   - Epicurious食谱: {status['epicurious_recipes']}")
        print(f"   - 向量嵌入数: {status['vector_count']}")
        print(f"   - CSV文件存在: {'是' if status['csv_file_exists'] else '否'}")
        
        if status['csv_file_exists']:
            size_mb = status['csv_file_size'] / (1024 * 1024)
            print(f"   - CSV文件大小: {size_mb:.1f} MB")
        
        # 计算覆盖率
        if status['total_recipes'] > 0:
            coverage = (status['vector_count'] / status['total_recipes']) * 100
            print(f"   - 向量覆盖率: {coverage:.1f}%")
        
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Meal Coach 数据导入工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 导入数据命令
    import_parser = subparsers.add_parser('import', help='导入Epicurious数据')
    import_parser.add_argument(
        '--csv-path', 
        type=str, 
        help='CSV文件路径 (默认: data/raw/epi_r.csv)'
    )
    import_parser.add_argument(
        '--start-from', 
        type=int, 
        default=0, 
        help='从第几行开始导入 (默认: 0)'
    )
    import_parser.add_argument(
        '--limit', 
        type=int, 
        help='限制导入数量'
    )
    import_parser.add_argument(
        '--no-embeddings', 
        action='store_false', 
        dest='embeddings',
        help='不生成向量嵌入'
    )
    
    # 重建嵌入命令
    rebuild_parser = subparsers.add_parser('rebuild', help='重建向量嵌入')
    rebuild_parser.add_argument(
        '--batch-size', 
        type=int, 
        default=100, 
        help='批处理大小 (默认: 100)'
    )
    
    # 状态检查命令
    status_parser = subparsers.add_parser('status', help='查看数据状态')
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行对应命令
    if args.command == 'import':
        asyncio.run(import_epicurious_data(args))
    elif args.command == 'rebuild':
        asyncio.run(rebuild_embeddings(args))
    elif args.command == 'status':
        asyncio.run(show_status(args))


if __name__ == "__main__":
    main()