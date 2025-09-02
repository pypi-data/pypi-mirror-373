# ag_draftking_utils

## get_selenium_driver
Modes:
- local: localhost
- cloud: uses AWS Device Farm
- proxy_local: uses localhost but using a proxy 

## DB - Usage

Make sure to set environmental variables for DK_DB_HOST and DK_DB_PASSWORD.

```python
from ag_draftking_utils.db_helper import create_connection 
from ag_draftking_utils.util import get_current_chicago_time, time_function, run_query_from_file 

@time_function
def main():
    conn = create_connection()
    df = run_query_from_file("sql_script.sql", conn)
    df['SCRAPE_TIME'] = get_current_chicago_time()
```