import requests
import tempfile
from pymsb.language.modules.pymsbmodule import PyMsbModule


# noinspection PyPep8Naming,PyMethodMayBeStatic
class Network(PyMsbModule):
    def DownloadFile(self, url):
        response = self.get_response(url)
        if not response:
            return ""
        ntf = tempfile.NamedTemporaryFile(suffix=".tmp", prefix="tmp", delete=False)
        ntf.write(response.content)
        ntf.close()
        return ntf.name

    def GetWebPageContents(self, url):
        response = self.get_response(url)
        if response:
            return response.text
        return ""

    def get_response(self, url):
        try:
            return requests.get(url)
        except BaseException as e:
            print(e)
            return None

