import json
import logging
import shlex
import subprocess
import subprocess as sp


def execute_command(args: list[str]):
    p = sp.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print(f"out {out} err {err}")
    if p.returncode != 0:
        err = "\n".join([err for err in err.decode().split("\n") if "Error" in err])
        raise Exception(err)
    return out.decode()


class FFMpegService:
    def __init__(self):
        self.__thread = 4

    # 执行ffbore命令
    @staticmethod
    def __ffprobe(path: str) -> dict:
        return json.loads(execute_command(["ffprobe", '-show_format', '-show_streams', '-of', 'json', path]))

    # 执行原始ffmpeg任务
    def ffmpeg_run(self, cmd: str):
        # 执行ffmpeg命令
        cmd = "ffmpeg -threads {} {}".format(self.__thread, cmd)
        logging.info("ffmpeg cmd is {}".format(cmd))
        return execute_command(shlex.split(cmd))

    # 获取文件时长(s)
    def get_duration(self, path: str) -> float:
        return float(self.__ffprobe(path)["format"]["duration"])
