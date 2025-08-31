# Encrep
# MIT license
# Copyright © 2025 Anatoly Petrov (petrov.projects@gmail.com)
# All rights reserved

"""Encrep

CLI tool for dumping and restoring Git repos via AWS S3.
Encryption, easy management, and pretty printing.
"""

# We don't use multiple modules to keep things simple.
# pylint: disable=too-many-lines

# We use implicit Optional in CLI parameters.
# Every None will be properly evaluated to default by the callback.
# mypy: disable-error-code="assignment"

import collections
import contextlib
import dataclasses
import datetime
import functools
import inspect
import io
import itertools
import json
from os import PathLike
import pathlib
import re
import subprocess
import tempfile
from typing import (
    Annotated,
    Any,
    BinaryIO,
    Callable,
    Final,
    Iterable,
    Iterator,
    Literal,
    Self,
    Sequence,
)
import zipfile

# You may install boto3-stubs to enable type checking for boto3 and botocore.
# See https://pypi.org/project/boto3-stubs/
import boto3  # type: ignore
import boto3.exceptions as boto3_exc  # type: ignore
import botocore  # type: ignore
import botocore.config  # type: ignore
import botocore.exceptions as botocore_exc  # type: ignore
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.tree import Tree
import typer
from typer import Context, Exit, Option, Typer


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------


__author__ = "Anatoly Petrov"
__version__ = "1.0.1"

ENCREP_SECRETS_DEFAULT: Final = "encrep-secrets.json"
AWS_PAGINATION_LIMIT: Final = 1000
AWS_REGIONS: Final = (
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-south-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ap-southeast-3",
    "ca-central-1",
    "cn-north-1",
    "cn-northwest-1",
    "eu-central-1",
    "eu-north-1",
    "eu-south-1",
    "eu-south-2",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "me-south-1",
    "sa-east-1",
    "us-east-1",  # Default for S3 buckets
    "us-east-2",
    "us-gov-east-1",
    "us-gov-west-1",
    "us-west-1",
    "us-west-2",
)


# -----------------------------------------------------------------------------
# Errors
# -----------------------------------------------------------------------------


class EncrepError(Exception):
    """Base exception for Encrep."""


class EncrepBadSecrets(EncrepError):
    """Secrets are missing or have a bad format."""


class EncrepS3Error(EncrepError):
    """Failed AWS S3 operation."""


class EncrepGitError(EncrepError):
    """Failed Git operation."""


class EncrepBadRepo(EncrepError):
    """Unable to dump or restore a repo/misc."""


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------


def is_aws_akid(s: str) -> bool:
    """Return True if a given string is a valid AWS access key ID."""
    res = re.match("(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])", s)
    return bool(res)


def is_aws_sk(s: str) -> bool:
    """Return True if a given string is a valid AWS secret access key."""
    res = re.match("(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])", s)
    return bool(res)


def is_region(s: str) -> bool:
    """Return True if a given string is a valid AWS region."""
    return s in AWS_REGIONS


def is_bucket(s: str) -> bool:
    """Return True if a given string is a valid bucket name."""
    res = re.match("(?!(^xn--|.+-s3alias$))^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$", s)
    return bool(res)


# -----------------------------------------------------------------------------
# Secrets and Configuration
# -----------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True, slots=True)
class ExclusionRule:
    """Rule for excluding unversioned files from archiving (case-sensitive)."""

    pattern: str
    comp: Literal["prefix", "suffix", "full-match"]

    def match(self, file: str) -> bool:
        """Return True if a file should be excluded from archiving."""
        match self.comp:
            case "prefix":
                return file.startswith(self.pattern)
            case "suffix":
                return file.endswith(self.pattern)
            case "full-match":
                return file == self.pattern


def is_excluded(file: str, rules: list[ExclusionRule]) -> bool:
    """Return True if a file should be excluded from archiving."""
    return any(rule.match(file) for rule in rules)


@dataclasses.dataclass
class Secrets:
    """Class for managing secrets/configuration.

    We don't use Pydantic model to avoid large dependency.
    """

    aws_access_key_id: str
    aws_secret_access_key: str
    encrep_secret_key: bytes
    region: str
    bucket: str
    excluded: list[ExclusionRule] = dataclasses.field(default_factory=list)

    @classmethod
    def from_file(cls, src: pathlib.Path) -> Self:
        """Load secrets from a file."""
        if not src.exists():
            raise EncrepBadSecrets(f"Secrets not found at: '{src.resolve()}'.")
        with open(src, "rt", encoding="utf-8") as f:
            try:
                row: dict[str, Any] = json.load(f)
            except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
                msg = f"Failed to decode secrets from: '{src.resolve()}'."
                raise EncrepBadSecrets(msg) from e
        for field in dataclasses.fields(cls):
            curr = field.name
            val = row.get(curr)
            if val is None:
                raise EncrepBadSecrets(f"Missing '{curr}' field.")
        if not is_aws_akid(row["aws_access_key_id"]):
            raise EncrepBadSecrets("Invalid AWS access key ID.")
        if not is_aws_sk(row["aws_secret_access_key"]):
            raise EncrepBadSecrets("Invalid AWS secret access key.")
        if not is_bucket(row["bucket"]):
            raise EncrepBadSecrets("Invalid bucket name.")
        if not is_region(row["region"]):
            raise EncrepBadSecrets("Bad AWS region.")
        try:
            row["encrep_secret_key"] = bytes.fromhex(row["encrep_secret_key"])
        except ValueError as e:
            raise EncrepBadSecrets("Failed to decode Encrep secret key.") from e
        row["excluded"] = [ExclusionRule(**kw) for kw in row["excluded"]]
        return cls(**row)

    def to_file(self, dest: pathlib.Path) -> None:
        """Write secrets to a file."""
        row = dataclasses.asdict(self)
        row["encrep_secret_key"] = self.encrep_secret_key.hex()
        folder = dest.parent
        if not folder.exists():
            folder.mkdir(parents=True)
        with open(dest, "wt", encoding="utf-8") as f:
            json.dump(row, f, indent=2)


# -----------------------------------------------------------------------------
# Cryptography (Fernet)
# -----------------------------------------------------------------------------


