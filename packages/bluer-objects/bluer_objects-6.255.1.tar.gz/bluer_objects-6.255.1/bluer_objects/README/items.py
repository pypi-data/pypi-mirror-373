from typing import List, Dict


# {image,jpg : url}
def ImageItems(items: Dict[str, str]) -> List[str]:
    def add_raw(url: str) -> str:
        return (
            f"{url}?raw=true" if "github.com" in url and "raw=true" not in url else url
        )

    return [
        (
            ""
            if not image
            else "[![image]({})]({})".format(
                add_raw(image), url if url else add_raw(image)
            )
        )
        for image, url in items.items()
    ]


# name, url, marquee, description
def Items(
    items: List[Dict[str, str]],
    sort: bool = False,
) -> List[str]:
    output = [
        (
            "{}[![image]({})]({}) {}".format(
                (
                    "[`{}`]({}) ".format(
                        item["name"],
                        item.get(
                            "url",
                            "#",
                        ),
                    )
                    if item["name"]
                    else ""
                ),
                item.get(
                    "marquee",
                    "https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true",
                ),
                item.get(
                    "url",
                    "#",
                ),
                item.get("description", ""),
            )
            if "name" in item
            else ""
        )
        for item in items
    ]

    if sort:
        output = sorted(output)

    return output
