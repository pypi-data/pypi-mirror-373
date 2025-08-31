#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移模块

这个模块提供了一个完整的数据库迁移解决方案，支持将本地Docker MySQL数据库的指定表
同步到远程服务器。

功能特性：
- 自动导出本地数据库表
- 通过SSH上传到远程服务器
- 自动导入到远程数据库
- 支持静默执行和交互式确认
- 完整的错误处理和日志记录

作者: qsir
版本: 1.0.0
"""

import os
import sys
import subprocess
import tempfile
import shutil
import logging
import platform
import locale
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatabaseConfig:
    """数据库配置类"""
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = "123wyk"
    database: str = "lz"
    docker_container: str = "mysql"


@dataclass
class RemoteConfig:
    """远程服务器配置类"""
    ssh_host: str = "git@e3"
    temp_dir: str = "/tmp/db_migration"
    database: DatabaseConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig(docker_container="mysql")


class DatabaseMigrator:
    """数据库迁移器主类"""
    
    def __init__(self, 
                 local_db: DatabaseConfig,
                 remote_config: RemoteConfig,
                 tables: List[str],
                 silent: bool = False,
                 log_level: str = "INFO"):
        """
        初始化数据库迁移器
        
        Args:
            local_db: 本地数据库配置
            remote_config: 远程服务器配置
            tables: 要迁移的表列表
            silent: 静默模式（True=自动执行，False=需要确认）
            log_level: 日志级别
        """
        self.local_db = local_db
        self.remote_config = remote_config
        self.tables = tables
        self.silent = silent
        
        # 设置日志
        self.logger = self._setup_logger(log_level)
        
        # 临时文件目录
        self.temp_dir = None
        
    def _setup_logger(self, level: str) -> logging.Logger:
        """设置日志器"""
        logger = logging.getLogger("DatabaseMigrator")
        logger.setLevel(getattr(logging, level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _run_command(self, command: List[str], cwd: Optional[str] = None, encoding: str = "utf-8") -> Tuple[bool, str, str]:
        """
        执行系统命令
        
        Args:
            command: 命令列表
            cwd: 工作目录
            encoding: 文本编码，默认utf-8
            
        Returns:
            (成功标志, 标准输出, 错误输出)
        """
        try:
            self.logger.debug(f"执行命令: {' '.join(command)}")
            
            # 在Windows系统上，使用二进制模式捕获输出以避免编码问题
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                timeout=300  # 5分钟超时
            )
            
            success = result.returncode == 0
            
            # 手动解码输出，处理编码错误
            try:
                stdout = result.stdout.decode(encoding, errors='replace')
                stderr = result.stderr.decode(encoding, errors='replace')
            except AttributeError:
                # 如果已经是字符串，直接使用
                stdout = result.stdout or ""
                stderr = result.stderr or ""
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error("命令执行超时")
            return False, "", "命令执行超时"
        except Exception as e:
            self.logger.error(f"命令执行失败: {e}")
            return False, "", str(e)
    
    def _confirm_action(self, message: str) -> bool:
        """
        确认操作
        
        Args:
            message: 确认消息
            
        Returns:
            是否确认
        """
        if self.silent:
            self.logger.info(f"静默模式: {message} - 自动确认")
            return True
        
        while True:
            response = input(f"{message} (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("请输入 y/yes 或 n/no")
    
    def _create_temp_directory(self) -> str:
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp(prefix="db_migration_")
        self.logger.info(f"创建临时目录: {self.temp_dir}")
        return self.temp_dir
    
    def _cleanup_temp_directory(self):
        """清理临时目录"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.logger.info(f"清理临时目录: {self.temp_dir}")
    
    def _detect_system_encoding(self) -> str:
        """检测系统编码"""
        # 在Windows上使用UTF-8，在其他系统上使用系统默认编码
        if platform.system() == "Windows":
            return "utf-8"
        else:
            return locale.getpreferredencoding() or "utf-8"
    
    def _run_mysql_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """
        专门用于运行MySQL命令的方法，处理编码问题
        
        Args:
            command: MySQL命令列表
            
        Returns:
            (成功标志, 标准输出, 错误输出)
        """
        try:
            self.logger.debug(f"执行MySQL命令: {' '.join(command)}")
            
            # 设置环境变量以确保UTF-8编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # 运行命令
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=300,
                env=env
            )
            
            success = result.returncode == 0
            
            # 尝试多种编码方式解码输出
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
            stdout = ""
            stderr = ""
            
            for encoding in encodings:
                try:
                    stdout = result.stdout.decode(encoding)
                    stderr = result.stderr.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用错误替换模式
            if not stdout and result.stdout:
                stdout = result.stdout.decode('utf-8', errors='replace')
            if not stderr and result.stderr:
                stderr = result.stderr.decode('utf-8', errors='replace')
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error("MySQL命令执行超时")
            return False, "", "MySQL命令执行超时"
        except Exception as e:
            self.logger.error(f"MySQL命令执行失败: {e}")
            return False, "", str(e)
    
    def _export_table(self, table: str) -> bool:
        """
        导出单个表
        
        Args:
            table: 表名
            
        Returns:
            是否成功
        """
        self.logger.info(f"正在导出表: {table}")
        
        output_file = os.path.join(self.temp_dir, f"{table}.sql")
        
        # 构建MySQL命令，在Windows上避免密码直接显示在命令行
        if platform.system() == "Windows":
            command = [
                "docker", "exec", "-e", f"MYSQL_PWD={self.local_db.password}",
                self.local_db.docker_container, "mysqldump",
                "-h", self.local_db.host,
                "-P", str(self.local_db.port),
                "-u", self.local_db.user,
                "--single-transaction",
                "--routines",
                "--triggers",
                "--set-gtid-purged=OFF",
                "--default-character-set=utf8mb4",  # 确保使用UTF-8字符集
                "--skip-comments",  # 跳过注释以减少编码问题
                self.local_db.database,
                table
            ]
        else:
            command = [
                "docker", "exec", self.local_db.docker_container, "mysqldump",
                "-h", self.local_db.host,
                "-P", str(self.local_db.port),
                "-u", self.local_db.user,
                f"-p{self.local_db.password}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--set-gtid-purged=OFF",
                "--default-character-set=utf8mb4",  # 确保使用UTF-8字符集
                "--skip-comments",  # 跳过注释以减少编码问题
                self.local_db.database,
                table
            ]
        
        # 使用专门的MySQL命令执行方法
        success, stdout, stderr = self._run_mysql_command(command)
        
        if success and stdout:
            # 将输出写入文件
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(stdout)
                self.logger.info(f"✓ 表 {table} 导出成功")
                return True
            except Exception as e:
                self.logger.error(f"✗ 表 {table} 写入文件失败: {e}")
                return False
        else:
            self.logger.error(f"✗ 表 {table} 导出失败: {stderr}")
            return False
    
    def _export_all_tables(self) -> bool:
        """导出所有表"""
        self.logger.info("开始导出本地数据库表...")
        
        for table in self.tables:
            if not self._export_table(table):
                return False
        
        self.logger.info("所有表导出完成！")
        return True
    
    def _upload_files_to_remote(self) -> bool:
        """上传文件到远程服务器"""
        self.logger.info("开始上传SQL文件到远程服务器...")
        
        # 创建远程目录
        command = ["ssh", self.remote_config.ssh_host, f"mkdir -p {self.remote_config.temp_dir}"]
        success, _, stderr = self._run_command(command)
        
        if not success:
            self.logger.error(f"无法创建远程目录: {stderr}")
            return False
        
        # 上传所有SQL文件
        for table in self.tables:
            local_file = os.path.join(self.temp_dir, f"{table}.sql")
            remote_path = f"{self.remote_config.ssh_host}:{self.remote_config.temp_dir}/"
            
            self.logger.info(f"正在上传 {table}.sql...")
            
            command = ["scp", local_file, remote_path]
            success, _, stderr = self._run_command(command)
            
            if success:
                self.logger.info(f"✓ {table}.sql 上传成功")
            else:
                self.logger.error(f"✗ {table}.sql 上传失败: {stderr}")
                return False
        
        self.logger.info("所有SQL文件上传完成！")
        return True
    
    def _write_script_file(self, content: str, file_path: str) -> bool:
        """
        安全地写入脚本文件，确保跨平台兼容性
        
        Args:
            content: 脚本内容
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        try:
            # 确保使用Unix换行符
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            # 使用二进制模式写入以避免换行符问题
            with open(file_path, 'wb') as f:
                f.write(content.encode('utf-8'))
            
            return True
        except Exception as e:
            self.logger.error(f"写入脚本文件失败: {e}")
            return False
    
    def _create_remote_import_script(self) -> str:
        """创建远程导入脚本"""
        script_lines = [
            "#!/bin/bash",
            "",
            "# 从参数获取配置",
            "REMOTE_DB_HOST=$1",
            "REMOTE_DB_PORT=$2", 
            "REMOTE_DB_USER=$3",
            "REMOTE_DB_PASSWORD=$4",
            "REMOTE_DB_NAME=$5",
            "REMOTE_TEMP_DIR=$6",
            "REMOTE_DOCKER_CONTAINER=$7",
            "",
            'echo "开始导入数据到远程数据库..."',
            "",
            "# 导入每个表",
            'for sql_file in "$REMOTE_TEMP_DIR"/*.sql; do',
            '    if [ -f "$sql_file" ]; then',
            '        table_name=$(basename "$sql_file" .sql)',
            '        echo "正在导入表: $table_name"',
            "        ",
            "        # 先删除表中的数据（如果需要覆盖）",
            '        docker exec "$REMOTE_DOCKER_CONTAINER" mysql \\',
            '              -h "$REMOTE_DB_HOST" \\',
            '              -P "$REMOTE_DB_PORT" \\',
            '              -u "$REMOTE_DB_USER" \\',
            '              -p"$REMOTE_DB_PASSWORD" \\',
            '              "$REMOTE_DB_NAME" \\',
            '              -e "SET FOREIGN_KEY_CHECKS=0; DROP TABLE IF EXISTS $table_name; SET FOREIGN_KEY_CHECKS=1;"',
            "        ",
            "        # 导入SQL文件",
            '        docker exec -i "$REMOTE_DOCKER_CONTAINER" mysql \\',
            '              -h "$REMOTE_DB_HOST" \\',
            '              -P "$REMOTE_DB_PORT" \\',
            '              -u "$REMOTE_DB_USER" \\',
            '              -p"$REMOTE_DB_PASSWORD" \\',
            '              "$REMOTE_DB_NAME" < "$sql_file"',
            "        ",
            "        if [ $? -eq 0 ]; then",
            '            echo "✓ 表 $table_name 导入成功"',
            "        else",
            '            echo "✗ 表 $table_name 导入失败"',
            "            exit 1",
            "        fi",
            "    fi",
            "done",
            "",
            'echo "所有表导入完成！"',
            "",
            "# 清理临时文件",
            'rm -rf "$REMOTE_TEMP_DIR"',
            'echo "临时文件已清理"'
        ]
        
        script_content = '\n'.join(script_lines)
        script_path = os.path.join(self.temp_dir, "remote_import.sh")
        
        if self._write_script_file(script_content, script_path):
            return script_path
        else:
            raise Exception("创建远程导入脚本失败")
    
    def _import_to_remote_database(self) -> bool:
        """导入数据到远程数据库"""
        self.logger.info("开始在远程服务器导入数据...")
        
        if not self.silent:
            self.logger.warning("注意: 这将覆盖远程服务器上的同名表！")
            if not self._confirm_action("确认要导入到远程数据库?"):
                self.logger.info("导入已跳过")
                return True
        
        # 创建远程导入脚本
        script_path = self._create_remote_import_script()
        
        # 上传脚本
        remote_script_path = f"{self.remote_config.ssh_host}:{self.remote_config.temp_dir}/remote_import.sh"
        command = ["scp", script_path, remote_script_path]
        success, _, stderr = self._run_command(command)
        
        if not success:
            self.logger.error(f"上传导入脚本失败: {stderr}")
            return False
        
        # 在远程服务器执行导入脚本
        remote_script = f"{self.remote_config.temp_dir}/remote_import.sh"
        remote_cmd = (
            f"dos2unix {remote_script} 2>/dev/null || sed -i 's/\\r$//' {remote_script} 2>/dev/null; "
            f"chmod +x {remote_script} && "
            f"{remote_script} "
            f"'{self.remote_config.database.host}' "
            f"'{self.remote_config.database.port}' "
            f"'{self.remote_config.database.user}' "
            f"'{self.remote_config.database.password}' "
            f"'{self.remote_config.database.database}' "
            f"'{self.remote_config.temp_dir}' "
            f"'{self.remote_config.database.docker_container}'"
        )
        
        command = ["ssh", self.remote_config.ssh_host, remote_cmd]
        success, stdout, stderr = self._run_command(command)
        
        if success:
            self.logger.info("✓ 远程数据库导入完成")
            if stdout:
                self.logger.info(f"导入输出: {stdout}")
            return True
        else:
            self.logger.error(f"✗ 远程数据库导入失败: {stderr}")
            return False
    
    def migrate(self) -> bool:
        """
        执行完整的数据库迁移流程
        
        Returns:
            是否成功
        """
        try:
            self.logger.info("==========================================")
            self.logger.info("      数据库迁移工具 v1.0 (Python)")
            self.logger.info("==========================================")
            self.logger.info("本工具将从本地数据库导出指定表，并同步到远程服务器")
            self.logger.info("")
            
            self.logger.info("配置信息：")
            self.logger.info(f"本地数据库: {self.local_db.user}@{self.local_db.host}:{self.local_db.port}/{self.local_db.database}")
            self.logger.info(f"远程服务器: {self.remote_config.ssh_host}")
            self.logger.info(f"要迁移的表: {', '.join(self.tables)}")
            self.logger.info(f"执行模式: {'静默模式' if self.silent else '交互模式'}")
            self.logger.info("")
            
            if not self._confirm_action("是否继续执行迁移?"):
                self.logger.info("操作已取消")
                return False
            
            # 创建临时目录
            self._create_temp_directory()
            
            # 第1步: 导出本地数据
            self.logger.info("")
            self.logger.info("第1步: 导出本地数据库表")
            self.logger.info("----------------------------------------")
            if not self._export_all_tables():
                return False
            
            # 第2步: 上传到远程服务器
            self.logger.info("")
            self.logger.info("第2步: 上传文件到远程服务器")
            self.logger.info("----------------------------------------")
            if not self._upload_files_to_remote():
                return False
            
            # 第3步: 导入到远程数据库
            self.logger.info("")
            self.logger.info("第3步: 导入数据到远程数据库")
            self.logger.info("----------------------------------------")
            if not self._import_to_remote_database():
                return False
            
            self.logger.info("")
            self.logger.info("==========================================")
            self.logger.info("           迁移完成！")
            self.logger.info("==========================================")
            self.logger.info("所有表已成功从本地数据库同步到远程服务器")
            self.logger.info(f"迁移的表: {', '.join(self.tables)}")
            self.logger.info("")
            
            return True
            
        except Exception as e:
            self.logger.error(f"迁移过程中发生错误: {e}")
            return False
        finally:
            # 清理临时文件
            self._cleanup_temp_directory()


def create_default_migrator(silent: bool = False) -> DatabaseMigrator:
    """
    创建默认配置的迁移器
    
    Args:
        silent: 是否静默执行
        
    Returns:
        DatabaseMigrator实例
    """
    # 本地数据库配置
    local_db = DatabaseConfig(
        host="localhost",
        port=3306,
        user="root",
        password="123wyk",
        database="lz",
        docker_container="mysql"
    )
    
    # 远程服务器配置
    remote_db = DatabaseConfig(
        host="localhost",
        port=3306,
        user="root",
        password="123wyk",
        database="lz",
        docker_container="mysql"
    )
    
    remote_config = RemoteConfig(
        ssh_host="git@e3",
        temp_dir="/tmp/db_migration",
        database=remote_db
    )
    
    # 要迁移的表
    tables = [
        "market_category",
        "market_country_sites",
        "market_product_ranking",
        "market_product_search_word"
    ]
    
    return DatabaseMigrator(
        local_db=local_db,
        remote_config=remote_config,
        tables=tables,
        silent=silent
    )