import urllib
import re
import json
from typing import Union, Tuple, Dict, Any
from simba.utils.read_write import get_pkg_version
from simba.utils.checks import check_valid_url


def fetch_pip_data(pip_url: str = "https://pypi.org/pypi/simba-uw-tf-dev/json") -> Union[Tuple[Dict[str, Any], str], None]:
    """ Helper to fetch the pypi data associated with a package """
    if check_valid_url(url=pip_url):
        try:
            opener = urllib.request.build_opener(urllib.request.HTTPHandler(), urllib.request.HTTPSHandler())
            with opener.open(pip_url, timeout=2) as response:
                if response.status == 200:
                    encoding = response.info().get_content_charset("utf-8")
                    data = response.read().decode(encoding)
                    json_data = json.loads(data)
                    latest_release = json_data.get("info", {}).get("version", "")
                    return json_data, latest_release
        except Exception as e:
            #print(e.args)
            return None
    else:
        return None



get_pkg_version('simba-uw-tf-dev')
pip_data = fetch_pip_data(pip_url="https://pypi.org/pypi/simba-uw-tf-dev/json")