def generate_key() -> bytes:
    """Generate the Encrep secret key."""
    return Fernet.generate_key()


def encrypt_file(buf: bytes, key: bytes) -> bytes:
    """Encrypt a file (in-memory)."""
    f = Fernet(key)
    return f.encrypt(buf)


def decrypt_file(buf: bytes, key: bytes) -> bytes:
    """Decrypt a file (in-memory)."""
    f = Fernet(key)
    try:
        return f.decrypt(buf)
    except InvalidToken as e:
        msg = "Repo dump is malformed, damaged, or hasn't a valid signature."
        raise EncrepBadRepo(msg) from e


# -----------------------------------------------------------------------------
# AWS S3
# -----------------------------------------------------------------------------


# Helpers and wrappers


def aws_config(region: str) -> botocore.config.Config:
    """Return advanced AWS config.

    See https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
    """
    return botocore.config.Config(
        region_name=region,
        signature_version="v4",
        connect_timeout=5.0,
        read_timeout=5.0,
        retries={"max_attempts": 3, "mode": "standard"},
    )


def wrap_boto_exc(f: Callable[..., Any]) -> Callable[..., Any]:
    """Re-raise all boto3/botocore exceptions as EncrepS3Error (method decorator)."""

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:

        def origin() -> Any:
            sig = inspect.signature(f)
            params = list(sig.parameters.keys())
            if params and params[0] == "self":
                return f(*args, **kwargs)
            if params and params[0] == "cls":
                return f(type(args[0]), *args[1:], **kwargs)
            # No params or params[0] not in ("self", "cls") -> staticmethod
            return f(*args[1:], **kwargs)

        try:
            return origin()
        except (
            botocore_exc.ClientError,
            botocore_exc.BotoCoreError,
            boto3_exc.Boto3Error,
        ) as e:
            raise EncrepS3Error("AWS S3 operation has failed.\n" + str(e)) from e

    return wrapper


def wrap_boto_exc_for_all(cls: type) -> type:
    """Re-raise all boto3/botocore exceptions as EncrepS3Error (class decorator)."""
    for attr in cls.__dict__:
        field = getattr(cls, attr)
        if callable(field):
            setattr(cls, attr, wrap_boto_exc(field))
    return cls


# AWS S3 paths


def eval_date(date: datetime.datetime | None = None) -> str:
    """Return a given date as %Y-%m-%d string (current date if missing)."""
    return (
        date.strftime("%Y-%m-%d")
        if date is not None
        else datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    )


def get_bundle_path(name: str, date: datetime.datetime | None = None) -> str:
    """Create a path for a Git bundle within AWS S3.

    Schema: repo-name / bundles / curr-date / git.bundle
    """
    date = eval_date(date)
    path = pathlib.PurePosixPath(name) / "bundles" / date / "git.bundle"
    return str(path)


def get_misc_path(repo: str, date: datetime.datetime | None = None) -> str:
    """Create a path for a misc archive within AWS S3.

    Schema: repo-name / extras / curr-date / misc.zip
    """
    date = eval_date(date)
    path = pathlib.PurePosixPath(repo) / "extras" / date / "misc.zip"
    return str(path)


def get_bundles_prefix(repo: str) -> str:
    """Create a search prefix for all bundles uploaded to AWS S3."""
    path = pathlib.PurePosixPath(repo).name + "/bundles"
    return str(path)


def get_extras_prefix(repo: str) -> str:
    """Create a search prefix for all misc archives uploaded to AWS S3."""
    path = pathlib.PurePosixPath(repo).name + "/extras"
    return str(path)


def extract_repo(path: str) -> str:
    """Extract a repo name from the AWS S3 path."""
    return pathlib.PurePosixPath(path).parts[0]


def extract_date(path: str) -> str:
    """Extract a date info from the AWS S3 path."""
    return pathlib.PurePosixPath(path).parts[-2]


def extract_filename(path: str) -> str:
    """Extract a filename from the AWS S3 path."""
    return pathlib.PurePosixPath(path).name


# AWS S3 client


