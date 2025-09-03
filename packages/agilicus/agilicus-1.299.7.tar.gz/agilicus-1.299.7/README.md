## Agilicus SDK (Python)


The [Agilicus Platform](https://www.agilicus.com/) [API](https://www.agilicus.com/api).
is defined using [OpenAPI 3.0](https://github.com/OAI/OpenAPI-Specification),
and may be used from any language. This allows configuration of our Zero-Trust Network Access cloud native platform
using REST. You can see the API specification [online](https://www.agilicus.com/api).

This package provides a Python SDK, class library interfaces for use in
accessing individual collections. In addition it provides a command-line-interface (CLI)
for interactive use.

Read the class-library documentation [online](https://www.agilicus.com/api/)

[Samples](https://git.agilicus.com/pub/samples) shows various examples of this code in use.

Generally you may install this from [pypi](https://pypi.org/project/agilicus/) as:

```
pip install --upgrade agilicus
```

You may wish to add bash completion by adding this to your ~/.bashrc:

```
eval "$(_AGILICUS_CLI_COMPLETE=source agilicus-cli)"
```

## Example: List users
The below python code will show the same output as the CLI command:
`agilicus-cli --issuer https://auth.dbt.agilicus.cloud list-users`

```
import agilicus
import argparse
import sys

scopes = agilicus.scopes.DEFAULT_SCOPES

parser = argparse.ArgumentParser(description="update-user")
parser.add_argument("--auth-doc", type=str)
parser.add_argument("--issuer", type=str)
parser.add_argument("--email", type=str)
parser.add_argument("--disable-user", type=bool, default=None)
args = parser.parse_args()

if not args.auth_doc and not args.issuer:
    print("error: specify either an --auth-doc or --issuer")
    sys.exit(1)

if not args.email:
    print("error: specify an email to search for a user")
    sys.exit(1)

api = agilicus.GetClient(
    agilicus_scopes=scopes, issuer=args.issuer, authentication_document=args.auth_doc
)

users = api.users.list_users(org_id=api.default_org_id, email=args.email)
if len(users.users) != 1:
    print(f"error: failed to find user with email: {args.email}")
    sys.exit(1)

user = users.users[0]

if args.disable_user is not None:
    user.enabled = args.disable_user

result = api.users.replace_user(
    user.id, user=user, _check_input_type=False, _host_index=0
)
print(result)
```
