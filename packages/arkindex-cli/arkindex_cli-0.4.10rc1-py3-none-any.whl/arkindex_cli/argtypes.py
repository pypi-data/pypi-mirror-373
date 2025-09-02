from urllib.parse import urlsplit, urlunsplit


class URLArgument:
    def __init__(
        self,
        default_scheme="https",
        allow_path=True,
        allow_query=True,
        allow_fragment=False,
    ):
        self.default_scheme = default_scheme
        self.allow_path = allow_path
        self.allow_query = allow_query
        self.allow_fragment = allow_fragment

    def __call__(self, value):
        try:
            parsed = urlsplit(value)
        except ValueError:
            raise ValueError(f"{value!r} is not a valid URL")

        if not self.allow_path and parsed.path:
            raise ValueError(f"{value!r} cannot have a path")

        if not self.allow_query and parsed.query:
            raise ValueError(
                f"URL {value!r} cannot have query parameters ({parsed.query!r})"
            )

        if not self.allow_fragment and parsed.fragment:
            raise ValueError(
                f"URL {value!r} cannot have a fragment ({parsed.fragment!r})"
            )

        if not parsed.scheme and self.default_scheme:
            # Rebuild the URL with the added scheme
            if parsed.path and not parsed.netloc:
                # When there is no scheme and no '//', the string is assumed to be the path
                # instead of the netloc (the hostname). This causes a string like 'arkindex.teklia.com'
                # to not be properly understood, so we reassign the attributes properly
                # by removing the part before the slash
                netloc, _, path = parsed.path.partition("/")
            else:
                netloc, path = parsed.netloc, parsed.path

            value = urlunsplit((self.default_scheme, netloc, path, *parsed[3:]))

        return value
