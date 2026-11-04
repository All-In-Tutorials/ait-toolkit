
from getpass import getpass


def request_test_credentials():
    """
    Request an authorized test voucher and password.

    Credentials are kept in memory only.
    They are not printed or saved to disk.
    """

    print("\n========== AUTHORIZED TEST ACCOUNT ==========")
    print("Enter the test credentials provided by the client.")
    print("These credentials will not be saved by this module.")
    print("=============================================")

    while True:
        voucher_code = getpass("Test voucher code: ").strip()

        if voucher_code:
            break

        print("Voucher code cannot be empty.")

    while True:
        password = getpass("Test account password: ")

        if password:
            break

        print("Password cannot be empty.")

    return {
        "username": voucher_code,
        "password": password,
    }


if __name__ == "__main__":
    credentials = request_test_credentials()

    print("\nCredential input successful.")
    print("Voucher code received.")
    print("Password received.")
    print("Credentials were not displayed.")
