from importlib.metadata import PackageNotFoundError, metadata, version

try:
    # NAME = __package__ or __name__
    NAME: str = "pyipxact-de"

    meta = metadata(NAME)
    __version__: str = version(NAME)
    __author__: str = meta.get("author", "")
    __author_email__: str = meta.get("author-email", "")
    # __maintainer__ = meta.get("maintainer", "")
    # __maintainer_email = meta.get("maintainer-email", "")
    __license__: str = meta.get("license", "")
    __url__: str = meta.get("home-page", "")
    __description__: str = meta.get("summary", "")
except PackageNotFoundError:
    __version__ = "0.0.0"
    __author__ = ""
    __author_email__ = ""
    # __maintainer__ = ""
    # __maintainer_email = ""
    __license__ = ""
    __url__ = ""
    __description__ = "Accellera IP-XACT CLI Tool"


__all__ = (
    "__version__",
    "__author__",
    "__author_email__",
    # "__maintainer__",
    # "__maintainer_email",
    "__license__",
    "__url__",
    "__description__",
)

# print(__version__)
# print(__author__)
# print(__author_email__)
# # print(__maintainer__)
# # print(__maintainer_email)
# print(__license__)
# print(__url__)
# print(__description__)
