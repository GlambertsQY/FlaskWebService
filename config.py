from urllib import parse

class Config:
    username = 'root'
    password = parse.unquote_plus('Abc123456@')
    connectString = 'mysql+pymysql://'+username+':'+password+'@106.14.141.128/graduationproject?charset=utf8'