import requests
from werkzeug.exceptions import BadRequest


class RequestSamples:
    BASE_URL = 'http://127.0.0.1:5000'

    def fill_up_db(self):
        self.base_request(url='/get_data')

    def get_cities(self, fake: bool = False):
        url = '/cities' if not fake else '/city'
        self.base_request(url=url)

    def get_mean(self, city: str, value_type: str, moving_mean: bool = False):
        url = '/mean' if not moving_mean else '/moving_mean'
        params = {'city': city,
                  'value_type': value_type}
        self.base_request(url=url, params=params)

    def get_records(self, city: str, start_dt: str, end_dt: str):
        params = {'city': city,
                  'start_dt': start_dt,
                  'end_dt': end_dt}
        self.base_request(url='/records', params=params)

    def base_request(self, url: str, params: dict = {}):
        try:
            response = requests.get(url=self.BASE_URL + url, params=params)
            if response.status_code == 404:
                raise BadRequest(f'Result - {response.status_code} - Page not found')
            result = response.json()['result']
            print(f'Result - {response.status_code} - {result}', end=' ')
        except BadRequest as exc:
            print(exc.description, end=' ')
        finally:
            print(f'--- on calling {url}')


if __name__ == '__main__':
    requests_sample = RequestSamples()

    requests_sample.fill_up_db()

    requests_sample.get_cities()
    # Next request will return 400 status code because this page doesn't exist
    requests_sample.get_cities(fake=True)

    requests_sample.get_mean(city='Lviv', value_type='clouds')
    requests_sample.get_mean(city='Kharkiv', value_type='humidity')

    requests_sample.get_mean(city='Lviv', value_type='clouds', moving_mean=True)
    requests_sample.get_mean(city='Kharkiv', value_type='humidity', moving_mean=True)

    requests_sample.get_records(city='Odessa', start_dt='16-12-2021', end_dt='18-12-2021')
    requests_sample.get_records(city='Kiev', start_dt='19-12-2021', end_dt='22-12-2021')
    # Next request will return 400 status code because end date is lower that start date
    requests_sample.get_records(city='Dnepr', start_dt='22-12-2021', end_dt='18-12-2021')