@wrap_boto_exc_for_all
class AwsS3Client(contextlib.AbstractContextManager):
    """Wrapper for the row-level AWS S3 client."""

    def __init__(self, secrets: Secrets) -> None:
        """Initialize a client."""
        self.s3 = boto3.client(
            service_name="s3",
            config=aws_config(secrets.region),
            aws_access_key_id=secrets.aws_access_key_id,
            aws_secret_access_key=secrets.aws_secret_access_key,
        )
        self.bucket = secrets.bucket
        self.region = secrets.region

    def close(self) -> None:
        """Close connections."""
        self.s3.close()

    def __enter__(self) -> Self:
        """Enter context."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context."""
        self.close()

    # -------------------------------------------------------------------------
    # Objects
    # -------------------------------------------------------------------------

    def upload(self, file: BinaryIO, path: str) -> None:
        """Upload a file to the storage."""
        self.s3.upload_fileobj(Fileobj=file, Bucket=self.bucket, Key=path)

    def download(self, path: str) -> bytes:
        """Download a file from the storage."""
        with io.BytesIO() as f:
            self.s3.download_fileobj(Fileobj=f, Bucket=self.bucket, Key=path)
            return f.getvalue()

    def remove(self, path: str) -> None:
        """Delete a file from the storage."""
        self.s3.delete_object(Bucket=self.bucket, Key=path)

    def is_file(self, path: str) -> bool:
        """Return True if the specified file exists."""
        try:
            self.s3.head_object(Bucket=self.bucket, Key=path)
            return True
        except self.s3.exceptions.NoSuchKey:
            return False
        except botocore_exc.ClientError as e:
            code = e.response["Error"]["Code"]
            # HTTP 404 Not Found
            if code == "404":
                return False
            # Some other error
            raise

    # -------------------------------------------------------------------------
    # Buckets
    # -------------------------------------------------------------------------

    def make_bucket(self, name: str | None = None) -> None:
        """Create a bucket."""
        bucket = name or self.bucket
        try:
            # Public access is blocked by default.
            # pylint: disable-next=line-too-long
            # See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html
            if self.region != "us-east-1":
                self.s3.create_bucket(
                    Bucket=self.bucket,
                    CreateBucketConfiguration={"LocationConstraint": self.region},
                )
            else:
                self.s3.create_bucket(Bucket=self.bucket)
        except self.s3.exceptions.BucketAlreadyExists as e:
            msg = f"Bucket '{bucket}' already exists within your AWS account."
            raise EncrepS3Error(msg) from e
        except botocore_exc.ClientError as e:
            # Seems that bucket exists within a third-party account.
            code = e.response["Error"]["Code"]
            if code in ["IllegalLocationConstraintException", "AccessDenied", "403"]:
                msg = (
                    f"Bucket '{bucket}' already exists within the third-party account.\n"
                    f"Bucket name must be unique across all AWS accounts."
                )
                raise EncrepS3Error(msg) from e
            # Some other error
            raise

    def unlink_bucket(self, name: str) -> None:
        """Remove an empty bucket from the storage."""
        bucket = name or self.bucket
        self.s3.delete_bucket(Bucket=bucket)

    def iterate(self, prefix: str | None = None) -> Iterator[str]:
        """Iterate over filenames within a bucket."""
        paginator = self.s3.get_paginator("list_objects_v2")
        opts = {"Bucket": self.bucket}
        if prefix is not None:
            opts["Prefix"] = prefix
        for page in paginator.paginate(**opts):
            if page["KeyCount"] == 0:
                return
            yield from [obj["Key"] for obj in page["Contents"]]

    def remove_many(self, prefix: str | None = None) -> None:
        """Remove files from a bucket."""
        bucket = self.bucket
        for page in itertools.batched(self.iterate(prefix), AWS_PAGINATION_LIMIT):
            objs = [{"Key": name} for name in page]
            self.s3.delete_objects(
                Bucket=bucket,
                Delete={"Objects": objs, "Quiet": True},
            )

    def is_bucket(
        self, name: str | None = None, search: Literal["global", "local"] = "global"
    ) -> bool:
        """Return True if bucket exists.

        The bucket name must be unique across all AWS accounts in all the AWS Regions.
        You may specify global (all accounts) or local (your account) search.
        """
        bucket = name or self.bucket
        try:
            self.s3.head_bucket(Bucket=bucket)
            return True
        except self.s3.exceptions.NoSuchBucket:
            return False
        except botocore_exc.ClientError as e:
            code = e.response["Error"]["Code"]
            # Seems that bucket exists within a third-party account.
            if code in ["IllegalLocationConstraintException", "AccessDenied", "403"]:
                return search == "global"
            # HTTP 404 Not Found
            if code == "404":
                return False
            # Some other error
            raise

    def empty(self, name: str | None = None) -> bool:
        """Return True if bucket is empty."""
        bucket = name or self.bucket
        resp = self.s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
        return bool(resp["KeyCount"] == 0)

    def list_buckets(self) -> list[str]:
        """Return all bucket names within the storage."""
        res = []
        paginator = self.s3.get_paginator("list_buckets")
        for page in paginator.paginate():
            res.extend([obj["Name"] for obj in page["Buckets"]])
        return res


# -----------------------------------------------------------------------------
# ZIP archives
# -----------------------------------------------------------------------------


def pretty_size(num_bytes):
    """Convert size in bytes to a human-readable string using binary (base-1024) units."""
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} ZB"


