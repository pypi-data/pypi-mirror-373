# Pytest Clerk

This is a collection of fixtures we've been using to perform integration tests using
the real Clerk APIs.

Usage of any of these fixture requires that the following be specified in environment
variables or a .env file:

* CLERK_SECRET_KEY: Set this to the value of your Clerk secret key. Conflicts with
                    CLERK_SECRET_ID.
* CLERK_SECRET_ID: Set this to the ID of the AWS SecretsManager Secret that contains the
                   Clerk secret key. This requires installing the `aws` extra. Conflicts
                   with CLERK_SECRET_KEY.

The fixtures themselves are heavily documented so please view their docstrings for more
information on their usage.
