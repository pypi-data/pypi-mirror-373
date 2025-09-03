
import re
from semver.version import Version as sem_version
from packaging import version as pkg_version


linux_version_pattern = re.compile(
    r"^"
    # epoch must start with a digit
    r"(\d+:)?"
    # upstream must start with a digit
    r"\d"
    r"("
    # upstream  can contain only alphanumerics and the characters . + -
    # ~ (full stop, plus, hyphen, tilde)
    r"[A-Za-z0-9\.\+\~\-]+"
    r"|"
    # If there is no debian_revision then hyphens are not allowed in version.
    r"[A-Za-z0-9\.\+\~]+-[A-Za-z0-9\+\.\~]+"
    r")?"
    r"$"
)
irregular_version_pattern = re.compile(r'\d+(\.\d+)*')

def parse_version(text):
    """ Semantic Versioning (SemVer)
     Date-based Versioning
     Alphanumeric or Custom Schemes
     Debian based version parser
     Ubuntu based version parser
     parse version with build:
    """
    if not text:
        return None

    if linux_version_pattern.match(text):
        match = linux_version_pattern.search(text)
        if match:
            version = match.group()
            if ":" in version:
                epoch, _, version = version.partition(":")
                epoch = int(epoch)
            else:
                epoch = 0

            if "-" in version:
                upstream, _, revision = version.rpartition("-")
            else:
                upstream = version
                revision = "0"

            version = upstream
            regex_matched = False

            if 'ubuntu' in version:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()
            elif 'debian' in version:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()
            elif 'git' in version:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()
            elif '-' in version:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()
            else:
                match = irregular_version_pattern.search(version)
                if match:
                    regex_matched = True
                    version = match.group()

            parsed = None
            if not regex_matched:
                try:
                    parsed = sem_version.parse(version)
                except ValueError:
                    try:
                        parsed = pkg_version.parse(version)
                    except pkg_version.InvalidVersion:
                        parsed = None

            if parsed:
                parsed_split_len = len(str(parsed).split("."))
                if parsed_split_len < 3:
                    version = [str(parsed.major), str(parsed.minor)]
                elif parsed_split_len == 3:
                    try:
                        version = [str(parsed.major), str(parsed.minor), str(parsed.patch)]
                    except AttributeError:
                        version = [str(parsed.major), str(parsed.minor), str(parsed.micro)]
                else:
                    version = parsed

                if isinstance(version, list):
                    version = ".".join(version)
                else:
                    version = version
            else:
                if not regex_matched:
                    print(f'Cannot definitely parse version {text}')
            return version