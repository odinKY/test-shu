import subprocess
import sys
import os


def install_dependencies():
    print("=" * 50)
    print("图舒图书管理系统 - 依赖安装工具")
    print("=" * 50)

    packages = ["ebooklib", "beautifulsoup4", "lxml"]

    for package in packages:
        print(f"\n正在安装 {package}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", package],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print(f"  ✓ {package} 安装成功")
            else:
                if "already satisfied" in result.stdout.lower() or "already satisfied" in result.stderr.lower():
                    print(f"  ✓ {package} 已安装")
                else:
                    print(f"  ✗ {package} 安装失败")
                    print(f"    错误: {result.stderr}")
        except Exception as e:
            print(f"  ✗ {package} 安装异常: {e}")

    print("\n" + "=" * 50)
    print("依赖安装完成!")
    print("=" * 50)
    print("\n验证安装:")

    for package in packages:
        module_name = package.replace("-", "_").lower()
        try:
            __import__(module_name)
            print(f"  ✓ {package} 可正常导入")
        except ImportError:
            print(f"  ✗ {package} 导入失败")

    usersite = site.getusersitepackages()
    print(f"\n用户包目录: {usersite}")

    input("\n按回车键退出...")


if __name__ == "__main__":
    import site
    install_dependencies()
