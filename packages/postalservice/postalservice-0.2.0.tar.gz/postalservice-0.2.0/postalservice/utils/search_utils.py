import json


class SearchResults:
    """
    Represents a collection of search results.
    Fields for each item:
    id -> string
    title -> string
    price -> float
    brand -> string
    size -> string
    url -> string
    img -> list of string
    """

    def __init__(self, results_json: str):
        try:
            results = json.loads(results_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string")

        for result in results:
            if not all(
                key in result for key in ["id", "title", "price", "size", "url", "img"]
            ):
                raise ValueError("Missing expected key in result, ", result)
            if not isinstance(result["id"], str):
                raise ValueError(f"id must be a string, not {type(result['id'])}")
            if not isinstance(result["title"], str):
                raise ValueError(f"title must be a string, not {type(result['title'])}")
            if not isinstance(result["price"], float):
                raise ValueError(f"price must be a float, not {type(result['price'])}")
            if not isinstance(result["brand"], str):
                raise ValueError(f"brand must be a string, not {type(result['brand'])}")
            if result["size"]:
                if not isinstance(result["size"], str):
                    raise ValueError(
                        f"size must be a string, not {type(result['size'])}"
                    )
            if not isinstance(result["url"], str):
                raise ValueError(f"url must be a string, not {type(result['url'])}")
            if not isinstance(result["img"], list) or not all(
                isinstance(i, str) for i in result["img"]
            ):
                raise ValueError(
                    f"img must be a list of strings, not {type(result['img'])}"
                )

        self.results: list = results

    def get(self, index: int) -> dict:
        """
        Returns the search result at the specified index as a dictionary.
        If the index is out of range, an empty dictionary is returned.
        """
        try:
            return self.results[index]
        except IndexError:
            return {}

    def to_json(self) -> str:
        """
        Returns the search results as a JSON string.
        """
        return json.dumps(self.results)

    def to_list(self) -> list:
        """
        Returns the search results as a list of dictionaries.
        """
        return self.results

    def count(self) -> int:
        """
        Returns the total number of search results.
        """
        return len(self.results)

    def __str__(self) -> str:
        return json.dumps(self.results, indent=4, ensure_ascii=False)
