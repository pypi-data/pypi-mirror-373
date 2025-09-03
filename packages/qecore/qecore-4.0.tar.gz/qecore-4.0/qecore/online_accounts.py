#!/usr/bin/env python3
"""
This file provides online accounts functions.
"""

# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel
# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=no-name-in-module
# ruff: noqa: E501
# ruff: noqa: E402

import os
import sys
import traceback
from time import sleep
import yaml

from behave import step

from qecore.utility import AUTOMATIC_LOGIN_IN_EFFECT
try:
    from dogtail.rawinput import pressKey, typeText

except Exception as error:
    if not AUTOMATIC_LOGIN_IN_EFFECT:
        print(f"Expected issues in Online Accounts: '{error}'")
    else:
        raise Exception from error

from qecore.utility import get_application, RunAndLog

#####################################################################################
# As we cannot have online accounts yaml data in, you have to provide them yourself #
#####################################################################################

#####################################################################################
#  !!!  Most of this is no longer usable in the original way it was made for.  !!!  #
#####################################################################################


class Accounts:
    """
    With this class all accounts are added and removed.
    """

    def __init__(self, context) -> None:
        """
        Initiate Accounts instance.

        :type context: <behave.runner.Context>
        :param context: Context object.
        """

        self.context = context
        self.account_data = None

        try:
            # If it is defined in environment.
            self.application = get_application(context, "gnome-control-center")
        except Exception:  # pylint: disable=broad-except
            # If it is not defined in environment.
            self.application = context.sandbox.get_application(
                name="gnome-control-center", desktop_file_name="gnome-control-center"
            )

    def remove_all_accounts(self) -> None:
        """
        Remove all accounts added via gnome-online-accounts.
        """

        self.context.sandbox._detect_keyring()  # pylint: disable=protected-access
        self.application.start_via_command("gnome-control-center online-accounts")

        target = self.application.instance.child("Connect to your data in the cloud")
        target_panel = target.parent.findChildren(lambda x: x.roleName == "panel")[0]
        existing_accounts = [
            x for x in target_panel.findChildren(lambda x: x.roleName == "label")
        ]

        for account in existing_accounts:
            account.click()
            self.application.instance.child("Remove Account").click()

        self.application.close_via_shortcut()

    def remove_account(self, account_name) -> None:
        """
        Remove single account added via gnome-online-accounts.

        :type account_name: string
        :param account_name: Name of the account.
        """

        self.context.sandbox._detect_keyring()  # pylint: disable=protected-access
        self.application.start_via_command("gnome-control-center online-accounts")

        target = self.application.instance.child("Connect to your data in the cloud")
        target_panel = target.parent.findChildren(lambda x: x.roleName == "panel")[0]
        existing_accounts = {
            x.name: x
            for x in target_panel.findChildren(lambda x: x.roleName == "label")
        }
        try:
            existing_accounts[account_name].click()
            self.application.instance.child("Remove Account").click()
        except Exception as error:  # pylint: disable=broad-except
            print(f"\nAccount '{error}' was not detected or was already removed.\n")

        self.application.close_via_shortcut()

    def account_exists(self, account_name) -> bool:
        """
        Found out if there is an account added via gnome-online-accounts.

        :type account_name: string
        :param account_name: Name of the account.

        :rtype: bool
        :return: Does the account exist or not.
        """

        target = self.application.instance.child("Connect to your data in the cloud")
        target_panel = target.parent.findChildren(lambda x: x.roleName == "panel")[0]
        existing_accounts = [
            x.name for x in target_panel.findChildren(lambda x: x.roleName == "label")
        ]
        result = False
        for account in existing_accounts:
            if account_name in account:
                result = True
        return result

    def add_account(
        self, account_id, login=None, password=None, server=None, yaml_file=None
    ) -> None:
        """
        Add account to the gnome-online-accounts.

        :type account_id: string
        :param account_id: Identification fo the account.

        :type login: string
        :param login: Login name of the account user.

        :type password: string
        :param password: Password for the login.

        :type server: string
        :param server: Server.

        :type yaml_file: string
        :param yaml_file: Location of yaml file.
        """

        self.context.sandbox._detect_keyring()  # pylint: disable=protected-access
        self.account_data = AccountData(
            account_id,
            login=login,
            password=password,
            server=server,
            yaml_file=yaml_file,
        )
        account_name = self.account_data.name

        self.application.start_via_command("gnome-control-center online-accounts")

        target = self.application.instance.child("Connect to your data in the cloud")
        target_panel = target.parent.findChildren(lambda x: x.roleName == "panel")[1]
        accounts_to_be_added = {
            x.name: x
            for x in target_panel.findChildren(lambda x: x.roleName == "label")
        }
        accounts_to_be_added[account_name].click()

        account_login_dialog = self.application.instance.child(
            f"{account_name} Account", "dialog"
        )

        if account_name == "Google":
            add_google_account(self.context, self.account_data, account_login_dialog)

        if account_name == "Nextcloud":
            add_nextcloud_account(self.context, self.account_data, account_login_dialog)

        if account_name == "Facebook":
            add_facebook_account(self.context, self.account_data, account_login_dialog)

        if account_name == "Microsoft":
            add_microsoft_account(self.context, self.account_data, account_login_dialog)

        if account_name == "Flickr":
            add_flickr_account(self.context, self.account_data, account_login_dialog)

        if account_name == "Pocket":
            add_pocket_account(self.context, self.account_data, account_login_dialog)

        if account_name == "Foursquare":
            add_foursquare_account(
                self.context, self.account_data, account_login_dialog
            )

        if account_name == "Microsoft Exchange":
            add_microsoft_exchange_account(
                self.context, self.account_data, account_login_dialog
            )

        sleep(1)
        pressKey("Esc")
        assert self.account_exists(
            account_name
        ), f"Account '{account_name}' was not detected.\n"


