# MCHost24 Certbot DNS Authentication Plugin

A plugin for certbot that enables performing DNS validation using the MCHost24 API.

## Usage

1. Obtain an MCHost24 API token (e.g. using the cli tool of the `mchost24` module found [here](https://github.com/JoeJoeTV/mchost24-api-python))
2. Install the plugin
3. Create a `mchost24.ini` config file that contains the `mchost24_dns_api_token` key with the value set to the previously obtained API token:
    ```ini
    # MCHost24 API token
    mchost24_dns_api_token=<insert obtained API token here>
    ```
4. Run `certbot` and tell it to use the plugin to perform dns authentication and the config file:
    ```sh
    certbot certonly --authenticator dns-mchost24 --dns-mchost24-credentials /etc/letsencrypt/mchost24/mchost24.ini -d domain.com
    ```

## Requirements

Requires the MCHost24 API python module, which can be found [here](https://github.com/JoeJoeTV/mchost24-api-python).