import base64
import sys
from typing import Callable, Any, Union
from urllib.parse import urljoin

import click

from ledgerwallet import __version__ as ledger_wallet_version
from ledgerwallet import utils
from stellar_sdk import (
    DecoratedSignature,
    Network,
    parse_transaction_envelope_from_xdr,
    Server,
    TransactionEnvelope,
    FeeBumpTransactionEnvelope,
    Keypair,
)
from stellar_sdk.xdr import HashIDPreimage
from stellar_sdk.exceptions import BaseRequestError
from stellar_sdk import __version__ as stellar_sdk_version
from strledger import __issue__
from strledger import __version__ as strledger_version
from strledger.core import (
    StrLedger,
    DEFAULT_KEYPAIR_INDEX,
    DeviceNotFoundException,
    BaseError,
)
from stellar_sdk.utils import sha256

DEFAULT_HORIZON_SERVER_URL = "https://horizon.stellar.org"
DEFAULT_NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
TESTNET_NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE


def echo_normal(message: str) -> None:
    click.echo(message)


def echo_success(message: str) -> None:
    click.echo(click.style(message, fg="green"))


def echo_error(message: Any) -> None:
    click.echo(click.style(message, fg="red"), err=True)


def parse_xdr(
    xdr: str, network_passphrase: str
) -> Union[TransactionEnvelope, FeeBumpTransactionEnvelope]:
    try:
        return parse_transaction_envelope_from_xdr(
            xdr=xdr, network_passphrase=network_passphrase
        )
    except Exception:
        echo_error(
            "Failed to parse XDR.\n"
            "Make sure to pass a valid base64-encoded transaction envelope.\n"
            "You can check whether the data you submitted is valid "
            "through XDR Viewer - https://laboratory.stellar.org/#xdr-viewer"
        )
        sys.exit(1)


def parse_soroban_auth(xdr: str) -> HashIDPreimage:
    try:
        return HashIDPreimage.from_xdr(xdr)
    except Exception:
        echo_error(
            "Failed to parse XDR.\n"
            "Make sure to pass a valid base64-encoded soroban authorization."
        )
        sys.exit(1)


def submit_transaction(
    te: Union[TransactionEnvelope, FeeBumpTransactionEnvelope], horizon_url: str
) -> None:
    echo_normal("Submitting to the network...")
    server = Server(horizon_url)
    try:
        server.submit_transaction(te)
    except BaseRequestError as e:
        echo_error("Submit failed, error info:")
        echo_error(e)
        sys.exit(1)

    echo_success("Successfully submitted.")
    tx_hash = te.hash_hex()
    if te.network_passphrase == Network.PUBLIC_NETWORK_PASSPHRASE:
        url = f"https://stellar.expert/explorer/public/tx/{tx_hash}"
    elif te.network_passphrase == Network.TESTNET_NETWORK_PASSPHRASE:
        url = f"https://stellar.expert/explorer/testnet/tx/{tx_hash}"
    else:
        url = urljoin(horizon_url, f"/transactions/{tx_hash}")
    echo_success(f"Stellar Explorer: {url}")


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Display exchanged APDU.")
@click.pass_context
def cli(ctx, verbose):
    """Stellar Ledger commands.

    This project is built on the basis of ledgerwallet,
    you can check ledgerwallet for more features.
    """
    if verbose:
        utils.enable_apdu_log()

    def get_client() -> StrLedger:
        try:
            return StrLedger()
        except DeviceNotFoundException:
            echo_error("No Ledger device has been found.")
            sys.exit(1)

    ctx.obj = get_client


@cli.command(name="app-info")
@click.pass_obj
def get_app_info(get_client: Callable[[], StrLedger]) -> None:
    """Get Stellar app configuration info."""
    client = get_client()
    data = client.get_app_info()
    echo_success(f"Stellar App Version: {data.version}")
    enabled = "Yes" if data.hash_signing_enabled else "No"
    echo_success(f"Hash Signing Enabled: {enabled}")
    if data.max_data_size is not None:
        echo_success(f"Max Data Size: {data.max_data_size} bytes")