class AccountData:
    """
    With this class we keep and get all data about accounts.
    """

    def __init__(
        self,
        account_id,
        login=None,
        password=None,
        server=None,
        yaml_data=None,
        yaml_file=None,
    ) -> None:
        """
        Account class.

        :type account_id: string
        :param account_id: Identification fo the account.

        :type login: string
        :param login: Login name of the account user.

        :type password: string
        :param password: Password for the login.

        :type server: string
        :param server: Server.

        :type yaml_file: string
        :param yaml_file: Location of yaml file.

        .. note::

            This class is called by :func:`online_accounts.Accounts.add_account`.
        """

        self.account_id = account_id

        self.name = account_id
        self.login = login
        self.password = password
        self.server = server

        self.yaml_data = yaml_data
        self.yaml_file = yaml_file

        if self.yaml_data:
            self.parse_account_data()

        elif self.yaml_file:
            self.get_account_data(self.yaml_file)
            self.parse_account_data()

        elif not (self.login and self.password):
            self.get_account_data()
            self.parse_account_data()

    def get_account_data(self, yaml_file="online_accounts.yaml") -> None:
        """
        Load yaml data to the class attribute.

        :type yaml_file: string
        :param yaml_file: Location of the yaml file.
        """

        assert os.path.isfile(yaml_file), "\n".join(
            (
                "\n\nFor online accounts you need to supply the credentials in yaml format.",
                "Expecting file 'online_accounts.yaml' in your project directory.",
                "If not found you have to provide the file yourself and use step-decorator as:.",
                '\'Add "{account_name}" account from file "{yaml_file}"\'\n',
            )
        )

        with open(yaml_file, "rb") as data:
            try:
                self.yaml_data = yaml.safe_load(data)
            except yaml.YAMLError:
                traceback.print_exc(file=sys.stdout)
                assert False, " ".join(
                    (
                        "Parsing YAML file was not successful.",
                        "Please check format of accounts.yaml file",
                    )
                )

    def parse_account_data(self) -> None:
        """
        Parse the data from the yaml data.
        Retrieves name, login, password, server.
        """

        try:
            self.name = self.yaml_data[self.account_id]["name"]
        except KeyError as error:
            raise KeyError(
                f"Name for account '{self.account_id}' is expected, but was not provided."
            ) from error

        try:
            self.login = self.yaml_data[self.account_id]["login"]
        except KeyError as error:
            raise KeyError(
                f"Login for account '{self.account_id}' is expected, but was not provided."
            ) from error

        try:
            self.password = self.yaml_data[self.account_id]["password"]
        except KeyError as error:
            raise KeyError(
                f"Password for account '{self.account_id}' is expected, but was not provided."
            ) from error

        try:
            self.server = self.yaml_data[self.account_id]["server"]
        except KeyError as error:
            if self.name in ("Nextcloud", "Microsoft Exchange"):
                raise KeyError(
                    f"Server for account '{self.account_id}' is expected, but was not provided."
                ) from error


