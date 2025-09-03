## KYWY is the official KAWA Python client

This project allows to connect to a KAWA instance to perform various data analytics tasks:

- Uploading data to a data warehouse
- Performing computations on the data warehouse managed by Kawa
- Managing advanced administration settings for KAWA administrators

Please visit our website for additional information and contact: https://www.kawa.ai

## Usage
The full documentation can be found here: https://github.com/kawa-analytics/kywy-documentation

## Dev setup
Make sure to create a .env file at the root of the project with the following content:

```
# Connection to KAWA configuration
# (Used for the scripts in the cloud directory)
KAWA_URL=http://127.0.0.1:8080
KAWA_API_KEY=****
KAWA_WORKSPACE=1

# E2E test configuration
# (Used to run the E2E tests)
E2E_KAWA_URL=http://127.0.0.1:8080
E2E_KAWA_API_KEY_USER_1=****
E2E_KAWA_API_KEY_USER_2=***
E2E_KAWA_WORKSPACE=1
```





