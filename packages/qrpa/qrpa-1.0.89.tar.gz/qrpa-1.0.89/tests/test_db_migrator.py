from qrpa import create_default_migrator
import logging
import sys


def main():
    """命令行入口点"""
    import argparse

    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument("--silent", action="store_true", help="静默模式（不需要确认）")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别")
    parser.add_argument("--version", action="version", version="db-migrator-docker 1.0.0")

    args = parser.parse_args()

    # 创建迁移器并执行
    # migrator = create_default_migrator(args.silent)
    migrator = create_default_migrator(True)
    migrator.logger.setLevel(getattr(logging, args.log_level))

    success = migrator.migrate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
