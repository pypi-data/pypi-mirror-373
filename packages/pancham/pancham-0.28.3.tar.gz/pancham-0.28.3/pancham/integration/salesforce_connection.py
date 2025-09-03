from simple_salesforce import Salesforce
import os

def get_connection() -> Salesforce:
    """
    Establishes a connection to a Salesforce instance using credentials stored
    in environment variables. The function retrieves the Salesforce username,
    password, and instance URL from the environment variables
    'PANCHAM_SF_USERNAME', 'PANCHAM_SF_PASSWORD', and
    'PANCHAM_SF_INSTANCE_URL', respectively.

    If the credentials are available, it initializes and returns a Salesforce
    client connection using these parameters.

    :returns: A Salesforce client connection object initialized with the
        specified username, password, and instance URL.
    :rtype: Salesforce
    """
    username = os.environ.get('PANCHAM_SF_USERNAME', None)
    password = os.environ.get('PANCHAM_SF_PASSWORD', None)
    url = os.environ.get('PANCHAM_SF_INSTANCE_URL', None)
    token = os.environ.get('PANCHAM_SF_TOKEN', None)
    domain = os.environ.get('PANCHAM_SF_DOMAIN', None)
    api_version = os.environ.get('PANCHAM_SF_API_VERSION', '59.0')

    return Salesforce(
        username=username,
        password=password,
        instance_url=url,
        security_token=token,
        domain=domain,
        version=api_version
    )