def wait_until_progress_bar_disappears_in(account_login_dialog) -> None:
    """
    Waiting until the progress bar from the gnome-online-accounts widget disappears.

    :type account_login_dialog: Node
    :param account_login_dialog: Node in which the progress bar is being searched in.
    """

    progress_bar = account_login_dialog.findChildren(
        lambda x: x.roleName == "progress bar"
    )
    while progress_bar and progress_bar[0].showing:
        sleep(0.2)


def add_google_account(context, data, account_login_dialog) -> None:
    """
    Adding a Google account to the gnome-online-accounts.

    :type context: <behave.runner.Context>
    :param context: Context object.

    :type data: AccountData
    :param data: Data needed: account_id, login, password, server.

    :type account_login_dialog: Node
    :param account_login_dialog: gnome-online-accounts dialog for given account.
    """

    wait_until_progress_bar_disappears_in(account_login_dialog)
    email_entry = account_login_dialog.child(roleName="entry")
    email_entry.click()
    sleep(2)
    typeText(data.login)
    pressKey("Enter")

    wait_until_progress_bar_disappears_in(account_login_dialog)
    password_entry = account_login_dialog.child(roleName="password text")
    password_entry.click()
    sleep(2)
    typeText(data.password)
    pressKey("Enter")

    wait_until_progress_bar_disappears_in(account_login_dialog)
    allow_button = account_login_dialog.child("Allow", "push button")
    while not allow_button.sensitive:
        sleep(0.2)

    pressKey("End")

    for _ in range(5):
        sleep(1)
        if not account_login_dialog.child("Allow", retry=False).showing:
            pressKey("End")
        else:
            break

    allow_button.click()

    try:
        for _ in range(10):
            if account_login_dialog.child("Allow", retry=False).showing:
                sleep(1)
    except Exception:  # pylint: disable=broad-except
        pass

    context.sandbox._detect_keyring()  # pylint: disable=protected-access


def add_nextcloud_account(context, data, account_login_dialog) -> None:
    """
    Adding a Nextcloud account to the gnome-online-accounts.

    :type context: <behave.runner.Context>
    :param context: Context object.

    :type data: AccountData
    :param data: Data needed: account_id, login, password, server.

    :type account_login_dialog: Node
    :param account_login_dialog: gnome-online-accounts dialog for given account.
    """

    server_entry = account_login_dialog.findChildren(lambda x: x.roleName == "text")[1]
    server_entry.text = data.server

    username_entry = account_login_dialog.findChildren(lambda x: x.roleName == "text")[
        0
    ]
    username_entry.text = data.login

    password_entry = account_login_dialog.findChildren(
        lambda x: x.roleName == "password text"
    )[0]
    password_entry.text = data.password

    account_login_dialog.child("Connect").click()

    try:
        account_login_dialog.child("Ignore").click()
    except Exception:  # pylint: disable=broad-except
        pass

    context.sandbox._detect_keyring()  # pylint: disable=protected-access


def add_facebook_account(context, data, account_login_dialog) -> None:
    """
    Adding a Facebook account to the gnome-online-accounts.

    :type context: <behave.runner.Context>
    :param context: Context object.

    :type data: AccountData
    :param data: Data needed: account_id, login, password, server.

    :type account_login_dialog: Node
    :param account_login_dialog: gnome-online-accounts dialog for given account.
    """

    print("Currently missing from gnome-online-accounts - therefore unsupported.")

    wait_until_progress_bar_disappears_in(account_login_dialog)
    email_entry = account_login_dialog.child(roleName="entry")
    email_entry.click()
    email_entry.text = data.login

    password_entry = account_login_dialog.child(roleName="password text")
    password_entry.click()
    password_entry.text = data.password
    pressKey("Enter")

    wait_until_progress_bar_disappears_in(account_login_dialog)
    continue_button = account_login_dialog.findChild(
        lambda x: "Continue as" in x.name or x.name == "OK"
    )
    continue_button.click()

    context.sandbox._detect_keyring()  # pylint: disable=protected-access


