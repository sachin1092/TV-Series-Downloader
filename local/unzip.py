if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import zipfile
import io
import os
import re
import shutil
from logger import write_to_downloader_log


def unzip(fl):
    path_list = fl.split("/")
    f_path = "/".join(path_list[:-1])
    match = re.search("(.*)_s(\d{1,2})", path_list[-1])
    series_name = match.group(1)
    season = match.group(2)
    zipfile.ZipFile(fl).extractall(f_path + "/" + series_name.title().replace("_", " ") + "/Season " + str(season))
    merge(f_path + "/" + series_name.title().replace("_", " ") + "/Season " + str(season), path_list[-1])
    os.remove(fl)


def merge(m_path, f_name):
    file_name = re.search("(.*).zip", f_name).group(1)
    final_file = io.BytesIO("")
    if not re.search('_part_', str(os.listdir(m_path))):
        return
    if os.path.isfile(m_path + "/status.txt"):
        os.remove(m_path + "/status.txt")
    for f in range(len(os.listdir(m_path))):
        if os.path.isfile(m_path + "/" + file_name.replace(" ", "_").lower() + "_part_" + str(f)):
            shutil.copyfileobj(open(m_path + "/" + file_name.replace(" ", "_").lower() + "_part_" + str(f), "r"),
                               final_file,
                               65536)
    final_file.seek(0, os.SEEK_END)
    write_to_downloader_log("file " + file_name + ".mp4 saved with size " + str(final_file.tell()))
    final_file.seek(0)
    fl = open(m_path + "/" + file_name + ".mp4", "wb")
    fl.write(final_file.read())
    fl.close()
    for f in range(len(os.listdir(m_path)) - 1):
        if os.path.isfile(m_path + "/" + file_name.replace(" ", "_").lower() + "_part_" + str(f)):
            os.remove(m_path + "/" + file_name.replace(" ", "_").lower() + "_part_" + str(f))


if __name__ == '__main__':
    unzip('/home/sachin/Series-Downloads/big_bang_theory_s8e11.zip')