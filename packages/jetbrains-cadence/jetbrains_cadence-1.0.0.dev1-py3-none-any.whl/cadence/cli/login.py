from http.server import SimpleHTTPRequestHandler
from pkgutil import get_data
from socketserver import TCPServer
from threading import Thread
from typing import override
from urllib.parse import urlparse, parse_qs, urlencode

import click
from click import Context
from keyring import set_password as keyring_set_password
# from pywinctl import getActiveWindow

from cadence.api.CadenceHTTPClient import CadenceHTTPClient
from cadence.api.exceptions import CadenceServerException


class _TokenAuthHandler(SimpleHTTPRequestHandler):
    def save_token_and_shutdown(self):
        parsed_url = urlparse(self.path)
        self.server.token = parse_qs(parsed_url.query).get('token', [None])[0]
        self.server.shutdown()

    @override
    def do_GET(self):
        try:
            self.send_response_only(200, "OK")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(get_data("cadence.resources", "login_success.html"))
            Thread(target=self.save_token_and_shutdown).start()
        except:
            self.send_error(500, "Error during login. Please try again or use --browserless option.")

    @override
    def log_message(self, format, *args):
        return


def _start_server(backend_url: str) -> str | None:
    with TCPServer(("", 0), _TokenAuthHandler) as httpd:
        port = httpd.server_address[1]
        params = urlencode({'redirect_url': f'http://localhost:{port}'})
        click.launch(f'{backend_url}/app/jettrain/auto_token.html?{params}')

        httpd.token = None

        httpd.serve_forever()

        return httpd.token


def get_browserless_prompt(server_url: str) -> str:
    return f"""Create yourself an API token.
Open {click.style(f'{server_url}/profile.html?item=accessTokens', fg='blue')} 
Go to <Profile Icon> | <Profile> | <Access Tokens>

Create a new access token with 'Permission scope' set to '<Same as current user>'.
"""


@click.command()
@click.pass_context
@click.option("--browserless", is_flag=True, default=False, help="Don't open browser")
def login(ctx: Context, browserless: bool):
    """Login to Cadence"""
    # cli_window = getActiveWindow()
    if not browserless:
        token = _start_server(ctx.obj["server_url"])
    else:
        click.echo(get_browserless_prompt(ctx.obj["server_url"]))
        token = None

    while True:
        if token is None:
            token = click.prompt("Enter your token", hide_input=True)

        client = CadenceHTTPClient(server_url=ctx.obj['server_url'], token=token)
        # cli_window.activate() # todo

        try:
            client.get_current_user()
        except CadenceServerException as e:
            if e.status == 401:
                click.secho("Invalid token", fg="red")
                token = None
                continue
            raise e

        click.secho("Login successful", fg="green")
        break

    keyring_set_password("cadence", "__token__", token)
    click.secho("Token saved to keyring", fg="green")


@click.command()
@click.pass_context
def user(ctx: Context):
    """Show current user"""
    client: CadenceHTTPClient = ctx.obj['client']
    user = client.get_current_user()
    click.echo(f"{user.name} ({user.username})")
