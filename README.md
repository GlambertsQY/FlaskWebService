# FlaskWebService
提供毕业设计App所需各种Web Service


#问题解决
##Mysql
1.数据库连接字符串不用域名：阿里云服务器为备案，会导致无法访问。
##Word2Vec
1.不需要在原模型基础上继续训练时，无需load model，只需load word vectors，同时load时可加上参数mmap='r'，只读模式更省内存。