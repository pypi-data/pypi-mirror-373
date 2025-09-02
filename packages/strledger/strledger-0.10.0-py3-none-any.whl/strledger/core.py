import binascii
import copy
import dataclasses
from enum import IntEnum
from typing import Optional, Union

from ledgerwallet.client import LedgerClient, CommException
from ledgerwallet.params import Bip32Path
from ledgerwallet.transport import enumerate_devices
from stellar_sdk import (
    Keypair,
    TransactionEnvelope,
    DecoratedSignature,
    FeeBumpTransactionEnvelope,
)
from stellar_sdk.xdr import HashIDPreimage, EnvelopeType

__all__ = [
    "StrLedger",
    "BaseError",
    "DeviceNotFoundException",
    "HashSigningNotEnabledError",
    "UserRefusedError",
    "DataParsingFailedError",
    "RequestDataTooLargeError",
]

APDU_MAX_PAYLOAD = 255
DEFAULT_KEYPAIR_INDEX = 0


class Ins(IntEnum):
    """Instruction enum for APDU commands."""

    GET_PK = 0x02
    SIGN_TX = 0x04
    GET_CONF = 0x06
    SIGN_HASH = 0x08
    SIGN_SOROBAN_AUTHORIZATION = 0x0A
    SIGN_MESSAGE = 0x0C


class P1(IntEnum):
    """P1 parameter enum for APDU commands."""

    NONE = 0x00
    FIRST_APDU = 0x00
    MORE_APDU = 0x80


class P2(IntEnum):
    """P2 parameter enum for APDU commands."""

    NON_CONFIRM = 0x00
    CONFIRM = 0x01
    LAST_APDU = 0x00
    MORE_APDU = 0x80


class SW(IntEnum):
    """Status Words enum for APDU responses.

    See https://github.com/lightsail-network/app-stellar/blob/develop/docs/COMMANDS.md#status-words
    """

    # Status word for denied by user.
    DENY = 0x6985
    # Status word for hash signing model not enabled.
    HASH_SIGNING_MODE_NOT_ENABLED = 0x6C66
    # Status word for data too large.
    REQUEST_DATA_TOO_LARGE = 0xB004
    # Status word for data parsing fail.
    DATA_PARSING_FAIL = 0xB005
    # Status word for success.
    OK = 0x9000


@dataclasses.dataclass
class AppConfiguration:
    """App configuration information."""

    version: str
    """The version of the app."""
    hash_signing_enabled: bool
    """Whether hash signing is enabled."""
    max_data_size: Optional[int] = None
    """The maximum data size in bytes that the device can sign"""