def add_microsoft_account(context, data, account_login_dialog) -> None:
    """
    Adding a Microsoft account to the gnome-online-accounts.

    :type context: <behave.runner.Context>
    :param context: Context object.

    :type data: AccountData
    :param data: Data needed: account_id, login, password, server.

    :type account_login_dialog: Node
    :param account_login_dialog: gnome-online-accounts dialog for given account.
    """

    wait_until_progress_bar_disappears_in(account_login_dialog)
    email_entry = account_login_dialog.child(roleName="entry")
    email_entry.click()
    sleep(2)
    typeText(data.login)

    next_button = account_login_dialog.child("Next")
    next_button.click()

    wait_until_progress_bar_disappears_in(account_login_dialog)
    password_entry = account_login_dialog.child(roleName="password text")
    password_entry.click()
    sleep(2)
    typeText(data.password)

    sign_in = account_login_dialog.child("Sign in")
    sign_in.click()

    context.sandbox._detect_keyring()  # pylint: disable=protected-access


def add_flickr_account(context, data, account_login_dialog) -> None:
    """
    Adding a Flickr account to the gnome-online-accounts.

    :type context: <behave.runner.Context>
    :param context: Context object.

    :type data: AccountData
    :param data: Data needed: account_id, login, password, server.

    :type account_login_dialog: Node
    :param account_login_dialog: gnome-online-accounts dialog for given account.
    """

    print("Currently missing from gnome-online-accounts - therefore unsupported.")

    wait_until_progress_bar_disappears_in(account_login_dialog)
    email_entry = account_login_dialog.child(roleName="entry")
    email_entry.click()
    email_entry.text = data.login

    next_button = account_login_dialog.child("Next")
    next_button.click()

    try:
        wait_until_progress_bar_disappears_in(account_login_dialog)
        next_button = account_login_dialog.child("Next", retry=False)
        next_button.click()
    except Exception:  # pylint: disable=broad-except
        pass

    wait_until_progress_bar_disappears_in(account_login_dialog)
    password_entry = account_login_dialog.child(roleName="password text")
    password_entry.click()
    typeText(data.password)

    sleep(5)
    pressKey("Enter")

    authorize_button = account_login_dialog.child("OK, I'LL AUTHORIZE IT")
    while not authorize_button.sensitive:
        sleep(0.2)
    pressKey("PageDown")
    authorize_button.click()

    context.sandbox._detect_keyring()  # pylint: disable=protected-access


def add_pocket_account(context, data, account_login_dialog) -> None:
    """
    Adding a Pocket account to the gnome-online-accounts.

    :type context: <behave.runner.Context>
    :param context: Context object.

    :type data: AccountData
    :param data: Data needed: account_id, login, password, server.

    :type account_login_dialog: Node
    :param account_login_dialog: gnome-online-accounts dialog for given account.
    """

    print("Currently missing from gnome-online-accounts - therefore unsupported.")

    wait_until_progress_bar_disappears_in(account_login_dialog)
    pressKey("PageDown")
    pressKey("PageDown")
    pressKey("PageDown")

    login_with_firefox_button = account_login_dialog.child("Continue with Firefox")
    login_with_firefox_button.click()

    wait_until_progress_bar_disappears_in(account_login_dialog)
    try:
        assert account_login_dialog.findChild(
            lambda x: x.roleName == "paragraph"
            and x.text == "desktopqe.pocket@gmail.com",
            retry=False,
        )
        pressKey("PageDown")
    except Exception:  # pylint: disable=broad-except
        email_entry = account_login_dialog.child("Email", "entry")
        while not email_entry.sensitive:
            sleep(0.2)
        email_entry.click()
        email_entry.text = data.login
        account_login_dialog.child("Continue").click()

    password_entry = account_login_dialog.child(roleName="password text")
    password_entry.click()
    password_entry.text = data.password

    sign_in = account_login_dialog.child("Sign in")
    sign_in.click()

    try:
        found_node = account_login_dialog.child("Accept")
        while found_node and not found_node.sensitive:
            sleep(0.2)
            break
        sleep(1)
        found_node.click()
    except Exception:  # pylint: disable=broad-except
        pass

    try:
        found_node = account_login_dialog.child("Authorize")
        while found_node and not found_node.sensitive:
            sleep(0.2)
            break
        sleep(1)
        found_node.click()
    except Exception:  # pylint: disable=broad-except
        pass

    context.sandbox._detect_keyring()  # pylint: disable=protected-access


