import requests

class JxHttpClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get(self, endpoint: str, params: dict = None):
        """发送 GET 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # 抛出异常以处理非 2xx 状态码
            return response.json()  # 返回 JSON 响应内容
        except requests.HTTPError as e:
            print(f"HTTP错误: {e}")
        except ValueError:
            print("返回的内容无法解析为 JSON")
        except Exception as e:
            print(f"发生错误: {e}")

    def post(self, endpoint: str, data: dict):
        """发送 POST 请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # 抛出异常以处理非 2xx 状态码
            return response.json()  # 返回 JSON 响应内容
        except requests.HTTPError as e:
            print(f"HTTP错误: {e}")
        except ValueError:
            print("返回的内容无法解析为 JSON")
        except Exception as e:
            print(f"发生错误: {e}")

    def put(self, endpoint: str, data: dict):
        """发送 PUT 请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        try:
            response = requests.put(url, json=data, headers=headers)
            response.raise_for_status()  # 抛出异常以处理非 2xx 状态码
            return response.json()  # 返回 JSON 响应内容
        except requests.HTTPError as e:
            print(f"HTTP错误: {e}")
        except ValueError:
            print("返回的内容无法解析为 JSON")
        except Exception as e:
            print(f"发生错误: {e}")

    def delete(self, endpoint: str):
        """发送 DELETE 请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.delete(url)
            response.raise_for_status()  # 抛出异常以处理非 2xx 状态码
            return response.json() if response.content else {}  # 如果没有内容，返回空字典
        except requests.HTTPError as e:
            print(f"HTTP错误: {e}")
        except ValueError:
            print("返回的内容无法解析为 JSON")
        except Exception as e:
            print(f"发生错误: {e}")