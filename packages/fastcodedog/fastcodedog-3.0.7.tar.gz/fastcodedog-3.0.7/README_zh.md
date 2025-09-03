# 概述
基于pdm文件(sap powerdesigner)，自动生成fastapi工程。   
包括sqlalchemy的model，crud。   
fastapi的schema，api。   
数据库引擎根据实际需要安装。   
3以上版本暂时退回到多线程，不支持协程。