# geolocation-api

Geolocation API using ipstack.com.

## Steps to run the app:
1. Provide an IPStack API key in *Docker compose* file - `IPSTACK_API_KEY` variable.
2. Run `setup.sh` script.

## Steps to run the tests:
1. Provide an IPStack API key in *tests/test_main.py* file - paste it instead of `provide_api_key`.
2. Create virtual environment and activate it.
3. Run `pip install -r requirements.txt`.
4. Run `pytest`.