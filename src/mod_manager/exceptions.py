class PackageMissingError(Exception):
    def __init__(self, pkg):
        super().__init__(f"Package {pkg} is missing from given index")


class InvalidVersionError(Exception):
    def __init__(self, pkg, version):
        super().__init__(f"Version {version} for pkg {pkg} is missing from given index")


class InvalidCommunityError(Exception):
    def __init__(self, c):
        super().__init__(f"Community {c} is an invalid community, cannot grab package index")
