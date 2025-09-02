import struct

type_dict = {
    # '424D': 'bmp',
    'FFD8FF': 'jpg',
    # '2E524D46': 'rm',
    # '4D546864': 'mid',
    '89504E47': 'png',
    '47494638': 'gif',
    '49492A00': 'tif',
    # '41433130': 'dwg',
    # '38425053': 'psd',
    # '2142444E': 'pst',
    # 'FF575043': 'wpd',
    # 'AC9EBD8F': 'qdf',
    # 'E3828596': 'pwl',
    '504B0304': 'zip',
    '52617221': 'rar',
    '57415645': 'wav',
    '41564920': 'avi',
    '2E7261FD': 'ram',
    '000001BA': 'mpg',
    '000001B3': 'mpg',
    '6D6F6F76': 'mov',
    # '7B5C727466': 'rtf',
    '3C3F786D6C': 'xml',
    '68746D6C3E': 'html',
    'D0CF11E0': 'doc/xls',
    '255044462D312E': 'pdf',
    'CFAD12FEC5FD746F': 'dbx',
    # '3026B2758E66CF11': 'asf',
    '5374616E64617264204A': 'mdb',
    # '252150532D41646F6265': 'ps/eps',
    # '44656C69766572792D646174653A': 'eml'
}
max_len = len(max(type_dict, key=len)) // 2


async def get_filetype(file):
    # 读取二进制文件开头一定的长度
    if isinstance(file, str):
        filename = file
        with open(filename, 'rb') as f:
            byte = f.read(max_len)
    else:
        filename = file.filename
        byte = await file.read(max_len)
        await file.seek(0)
    # 解析为元组
    byte_list = struct.unpack('B' * max_len, byte)
    # 转为16进制
    code = ''.join([('%X' % each).zfill(2) for each in byte_list])
    # 根据标识符筛选判断文件格式
    result = list(filter(lambda x: code.startswith(x), type_dict))
    nametype = filename.split('.')[-1]
    if result:
        filetype = type_dict[result[0]]
        if filetype == "zip":
            filetype = nametype if nametype in ['xlsx', 'docx'] else "zip"
        elif filetype == "doc/xls":
            filetype = nametype if nametype in ['doc', 'xls'] else None
        elif filetype == "jpg":
            filetype = nametype if nametype in ['jpg', 'jpeg'] else None
        else:
            filetype = filetype if filetype == nametype else None
    else:
        filetype = nametype if nametype in ['mp3', 'mp4', 'txt'] else None
    return filetype

file_type = {
    "image": ["jpg", "png", "gif", "tif"],
    "document": ["zip", "rar", "wav", "xml", "html", "doc", "xls", "pdf", "dbx", "mdb"],
    "voice": ["mp3", "amr"],
    "video": ["wav", "avi", "ram", "mpg", "mov", "mp4"],
}