def add_foursquare_account(context, data, account_login_dialog) -> None:
    """
    Adding a FourSquare account to the gnome-online-accounts.

    :type context: <behave.runner.Context>
    :param context: Context object.

    :type data: AccountData
    :param data: Data needed: account_id, login, password, server.

    :type account_login_dialog: Node
    :param account_login_dialog: gnome-online-accounts dialog for given account.
    """

    print("Currently missing from gnome-online-accounts - therefore unsupported.")

    wait_until_progress_bar_disappears_in(account_login_dialog)
    email_entry = account_login_dialog.child(roleName="entry")
    email_entry.click()
    email_entry.text = data.login

    password_entry = account_login_dialog.child(roleName="password text")
    password_entry.click()
    password_entry.text = data.password

    pressKey("PageDown")

    log_in_and_allow_button = account_login_dialog.child("Log in and allow")
    log_in_and_allow_button.click()

    context.sandbox._detect_keyring()  # pylint: disable=protected-access


def add_microsoft_exchange_account(context, data, account_login_dialog) -> None:
    """
    Adding a Microsoft Exchange account to the gnome-online-accounts.

    :type context: <behave.runner.Context>
    :param context: Context object.

    :type data: AccountData
    :param data: Data needed: account_id, login, password, server.

    :type account_login_dialog: Node
    :param account_login_dialog: gnome-online-accounts dialog for given account.
    """

    RunAndLog("sudo sed -i 's/DEFAULT/LEGACY/g' /etc/crypto-policies/config")
    RunAndLog("sudo update-crypto-policies")

    wait_until_progress_bar_disappears_in(account_login_dialog)
    email_entry = account_login_dialog.findChildren(lambda x: x.roleName == "text")[2]
    email_entry.click()
    email_entry.text = data.login

    password_entry = account_login_dialog.findChildren(
        lambda x: x.roleName == "password text"
    )[0]
    password_entry.click()
    password_entry.text = data.password

    custom_button = account_login_dialog.child("Custom")
    custom_button.doActionNamed("activate")

    server_entry = account_login_dialog.findChildren(lambda x: x.roleName == "text")[0]
    server_entry.click()
    server_entry.text = data.server

    account_login_dialog.child("Connect").click()

    ignore_button = account_login_dialog.findChild(lambda x: x.name == "Ignore")
    while not ignore_button.sensitive:
        sleep(0.2)
    ignore_button.click()

    context.sandbox._detect_keyring()  # pylint: disable=protected-access


@step('Add "{account_name}" account')
@step('Add "{account_name}" account from file "{yaml_file}"')
@step('Add "{account_name}" account with login "{login}" and password "{password}"')
def add_account(
    context, account_name, login=None, password=None, yaml_file=None
) -> None:
    """
    Function with behave step decorators::

        Add "{account_name}" account
        Add "{account_name}" account from file "{yaml_file}"
        Add "{account_name}" account with login "{login}" and password "{password}"
    """

    accounts = Accounts(context)
    try:
        accounts.add_account(
            account_name, login=login, password=password, yaml_file=yaml_file
        )
    except KeyError as error:
        raise KeyError(error) from error
    except Exception:  # pylint: disable=broad-except
        RunAndLog(f"rm -rf {os.path.expanduser('~')}/.local/share/webkitgtk/*")
        accounts.add_account(
            account_name, login=login, password=password, yaml_file=yaml_file
        )


@step("Remove all accounts")
def remove_accounts(context) -> None:
    """
    Function with behave step decorator::

        Remove all accounts
    """

    accounts = Accounts(context)
    try:
        accounts.remove_all_accounts()
    except Exception:  # pylint: disable=broad-except
        accounts.remove_all_accounts()
