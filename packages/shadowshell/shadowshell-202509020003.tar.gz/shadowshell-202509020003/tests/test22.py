from base_test import BaseTest

from src.shadowshell.monitor.monitor import function_monitor
from src.shadowshell.request.request import Request 
from src.shadowshell.file.file_util import FileUtil
from src.shadowshell.boot.starter import Starter
from src.shadowshell.serialize.serializable import Serializable
from src.shadowshell.serialize.serializer_factory import SerializerFactory
from src.shadowshell.model.dataset import DataSet

class_mame = 'Test'
work_dir = '/Users/shadowwalker/shadowshellxyz/OneDrive/BK/AICloudKeeper'
test_data_url = '/Users/shadowwalker/Downloads/线索报盘测试用例-单意图.xlsx'

class Test(Starter):

    @function_monitor(class_mame)
    def get_work_dir(self):
        """获取工作目录"""
        return work_dir

    @function_monitor(class_mame)
    def test(self):

      DataSet().iterate_excel(test_data_url, lambda item : print(item))

      url = self.configurator.get('test', 'url')
      headers = headers={'Content-Type': 'application/json'}
      payload = FileUtil.get_all(self.work_dir + '/线索报盘/测试/线索报盘.json')
      
      response = Request().post(url, headers, payload)
      
      res_data = response.text
      serializer = SerializerFactory().get_instance()
      print(res_data)

      items = serializer.deserialize(res_data)
      
      for item in items:
        print(f"{item['content']} -->> {item['actualAssistantText']}")

Test().test()

