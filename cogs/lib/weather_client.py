from typing import Union
import requests
import datetime


class WeatherCache():
    """気象庁から天気予報を保管するキャッシュインスタンス
    Args:
        expire_minutes (int): キャッシュの維持時間(デフォルト30分)
    """

    def __init__(self, expire_minutes: int = 30):
        self.CACHE = {}
        self.expire_minutes = expire_minutes

    def set(self, area_code: str, jsResp: dict) -> None:
        """指定した地域の天気をキャッシュに保管する
        Args:
            area_code (str): 都道府県エリアコード
            jsResp (dict): 天気予報のJSONデータ
        """
        self.CACHE[area_code] = {
            "saved": datetime.datetime.now(),
            "resp": jsResp
        }

    def get(self, area_code: str) -> Union[dict, None]:
        """指定した地域の天気をキャッシュから取得する、キャッシュに存在しない場合はNoneを返す
        Args:
            area_code (str): 都道府県エリアコード
        """
        # 期限切れのキャッシュを消去
        expire_minutes = datetime.timedelta(minutes=self.expire_minutes)
        current_time = datetime.datetime.now()
        for k in self.CACHE.keys():
            if self.CACHE[k]["saved"] + expire_minutes <= current_time:
                del self.CACHE[area_code]
        # キャッシュにあればキャッシュから取得
        if area_code in self.CACHE:
            return self.CACHE[area_code]["resp"]
        return None


class WeatherClient():
    """気象庁から天気予報を取得するAPIクライアント
    Args:
        endpoint (str): APIエンドポイント
    """

    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.cache = WeatherCache()
        self.areas = requests.get(
            f'{self.endpoint}/common/const/area.json'
        ).json()["offices"]
        self.error_message = "\n".join([
            "天気情報を取得することができませんでした。",
            "エリア名を再確認してください。",
            "",
            "例: '大阪府', 'Kyoto",
            "",
            "全国の天気予報",
            f"{self.endpoint}/forecast/"
        ])

    def __get_area_code(self, area_name: str) -> str:
        """指定した地域のエリアコードを取得する
        Args:
            area_name (str): 都道府県名
        """
        key = [
            k for k, d in self.areas.items()
            if d['name'] == area_name or d['enName'] == area_name
        ]
        area_code = ''.join(key)
        return area_code

    def __request_weather(self, area_code: str) -> dict:
        """指定したエリアコードの天気を取得する、キャッシュにある場合キャッシュから取得する
        Args:
            area_code (str): 都道府県エリアコード
        """
        url = (
            f'{self.endpoint}/forecast'
            f'/data/overview_forecast/{area_code}.json'
        )
        data = self.cache.get(area_code)
        if data is None:
            data = requests.get(url).json()
            self.cache.set(area_code, data)
        return data

    def __parse_weather(self, data: dict, area_code: str) -> str:
        """天気予報からメッセージを生成する
        Args:
            data (dict): 天気予報
            area_code (str): エリアコード
        """
        report_time = datetime.datetime.fromisoformat(
            data['reportDatetime']
        ).replace(tzinfo=None)
        url = (
            f'{self.endpoint}/forecast'
            f'/data/overview_forecast/{area_code}.json'
        )
        message = "\n".join([
            data['publishingOffice'],
            data['headlineText'],
            data['text'],
            "",
            report_time.strftime('%Y年%m月%d日%H時%M分 発表'),
            f"引用元: {url}",
            "",
            "全国の天気予報",
            f"{self.endpoint}/forecast/"
        ]).replace('\u3000', '')
        return message

    def get_weather(self, area_name: str = '東京都') -> str:
        """指定した地域の天気を取得する
        Args:
            area_name (str): 都道府県名
        """
        area_code = self.__get_area_code(area_name)
        if(area_code == ''):
            return self.error_message
        data = self.__request_weather(area_code)
        message = self.__parse_weather(data, area_code)
        return message


if __name__ == '__main__':
    cl = WeatherClient("https://www.jma.go.jp/bosai")
    print(cl.get_weather("石川県"))
