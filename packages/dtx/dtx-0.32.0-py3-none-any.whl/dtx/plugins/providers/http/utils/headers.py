from typing import Dict, Optional


class HeaderUtils:
    """
    A utility class for handling HTTP headers while maintaining case sensitivity
    but allowing case-insensitive lookup.

    Usage:
    ```
    headers = HeaderUtils({
        "Content-Type": "application/json",
        "Authorization": "Bearer my_token",
        "Cookie": "sessionid=xyz"
    })

    print(headers.get("content-type"))  # application/json (case-insensitive lookup)
    print(headers.is_content_type("application/json"))  # True
    print(headers.is_json())  # True
    ```

    Attributes:
        headers (dict): A dictionary storing HTTP headers with case-sensitive keys.
    """

    def __init__(self, headers: Dict[str, str]):
        """
        Initializes the HeaderUtils instance with given headers.

        Args:
            headers (dict): The HTTP headers to store (case-sensitive keys).
        """
        self.headers = headers  # Store headers as-is (case-sensitive)
        self._lowercase_map = {
            k.lower(): k for k in headers
        }  # Mapping for case-insensitive lookup

    def get(self, header_key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieves the value of a header using case-insensitive lookup.

        Args:
            header_key (str): The header key to look up.
            default (str, optional): The default value if the header is not found.

        Returns:
            str | None: The header value if found, else `default`.
        """
        original_key = self._lowercase_map.get(header_key.lower())
        return self.headers.get(original_key, default) if original_key else default

    def content_type(self) -> Optional[str]:
        """
        Returns the `Content-Type` header value.

        Returns:
            str | None: The `Content-Type` value if present, otherwise `None`.
        """
        return self.get("Content-Type")

    def cookie(self) -> Optional[str]:
        """
        Returns the `Cookie` header value.

        Returns:
            str | None: The `Cookie` value if present, otherwise `None`.
        """
        return self.get("Cookie")

    def is_content_type(self, content_type: str) -> bool:
        """
        Checks if the `Content-Type` header matches a given value (case-insensitive).

        Args:
            content_type (str): The content type to compare.

        Returns:
            bool: `True` if the `Content-Type` matches the given value, otherwise `False`.
        """
        actual_content_type = self.content_type()
        return (
            actual_content_type.lower() == content_type.lower()
            if actual_content_type
            else False
        )

    def is_json(self) -> bool:
        """
        Checks if the `Content-Type` is JSON (`application/json` or `application/*+json`).

        Returns:
            bool: `True` if the `Content-Type` indicates JSON, otherwise `False`.
        """
        content_type = self.content_type()
        return content_type and (
            "application/json" in content_type.lower()
            or "+json" in content_type.lower()
        )

    def __repr__(self):
        return f"HeaderUtils({self.headers})"


# Example Usage
if __name__ == "__main__":
    headers = HeaderUtils(
        {
            "Content-Type": "application/json",
            "Authorization": "Bearer my_token",
            "Cookie": "sessionid=xyz",
        }
    )

    print("Content-Type:", headers.content_type())  # application/json
    print("Authorization:", headers.get("authorization"))  # Bearer my_token
    print("Cookie:", headers.cookie())  # sessionid=xyz
    print("Is JSON Content-Type:", headers.is_json())  # True
    print(
        "Is Content-Type application/xml:", headers.is_content_type("application/xml")
    )  # False
