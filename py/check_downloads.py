from google.appengine.ext.deferred import deferred
from py import part_download


def initiate_download(status):
    url = status['url']
    size = status['size']
    index = status['last_block']
    filename = status['filename']
    start = []
    end = []
    BLOCK_SIZE = 1000 * 1000 * 5  # 2000K Bytes per block
    if size > 0:
        # split the content into several parts: #BLOCK_SIZE per block.
        blockNum = size / BLOCK_SIZE
        lastBlock = size % BLOCK_SIZE

        for i in range(0, blockNum + 1):
            start_byte = BLOCK_SIZE * i
            end_byte = start_byte + BLOCK_SIZE - 1

            if end_byte > size - 1:
                end_byte = size - 1

            if start_byte < end_byte:
                start.append(start_byte)
                end.append(end_byte)

    conn = part_download.login()

    deferred.defer(
        part_download.part_download, url=url,
        start=start, end=end, index=index, filename=filename, size=size, conn=conn)