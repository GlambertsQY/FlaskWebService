from urllib import parse

class Config:
    username = 'root'
    password = parse.quote_plus('Abc123456@')
    connectString = 'mysql+pymysql://'+username+':'+password+'@124.221.247.99/GraduationProject?charset=utf8'
    wordVectorLocation = 'D:\\Document\\GraduationProject\\Project\\Word2VecTest\\MainPyFile\\wiki_new.wordvectors'