@cli.command(name="sign-tx")
@click.option(
    "-n",
    "--network-passphrase",
    default=DEFAULT_NETWORK_PASSPHRASE,
    required=False,
    help="Network passphrase (blank for public network).",
)
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.option(
    "-a",
    "--hash-signing",
    is_flag=True,
    help="Only send the hash to the device for signing.",
)
@click.option("-s", "--submit", is_flag=True, help="Submit to Stellar Network.")
@click.option(
    "-u",
    "--horizon-url",
    type=str,
    required=False,
    help="Horizon Server URL.",
    default=DEFAULT_HORIZON_SERVER_URL,
    show_default=True,
)
@click.argument("transaction_envelope")
@click.pass_obj
def sign_transaction(
    get_client: Callable[[], StrLedger],
    network_passphrase: str,
    transaction_envelope: str,
    keypair_index: int,
    hash_signing: bool,
    submit: bool,
    horizon_url: str,
):
    """Sign a base64-encoded transaction envelope."""
    client = get_client()
    te = parse_xdr(transaction_envelope, network_passphrase)

    tx_hash = te.hash_hex()
    echo_normal(f"Network Passphrase: {network_passphrase}")
    echo_normal(f"Transaction Hash: {tx_hash}")
    echo_normal("Please confirm the transaction on Ledger.")

    try:
        if hash_signing:
            signature = client.sign_hash(tx_hash, keypair_index)
            keypair = client.get_keypair(keypair_index=keypair_index)
            decorated_signature = DecoratedSignature(
                keypair.signature_hint(), signature
            )
            te.signatures.append(decorated_signature)
        else:
            assert isinstance(te, (TransactionEnvelope, FeeBumpTransactionEnvelope))
            te = client.sign_transaction(
                transaction_envelope=te, keypair_index=keypair_index
            )
    except BaseError as e:
        echo_error(e)
        sys.exit(1)
    except Exception as e:
        echo_error(f"Unknown exception, you can report the problem here: {__issue__}")
        raise e
    echo_success("Signed successfully.")
    echo_success("Base64-encoded signed transaction envelope:")
    echo_success(te.to_xdr())

    if submit:
        submit_transaction(te, horizon_url)


@cli.command(name="sign-hash")
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.argument("hash")
@click.pass_obj
def sign_hash(get_client: Callable[[], StrLedger], hash: str, keypair_index: int):
    """Sign a hex encoded hash."""
    client = get_client()
    try:
        signature = client.sign_hash(hash, keypair_index)
    except BaseError as e:
        echo_error(e)
        sys.exit(1)
    except Exception as e:
        echo_error(f"Unknown exception, you can report the problem here: {__issue__}")
        raise e
    signature_base64 = base64.b64encode(signature).decode()
    echo_success(signature_base64)


@cli.command(name="get-address")
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.option("-c", "--confirm", is_flag=True, help="Confirm address on the device.")
@click.pass_obj
def get_address(
    get_client: Callable[[], StrLedger], keypair_index: int, confirm: bool
) -> None:
    """Get Stellar public address."""
    client = get_client()
    try:
        keypair = client.get_keypair(keypair_index, confirm)
    except BaseError as e:
        echo_error(e)
        sys.exit(1)
    except Exception as e:
        echo_error(f"Unknown exception, you can report the problem here: {__issue__}")
        raise e
    echo_success(keypair.public_key)


@cli.command(name="sign-auth")
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.option(
    "-a",
    "--hash-signing",
    is_flag=True,
    help="Only send the hash to the device for signing.",
)
@click.argument("soroban_authorization")
@click.pass_obj
def sign_soroban_authorization(
    get_client: Callable[[], StrLedger],
    keypair_index: int,
    hash_signing: bool,
    soroban_authorization: str,
):
    """Sign a base64-encoded soroban authorization (HashIDPreimage)."""
    client = get_client()
    auth = parse_soroban_auth(soroban_authorization)

    preimage_hash = sha256(auth.to_xdr_bytes()).hex()
    echo_normal(f"HashIDPreimage Hash: {preimage_hash}")
    echo_normal("Please confirm the Soroban authorization on Ledger.")

    try:
        if hash_signing:
            signature = client.sign_hash(preimage_hash, keypair_index)
        else:
            signature = client.sign_soroban_authorization(
                auth, keypair_index=keypair_index
            )
    except BaseError as e:
        echo_error(e)
        sys.exit(1)
    except Exception as e:
        echo_error(f"Unknown exception, you can report the problem here: {__issue__}")
        raise e

    echo_success("Signed successfully.")
    echo_success("Base64-encoded signature:")
    echo_success(base64.b64encode(signature).decode())


@cli.command(name="sign-message")
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.option(
    "-a",
    "--hash-signing",
    is_flag=True,
    help="Only send the hash to the device for signing.",
)
@click.argument("message")
@click.pass_obj
def sign_message(
    get_client: Callable[[], StrLedger],
    keypair_index: int,
    hash_signing: bool,
    message: str,
):
    """Sign a base64-encoded message."""
    client = get_client()
    echo_normal("Please confirm the message on Ledger.")

    message_bytes = base64.b64decode(message)

    try:
        if hash_signing:
            message_hash = Keypair._calculate_message_hash(message_bytes)
            signature = client.sign_hash(message_hash, keypair_index)
        else:
            signature = client.sign_message(message_bytes, keypair_index)
    except BaseError as e:
        echo_error(e)
        sys.exit(1)
    except Exception as e:
        echo_error(f"Unknown exception, you can report the problem here: {__issue__}")
        raise e

    echo_success("Signed successfully.")
    echo_success("Base64-encoded signature:")
    echo_success(base64.b64encode(signature).decode())


@cli.command(name="version")
def version() -> None:
    """Get strledger version info."""
    echo_success(f"StrLedger Version: {strledger_version}")
    echo_success(f"Ledger Wallet Version: {ledger_wallet_version}")
    echo_success(f"Stellar SDK Version: {stellar_sdk_version}")


if __name__ == "__main__":
    cli()
