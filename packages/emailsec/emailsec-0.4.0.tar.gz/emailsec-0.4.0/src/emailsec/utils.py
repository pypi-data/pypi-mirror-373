import re
import collections

Body = bytes
Header = tuple[bytes, bytes]
Headers = dict[str, list[Header]]

type BodyAndHeaders = tuple[Body, Headers]


def body_and_headers_for_canonicalization(message: bytes) -> BodyAndHeaders:
    lines = re.split(b"\r?\n", message)

    headers_idx = collections.defaultdict(list)
    headers = []
    for header_line in lines[: lines.index(b"")]:
        if (m := re.match(rb"([\x21-\x7e]+?):", header_line)) is not None:
            header_name = m.group(1)
            header_value = header_line[m.end() :] + b"\r\n"
            headers.append([header_name, header_value])
        elif header_line.startswith(b" ") or header_line.startswith(b"\t"):
            # Unfold header values
            headers[-1][1] += header_line + b"\r\n"
        else:
            raise ValueError(f"Invalid line {header_line!r}")

    for header_name, header_value in headers:
        headers_idx[header_name.decode().lower()].append((header_name, header_value))

    try:
        # Split on the first empty line and join the remaining ones with CRLF
        can_body = b"\r\n".join(lines[lines.index(b"") + 1 :])
    except ValueError:
        # No body defaults to CRLF
        can_body = b"\r\n"

    return can_body, dict(headers_idx)


def header_value(headers: Headers, header_name: str) -> str:
    """Returns the first value matching the header name (case-insensitive lookup)."""
    return headers[header_name][0][1].decode().strip()
