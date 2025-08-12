#!/usr/bin/env python3
"""
依赖检查和测试脚本

此脚本检查AI后端和search后端的所必需依赖，并进行测试。
如果发现缺失的依赖，会提供安装建议。
"""

import sys
import subprocess
import importlib
import traceback
from pathlib import Path

# 预期的依赖列表
REQUIRED_PACKAGES = {
    # AI后端 (aire-backend) 核心依赖
    'fastapi': 'FastAPI web框架',
    'uvicorn': 'ASGI服务器',
    'sqlalchemy': '数据库ORM',
    'alembic': '数据库迁移工具',
    'psycopg2': 'PostgreSQL数据库驱动', 
    'redis': 'Redis客户端',
    'celery': '任务队列',
    'structlog': '结构化日志',
    'click': 'CLI工具（uvicorn/celery依赖）',
    'pydantic': '数据验证',
    'passlib': '密码哈希',
    'python_jose': 'JWT处理',
    'python_multipart': '文件上传',
    'httpx': 'HTTP客户端',
    'aiohttp': '异步HTTP客户端',
    'requests': 'HTTP请求库',
    'python_dotenv': '配置管理',
    'pandas': '数据处理',
    'numpy': '数值计算',
    'prometheus_client': '监控指标',
    'email_validator': '邮箱验证',
    
    # AI/ML 依赖
    'google.generativeai': 'Google AI API',
    'openai': 'OpenAI API', 
    'langchain': 'LangChain框架',
    'langchain_google_genai': 'LangChain Google集成',
    'transformers': 'Transformers模型库',
    'sentence_transformers': '句子转换器',
    'faiss': 'FAISS向量数据库',
    
    # 工具库  
    'tqdm': '进度条',
    'pillow': '图像处理',
    'python_slugify': 'URL slug生成',
    'unstructured': '文档解析',
    'pdfminer': 'PDF解析',
    
    # Search后端依赖
    'jieba': '中文分词',
}

MISSING_PACKAGES = []
IMPORT_ERRORS = []

def check_package_import(package_name, description):
    """检查包是否可以导入"""
    try:
        # 处理特殊的包名映射
        import_mapping = {
            'python_jose': 'jose',
            'python_multipart': 'multipart', 
            'python_dotenv': 'dotenv',
            'python_slugify': 'slugify',
            'google.generativeai': 'google.generativeai',
            'sentence_transformers': 'sentence_transformers',
            'langchain_google_genai': 'langchain_google_genai',
            'email_validator': 'email_validator',
            'prometheus_client': 'prometheus_client',
            'psycopg2': 'psycopg2',
            'pdfminer': 'pdfminer.six',
        }
        
        import_name = import_mapping.get(package_name, package_name)
        importlib.import_module(import_name)
        print(f"✅ {package_name}: {description}")
        return True
        
    except ImportError as e:
        print(f"❌ {package_name}: {description} - 导入失败")
        print(f"   错误: {str(e)}")
        MISSING_PACKAGES.append(package_name)
        IMPORT_ERRORS.append(f"{package_name}: {str(e)}")
        return False
    except Exception as e:
        print(f"⚠️  {package_name}: {description} - 意外错误")
        print(f"   错误: {str(e)}")
        IMPORT_ERRORS.append(f"{package_name}: {str(e)}")
        return False

def check_python_version():
    """检查Python版本"""
    print("🐍 Python版本检查:")
    version = sys.version_info
    print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 9:
        print("✅ Python版本兼容")
        return True
    else:
        print("❌ 需要Python 3.9或更高版本")
        return False

