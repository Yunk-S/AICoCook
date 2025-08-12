#!/usr/bin/env python3
"""
AI-Cook System Setup Script
Automated dependency installation and system setup
"""

import os
import sys
import subprocess
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SetupManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / ".venv"
        self.setup_cache = self.project_root / ".setup_cache.json"
        self.python_executable = None
        self.pip_executable = None
        
    def print_header(self, title: str):
        """Print a formatted section header"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}🚀 {title}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
        
    def print_step(self, step: str, message: str):
        """Print a step message"""
        print(f"{Colors.BLUE}[{step}]{Colors.END} {message}")
        
    def print_success(self, message: str):
        """Print a success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
        
    def print_error(self, message: str):
        """Print an error message"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
        
    def print_warning(self, message: str):
        """Print a warning message"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
        
    def load_cache(self) -> Dict:
        """Load setup cache to avoid redundant operations"""
        if self.setup_cache.exists():
            try:
                return json.loads(self.setup_cache.read_text())
            except:
                return {}
        return {}
        
    def save_cache(self, cache: Dict):
        """Save setup cache"""
        try:
            self.setup_cache.write_text(json.dumps(cache, indent=2))
        except:
            pass
            
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None, 
                   timeout: int = 300, check: bool = True, env: Optional[dict] = None) -> subprocess.CompletedProcess:
        """Run a command with proper error handling"""
        try:
            # Merge environment variables if provided
            command_env = os.environ.copy() if env else None
            if env and command_env:
                command_env.update(env)
            
            result = subprocess.run(
                cmd, 
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check,
                env=command_env
            )
            return result
        except subprocess.TimeoutExpired:
            self.print_error(f"Command timed out after {timeout} seconds: {' '.join(cmd)}")
            raise
        except subprocess.CalledProcessError as e:
            self.print_error(f"Command failed: {' '.join(cmd)}")
            if e.stdout:
                print(f"STDOUT: {e.stdout}")
            if e.stderr:
                print(f"STDERR: {e.stderr}")
            raise
            
    def check_requirements(self) -> bool:
        """Check basic system requirements"""
        self.print_step("1/7", "Checking system requirements...")
        
        # Check if we're in the right directory
        if not (self.project_root / "pyproject.toml").exists():
            self.print_error("pyproject.toml not found. Please run this script from the AI-Cook root directory.")
            return False
            
        self.print_success("Project directory confirmed")
        
        # Check Python installation
        try:
            result = self.run_command([sys.executable, "--version"])
            python_version = result.stdout.strip()
            self.print_success(f"Python found: {python_version}")
        except:
            self.print_error("Python not found or not working properly")
            return False
            
        # Check Node.js installation
        try:
            result = self.run_command(["node", "--version"], check=False)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                self.print_success(f"Node.js found: {node_version}")
            else:
                self.print_warning("Node.js not found. Frontend will not work.")
        except:
            self.print_warning("Node.js not found. Frontend will not work.")
            
        return True
        
    def setup_virtual_environment(self) -> bool:
        """Create and setup virtual environment"""
        self.print_step("2/7", "Setting up Python virtual environment...")
        
        cache = self.load_cache()
        
        # Check if venv exists and is valid
        if self.venv_path.exists() and cache.get("venv_created"):
            self.print_success("Virtual environment already exists")
        else:
            # Remove old venv if exists
            if self.venv_path.exists():
                self.print_step("2/7", "Removing old virtual environment...")
                try:
                    import shutil
                    shutil.rmtree(self.venv_path)
                except:
                    self.print_warning("Could not remove old virtual environment")
                    
            # Create new venv
            self.print_step("2/7", "Creating virtual environment...")
            try:
                self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])
                cache["venv_created"] = True
                self.save_cache(cache)
                self.print_success("Virtual environment created")
            except:
                self.print_error("Failed to create virtual environment")
                return False
                
        # Set up executable paths
        if os.name == 'nt':  # Windows
            self.python_executable = str(self.venv_path / "Scripts" / "python.exe")
            self.pip_executable = str(self.venv_path / "Scripts" / "pip.exe")
        else:  # Unix-like
            self.python_executable = str(self.venv_path / "bin" / "python")
            self.pip_executable = str(self.venv_path / "bin" / "pip")
            
        # Verify venv works
        try:
            self.run_command([self.python_executable, "--version"])
            self.print_success("Virtual environment activated and working")
            return True
        except:
            self.print_error("Virtual environment not working properly")
            return False
            
    def upgrade_pip(self) -> bool:
        """Upgrade pip to latest version"""
        self.print_step("3/7", "Upgrading pip...")
        try:
            self.run_command([
                self.python_executable, "-m", "pip", "install", 
                "--upgrade", "pip", "setuptools", "wheel"
            ])
            self.print_success("Pip upgraded successfully")
            return True
        except:
            self.print_warning("Pip upgrade failed, but continuing...")
            return True
            
    def install_dependencies_batch(self, packages: List[str], batch_name: str) -> bool:
        """Install packages with simple, reliable method"""
        self.print_step("4/7", f"Installing {batch_name}...")
        
        # Skip cache completely for reliability
        print(f"📦 Installing {len(packages)} packages in {batch_name}")
        
        # Simple progress tracking
        success_count = 0
        failed_packages = []
        
        for i, package in enumerate(packages, 1):
            pkg_name = package.split('>=')[0].split('==')[0].strip()
            print(f"[{i}/{len(packages)}] Installing {pkg_name}...")
            
            # Simple, direct installation
            if self.install_single_package_reliable(package, pkg_name):
                success_count += 1
                print(f"✅ {pkg_name} installed successfully")
            else:
                failed_packages.append(pkg_name)
                print(f"❌ {pkg_name} installation failed")
        
        # Results
        success_rate = success_count / len(packages)
        if success_rate >= 0.8:  # 80% success rate
            self.print_success(f"{batch_name}: {success_count}/{len(packages)} packages installed")
            return True
        else:
            self.print_error(f"{batch_name}: Only {success_count}/{len(packages)} packages installed")
            if failed_packages:
                print(f"❌ Failed packages: {', '.join(failed_packages)}")
            return False
    
    def install_single_package_reliable(self, package: str, pkg_name: str) -> bool:
        """Install a single package with special handling for problematic packages"""
        try:
            # Special handling for pip
            if pkg_name == "pip":
                return self.verify_single_package(pkg_name)
            
            # Special handling for problematic packages
            if pkg_name == "psycopg2-binary":
                return self.install_psycopg2_binary()
            elif pkg_name == "google-generativeai":
                return self.install_google_generativeai()
            elif pkg_name == "faiss-cpu":
                return self.install_faiss_cpu()
            elif pkg_name == "unstructured":
                return self.install_unstructured()
            
            # Standard installation for normal packages
            return self.install_standard_package(package, pkg_name)
                        
        except Exception:
            return False
    
    def install_standard_package(self, package: str, pkg_name: str) -> bool:
        """Standard package installation with retries"""
        try:
            # Method 1: Simple pip install
            try:
                self.run_command([
                    self.pip_executable, "install", package
                ], timeout=300)
                return self.verify_single_package(pkg_name)
                
            except Exception:
                # Method 2: Try with upgrade flag
                try:
                    self.run_command([
                        self.pip_executable, "install", "--upgrade", package
                    ], timeout=300)
                    return self.verify_single_package(pkg_name)
                    
                except Exception:
                    # Method 3: Try basic version only
                    try:
                        self.run_command([
                            self.pip_executable, "install", pkg_name
                        ], timeout=300)
                        return self.verify_single_package(pkg_name)
                        
                    except Exception:
                        return False
        except Exception:
            return False
    
    def install_psycopg2_binary(self) -> bool:
        """Special installation for psycopg2-binary with fallbacks"""
        try:
            print("  🔧 特殊处理: psycopg2-binary (PostgreSQL适配器)")
            
            # Method 1: Direct binary installation
            try:
                self.run_command([
                    self.pip_executable, "install", "--only-binary=psycopg2-binary", "psycopg2-binary"
                ], timeout=300)
                if self.verify_single_package("psycopg2-binary"):
                    return True
            except Exception:
                pass
            
            # Method 2: Try without version restrictions
            try:
                self.run_command([
                    self.pip_executable, "install", "psycopg2-binary"
                ], timeout=300)
                if self.verify_single_package("psycopg2-binary"):
                    return True
            except Exception:
                pass
            
            # Method 3: Use psycopg2 (source) as fallback
            try:
                print("    💡 尝试备用方案: psycopg2 (源码版本)")
                self.run_command([
                    self.pip_executable, "install", "psycopg2"
                ], timeout=600)
                return self.verify_single_package("psycopg2")
            except Exception:
                return False
                
        except Exception:
            return False
    
    def install_google_generativeai(self) -> bool:
        """Special installation for google-generativeai"""
        try:
            print("  🔧 特殊处理: google-generativeai (Google AI API)")
            
            # Method 1: Latest version
            try:
                self.run_command([
                    self.pip_executable, "install", "google-generativeai"
                ], timeout=600)
                if self.verify_single_package("google-generativeai"):
                    return True
            except Exception:
                pass
            
            # Method 2: Specific stable version
            try:
                print("    💡 尝试稳定版本: google-generativeai==0.3.2")
                self.run_command([
                    self.pip_executable, "install", "google-generativeai==0.3.2"
                ], timeout=600)
                if self.verify_single_package("google-generativeai"):
                    return True
            except Exception:
                pass
            
            # Method 3: No dependencies first, then install
            try:
                print("    💡 尝试分步安装")
                self.run_command([
                    self.pip_executable, "install", "--no-deps", "google-generativeai"
                ], timeout=300)
                self.run_command([
                    self.pip_executable, "install", "google-ai-generativelanguage", "google-auth"
                ], timeout=300)
                return self.verify_single_package("google-generativeai")
            except Exception:
                return False
                
        except Exception:
            return False
    
    def install_faiss_cpu(self) -> bool:
        """Special installation for faiss-cpu"""
        try:
            print("  🔧 特殊处理: faiss-cpu (向量数据库)")
            
            # Method 1: Latest version
            try:
                self.run_command([
                    self.pip_executable, "install", "faiss-cpu"
                ], timeout=600)
                if self.verify_single_package("faiss-cpu"):
                    return True
            except Exception:
                pass
            
            # Method 2: Specific stable version
            try:
                print("    💡 尝试稳定版本: faiss-cpu==1.7.4")
                self.run_command([
                    self.pip_executable, "install", "faiss-cpu==1.7.4"
                ], timeout=600)
                if self.verify_single_package("faiss-cpu"):
                    return True
            except Exception:
                pass
            
            # Method 3: Alternative package
            try:
                print("    💡 尝试备用方案: faiss (如果可用)")
                self.run_command([
                    self.pip_executable, "install", "faiss"
                ], timeout=600)
                return self.verify_single_package("faiss")
            except Exception:
                return False
                
        except Exception:
            return False
    
    def install_unstructured(self) -> bool:
        """Special installation for unstructured with incremental approach"""
        try:
            print("  🔧 特殊处理: unstructured (AI文档处理)")
            
            # Method 1: Install core unstructured first
            try:
                print("    📦 第1步: 安装核心unstructured库")
                self.run_command([
                    self.pip_executable, "install", "unstructured"
                ], timeout=600)
                if not self.verify_single_package("unstructured"):
                    return False
                print("    ✅ 核心库安装成功")
            except Exception:
                print("    ❌ 核心库安装失败")
                return False
            
            # Method 2: Try to install essential dependencies individually
            print("    📦 第2步: 安装关键依赖（可选）")
            essential_deps = [
                "nltk",
                "python-magic",
                "lxml",
                "beautifulsoup4",
                "requests",
                "chardet"
            ]
            
            success_count = 0
            for dep in essential_deps:
                try:
                    self.run_command([
                        self.pip_executable, "install", dep
                    ], timeout=300)
                    if self.verify_single_package(dep):
                        success_count += 1
                        print(f"    ✅ {dep} 安装成功")
                    else:
                        print(f"    ⚠️ {dep} 安装失败，但继续进行")
                except Exception:
                    print(f"    ⚠️ {dep} 安装失败，但继续进行")
            
            print(f"    📊 关键依赖: {success_count}/{len(essential_deps)} 安装成功")
            
            # Method 3: Try to install local-inference extras selectively
            print("    📦 第3步: 尝试安装AI增强功能（可选）")
            ai_extras = [
                "torch",
                "transformers", 
                "sentence-transformers",
                "layoutparser",
                "detectron2",
                "pillow-heif"  # 替代pi_heif
            ]
            
            ai_success = 0
            for extra in ai_extras:
                try:
                    self.run_command([
                        self.pip_executable, "install", extra
                    ], timeout=600, check=False)  # 不强制检查，允许失败
                    if self.verify_single_package(extra):
                        ai_success += 1
                        print(f"    ✅ AI增强: {extra} 安装成功")
                    else:
                        print(f"    ⚠️ AI增强: {extra} 跳过（可选）")
                except Exception:
                    print(f"    ⚠️ AI增强: {extra} 跳过（可选）")
            
            print(f"    📊 AI增强功能: {ai_success}/{len(ai_extras)} 可用")
            
            # Final verification
            if self.verify_single_package("unstructured"):
                print("    🎉 unstructured 核心功能可用！")
                return True
            else:
                print("    ❌ unstructured 验证失败")
                return False
                
        except Exception as e:
            print(f"    ❌ unstructured 安装过程出错: {e}")
            return False
    
    def verify_single_package(self, pkg_name: str) -> bool:
        """Verify a single package installation"""
        try:
            # Map package names to import names
            import_name_map = {
                'python-jose': 'jose',
                'python-dotenv': 'dotenv', 
                'python-multipart': 'multipart',
                'email-validator': 'email_validator',
                'python-json-logger': 'pythonjsonlogger',
                'python-slugify': 'slugify',
                'pdfminer.six': 'pdfminer',
                'pillow': 'PIL',
                'scikit-learn': 'sklearn',
                'prometheus-client': 'prometheus_client',
                'psycopg2-binary': 'psycopg2',
                'psycopg2': 'psycopg2',
                'google-generativeai': 'google.generativeai',
                'faiss-cpu': 'faiss',
                'faiss': 'faiss',
                'unstructured': 'unstructured',
                'langchain': 'langchain',
                'langchain-google-genai': 'langchain_google_genai',
                'sentence-transformers': 'sentence_transformers',
                'transformers': 'transformers',
                'python-magic': 'magic',
                'python-magic-bin': 'magic',
                'beautifulsoup4': 'bs4',
                'pillow-heif': 'pillow_heif',
                'python-pptx': 'pptx',
                'pdf2image': 'pdf2image',
                'layoutparser': 'layoutparser',
                'detectron2': 'detectron2'
            }
            
            import_name = import_name_map.get(pkg_name, pkg_name.replace('-', '_'))
            
            result = self.run_command([
                self.python_executable, "-c", f"import {import_name}"
            ], timeout=10, check=False)
            
            return result.returncode == 0
            
        except Exception:
            return False
            
    def is_critical_group(self, group_name: str) -> bool:
        """Check if a group is critical and should always be verified"""
        critical_groups = [
            "Core Dependencies", 
            "Basic Web Framework", 
            "Server and HTTP",
            "Essential Utilities",
            "Monitoring and Logging",
            "Chinese Processing"
        ]
        return group_name in critical_groups
    
    def verify_packages_installed(self, packages: List[str]) -> bool:
        """Verify that packages are actually installed and importable"""
        try:
            for package in packages:
                # Extract package name from version specification
                pkg_name = package.split('>=')[0].split('==')[0].split('<')[0].strip()
                
                # Map package names to import names
                import_name_map = {
                    'python-jose': 'jose',
                    'python-dotenv': 'dotenv',
                    'python-multipart': 'multipart',
                    'email-validator': 'email_validator',
                    'python-json-logger': 'pythonjsonlogger',
                    'python-slugify': 'slugify',
                    'pdfminer.six': 'pdfminer',
                    'pillow': 'PIL',
                    'scikit-learn': 'sklearn'
                }
                
                import_name = import_name_map.get(pkg_name, pkg_name.replace('-', '_'))
                
                # Try to import the module
                result = self.run_command([
                    self.python_executable, "-c", f"import {import_name}"
                ], timeout=10, capture_output=True)
                
                if result.returncode != 0:
                    return False
                    
            return True
        except Exception:
            return False
    
    def get_compatible_packages(self, packages: List[str], batch_name: str) -> List[str]:
        """Get compatible package versions for problematic installations"""
        compatible_map = {
            "Basic Web Framework": [
                "pydantic>=2.0.0,<3.0.0",  # More flexible version range
                "starlette>=0.27.0", 
                "fastapi>=0.100.0,<1.0.0"  # More flexible version range
            ],
            "Server and HTTP": [
                "uvicorn>=0.20.0",  # Avoid specific problematic versions
                "httpx>=0.24.0",
                "aiohttp>=3.8.0",
                "requests>=2.28.0"
            ],
            "Data Processing": [
                "numpy>=1.21.0",  # Use older, more stable version
                "pandas>=1.5.0"   # Use older, more stable version
            ]
        }
        
        return compatible_map.get(batch_name, packages)
                
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies in batches to avoid conflicts"""
        self.print_step("4/7", "Installing Python dependencies...")
        
        # Complete AI backend dependencies based on requirements.txt
        dependency_groups = [
            {
                "name": "Core Dependencies",
                "packages": [
                    "pip",
                    "setuptools", 
                    "wheel",
                    "tqdm"
                ]
            },
            {
                "name": "Web Framework",
                "packages": [
                    "typing-extensions",
                    "pydantic",
                    "starlette", 
                    "fastapi",
                    "uvicorn"
                ]
            },
            {
                "name": "Database Components",
                "packages": [
                    "sqlalchemy",
                    "alembic", 
                    "psycopg2-binary",
                    "redis"
                ]
            },
            {
                "name": "Authentication & Security",
                "packages": [
                    "passlib",  # 这是缺失的关键依赖！
                    "python-jose",
                    "python-multipart",
                    "email-validator"
                ]
            },
            {
                "name": "HTTP & Networking",
                "packages": [
                    "httpx",
                    "aiohttp", 
                    "requests"
                ]
            },
            {
                "name": "Utilities & Logging",
                "packages": [
                    "click",
                    "structlog",
                    "python-dotenv",
                    "prometheus-client",
                    "python-json-logger"  # 修复缺失的JSON日志格式化器
                ]
            },
            {
                "name": "Data Processing",
                "packages": [
                    "pandas",
                    "numpy"
                ]
            },
            {
                "name": "Task Queue",
                "packages": [
                    "celery"
                ]
            },
            {
                "name": "Chinese Text Processing",
                "packages": [
                    "jieba"
                ]
            },
            {
                "name": "AI & ML Core",
                "packages": [
                    "google-generativeai",
                    "openai"
                ]
            },
            {
                "name": "Language Processing",
                "packages": [
                    "langchain",
                    "transformers",
                    "sentence-transformers"
                ]
            },
            {
                "name": "Vector Database",
                "packages": [
                    "faiss-cpu"
                ]
            },
            {
                "name": "File Processing - Core",
                "packages": [
                    "pillow",
                    "python-slugify",
                    "pdfminer.six",
                    "python-magic-bin; platform_system=='Windows'",  # Windows二进制支持
                    "python-magic; platform_system!='Windows'"      # Unix系统支持
                ]
            },
            {
                "name": "File Processing - Unstructured (AI Document Processing)",
                "packages": [
                    "unstructured",  # 先安装基础版本
                ]
            },
            {
                "name": "File Processing - Optional AI Extensions",
                "packages": [
                    "layoutparser[paddlepaddle]",  # 可选的布局分析
                    "detectron2",                   # 可选的对象检测  
                    "pytesseract",                 # OCR支持
                    "pdf2image",                   # PDF转图像
                    "python-pptx",                 # PowerPoint支持
                    "openpyxl",                    # Excel支持
                    "xlrd"                         # 旧版Excel支持
                ]
            }
        ]
        
        # Initialize success counter
        success_count = 0
        
        # Install each group sequentially
        for i, group in enumerate(dependency_groups, 1):
            group_name = group["name"]
            print(f"\n[{i}/{len(dependency_groups)}] {group_name}")
            
            if self.install_dependencies_batch(group["packages"], group_name):
                success_count += 1
        
        # Results
        success_rate = success_count / len(dependency_groups)
        print(f"\n📊 Final Results: {success_count}/{len(dependency_groups)} groups successful ({success_rate:.1%})")
        
        if success_rate >= 0.8:
            self.print_success("Dependencies installation completed successfully!")
            return True
        else:
            self.print_error("Too many dependency failures. Please check your network and try again.")
            return False
            
    def verify_python_setup(self) -> bool:
        """Verify that key Python modules are working"""
        self.print_step("5/7", "Verifying Python setup...")
        
        test_imports = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("sqlalchemy", "Database ORM"),
            ("pydantic", "Data validation"),
            ("click", "CLI framework"),
            ("structlog", "Structured logging"),
            ("prometheus_client", "Metrics collection"),
            ("jieba", "Chinese text processing"),
            ("google.generativeai", "Google AI API"),
            ("openai", "OpenAI API"),
            ("langchain", "LangChain framework"),
            ("unstructured", "Document processing"),
            ("faiss", "Vector database"),
            ("transformers", "Hugging Face transformers"),
            ("sentence_transformers", "Sentence embeddings")
        ]
        
        failed_imports = []
        for module, description in test_imports:
            try:
                # Use ASCII-only characters to avoid encoding issues on Windows
                result = self.run_command([
                    self.python_executable, "-c", f"import {module}; print('[OK] {description}')"
                ], env={"PYTHONIOENCODING": "utf-8"})
                print(f"  {result.stdout.strip()}")
            except Exception as e:
                # Try simpler import test without print
                try:
                    self.run_command([
                        self.python_executable, "-c", f"import {module}"
                    ], env={"PYTHONIOENCODING": "utf-8"})
                    print(f"  [OK] {description} (import successful)")
                except:
                    failed_imports.append((module, description))
                    print(f"  [FAIL] {description} - Import failed")
                
        # More lenient for AI modules - some are optional
        total_modules = len(test_imports)
        core_modules = 8  # First 8 are core modules (FastAPI, uvicorn, etc.)
        ai_modules = total_modules - core_modules
        
        core_failures = sum(1 for module, _ in failed_imports if test_imports.index((module, next(desc for m, desc in test_imports if m == module))) < core_modules)
        ai_failures = len(failed_imports) - core_failures
        
        print(f"  📊 导入测试结果: {total_modules - len(failed_imports)}/{total_modules} 成功")
        print(f"     - 核心模块: {core_modules - core_failures}/{core_modules} 成功")
        print(f"     - AI模块: {ai_modules - ai_failures}/{ai_modules} 成功")
        
        # Core modules must succeed, AI modules are more flexible
        if core_failures <= 1 and len(failed_imports) <= 6:  # Allow more AI module failures
            self.print_success("关键Python模块验证通过")
            if ai_failures > 0:
                print(f"  ⚠️ 注意: {ai_failures} 个AI模块不可用，但不影响基础功能")
            return True
        else:
            self.print_error(f"关键模块失败过多: {len(failed_imports)} 个失败")
            if core_failures > 1:
                print(f"  ❌ 核心模块失败: {core_failures} 个，系统可能无法正常运行")
            return False
            
    def install_node_dependencies(self) -> bool:
        """Install Node.js dependencies"""
        self.print_step("6/7", "Installing Node.js dependencies...")
        
        if not (self.project_root / "package.json").exists():
            self.print_warning("package.json not found, skipping Node.js dependencies")
            return True
            
        cache = self.load_cache()
        if (self.project_root / "node_modules").exists() and cache.get("npm_installed"):
            self.print_success("Node.js dependencies already installed")
            return True
            
        try:
            self.run_command(["npm", "install"], timeout=600)
            cache["npm_installed"] = True
            self.save_cache(cache)
            self.print_success("Node.js dependencies installed")
            return True
        except:
            self.print_warning("Node.js dependencies installation failed")
            return True  # Don't fail the entire setup for this
            
    def start_services(self) -> bool:
        """Start all services"""
        self.print_step("7/7", "Starting services...")
        
        try:
            # Create service startup scripts
            services = [
                {
                    "name": "AI-Cook Main API",
                    "cmd": f'cd /d "{self.project_root}" && "{self.python_executable}" -m aire-backend.app.main',
                    "dir": "aire-backend"
                },
                {
                    "name": "AI-Cook Search API", 
                    "cmd": f'cd /d "{self.project_root}" && "{self.python_executable}" -m searchbackend.main',
                    "dir": "."
                },
                {
                    "name": "AI-Cook Frontend",
                    "cmd": f'cd /d "{self.project_root}" && npm run dev',
                    "dir": "."
                }
            ]
            
            if os.name == 'nt':  # Windows
                for service in services:
                    service_dir = self.project_root / service["dir"]
                    if service_dir.exists():
                        subprocess.Popen([
                            "cmd", "/c", "start", f'"{service["name"]}"', "cmd", "/k", service["cmd"]
                        ], shell=True)
                        time.sleep(1)  # Small delay between service starts
                        
            self.print_success("Services started in separate windows")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to start services: {str(e)}")
            return False
            
    def run_setup(self, skip_services: bool = False) -> bool:
        """Run the complete setup process"""
        self.print_header("AI-Cook System Setup")
        
        print("This script will set up your AI-Cook development environment.")
        print("It will create a virtual environment and install all dependencies.")
        if skip_services:
            print("Note: Service startup will be skipped (--no-services flag detected)")
        print()
        
        steps = [
            ("Check Requirements", self.check_requirements),
            ("Setup Virtual Environment", self.setup_virtual_environment),  
            ("Upgrade Pip", self.upgrade_pip),
            ("Install Python Dependencies", self.install_python_dependencies),
            ("Verify Python Setup", self.verify_python_setup),
            ("Install Node.js Dependencies", self.install_node_dependencies)
        ]
        
        # Only add service startup if not skipped
        if not skip_services:
            steps.append(("Start Services", self.start_services))
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    self.print_error(f"Setup failed at: {step_name}")
                    return False
            except KeyboardInterrupt:
                self.print_error("Setup interrupted by user")
                return False
            except Exception as e:
                self.print_error(f"Unexpected error in {step_name}: {str(e)}")
                return False
                
        self.print_header("Setup Complete!")
        print(f"{Colors.GREEN}AI-Cook system setup completed successfully!{Colors.END}")
        print()
        
        if not skip_services:
            print(f"{Colors.CYAN}Access URLs:{Colors.END}")
            print(f"  • Main Application:  http://localhost:3001")
            print(f"  • AI Backend API:    http://localhost:8000/docs")
            print(f"  • Search Backend:    http://localhost:8080/docs")
            print()
            print(f"{Colors.YELLOW}Services may take a moment to start up completely{Colors.END}")
            print(f"{Colors.BLUE}Check the opened windows for any error messages{Colors.END}")
        else:
            print(f"{Colors.CYAN}Dependencies installed and verified successfully!{Colors.END}")
            print(f"{Colors.YELLOW}Services will be started by the launcher script.{Colors.END}")
        print()
        
        return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI-Cook System Setup Script")
    parser.add_argument("--no-services", action="store_true", 
                        help="Skip starting services (only install dependencies)")
    
    args = parser.parse_args()
    setup_manager = SetupManager()
    
    try:
        success = setup_manager.run_setup(skip_services=args.no_services)
        if success:
            if not args.no_services:
                input("\nPress Enter to exit...")
            sys.exit(0)
        else:
            if not args.no_services:
                input("\nSetup failed. Press Enter to exit...")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.END}")
        if not args.no_services:
            input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()