class StrLedger:
    """Stellar Ledger client class."""

    def __init__(self, client: LedgerClient = None) -> None:
        """Initialize the Stellar Ledger client.

        Args:
            client (LedgerClient): The Ledger client instance, or None to use the default client.
        """
        if client is None:
            client = _get_default_client()
        self.client = client

    def get_app_info(self) -> AppConfiguration:
        """Get the app configuration information.

        Returns:
            AppConfiguration: The app configuration information.
        """
        data = self._send_payload(Ins.GET_CONF, b"")
        hash_signing_enabled = data[0] == 0x01
        major, minor, patch = data[1], data[2], data[3]
        version = f"{major}.{minor}.{patch}"
        max_data_size = (data[4] << 8 | data[5]) if len(data) > 4 else None
        return AppConfiguration(
            version=version,
            hash_signing_enabled=hash_signing_enabled,
            max_data_size=max_data_size,
        )

    def get_keypair(
        self,
        keypair_index: int = DEFAULT_KEYPAIR_INDEX,
        confirm_on_device: bool = False,
    ) -> Keypair:
        """Get the public key for the specified keypair index.

        Args:
            keypair_index (int): The keypair index (default is 0).
            confirm_on_device (bool): Whether to confirm the action on the device (default is False).

        Returns:
            Keypair: The keypair instance.
        """
        path = Bip32Path.build(f"44'/148'/{keypair_index}'")
        try:
            data = self.client.apdu_exchange(
                ins=Ins.GET_PK,
                data=path,
                p1=P1.NONE,
                p2=P2.CONFIRM if confirm_on_device else P2.NON_CONFIRM,
            )
        except CommException as e:
            raise _remap_error(e) from e
        keypair = Keypair.from_raw_ed25519_public_key(data)
        return keypair

    def sign_transaction(
        self,
        transaction_envelope: Union[TransactionEnvelope, FeeBumpTransactionEnvelope],
        keypair_index: int = DEFAULT_KEYPAIR_INDEX,
    ) -> Union[TransactionEnvelope, FeeBumpTransactionEnvelope]:
        """Sign a transaction envelope.

        Args:
            transaction_envelope (Union[TransactionEnvelope, FeeBumpTransactionEnvelope]): The transaction envelope to sign.
            keypair_index (int): The keypair index (default is 0).

        Returns:
            Union[TransactionEnvelope, FeeBumpTransactionEnvelope]: The signed transaction envelope.
        """
        sign_data = transaction_envelope.signature_base()
        keypair = self.get_keypair(keypair_index=keypair_index)

        path = Bip32Path.build(f"44'/148'/{keypair_index}'")
        payload = path + sign_data
        signature = self._send_payload(Ins.SIGN_TX, payload)
        assert isinstance(signature, bytes)
        decorated_signature = DecoratedSignature(keypair.signature_hint(), signature)
        copy_transaction_envelope = copy.deepcopy(transaction_envelope)
        copy_transaction_envelope.signatures.append(decorated_signature)
        return copy_transaction_envelope

    def sign_hash(
        self,
        transaction_hash: Union[str, bytes],
        keypair_index: int = DEFAULT_KEYPAIR_INDEX,
    ) -> bytes:
        """Sign a transaction hash.

        Args:
            transaction_hash (Union[str, bytes]): The transaction hash to sign.
            keypair_index (int): The keypair index (default is 0).

        Returns:
            bytes: The signature.
        """
        if isinstance(transaction_hash, str):
            transaction_hash = binascii.unhexlify(transaction_hash)
        path = Bip32Path.build(f"44'/148'/{keypair_index}'")
        payload = path + transaction_hash
        signature = self._send_payload(Ins.SIGN_HASH, payload)
        return signature

    def sign_soroban_authorization(
        self,
        soroban_authorization: Union[str, bytes, HashIDPreimage],
        keypair_index: int = DEFAULT_KEYPAIR_INDEX,
    ) -> bytes:
        """Sign a Soroban authorization.

        Args:
            soroban_authorization (Union[str, bytes, HashIDPreimage]): The Soroban authorization to sign.
            keypair_index (int): The keypair index (default is 0).

        Returns:
            bytes: The signature.

        Raises:
            ValueError: If the Soroban authorization type is invalid.
        """
        if isinstance(soroban_authorization, str):
            soroban_authorization = HashIDPreimage.from_xdr(soroban_authorization)
        if isinstance(soroban_authorization, bytes):
            soroban_authorization = HashIDPreimage.from_xdr_bytes(soroban_authorization)

        if (
            soroban_authorization.type
            != EnvelopeType.ENVELOPE_TYPE_SOROBAN_AUTHORIZATION
        ):
            raise ValueError(
                f"Invalid type, expected {EnvelopeType.ENVELOPE_TYPE_SOROBAN_AUTHORIZATION}, but got {soroban_authorization.type}"
            )
        path = Bip32Path.build(f"44'/148'/{keypair_index}'")
        payload = path + soroban_authorization.to_xdr_bytes()
        signature = self._send_payload(Ins.SIGN_SOROBAN_AUTHORIZATION, payload)
        return signature

    def sign_message(
        self, message: Union[str, bytes], keypair_index: int = DEFAULT_KEYPAIR_INDEX
    ) -> bytes:
        """Sign a SEP-0053 message.

        Args:
            message (Union[str, bytes]): The message to sign.
            keypair_index (int): The keypair index (default is 0).

        Returns:
            bytes: The signature.
        """
        sign_data = message.encode() if isinstance(message, str) else message
        path = Bip32Path.build(f"44'/148'/{keypair_index}'")
        payload = path + sign_data
        signature = self._send_payload(Ins.SIGN_MESSAGE, payload)
        return signature

    def _send_payload(self, ins: Ins, payload) -> bytes:
        """Send a payload to the Ledger device.

        Args:
            ins (Ins): The instruction for the APDU command.
            payload: The payload to send.

        Returns:
            Optional[Union[int, bytes]]: The response from the Ledger device.
        """
        response = b""
        remaining = len(payload)
        while True:
            chunk_size = min(remaining, APDU_MAX_PAYLOAD)
            p1 = P1.FIRST_APDU if remaining == len(payload) else P1.MORE_APDU
            p2 = P2.LAST_APDU if remaining - chunk_size == 0 else P2.MORE_APDU
            chunk = payload[
                len(payload) - remaining : len(payload) - remaining + chunk_size
            ]
            try:
                response = self.client.apdu_exchange(ins=ins, p1=p1, p2=p2, data=chunk)
            except CommException as e:
                raise _remap_error(e) from e
            remaining -= chunk_size
            if remaining == 0:
                break
        return response


class BaseError(Exception):
    """Base exception class for Ledger errors."""

    pass


class DeviceNotFoundException(BaseError):
    """Exception raised when no Ledger device is found."""

    pass


class HashSigningNotEnabledError(BaseError):
    """Exception raised when hash signing is not enabled on the Ledger device."""

    pass


class RequestDataTooLargeError(BaseError):
    """Exception raised when the request data is too large."""

    pass


class DataParsingFailedError(BaseError):
    """Exception raised when parsing Stellar data fails."""

    pass


class UserRefusedError(BaseError):
    """Exception raised when the user refuses the action."""

    pass


def _get_default_client() -> LedgerClient:
    """Get the default Ledger client.

    Returns:
        LedgerClient: The default Ledger client instance.

    Raises:
        DeviceNotFoundException: If no Ledger device is found.
    """
    devices = enumerate_devices()
    if len(devices) == 0:
        raise DeviceNotFoundException("No Ledger device found")
    return LedgerClient(devices[0])


def _remap_error(e: CommException) -> Exception:
    status = e.sw
    if status == SW.DENY:
        return UserRefusedError("User refused the request")
    elif status == SW.DATA_PARSING_FAIL:
        return DataParsingFailedError("Unable to parse the provided data")
    elif status == SW.HASH_SIGNING_MODE_NOT_ENABLED:
        return HashSigningNotEnabledError(
            "Hash signing not allowed. Have you enabled it in the app settings?"
        )
    elif status == SW.REQUEST_DATA_TOO_LARGE:
        return RequestDataTooLargeError(
            "The provided data is too large for the device to process"
        )
    return e