def test_fastapi_app():
    """测试FastAPI应用是否能够启动"""
    print("\n🚀 测试FastAPI应用:")
    try:
        # 添加项目路径
        sys.path.insert(0, str(Path(__file__).parent.parent / 'aire-backend'))
        
        from app.main import create_application
        app = create_application()
        print("✅ FastAPI应用创建成功")
        return True
    except Exception as e:
        print(f"❌ FastAPI应用创建失败: {str(e)}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def test_search_backend():
    """测试Search后端"""
    print("\n🔍 测试Search后端:")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from searchbackend.main import app
        print("✅ Search后端应用创建成功")
        return True
    except Exception as e:
        print(f"❌ Search后端应用创建失败: {str(e)}")
        print(f"   详细错误: {traceback.format_exc()}")
        return False

def install_missing_packages():
    """安装缺失的包"""
    if not MISSING_PACKAGES:
        print("\n✅ 所有依赖都已安装!")
        return True
        
    print(f"\n📦 发现 {len(MISSING_PACKAGES)} 个缺失的包:")
    for pkg in MISSING_PACKAGES:
        print(f"   - {pkg}")
    
    # 使用poetry安装缺失的包
    choice = input("\n是否使用poetry安装缺失的包? (y/n): ").lower().strip()
    if choice == 'y':
        try:
            print("\n正在安装缺失的包...")
            subprocess.run(['poetry', 'install'], check=True, cwd=Path(__file__).parent.parent)
            print("✅ 安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Poetry安装失败: {e}")
            print("\n手动安装建议:")
            print("cd 到根目录并运行: poetry install")
            return False
        except FileNotFoundError:
            print("❌ Poetry未找到")
            print("\n手动安装建议:")
            print("1. 安装Poetry: curl -sSL https://install.python-poetry.org | python3 -")
            print("2. cd 到根目录并运行: poetry install")
            return False
    else:
        print("\n手动安装建议:")
        print("cd 到根目录并运行: poetry install")
        return False

def test_database_connection():
    """测试数据库连接"""
    print("\n💾 测试数据库连接:")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / 'aire-backend'))
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"⚠️  数据库连接失败: {str(e)}")
        print("   这可能是正常的，如果数据库尚未设置")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 AI-Cook 依赖检查和测试脚本")
    print("=" * 60)
    
    # 检查Python版本
    python_ok = check_python_version()
    
    print("\n📦 检查Python包依赖:")
    print("-" * 40)
    
    # 检查每个包
    for package, description in REQUIRED_PACKAGES.items():
        check_package_import(package, description)
    
    print(f"\n📊 依赖检查总结:")
    print(f"   ✅ 可用包: {len(REQUIRED_PACKAGES) - len(MISSING_PACKAGES)}")
    print(f"   ❌ 缺失包: {len(MISSING_PACKAGES)}") 
    
    if IMPORT_ERRORS:
        print(f"\n❌ 导入错误详情:")
        for error in IMPORT_ERRORS[:10]:  # 显示前10个错误
            print(f"   {error}")
        if len(IMPORT_ERRORS) > 10:
            print(f"   ... 还有 {len(IMPORT_ERRORS) - 10} 个错误")
    
    # 尝试安装缺失的包
    if MISSING_PACKAGES:
        install_missing_packages()
    
    # 测试应用程序
    print("\n" + "=" * 60)
    print("🧪 应用程序测试")
    print("=" * 60)
    
    fastapi_ok = test_fastapi_app()
    search_ok = test_search_backend()
    db_ok = test_database_connection()
    
    # 最终总结
    print("\n" + "=" * 60)
    print("📋 最终总结")
    print("=" * 60)
    
    all_good = (
        python_ok and 
        len(MISSING_PACKAGES) == 0 and 
        fastapi_ok and 
        search_ok
    )
    
    if all_good:
        print("🎉 所有检查都通过了！系统已准备就绪。")
    else:
        print("⚠️  发现一些问题需要解决:")
        if not python_ok:
            print("   - Python版本不兼容")
        if MISSING_PACKAGES:
            print("   - 缺失Python包依赖")
        if not fastapi_ok:
            print("   - AI后端应用无法启动")
        if not search_ok:
            print("   - Search后端应用无法启动")
        if not db_ok:
            print("   - 数据库连接问题（可能正常）")
            
        print("\n建议解决步骤:")
        print("1. 确保使用Python 3.9+")
        print("2. 在根目录运行: poetry install")
        print("3. 重新运行此测试脚本")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())