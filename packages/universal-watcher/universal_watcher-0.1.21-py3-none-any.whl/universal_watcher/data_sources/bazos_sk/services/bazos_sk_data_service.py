import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

from ....core.decorators.injector import DependencyInjector as Injector
from .bazos_sk_db_service import BazosSkDbService
from ..models.bazos_sk_parameters import BazosSkParameters
from ..models.bazos_sk_item import BazosSkItem
from ..config import BASE_URL


@Injector.inject_as_singleton
@Injector.inject_dependencies
class BazosSkDataService:
    def __init__(self, *, db_service: BazosSkDbService, http_client=requests):
        self._db_service = db_service
        self._http_client = http_client

    def _build_url(self, params: BazosSkParameters) -> str:
        """
        Constructs a URL with query parameters based on the provided
        parameters and defaults from the BazosSkParameters model.

        Args:
            params (BazosSkParameters): An instance of BazosSkParameters containing
                                        the parameters to include in the URL. If a
                                        parameter is not provided, its default value
                                        from the model will be used.

        Returns:
            str: The constructed URL with encoded query parameters.
        """
        uri_param_names = {
            field_name: field_info.json_schema_extra["uri_param_name"]
            for field_name, field_info in params.model_fields.items()
        }

        uri = ""
        for i, (param_name, param_value) in enumerate(
            params.model_dump().items()
        ):
            if not param_value:
                continue

            url_param_value = urllib.parse.quote(str(param_value))
            url_param_name = uri_param_names[param_name]            

            if url_param_name == "rub":
                url_param_value = url_param_value[:2]

            if i != 0:
                uri += "&"

            uri += f"{url_param_name}={url_param_value}"

        return f"{BASE_URL}?{uri}"

    def _parse_response_xml(self, content: str) -> list[BazosSkItem]:
        """
        Parses the XML response from the server.

        Args:
            content (str): The XML content as a string.

        Returns:
            list: A list of dictionaries containing the parsed data.
        """
        root = ET.fromstring(content)
        items = []
        for item in root.findall(".//item"):
            title_parts = item.find("title").text.strip().split(":")
            title = ":".join(title_parts[:-1])
            url = item.find("link").text
            description = item.find("description").text
            pub_date = item.find("pubDate").text
            price_str = title_parts[-1].strip()

            # Remove the image tag from the description
            if description.startswith("<img"):
                index = description.find("/>")
                description = description[index + 2 :]

            pub_date_datetime = datetime.strptime(
                pub_date, "%a, %d %b %Y %H:%M:%S %z"
            )
            items.append(
                BazosSkItem(
                    title=title,
                    price=price_str,
                    url=url,
                    description=description,
                    pub_date=pub_date_datetime,
                )
            )

        return items

    def get_items(self, params: BazosSkParameters) -> list[BazosSkItem]:
        """
        Fetches data from the Bazos.sk RSS feed based on the provided parameters.

        Args:
            params (BazosSkParameters): Parameters to include in the URL. If a
                           parameter is not provided, its default value from the
                           model will be used.

        Raises:
            Exception: If the request to the Bazos.sk RSS feed fails.

        Returns:
            list: A list of dictionaries containing the parsed data from
            the RSS feed.
        """
        url = self._build_url(params)
        response = self._http_client.get(url)

        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch data from {url}. Response code: {response.status_code}"
            )

        return self._parse_response_xml(response.text)
