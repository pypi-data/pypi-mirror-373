"""FTP Library"""

# ftplib: https://docs.python.org/3.12/library/ftplib.html
import os
from ftplib import FTP
from pathlib import Path

from loguru import logger


class XFTP:
    """XFTP"""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 21,
        username: str = "anonymous",
        password: str = "",
        encoding: str = "UTF-8",
        debuglevel: int = 0,
    ):
        """Initiation"""
        self.ftp = FTP()
        self.ftp.set_debuglevel(debuglevel)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.encoding = encoding
        self.retry = 1

    def connect(self) -> bool:
        """FTP connect"""
        try:
            self.ftp.connect(host=self.host, port=self.port, timeout=10)
            self.ftp.encoding = self.encoding
            self.ftp.login(user=self.username, passwd=self.password)
            logger.success("FTP connect success")
            logger.info("-" * 80)
            return True
        except Exception as e:
            # print(f"FTP connect error: {e}, retry...")
            # if self.retry >= 3:
            #     print("FTP connect faild")
            #     return False
            # self.retry += 1
            # self.connect()
            logger.exception(e)
            return False

    def close(self, info=None) -> bool:
        """FTP close"""
        if info is not None:
            logger.info(info)
        try:
            self.ftp.quit()
        except Exception as e:
            logger.exception(e)
            self.ftp.close()
        logger.info("-" * 80)
        logger.success("FTP connect closed")
        return True

    def get_file_list(self, target="/") -> list[str] | None:
        """Get file list"""
        try:
            self.chdir_to_remote(target)
            return self.ftp.nlst()
        except Exception as e:
            logger.exception(e)
            return None

    def get_file_size(self, file, target="/") -> int | None:
        """Get file size"""
        try:
            self.chdir_to_remote(target)
            return self.ftp.size(file)
        except Exception as e:
            logger.exception(e)
            return None

    def mkdir(self, target="/") -> bool:
        """创建目录 (从 / 目录依次递增创建子目录. 如果目录存在, 创建目录时会报错, 所以这里忽略所有错误.)"""
        try:
            dir_list = target.split("/")
            for i, _ in enumerate(dir_list):
                dir_path = "/".join(dir_list[: i + 1])
                try:
                    self.ftp.mkd(dir_path)
                except Exception as e:
                    logger.exception(e)
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def chdir_to_remote(self, target="/") -> bool:
        """change to remote directory"""
        try:
            self.ftp.cwd(target)
            return True
        except Exception as e:
            self.close(f"remote directory error: {target}")
            logger.exception(e)
            return False

    def x_exit(self, info=None):
        """Exit"""
        if info is not None:
            logger.info(info)
        # 注意: exit() 并不会退出脚本, 配合 try 使用
        exit()

    def x_exec(
        self, local_dir=".", local_file="", remote_dir="/", remote_file="", upload=False
    ):
        """Download or Upload"""

        bufsize = 1024
        local_path = f"{local_dir}/{local_file}"
        remote_path = f"{remote_dir}/{remote_file}"

        info = "Download"
        if upload is True:
            info = "Upload"

        # 检查参数
        if upload is True:
            if local_file == "":
                self.close("Argument Miss: local file")
            # 如果没有设置 远程文件 名称, 则使用 本地文件 名称
            if remote_file == "":
                remote_file = local_file
                remote_path = f"{remote_dir}/{remote_file}"
        else:
            if remote_file == "":
                self.close("Argument Miss: remote file")
            # 如果没有设置 本地文件 名称, 则使用 远程文件 名称
            if local_file == "":
                local_file = remote_file
                local_path = f"{local_dir}/{local_file}"

        # 进入本地目录
        try:
            if upload is True:
                # 检查本地目录
                stat = Path(local_dir)
                if stat.exists() is False:
                    self.close(f"Local directory error: {local_dir}")
            else:
                # 创建本地目录
                Path(local_dir).mkdir(parents=True, exist_ok=True)
            # 进入本地目录
            os.chdir(local_dir)
        except Exception as e:
            logger.exception(e)
            # 第一层 try 使用 self.x_exit() 无效, 直接使用 self.close()
            self.close(f"Local directory error: {local_dir}")

        # 上传或下载
        try:

            if upload is True:

                # 上传

                # 创建远程目录
                if remote_dir != "/":
                    self.mkdir(remote_dir)

                # 进入远程目录
                self.chdir_to_remote(remote_dir)

                # 上传文件
                stat = Path(local_file)
                if stat.exists() and stat.is_file():
                    with open(local_file, "rb") as fid:
                        self.ftp.storbinary(f"STOR {remote_file}", fid, bufsize)
                    logger.success(
                        f"{info} success: {local_path.replace('//', '/')} -> {remote_path.replace('//', '/')}"
                    )
                    return True

                self.x_exit(
                    f"{info} error: {local_path.replace('//', '/')} is not exist"
                )

            else:

                # 下载

                # 进入远程目录
                self.chdir_to_remote(remote_dir)

                # 下载文件
                if remote_file in self.ftp.nlst():
                    with open(local_file, "wb") as fid:
                        self.ftp.retrbinary(f"RETR {remote_file}", fid.write, bufsize)
                    logger.success(
                        f"{info} success: {remote_path.replace('//', '/')} -> {local_path.replace('//', '/')}"
                    )
                    return True

                self.x_exit(
                    f"{info} error: {remote_path.replace('//', '/')} is not exist"
                )

        except Exception as e:
            # 第一层 try 使用 self.x_exit() 无效, 直接使用 self.close()
            # self.close('{} faild! Please check {} or {}'.format(info, local_path, remote_path))
            self.close(f"{info} error: {e}")
            return False

    def handle_all(self, local_dir=".", remote_dir="/", upload=False):
        """Handle All"""
        if upload is True:
            # 检查本地目录
            stat = Path(local_dir)
            if stat.exists() is False:
                self.close(f"Local directory error: {local_dir}")
            # 获取文件列表
            local_files = [
                f
                for f in os.listdir(local_dir)
                if os.path.isfile(os.path.join(local_dir, f))
            ]
            for i in local_files:
                self.x_exec(
                    local_dir=local_dir,
                    remote_dir=remote_dir,
                    local_file=i,
                    upload=True,
                )
        else:
            remote_files = self.get_file_list(remote_dir)
            if remote_files is not None:
                for i in remote_files:
                    self.x_exec(
                        local_dir=local_dir, remote_dir=remote_dir, remote_file=i
                    )

    def retrlines(self, remote_dir="/", cmd="LIST"):
        """Retrlines"""
        try:
            self.chdir_to_remote(remote_dir)
            print(self.ftp.retrlines(cmd))
            self.close()
        except Exception as e:
            # 第一层 try 使用 self.x_exit() 无效, 直接使用 self.close()
            self.close(e)
