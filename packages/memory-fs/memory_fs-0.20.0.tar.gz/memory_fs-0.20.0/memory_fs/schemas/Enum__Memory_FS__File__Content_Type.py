from enum import Enum

class Enum__Memory_FS__File__Content_Type(Enum):
    BINARY     : str = "application/octet-stream"
    HTML       : str = 'text/html; charset=utf-8'
    GZIP       : str = "application/gzip"
    JSON       : str = 'application/json; charset=utf-8'
    JPEG       : str = 'image/jpeg'
    MARKDOWN   : str = "text/markdown; charset=utf-8"
    DOT        : str = "text/vnd.graphviz; charset=utf-8"
    PNG        : str = 'image/png'
    TXT        : str = 'text/plain; charset=utf-8'
    ZIP        : str = "application/zip"


# or should we be using something like

# S3_FILES_CONTENT_TYPES       = { '.js'  : 'application/javascript; charset=utf-8',
#                                  '.jpg' : 'image/jpeg'                           ,
#                                  '.jpeg': 'image/jpeg'                           ,
#                                  '.png' : 'image/png'                            ,
#                                  '.txt' : 'text/plain; charset=utf-8'            ,
#                                  '.pdf' : 'application/pdf'                      ,
#                                  '.html': 'text/html; charset=utf-8'             ,
#                                  '.css' : 'text/css; charset=utf-8'              ,
#                                  '.svg' : 'image/svg+xml'                        ,
#                                  '.gif' : 'image/gif'                            ,
#                                  '.webp': 'image/webp'                           ,
#                                  '.json': 'application/json; charset=utf-8'      ,
#                                  '.xml' : 'application/xml; charset=utf-8'       ,
#                                  '.zip' : 'application/zip'                      ,
#                                  '.mp3' : 'audio/mpeg'                           ,
#                                  '.mp4' : 'video/mp4'                            ,
#                                  '.avi' : 'video/x-msvideo'                      ,
#                                  '.mov' : 'video/quicktime'                      }