def archive(files: Iterable[str | PathLike[str]], repo: str | PathLike[str]) -> bytes:
    """Create a zip archive with the given files."""
    with (
        tempfile.TemporaryFile(mode="w+b") as f,
        zipfile.ZipFile(
            f, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as arc,
    ):
        repo = pathlib.Path(repo)
        for file in files:
            arc.write(repo / file, file)
        arc.close()
        f.seek(0)
        return f.read()


UnarchiveStats = collections.namedtuple(
    "UnarchiveStats", ["permitted", "suppressed", "tot"]
)


def unarchive(data: bytes, repo: pathlib.Path) -> UnarchiveStats:
    """Unpack all files from the archive to a given directory."""
    try:
        permitted, suppressed, tot = 0, 0, 0
        with io.BytesIO(data) as f, zipfile.ZipFile(f, "r") as arc:
            for src in arc.namelist():
                dest = repo / src
                if not dest.exists():
                    arc.extract(src, repo)
                    permitted += 1
                    tot += dest.stat().st_size
                else:
                    console.print(f":exclamation: File already exists: '{dest}'.")
                    suppressed += 1
    except zipfile.BadZipFile as e:
        raise EncrepBadRepo("Unable to extract files from the archive.") from e
    return UnarchiveStats(permitted, suppressed, tot)


# -----------------------------------------------------------------------------
# Git
# -----------------------------------------------------------------------------


def git_exec(
    args: Sequence[str | PathLike[str]],
    cwd: str | PathLike[str] | None = None,
    strict: bool = True,
) -> tuple[str, str]:
    """Execute a Git command and return tuple with stdout and stderr."""
    cmd: list[str | PathLike[str]] = ["git"]
    cmd.extend(args)
    try:
        res = subprocess.run(
            cmd, capture_output=True, encoding="utf-8", check=True, cwd=cwd
        )
    except subprocess.CalledProcessError as e:
        raise EncrepGitError(f"Git '{args[0]}' command failed:\n{e.stderr}") from e
    except FileNotFoundError as e:
        raise EncrepGitError("Git is not available.") from e
    if strict and res.stderr:
        raise EncrepGitError(f"Git '{args[0]}' command failed:\n{res.stderr}")
    # Ok
    return res.stdout, res.stderr


def git_ls_others(repo: pathlib.Path) -> list[str]:
    """Find all files that are not under the version control."""
    # Git doesn't return files from /.git directory, so we don't need to filter them.
    out, _ = git_exec(["ls-files", "--others", repo])
    files = out.splitlines()
    return sorted(files)


def git_create_bundle(repo: pathlib.Path) -> pathlib.Path:
    """Bundle a Git repo."""
    name = repo.name + ".bundle"
    git_exec(["bundle", "create", name, "--all"], cwd=repo)
    return repo / name


def git_verify_bundle(file: pathlib.Path) -> tuple[str, str]:
    """Verify a Git bundle."""
    repo = file.parent
    return git_exec(["bundle", "verify", file], strict=False, cwd=repo)


def git_clone_bundle(src: pathlib.Path, dest: pathlib.Path) -> None:
    """Clone a Git bundle to a given directory."""
    if dest.exists():
        raise EncrepBadRepo(f"Destination directory '{dest}' already exists.")
    dest.mkdir(parents=True)
    git_exec(["clone", src, dest], cwd=dest, strict=False)


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


# Core


def create_app() -> Typer:
    """Create a Typer app."""
    return Typer(
        no_args_is_help=True,
        rich_markup_mode="rich",
        pretty_exceptions_show_locals=False,  # we don't want to disclose the keys
    )


app = create_app()
ls_app = create_app()
dump_app = create_app()
restore_app = create_app()
rm_app = create_app()
drop_app = create_app()

app.add_typer(ls_app, name="ls", help="List the repos available from AWS S3.")
app.add_typer(dump_app, name="dump", help="Dump a repo to AWS S3.")
app.add_typer(restore_app, name="restore", help="Restore a repo from AWS S3.")
app.add_typer(rm_app, name="rm", help="Remove a single repo backup from AWS S3 for the specified date.")
app.add_typer(drop_app, name="drop", help="Delete multiple repo backups from AWS S3 within a specified date range.")

console = Console(color_system="256")
err_console = Console(color_system="256", stderr=True)


# Wrappers


def trace(f: Callable[..., Any]) -> Callable[..., Any]:
    """Print the command that was launched, along with the provided arguments."""

    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        cmd = "encrep " + f.__name__.replace("_", " ")
        params = [f"--{k} '{v}'" for k, v in kwargs.items() if k != "ctx"]
        info = f"{cmd} {" ".join(params)}"
        console.print()
        cmd = Panel(
            info, title="Command", title_align="left", border_style="cyan", style="bold"
        )
        console.print(cmd)
        return f(*args, **kwargs)

    return wrapper


# Commands


# -----------------------------------------------------------------------------
# encrep
# -----------------------------------------------------------------------------


def keys_callback(keys: pathlib.Path | None) -> pathlib.Path:
    """Evaluate 'keys' argument.

    If missing, return app_dir / ENCREP_SECRETS_DEFAULT path.
    """
    if keys is not None:
        return keys
    # Missing
    return pathlib.Path(typer.get_app_dir("encrep")) / ENCREP_SECRETS_DEFAULT


KeysOutParam = Annotated[
    pathlib.Path,
    Option(
        "--keys",
        "-k",
        help="Path to secrets file (app_dir / 'encrep-secrets.json' by default).",
        callback=keys_callback,
        envvar="ENCREP_KEYS",
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
    ),
]


@app.command()
@trace
def setup(keys: KeysOutParam = None) -> None:
    """Set up secrets, AWS region, and bucket name."""
    console.print(":gear: Setting up Encrep...", style="yellow")
    if keys.exists():
        _secrets_exist(keys)
    _input_secrets(keys)
    repo = keys.parent
    git = repo / ".git"
    gitignore = repo / ".gitignore"
    if git.exists():
        _gitignore_secrets(gitignore, keys.name)
    console.print("Setup done :thumbs_up:", style="yellow")


def _secrets_exist(keys: pathlib.Path) -> None:
    console.print(":exclamation: Secrets file already exists.")
    if not Confirm.ask("Do you want to overwrite it?"):
        _abort()
    # Confirmed
    dt = datetime.datetime.fromtimestamp(keys.stat().st_mtime)
    name = f"{keys.stem} from {dt.strftime("%Y-%m-%d %H:%M:%S")}{keys.suffix}"
    keys.rename(keys.parent / name)
    repo = keys.parent
    git = repo / ".git"
    gitignore = repo / ".gitignore"
    if git.exists():
        _gitignore_secrets(gitignore, name)


def _abort(msg: str | None = None) -> None:
    """Abnormal exit with an optional message."""
    if msg is not None:
        err = Panel(f"{msg}", title="Error", title_align="left", border_style="red")
        console.print(err)
    console.print("Aborting :stop_sign:", style="bold red")
    raise Exit(code=20)


def _input_secrets(keys: pathlib.Path):
    # AWS AKID
    while True:
        aws_akid = Prompt.ask("Enter your AWS access key id :lock:", password=True)
        if is_aws_akid(aws_akid):
            break
        console.print(":exclamation: Invalid AWS access key id. Please retry.")
    # AWS SK
    while True:
        aws_sk = Prompt.ask("Enter your AWS secret access key :lock:", password=True)
        if is_aws_sk(aws_sk):
            break
        console.print(":exclamation: Invalid AWS secret access key. Please retry.")
    # Region
    while True:
        region = Prompt.ask("Enter your AWS region")
        if is_region(region):
            break
        console.print(":exclamation: Invalid AWS region. Please retry.")
        if Confirm.ask("Show available regions?"):
            console.print(AWS_REGIONS)
    # Bucket
    while True:
        bucket = Prompt.ask("Enter your bucket name")
        if is_bucket(bucket):
            break
        console.print(":exclamation: Invalid bucket name. Please retry.")
    # Excluded
    excluded = []
    if Confirm.ask("Do you want to exclude Encrep secrets from archiving?"):
        excluded.append(ExclusionRule(f"{keys.stem}", comp="prefix"))
        if not keys.name.startswith("encrep-secrets"):
            excluded.append(ExclusionRule("encrep-secrets", comp="prefix"))
    if Confirm.ask("Do you want to exclude other files from archiving?"):
        console.print(
            ":exclamation: Excluded paths will be resolved relative to the repo dir."
        )
        excluded.extend(_exclude_file())
    console.print("List of excluded files:", excluded)
    # Serde
    secrets = Secrets(aws_akid, aws_sk, generate_key(), region, bucket, excluded)
    secrets.to_file(keys)
    console.print(f":white_check_mark: Encrep secrets file created at '{keys}'.")


def _exclude_file() -> list[ExclusionRule]:
    res = []
    while True:
        comp = Prompt.ask(
            "Choose the comparator", choices=["prefix", "suffix", "full-match"]
        )
        pattern = Prompt.ask("Enter a pattern for excluding")
        res.append(ExclusionRule(pattern, comp))  # type: ignore[arg-type]
        if not Confirm.ask("Do you want to exclude other files?"):
            break
    return res


def _gitignore_secrets(gitignore: pathlib.Path, name: str) -> None:
    if gitignore.exists():
        with open(gitignore, "rt+", encoding="utf-8") as f:
            content = f.read()
            if name not in content:
                console.print("The current directory is a git repo.")
                if Confirm.ask("Would you like to add secrets file to .gitignore?"):
                    f.write("\n" + name)
    else:
        console.print("The current directory is a git repo.")
        if Confirm.ask("Would you like to add secrets file to .gitignore?"):
            with open(gitignore, "wt", encoding="utf-8") as f:
                f.write(name)


@app.command()
@trace
def cleanup(keys: KeysOutParam = None) -> None:
    """Remove the secrets file."""
    console.print(":recycle: Removing secrets file...", style="yellow")
    if keys.exists():
        keys.unlink()
    else:
        _abort(f"Secrets file not found at: '{keys}'.")
    console.print("Cleanup done :thumbs_up:", style="yellow")


@app.command()
@trace
def loc(keys: KeysOutParam = None) -> None:
    """Show path to secrets file."""
    console.print(":gear: Deducing path to secrets file...", style="yellow")
    console.print(f"Location: '{keys}'")
    console.print(f"Exists: {keys.exists()}")


KeysInParam = Annotated[
    pathlib.Path,
    Option(
        "--keys",
        "-k",
        help="Path to secrets file (app_dir / 'encrep-secrets.json' by default).",
        callback=keys_callback,
        envvar="ENCREP_KEYS",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
    ),
]


@app.command()
@trace
def tree(keys: KeysInParam = None) -> None:
    """Display the structure of the AWS S3 bucket specified in the secrets file."""
    secrets = Secrets.from_file(keys)
    console.print(
        ":magnifying_glass_tilted_right: Collecting bucket objects...",
        style="bold yellow",
    )
    with AwsS3Client(secrets) as client:
        files: list[str] = sorted(client.iterate())
    if not files:
        _abort("Bucket is empty.")

    # Non-empty

    tmp: set[tuple[str, ...]] = set()
    for file in files:
        segs: list[str]
        for segs in itertools.accumulate(
            file.split("/"), lambda seq, elm: [*seq, elm], initial=[]  # type: ignore
        ):
            if segs:
                tmp.add(tuple(segs))

    files: list[tuple[str]] = sorted(tmp)  # type: ignore[no-redef]
    n = 0  # shared by all recursive calls

    def build(node: Tree, lvl: int = 0) -> None:
        nonlocal n
        while n < len(files):
            # Parts
            parts = files[n]
            if lvl >= len(parts):
                break
            n += 1
            # File/dir
            if "." in parts[-1]:
                node.add(f"📄 {parts[lvl]}")
            else:
                new = node.add(f":open_file_folder: {parts[lvl]}")
                build(new, lvl + 1)

    tr = Tree(f"[cyan bold italic]'{secrets.bucket}' bucket")
    build(tr)
    console.print(tr)


# -----------------------------------------------------------------------------
# ls
# -----------------------------------------------------------------------------


@ls_app.command("project")
@trace
def ls_project(keys: KeysInParam = None) -> None:
    """List all projects available from AWS S3."""
    secrets = Secrets.from_file(keys)
    console.print(
        ":magnifying_glass_tilted_right: Collecting projects available from AWS S3...",
        style="bold yellow",
    )
    with AwsS3Client(secrets) as client:
        _projects_table(client)


def _projects_table(client: AwsS3Client) -> None:
    console.print(f"Bucket: '{client.bucket}'.")
    if not client.is_bucket(search="local"):
        _abort("Bucket doesn't exist.")
    files = sorted(client.iterate())
    if not files:
        _abort("No objects found.")
    table = Table(
        title="Available Projects", show_header=True, header_style="bold blue"
    )
    table.add_column("Repo", justify="center", style="cyan")
    table.add_column("Bundles (tot)", justify="center", style="magenta")
    table.add_column("Misc archives (tot)", justify="center", style="magenta")
    for repo, it in itertools.groupby(files, key=extract_repo):
        group = list(it)
        bundles = sum(1 for f in group if "bundles" in f)
        archives = sum(1 for f in group if "misc" in f)
        table.add_row(repo, str(bundles), str(archives))
    console.print(table)


def name_callback(repo: str | None) -> str:
    """Evaluate 'name' argument.

    If missing, return cwd.name.
    """
    if repo is not None:
        return repo
    # Missing
    return pathlib.Path.cwd().name


NameParam = Annotated[
    str,
    Option(
        "--name",
        "-n",
        help="Repo name (cwd.name by default).",
        callback=name_callback,
        envvar="ENCREP_NAME",
    ),
]


@ls_app.command("repo")
@trace
def ls_repo(name: NameParam = None, keys: KeysInParam = None) -> None:
    """List all bundles for a given repo available from AWS S3."""
    secrets = Secrets.from_file(keys)
    prefix = get_bundles_prefix(name)
    console.print(
        ":magnifying_glass_tilted_right: Collecting bundles available from AWS S3...",
        style="bold yellow",
    )
    with AwsS3Client(secrets) as client:
        _objects_table("Available Bundles", prefix, client)


def _objects_table(title: str, prefix: str, client: AwsS3Client) -> None:
    console.print(f"Search prefix: '{prefix}'.")
    console.print(f"Bucket: '{client.bucket}'.")
    files = sorted(client.iterate(prefix))
    if not files:
        console.print(":exclamation: No objects found.")
        if Confirm.ask("Would you like to see all objects in a bucket?"):
            _objects_table("Available Objects", "", client)
        return
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("Date", justify="center", style="cyan")
    table.add_column("Filename")
    table.add_column("Object", justify="center", style="magenta")
    table.add_column("Bucket", justify="center", style="magenta")
    for file in files:
        table.add_row(extract_date(file), extract_filename(file), file, client.bucket)
    console.print(table)


@ls_app.command("misc")
@trace
def ls_misc(name: NameParam = None, keys: KeysInParam = None) -> None:
    """List all misc archives for a given repo available from AWS S3.

    Misc archives contain files excluded from version control.
    """
    secrets = Secrets.from_file(keys)
    prefix = get_extras_prefix(name)
    console.print(
        ":magnifying_glass_tilted_right: Collecting misc archives available from AWS S3...",
        style="bold yellow",
    )
    with AwsS3Client(secrets) as client:
        _objects_table("Available Extras", prefix, client)


# -----------------------------------------------------------------------------
# dump
# -----------------------------------------------------------------------------


def repo_input_callback(src: pathlib.Path | None) -> pathlib.Path:
    """Evaluate 'src' argument (input).

    If missing, return cwd.
    """
    if src is not None:
        return src
    # Missing
    return pathlib.Path.cwd()


RepoInParam = Annotated[
    pathlib.Path,
    Option(
        "--src",
        "-s",
        help="Path to existing Git repo (cwd by default).",
        callback=repo_input_callback,
        envvar="ENCREP_SRC",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
    ),
]


@dump_app.command("project")
@trace
def dump_project(
    ctx: Context, src: RepoInParam = None, keys: KeysInParam = None
) -> None:
    """Invoke dump repo + dump misc with the same arguments."""
    ctx.invoke(dump_repo, src=src, keys=keys)
    ctx.invoke(dump_misc, src=src, keys=keys)


@dump_app.command("repo")
@trace
def dump_repo(src: RepoInParam = None, keys: KeysInParam = None) -> None:
    """Bundle a given Git repo, encrypt it, and send to AWS S3."""
    secrets = Secrets.from_file(keys)
    bundle = _bundle_repo(src)
    encrypted = _encrypt_file(bundle, secrets)
    path = get_bundle_path(src.name)
    with AwsS3Client(secrets) as client:
        _upload_file(io.BytesIO(encrypted), path, client)


def _bundle_repo(repo: pathlib.Path) -> bytes:
    console.print(Rule("Bundle", align="center", end="\n"))
    console.print(":takeout_box: Starting repo bundling...", style="bold yellow")
    dest = git_create_bundle(repo)
    console.print(f"Repo: '{repo}'.")
    out, err = git_verify_bundle(dest)
    if not err.endswith("is okay\n"):
        dest.unlink()
        raise EncrepGitError(f"Bundle verification failed:\n{err}")
    console.print(out, err.removesuffix("\n"))
    with open(dest, "rb") as f:
        bundle = f.read()
    dest.unlink()
    console.print(f"Total size: {pretty_size(len(bundle))}.")
    console.print("Bundling done :thumbs_up:", style="bold yellow")
    return bundle


def _encrypt_file(data: bytes, secrets: Secrets) -> bytes:
    console.print(Rule("Encrypt", align="center"))
    console.print(":key: Starting encryption (in-memory)...", style="bold yellow")
    encrypted = encrypt_file(data, secrets.encrep_secret_key)
    console.print(f"Total size: {pretty_size(len(encrypted))}.")
    console.print("File encrypted :thumbs_up:", style="bold yellow")
    return encrypted


def _upload_file(file: io.BytesIO, path: str, client: AwsS3Client) -> None:
    console.print(Rule("Send", align="center"))
    console.print(":mailbox: Uploading file to AWS S3...", style="bold yellow")
    console.print(f"Object: '{path}'.")
    console.print(f"Bucket: '{client.bucket}'.")
    if not client.is_bucket(search="local"):
        _create_bucket(client)
    if client.is_file(path):
        console.print(":exclamation: Today's repo bundle already exists.")
        if not Confirm.ask("Do you want to overwrite it?"):
            _abort()
    client.upload(file, path)
    console.print("File uploaded :thumbs_up:", style="bold yellow")


def _create_bucket(client: AwsS3Client) -> None:
    console.print(f":exclamation: Bucket '{client.bucket}' doesn't exist.")
    if not Confirm.ask("Do you want to create it?"):
        _abort()
    # Confirmed
    client.make_bucket()


@dump_app.command("misc")
@trace
def dump_misc(src: RepoInParam = None, keys: KeysInParam = None) -> None:
    """Create a misc archive for a given repo, encrypt it, and send to AWS S3.

    Misc archives contain files excluded from version control.
    """
    secrets = Secrets.from_file(keys)
    arc = _archive_misc(src, secrets.excluded)
    encrypted = _encrypt_file(arc, secrets)
    path = get_misc_path(src.name)
    with AwsS3Client(secrets) as client:
        _upload_file(io.BytesIO(encrypted), path, client)


def _archive_misc(repo: pathlib.Path, excluded: list[ExclusionRule]) -> bytes:
    console.print(Rule("Archive", align="center"))
    console.print(":file_cabinet: Archiving unversioned files...", style="bold yellow")
    console.print(f"Repo: '{repo}'.")
    files = git_ls_others(repo)
    console.print(f"Found {len(files)} unversioned files.")
    console.print("Excluding files concerning user policy...")
    permitted, suppressed = [], []
    for file in files:
        if is_excluded(file, excluded):
            suppressed.append(file)
        else:
            permitted.append(file)
    console.print(f"Permitted files: {len(permitted)}.")
    console.print(f"Suppressed files: {len(suppressed)}.")
    if suppressed and Confirm.ask("Show suppressed files?"):
        console.print(suppressed)
    if not permitted:
        _abort("Nothing to do.")
    console.print("Archiving permitted files...")
    arc = archive(permitted, repo)
    console.print(f"Total size: {pretty_size(len(arc))}.")
    console.print("Archive created :thumbs_up:", style="bold yellow")
    return arc


# -----------------------------------------------------------------------------
# restore
# -----------------------------------------------------------------------------


def repo_output_callback(dest: pathlib.Path | None) -> pathlib.Path:
    """Evaluate 'dest' argument (output).

    If missing, return cwd.parent / cwd.name-restored.
    """
    if dest is not None:
        return dest
    # Missing
    cwd = pathlib.Path.cwd()
    return cwd.parent / f"{cwd.name}-restored"


RepoOutParam = Annotated[
    pathlib.Path,
    Option(
        "--dest",
        "-d",
        help="Path to restored repo (cwd.parent / cwd.name-restored by default).",
        callback=repo_output_callback,
        envvar="ENCREP_DEST",
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
]


DateParam = Annotated[
    datetime.datetime,  # datetime since Typer doesn't support date
    Option(
        "--date",
        "-d",
        help="Creation date for a Git bundle or misc archive (latest by default).",
        envvar="ENCREP_DATE",
        formats=["%Y-%m-%d"],
    ),
]


@restore_app.command("project")
@trace
def restore_project(
    ctx: Context,
    name: NameParam = None,
    date: DateParam = None,
    dest: RepoOutParam = None,
    keys: KeysInParam = None,
) -> None:
    """Invoke restore repo + restore misc with the same arguments."""
    ctx.invoke(restore_repo, name=name, date=date, dest=dest, keys=keys)
    ctx.invoke(restore_misc, name=name, date=date, dest=dest, keys=keys)


@restore_app.command("repo")
@trace
def restore_repo(
    name: NameParam = None,
    date: DateParam = None,
    dest: RepoOutParam = None,
    keys: KeysInParam = None,
) -> None:
    """Download a Git bundle from AWS S3, decrypt it, and clone to a given directory."""
    secrets = Secrets.from_file(keys)
    if dest.exists() and any(dest.iterdir()):
        _abort(f"Destination directory '{dest}' is not empty.")
    with AwsS3Client(secrets) as client:
        prefix = get_bundles_prefix(name)
        path = get_bundle_path(name, date) if date else _find_latest(prefix, client)
        encrypted = _download_file(path, client)
    decrypted = _decrypt_file(encrypted, secrets)
    _clone_bundle(decrypted, dest)


def _find_latest(prefix: str, client: AwsS3Client) -> str:
    console.print(Rule("Search", align="center"))
    console.print(
        ":magnifying_glass_tilted_right: Searching the latest file within AWS S3...",
        style="bold yellow",
    )
    console.print(f"Prefix: '{prefix}'.")
    console.print(f"Bucket: '{client.bucket}'.")
    files = sorted(client.iterate(prefix))
    if not files:
        _abort("No files found.")
    lst = files[-1]
    console.print(f"The latest file: '{lst}'.")
    console.print(f"Date: {extract_date(lst)}.")
    console.print("File is found :thumbs_up:", style="bold yellow")
    return lst


def _download_file(path: str, client: AwsS3Client) -> bytes:
    console.print(Rule("Download", align="center"))
    console.print(":mailbox: Downloading file from AWS S3...", style="bold yellow")
    console.print(f"Object: '{path}'.")
    console.print(f"Bucket: '{client.bucket}'.")
    if not client.is_bucket(search="local"):
        _abort("Bucket doesn't exist.")
    if not client.is_file(path):
        _abort("File doesn't exist.")
    file = client.download(path)
    console.print(f"Total size: {pretty_size(len(file))}.")
    console.print("File downloaded :thumbs_up:", style="bold yellow")
    return file


def _decrypt_file(data: bytes, secrets: Secrets) -> bytes:
    console.print(Rule("Decrypt", align="center"))
    console.print(":key: Starting decryption (in-memory)...", style="bold yellow")
    decrypted = decrypt_file(data, secrets.encrep_secret_key)
    console.print(f"Total size: {pretty_size(len(decrypted))}.")
    console.print("File decrypted :thumbs_up:", style="bold yellow")
    return decrypted


def _clone_bundle(decrypted: bytes, dest: pathlib.Path) -> None:
    console.print(Rule("Clone", align="center"))
    console.print(
        ":counterclockwise_arrows_button: Cloning a bundle...", style="bold yellow"
    )
    console.print(f"Repo directory: '{dest}'.")
    with tempfile.NamedTemporaryFile(
        "wb+", suffix=".bundle", delete_on_close=False
    ) as f:
        f.write(decrypted)
        f.close()
        git_clone_bundle(pathlib.Path(f.name), dest)
    console.print("Bundle cloned :thumbs_up:", style="bold yellow")


@restore_app.command("misc")
@trace
def restore_misc(
    name: NameParam = None,
    date: DateParam = None,
    dest: RepoOutParam = None,
    keys: KeysInParam = None,
) -> None:
    """Download the misc archive from AWS S3, decrypt it, and unarchive into a given directory.

    Misc archives contain files excluded from version control.
    """
    secrets = Secrets.from_file(keys)
    if dest.exists() and any(dest.iterdir()):
        console.print(f":exclamation: Destination directory '{dest}' is not empty.")
        if not Confirm.ask("Do you want to continue?"):
            _abort()
    with AwsS3Client(secrets) as client:
        prefix = get_extras_prefix(name)
        path = get_misc_path(name, date) if date else _find_latest(prefix, client)
        encrypted = _download_file(path, client)
    decrypted = _decrypt_file(encrypted, secrets)
    _unarchive_misc(decrypted, dest)


def _unarchive_misc(data: bytes, repo: pathlib.Path) -> None:
    console.print(Rule("Unarchive", align="center"))
    console.print(":file_cabinet: Extracting unversioned files...", style="bold yellow")
    console.print(f"Repo: '{repo}'.")
    permitted, suppressed, tot = unarchive(data, repo)
    console.print(f"Permitted: {permitted}.")
    console.print(f"Suppressed: {suppressed}.")
    console.print(f"Total size: {pretty_size(tot)}.")
    console.print("Files extracted :thumbs_up:", style="bold yellow")


# -----------------------------------------------------------------------------
# rm
# -----------------------------------------------------------------------------


ForceParam = Annotated[
    bool,
    Option(
        "--force",
        "-f",
        help="Don't ask before file deletion.",
    ),
]


@rm_app.command("project")
@trace
def rm_project(
    ctx: Context,
    name: NameParam = None,
    date: DateParam = None,
    keys: KeysInParam = None,
) -> None:
    """Invoke rm repo + rm misc with the same arguments."""
    ctx.invoke(rm_repo, name=name, date=date, keys=keys)
    ctx.invoke(rm_misc, name=name, date=date, keys=keys)


@rm_app.command("repo")
@trace
def rm_repo(
    name: NameParam = None,
    date: DateParam = None,
    force: ForceParam = False,
    keys: KeysInParam = None,
) -> None:
    """Delete a single repo bundle from AWS S3."""
    secrets = Secrets.from_file(keys)
    with AwsS3Client(secrets) as client:
        prefix = get_bundles_prefix(name)
        path = get_bundle_path(name, date) if date else _find_latest(prefix, client)
        _delete_file(path, force, client)


def _delete_file(path: str, force: bool, client: AwsS3Client) -> None:
    console.print(Rule("Delete", align="center"))
    console.print(":recycle: Deleting file...", style="bold yellow")
    _show_info(path, client.bucket)
    if not force and not Confirm.ask("Do you want to delete this file?"):
        _abort()
    client.remove(path)
    console.print("File deleted :thumbs_up:", style="bold yellow")


def _show_info(path: str, bucket: str) -> None:
    console.print(f"Repo: '{extract_repo(path)}'.")
    console.print(f"Filename: '{extract_filename(path)}'.")
    console.print(f"Date: {extract_date(path)}.")
    console.print(f"Object: '{path}'.")
    console.print(f"Bucket: '{bucket}'.")


@rm_app.command("misc")
@trace
def rm_misc(
    name: NameParam = None,
    date: DateParam = None,
    force: ForceParam = False,
    keys: KeysInParam = None,
) -> None:
    """Delete a single misc archive from AWS S3.

    Misc archives contain files excluded from version control.
    """
    secrets = Secrets.from_file(keys)
    with AwsS3Client(secrets) as client:
        prefix = get_extras_prefix(name)
        path = get_misc_path(name, date) if date else _find_latest(prefix, client)
        _delete_file(path, force, client)


StartDateParam = Annotated[
    datetime.datetime,  # datetime since Typer doesn't support date
    Option(
        "--start",
        "-s",
        help="Start date for a Git bundle or misc archive (earliest by default).",
        envvar="ENCREP_START",
        formats=["%Y-%m-%d"],
    ),
]


EndDateParam = Annotated[
    datetime.datetime,  # datetime since Typer doesn't support date
    Option(
        "--end",
        "-e",
        help="End date for a Git bundle or misc archive (latest by default).",
        envvar="ENCREP_END",
        formats=["%Y-%m-%d"],
    ),
]


@drop_app.command("project")
@trace
def drop_project(
    ctx: Context,
    name: NameParam = None,
    start: StartDateParam = datetime.datetime(datetime.MINYEAR, 1, 1),
    end: EndDateParam = datetime.datetime(datetime.MAXYEAR, 12, 31),
    keys: KeysInParam = None,
) -> None:
    """Invoke drop repo + drop misc with the same arguments."""
    ctx.invoke(drop_repo, name=name, start=start, end=end, keys=keys)
    ctx.invoke(drop_misc, name=name, start=start, end=end, keys=keys)


@drop_app.command("repo")
@trace
def drop_repo(
    name: NameParam = None,
    start: StartDateParam = datetime.datetime(datetime.MINYEAR, 1, 1),
    end: EndDateParam = datetime.datetime(datetime.MAXYEAR, 12, 31),
    keys: KeysInParam = None,
) -> None:
    """Delete all repo bundles within a given date range from AWS S3."""
    secrets = Secrets.from_file(keys)
    with AwsS3Client(secrets) as client:
        prefix = get_bundles_prefix(name)
        files = _filter_by_date(prefix, start, end, client)
        if not Confirm.ask("Do you want to delete these files?"):
            _abort()
        for file in files:
            _delete_file(file, True, client)


def _filter_by_date(
    prefix: str,
    start: datetime.datetime,
    end: datetime.datetime,
    client: AwsS3Client,
) -> list[str]:
    console.print(Rule("Search", align="center"))
    console.print(
        ":magnifying_glass_tilted_right: Searching files in AWS S3...",
        style="bold yellow",
    )
    console.print(f"Prefix: '{prefix}'.")
    console.print(f"Bucket: '{client.bucket}'.")
    console.print(f"Start date: {start.strftime('%Y-%m-%d')}.")
    console.print(f"End date: {end.strftime('%Y-%m-%d')}.")
    files = [
        file
        for file in client.iterate(prefix)
        if start <= datetime.datetime.fromisoformat(extract_date(file)) <= end
    ]
    if not files:
        _abort("No files found.")
    console.print("Files found:")
    for file in files:
        console.print(f"{file}", style="cyan")
    console.print(f"Total files: {len(files)}.")
    console.print("Files are found :thumbs_up:", style="bold yellow")
    return files


@drop_app.command("misc")
@trace
def drop_misc(
    name: NameParam = None,
    start: StartDateParam = datetime.datetime(datetime.MINYEAR, 1, 1),
    end: EndDateParam = datetime.datetime(datetime.MAXYEAR, 12, 31),
    keys: KeysInParam = None,
) -> None:
    """Delete all misc archives within a given date range from AWS S3."""
    secrets = Secrets.from_file(keys)
    with AwsS3Client(secrets) as client:
        prefix = get_extras_prefix(name)
        files = _filter_by_date(prefix, start, end, client)
        if not Confirm.ask("Do you want to delete these files?"):
            _abort()
        for file in files:
            _delete_file(file, True, client)


# Main


def version_callback(value: bool | None) -> None:
    """Print a current app version."""
    if value is not None:
        console.print("Version", __version__)


VersionParam = Annotated[
    bool,
    Option(
        "--version",
        "-v",
        help="Print a current version.",
        callback=version_callback,
        is_eager=True,
    ),
]


@app.callback()
def main(_: VersionParam = None) -> None:
    """Encrep

    CLI tool for dumping and restoring Git repos via AWS S3.
    Encryption, easy management, and pretty printing.
    """
