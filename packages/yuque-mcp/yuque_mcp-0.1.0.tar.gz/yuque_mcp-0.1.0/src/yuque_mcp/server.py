#from mcp.server.fastmcp import FastMCP
import sys
from pathlib import Path
import importlib.util
from .mcp_instance import mcp


# 加载工具模块
TOOLS_DIR = Path(__file__).parent / "tools"

def load_all_modules_from_directory():
    """加载 tools/ 下所有 .py 模块，不做任何判断"""
    tools_path = Path(TOOLS_DIR)

    if not tools_path.exists():
        raise FileNotFoundError(f"Tools directory '{TOOLS_DIR}' not found.")

    for file in tools_path.iterdir():
        if file.is_file() and file.suffix == ".py" and file.name != "__init__.py":
            module_name = f"yuque_mcp.tools.{file.stem}"
            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # 输出到stderr，避免干扰stdio模式的MCP协议通信
            print(f"Loaded module: {module_name}", file=sys.stderr)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run MCP server with transport option")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["streamable-http", "sse", "stdio"],
        default="stdio",
        help="Transport mode for the server (default: streamable-http)",
    )
    args = parser.parse_args()

    # 加载工具模块
    try:
        load_all_modules_from_directory()  # ✅ 调用函数加载模块
    except Exception as e:
        print(f"Error loading tools: {e}", file=sys.stderr)
        sys.exit(1)

    # 初始化并运行服务器
    try:
        if args.transport == "stdio":
            # stdio模式下不打印启动信息到stdout，避免干扰MCP协议通信
            mcp.run(transport=args.transport)
        else:
            print(f"Starting server with transport={args.transport}...")
            mcp.run(transport=args.transport)

    except KeyboardInterrupt:  # 捕获 Ctrl+C 中断信号, 优雅退出
        print("Server stopped by user.", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()