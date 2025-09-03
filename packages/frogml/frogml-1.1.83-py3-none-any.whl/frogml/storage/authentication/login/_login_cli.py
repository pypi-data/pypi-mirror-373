from typing import List, Optional, Union

from frogml.storage.authentication.login._login_command import run as run_login
from frogml.storage.authentication.models import LoginArguments
from frogml.storage.authentication.utils import (
    get_frogml_configuration,
    parse_cli_config_server,
    read_jfrog_cli_config,
    get_list_of_servers_from_config,
    is_login_without_params,
    login_input_checks,
)
from frogml.storage.constants import CONFIG_FILE_PATH, JFROG_CLI_CONFIG_FILE_PATH
from frogml.storage.utils import assemble_artifact_url, join_url


def login(
    url: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    anonymous: Optional[bool],
    is_interactive: Optional[bool],
    server_id: Optional[str],
) -> bool:
    if anonymous is None:
        anonymous = False
    if is_login_without_params(url, username, password, token, anonymous):
        if not is_interactive:
            return __login_by_frogml_configuration_file_flow()
        else:
            return __interactive_flow()
    elif login_input_checks(url, username, password, token, anonymous):
        url = assemble_artifact_url(url)
        return __login_by_command_line_params(
            url, username, password, token, anonymous, server_id
        )
    else:
        print(
            f"{__get_failed_reason(url, username, password, token, anonymous)}Login failed"
        )
        return False


def __get_failed_reason(
    url: Optional[str],
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    anonymous: Optional[bool],
) -> str:
    details = ""
    if url is None:
        details += "Url is required.\n"
    if token is not None and (
        any(params is not None for params in [username, password])
    ):
        details += "Token is specified when username/password is specified.\n"
    if anonymous is True and any(
        params is not None for params in [username, password, token]
    ):
        details += "Anonymous is specified with authentication details.\n"
    if username is None and password is not None:
        details += "Username is required when password is specified.\n"
    elif username is not None and password is None:
        details += "Password is required when username is specified.\n"
    return details


def __run_interactive_mode() -> Union[LoginArguments, None]:
    jfrog_cli_config = read_jfrog_cli_config()

    if jfrog_cli_config is not None:
        jfrog_cli_servers = get_list_of_servers_from_config(jfrog_cli_config)
        if jfrog_cli_servers is not None and len(jfrog_cli_servers) > 0:
            login_method_id = input(
                f"Please select from the following options:\n"  # nosec B608
                f"1.Login by jfrog-cli configuration file: {JFROG_CLI_CONFIG_FILE_PATH}\n"
                f"2.Connecting to a new server\n"
            )

            while (
                not login_method_id.isdigit()
                or int(login_method_id) > 2
                or int(login_method_id) <= 0
            ):
                login_method_id = input("Bad Input. Choose your preferred login option")

            login_method_id = int(login_method_id)
            if login_method_id == 1:
                return __prompt_jfrog_cli_configuration_list(
                    jfrog_cli_config, jfrog_cli_servers
                )

        return __prompt_manual_details()

    return None


def __prompt_manual_details() -> Union[LoginArguments, None]:
    login_args = LoginArguments()
    login_args.server_id = input("Enter server ID: ")
    login_args.artifactory_url = input("Enter artifactory base url")

    if login_args.artifactory_url is not None:
        login_args.artifactory_url = join_url(login_args.artifactory_url, "artifactory")

    auth_options = ["Username and Password", "Access Token", "Anonymous Access"]
    authentication_types = ""
    for index, item in enumerate(auth_options):
        authentication_types += f"{index}: {item} \n"
    selected_auth_type = input(
        f"Choose your preferred authentication option:\n{authentication_types}"
    )
    while (
        not selected_auth_type.isdigit()
        or int(selected_auth_type) >= len(auth_options)
        or int(selected_auth_type) < 0
    ):
        selected_auth_type = input("Bad Input. Choose your preferred authentication")
    selected_auth_type = int(selected_auth_type)
    if selected_auth_type == 0:
        return __prompt_username_password(login_args)
    elif selected_auth_type == 1:
        return __prompt_access_token(login_args)
    elif selected_auth_type == 2:
        login_args.isAnonymous = True
        return login_args
    return None


def __prompt_username_password(login_args: LoginArguments) -> LoginArguments:
    username = input("Enter JFrog user name")
    password = input("Enter JFrog password")
    login_args.username = username
    login_args.password = password
    return login_args


def __prompt_access_token(login_args: LoginArguments) -> LoginArguments:
    token = input("Enter JFrog access token")
    login_args.access_token = token
    return login_args


def __prompt_jfrog_cli_configuration_list(
    jfrog_cli_config: dict, jfrog_cli_servers: List[str]
) -> Union[LoginArguments, None]:
    list_server_options = ""
    for index, item in enumerate(jfrog_cli_servers):
        list_server_options += f"{index}: {item}\n"
    server_index_cli_conf = input(
        f"Found the following servers in your JFrog CLI configuration, "
        f"choose one of the following:\n{list_server_options}"
    )
    while (
        not server_index_cli_conf.isdigit()
        or int(server_index_cli_conf) < 0
        or int(server_index_cli_conf) >= len(jfrog_cli_servers)
    ):
        server_index_cli_conf = input(
            "Invalid choice. Please choose a number from the list"
        )
    server_index_cli_conf = int(server_index_cli_conf)
    print(f"{jfrog_cli_servers[server_index_cli_conf]} was chosen")
    servers = jfrog_cli_config.get("servers")
    if servers is not None:
        return parse_cli_config_server(servers[server_index_cli_conf])
    else:
        raise ValueError("No servers found in the JFrog CLI configuration.")


def __execute_login(login_args: LoginArguments) -> bool:
    if run_login(login_args, login_args.isAnonymous):
        success_message = "Logged in successfully"
        if login_args.artifactory_url is not None:
            success_message += (
                f" to: {login_args.artifactory_url.replace('/artifactory', '')}"
            )
        print(success_message)
        return True
    else:
        print("Failed to login, bad authentication")
        return False


def __login_by_frogml_configuration_file_flow() -> bool:
    login_args: LoginArguments = get_frogml_configuration()
    if login_args is not None:
        print(f"Using existing frogml authentication config file: {CONFIG_FILE_PATH}")
        if __execute_login(login_args):
            return True

    return __interactive_flow()


def __interactive_flow() -> bool:
    login_args = __run_interactive_mode()
    if login_args is not None:
        return __execute_login(login_args)
    return False


def __login_by_command_line_params(
    url: str,
    username: Optional[str],
    password: Optional[str],
    token: Optional[str],
    anonymous: Optional[bool],
    server_id: Optional[str],
) -> bool:
    anonymous_value = anonymous if anonymous is not None else False
    login_args = LoginArguments()
    login_args.artifactory_url = url
    login_args.username = username
    login_args.password = password
    login_args.access_token = token
    login_args.isAnonymous = anonymous_value
    login_args.server_id = server_id
    return __execute_login(login_args)
