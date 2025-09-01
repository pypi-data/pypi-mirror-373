from mignonFramework import InsertQuick, Logger, ConfigManager, inject, QueueIter, target, Rename, extractDDL2List
from mignonFramework.utils import SqlDDL2List


log = Logger(True)
config = ConfigManager("./resources/config/insertConfig.ini")

queueStarter = QueueIter(config)


@inject(config)
class RowsData:
    rows: int
    num: int


rowsData = config.getInstance(RowsData)


InsertQuick(

).run("D:\专利\备份\科技成果.txt", rowsData.rows)
