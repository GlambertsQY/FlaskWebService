from urllib import parse

class Config:
    username = 'root'
    password = parse.quote_plus('Abc123456@')
    connectString = 'mysql+pymysql://'+username+':'+password+'@106.15.138.211/graduationproject?charset=utf8'
    wordVectorLocation = 'D:\\Document\\GraduationProject\\Project\\Word2VecTest\\MainPyFile\\wiki_new.wordvectors'
