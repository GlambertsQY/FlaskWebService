from urllib import parse

class Config:
    username = 'root'
    password = parse.unquote_plus('Abc123456@')
    connectString = 'mysql+pymysql://'+username+':'+password+'@127.0.0.1/graduationproject?charset=utf8'
    wordVectorLocation = 'D:\\Document\\GraduationProject\\Project\\Word2VecTest\\MainPyFile\\wiki_new.wordvectors'
