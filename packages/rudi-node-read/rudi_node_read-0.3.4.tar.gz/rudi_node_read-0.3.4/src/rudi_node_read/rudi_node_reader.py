from json import dumps
from os.path import isdir
from typing import Union

from termcolor import colored

from rudi_node_read.connectors.io_connector import https_download
from rudi_node_read.connectors.io_rudi_node_read import RudiNodeConnector
from rudi_node_read.utils.log import log_d
from rudi_node_read.utils.type_dict import (
    filter_dict_list,
    find_in_dict_list,
    pick_in_dict,
    safe_get_key,
)
from rudi_node_read.utils.type_string import absolute_path

_STATUS_SKIPPED = "skipped"
_STATUS_MISSING = "missing"
_STATUS_DOWNLOADED = "downloaded"

LONG_SEP = "========================================================================"
RUDI_ART = """
                    ______    __   __  ______   ___
                    |    _ |  |  | |  ||      | |   |
                    |   | ||  |  | |  ||  _    ||   |
                    |   |_||_ |  |_|  || | |   ||   |
                    |    __  ||       || |_|   ||   |
                    |   |  | ||       ||       ||   |
                    |___|  |_||_______||______| |___|
"""  # http://patorjk.com/software/taag/#p=display&c=c%2B%2B&w=%20&f=Modular&t=RUDI


class RudiNodeReader:
    _default_getter = None

    def __init__(self, server_url: str, headers_user_agent: str = "RudiNodeReader"):
        here = "RudiNodeReader.__init__"
        self._server_url = server_url
        self._headers_user_agent = headers_user_agent
        log_d(here, "connecting")
        self._connector = RudiNodeConnector(self._server_url, self._headers_user_agent)
        log_d(here, self._connector)

        self._meta_list = None
        self._meta_list_available = None
        self._meta_count = 0
        self._org_list = None
        self._org_names = None
        self._contact_list = None
        self._contact_names = None
        self._themes = None
        self._keywords = None

    def _reset_cache(self) -> None:
        """
        Resets the cached metadata
        """
        self._meta_list = None
        self._meta_list_available = None
        self._meta_count = 0
        self._org_list = None
        self._org_names = None
        self._contact_list = None
        self._contact_names = None
        self._themes = None
        self._keywords = None

    @property
    def server_url(self) -> str:
        """
        :return: the URL of the RUDI Producer node
        """
        return self._server_url

    @property
    def connector(self) -> RudiNodeConnector:
        """
        :return: the RudiNodeConnector object used for requesting the RUDI node
        """
        if not self._connector:
            self._connector = RudiNodeConnector(self._server_url, self._headers_user_agent)
        return self._connector

    def connect(self, server_url: str, headers_user_agent: str = "RudiNodeGet") -> None:
        """
        Reinitialize the connection to a RUDI node
        :param server_url: the URL of the RUDI node
        :param headers_user_agent: (optional) a way to identify the requests made to the node
        """
        self._server_url = server_url
        self._headers_user_agent = headers_user_agent
        self._connector = RudiNodeConnector(self._server_url, self._headers_user_agent)
        self._reset_cache()

    @property
    def light_node_summary_title(self) -> str:
        """
        Return a str with a nice and colored summary of the rudi-node
        """
        node_summary = colored(LONG_SEP, color="magenta")
        node_summary += colored(RUDI_ART, color="green", attrs=["bold"])
        node_summary += f"\n{colored('node url', color='green')} : {self.server_url}"
        node_summary += f"\n{colored('metadata count', color='green')} : {self.metadata_count}\n"
        node_summary += f"{colored(LONG_SEP, color='magenta')}\n"
        return node_summary

    @property
    def catalogue_summary(self) -> str:
        """
        Return a str with a light catalogue summary
        """
        catalogue_summary = self.light_node_summary_title
        catalogue_summary += self.create_textual_description_metadata(self.metadata_list)
        return catalogue_summary

    @property
    def metadata_count(self) -> int:
        """
        :return: the number of metadata stored on the RUDI Producer node
        """
        if not self._meta_count:
            self._meta_count = self.connector.get_metadata_count()
        return self._meta_count

    @property
    def metadata_list(self) -> list[dict]:
        """
        :return: the full list of the metadata stored on the RUDI Producer node
        """
        if not self._meta_list:
            self._meta_list = self.connector.get_metadata_list()

        return self._meta_list

    @property
    def organization_list(self) -> list[dict]:
        """
        :return: the list of the organizations that appear in the metadata
        (both data producer and metadata publisher)
        """
        if not self._org_list:
            self._org_list = []
            for meta in self.metadata_list:
                producer_info = safe_get_key(meta, "producer")
                publisher_info = safe_get_key(meta, "metadata_info", "metadata_provider")

                producer_id = safe_get_key(producer_info, "organization_id")
                was_producer_found = not producer_id

                publisher_id = safe_get_key(publisher_info, "organization_id")
                was_publisher_found = not publisher_id or publisher_id == producer_id

                for org in self._org_list:
                    if was_producer_found and was_publisher_found:
                        break
                    org_id = safe_get_key(org, "organization_id")
                    if not was_producer_found and org_id == producer_id:
                        was_producer_found = True
                    if not was_publisher_found and org_id == publisher_id:
                        was_publisher_found = True

                if not was_producer_found:
                    self._org_list.append(producer_info)
                if not was_publisher_found:
                    self._org_list.append(publisher_info)

        return self._org_list

    @property
    def organization_names(self) -> list[str]:
        """
        :return: the list of the names of the organizations that appear in the metadata
        (both data producer and metadata publisher)
        """
        if not self._org_names:
            self._org_names = []
            for org in self.organization_list:
                self._org_names.append(safe_get_key(org, "organization_name"))
        self._org_names.sort()
        return self._org_names

    @property
    def contact_list(self) -> list[dict]:
        """
        :return: the list of the contacts declared in the RUDI node metadata
        """
        if not self._contact_list:
            self._contact_list = []
            for meta in self.metadata_list:
                meta_contacts = safe_get_key(meta, "contacts")
                publ_contacts = safe_get_key(meta, "metadata_info", "metadata_contacts")
                if publ_contacts:
                    meta_contacts = meta_contacts + publ_contacts

                if meta_contacts:
                    for prod_contact in meta_contacts:
                        prod_contact_id = safe_get_key(prod_contact, "contact_id")
                        if prod_contact_id:
                            if not find_in_dict_list(self._contact_list, {"contact_id": prod_contact_id}):
                                self._contact_list.append(prod_contact)

        return self._contact_list

    @property
    def contact_names(self) -> list[str]:
        """
        :return: the list of the names of the contacts declared in the RUDI node metadata
        """
        if not self._contact_names:
            self._contact_names = []
            for contact in self.contact_list:
                self._contact_names.append(safe_get_key(contact, "contact_name"))
        self._contact_names.sort()
        return self._contact_names

    @property
    def themes(self) -> list[str]:
        """
        :return: the list of the themes declared in the RUDI node metadata
        """
        if self._themes is None:
            self._themes = []
            for meta in self.metadata_list:
                theme = safe_get_key(meta, "theme")
                if theme and theme not in self._themes:
                    self._themes.append(theme)
        self._themes.sort()
        return self._themes

    @property
    def keywords(self) -> list[str]:
        """
        :return: the list of the keywords declared in the RUDI node metadata
        """
        if self._keywords is None:
            self._keywords = []
            for meta in self.metadata_list:
                keywords = safe_get_key(meta, "keywords")
                if keywords:
                    for kword in keywords:
                        if kword not in self._keywords:
                            self._keywords.append(kword)
        self._keywords.sort()
        return self._keywords

    def filter_metadata(self, matching_filter: dict) -> list[dict]:
        """
        Returns an object with the following attributes:
        - total: the number of metadata that match the filter
        - items: the list of the metadata that match the filter
        :param matching_filter: JSON-like object whose attributes are all matched in the resulting
        metadata list
        :return: list of the metadata that match the filter
        """
        """
        items = filter_dict_list(self.metadata_list, matching_filter)
        total = len(items)
        return {'total': total, 'items': items}
        """
        return filter_dict_list(self.metadata_list, matching_filter)

    @property
    def metadata_with_available_media(self) -> list[dict]:
        """
        :return: list of the metadata whose `available_data` attribute contains at least one media for which
        `file_storage_status`attribute is set to `available`
        """
        if self._meta_list_available is None:
            self._meta_list_available = self.filter_metadata(
                {"available_formats": [{"file_storage_status": "available"}]}
            )
        return self._meta_list_available

    def get_metadata_with_producer(self, producer_name: str) -> list[dict]:
        """
        :param producer_name: the meta_contact of the organization declared in the metadata
        :return: list of the metadata whose `producer.organization_name` attribute matches the `producer_name` input
        parameter
        """
        return self.filter_metadata({"producer": {"organization_name": producer_name}})

    def get_metadata_with_contact(self, contact_name: str) -> list[dict]:
        """
        :param contact_name: the meta_contact of the contact declared in the metadata
        :return: list of the metadata whose `contacts` attribute contains a contact object whose `contact_name`
        attribute matches the `contact_name` input parameter
        """
        return self.filter_metadata({"contacts": [{"contact_name": contact_name}]})

    def get_metadata_with_theme(self, theme: str) -> list[dict]:
        """
        :param theme: a string used to filter the metadata by theme
        :return: list of the metadata whose `theme` attribute matches the `theme` input parameter
        """
        return self.filter_metadata({"theme": theme})

    def get_metadata_with_keywords(self, keywords: Union[str, list]) -> list[dict]:
        """
        :param keywords: a string or a list of strings used to filter the metadata by keywords
        :return: list of the metadata whose `keywords` attribute contains every `keywords` input parameter
        """
        return self.filter_metadata({"keywords": keywords})

    def find_metadata_with_uuid(self, metadata_id: str) -> dict | None:
        """
        :param metadata_id: a UUIDv4 string
        :return: metadata whose `global_id` attribute matches the `metadata_id` input parameter
        """
        return find_in_dict_list(self.metadata_list, {"global_id": metadata_id})

    def find_metadata_with_source_id(self, source_id: str) -> dict | None:
        """
        :param source_id: a string that was used in the producer data source to identify the dataset
        :return: metadata whose `local_id` attribute matches the `media_name` input parameter
        """
        return find_in_dict_list(self.metadata_list, {"local_id": source_id})

    def find_metadata_with_title(self, title: str) -> dict | None:
        """
        :param title: media_name of the metadata
        :return: metadata whose `resource_title` attribute matches the `media_name` input parameter
        """
        return find_in_dict_list(self.metadata_list, {"resource_title": title})

    def find_metadata_with_media_name(self, media_name: str) -> dict | None:
        """
        :param media_name: meta_contact of the media
        :return: metadata whose `resource_title` attribute matches the `title` input parameter
        """
        return find_in_dict_list(self.metadata_list, {"available_formats": [{"media_name": media_name}]})

    def find_metadata_with_media_uuid(self, media_uuid: str) -> dict | None:
        """
        :param media_uuid: UUIDv4 of the media
        :return: metadata whose `resource_title` attribute matches the `title` input parameter
        """
        return find_in_dict_list(self.metadata_list, {"available_formats": [{"media_id": media_uuid}]})

    def create_textual_description_single_metadata(self, metadata: dict | str) -> str:
        """
        Return a small textual description of a single metadata, including title, metadata url and medias url
        :param metadata: a metadata (as json) or the global uuid of the metadata
        :return: a python str with the description of the metadata
        """
        if isinstance(metadata, str):
            metadata_ = self.find_metadata_with_uuid(metadata)
            if metadata_ is None:
                raise Exception(f"No metadata with uuid {metadata} was found on rudi node.")
            metadata = metadata_
        resource_title = metadata["resource_title"]
        meta_link = f"{self.server_url}/api/v1/resources/{metadata['global_id']}"
        files_str = "\n"
        for each_file in metadata["available_formats"]:
            files_str += f"    {each_file['connector']['url']},\n"

        textual_desc = f"""\n {colored(resource_title, 'magenta', attrs=['bold', 'underline'])} :\n    {colored('Métadonnée', attrs=['bold'])} : {meta_link} ,\n    {colored('Résumé', attrs=['bold'])} : {metadata["summary"][0]["text"]} ,\n    {colored('Fichier(s)', attrs=['bold'])} : {files_str}\n"""
        return textual_desc

    def create_textual_description_metadata(
        self,
        metadata: dict | str | list[str] | list[dict],
        show_node_summary: bool = False,
    ) -> str:
        """
        Provide a small and light textual description of a single metadata or a list of metadata, including title, metadata url and medias url
        :param metadata: a metadata (as json) or the global uuid of the metadata or a list of metadata or a list of uuids
        :param show_node_summary: if True, adds a small and nice summary of the node to the output of the function
        :return: a python str with the description of the metadata
        """
        if isinstance(metadata, dict) or isinstance(metadata, str):
            return self.create_textual_description_single_metadata(metadata)

        result = self.light_node_summary_title if show_node_summary else ""
        for each_metadata in metadata:
            result += self.create_textual_description_single_metadata(each_metadata)
        return result

    @staticmethod
    def _download_media_from_info(media: dict, local_download_dir: str) -> dict:
        """
        Download a file from its media metadata
        :param media: the file metadata (as found in the RUDI metadata `available_formats` attribute
        :param local_download_dir: the path to a local folder
        :return: an object that states if the file was downloaded, skipped or found missing
        """
        media_type = safe_get_key(media, "media_type")

        # Most likely for media_type == 'SERVICE'
        if media_type != "FILE":
            return {
                "status": _STATUS_SKIPPED,
                "media": pick_in_dict(media, ["media_name", "media_id", "media_url", "media_type"]),
            }

        # If the file is not available on storage, we won't try to download it.
        if safe_get_key(media, "file_storage_status") != "available":
            return {
                "status": _STATUS_MISSING,
                "media": pick_in_dict(
                    media,
                    [
                        "media_name",
                        "media_id",
                        "media_url",
                        "file_type",
                        "file_storage_status",
                    ],
                ),
            }

        # The metadata says the file is available, let's download it
        if not isdir(local_download_dir):
            raise FileNotFoundError(f"The following folder does not exist: '{local_download_dir}'")

        media_name = safe_get_key(media, "media_name")
        media_url = safe_get_key(media, "connector", "url")

        destination_path = absolute_path(local_download_dir, media_name)
        content = https_download(media_url)
        open(destination_path, "wb").write(content)
        log_d("media_download", "content saved to file", destination_path)

        file_info = {
            "media_name": media_name,
            "media_id": safe_get_key(media, "media_id"),
            "media_url": media_url,
            "file_type": safe_get_key(media, "file_type"),
            "created": safe_get_key(media, "media_dates", "created"),
            "updated": safe_get_key(media, "media_dates", "updated"),
            "file_path": destination_path,
        }
        return {"status": _STATUS_DOWNLOADED, "media": file_info}

    def download_file_with_uuid(self, media_uuid: str, local_download_dir: str) -> dict | None:
        """
        Download a file identified with the input UUID
        :param media_uuid: a UUIDv4 that identifies the media on the RUDI node
        :param local_download_dir: the path to a local folder
        :return: an object that states if the file was downloaded, skipped or found missing
        """
        meta = self.find_metadata_with_media_uuid(media_uuid)
        media_list = safe_get_key(meta, "available_formats")
        if not media_list:
            return None

        media = find_in_dict_list(media_list, {"media_id": media_uuid})
        return self._download_media_from_info(media, local_download_dir)

    def download_file_with_name(self, media_name: str, local_download_dir: str) -> dict | None:
        """
        Find a file from its name and download it if it is available
        :param media_name: the name of the file we want to download
        :param local_download_dir: the path to a local folder
        :return: an object that states if the file was downloaded, skipped or found missing
        """
        meta = self.find_metadata_with_media_name(media_name)
        media_list = safe_get_key(meta, "available_formats")
        if not media_list:
            return None
        media = find_in_dict_list(media_list, {"media_name": media_name})
        return self._download_media_from_info(media, local_download_dir)

    def download_files_for_metadata(self, metadata_id, local_download_dir) -> dict | None:
        """
        Download all the available files for a metadata
        :param metadata_id: the UUIDv4 of the metadata
        :param local_download_dir: the path to a local folder
        :return: an object that lists the files that were downloaded, skipped or found missing
        """
        if not isdir(local_download_dir):
            raise FileNotFoundError(f"The following folder does not exist: '{local_download_dir}'")

        meta = self.find_metadata_with_uuid(metadata_id)
        media_list = safe_get_key(meta, "available_formats")
        if not media_list:
            return None
        files_dwnld_info: dict = {
            _STATUS_DOWNLOADED: [],
            _STATUS_MISSING: [],
            _STATUS_SKIPPED: [],
        }
        for media in media_list:
            dwnld_info = self._download_media_from_info(media, local_download_dir)
            status = dwnld_info["status"]
            files_dwnld_info[status].append(dwnld_info["media"])
        return files_dwnld_info

    def save_metadata_to_file(self, local_download_dir: str, file_name: str = "rudi_node_metadata.json") -> None:
        """
        Dumps the metadata list to a local file
        :param local_download_dir: the path to a local folder
        :param file_name: the name of the file in which the JSON representation of the list of metadata will be saved
        """
        file_path = absolute_path(local_download_dir, file_name)
        json_str = dumps(obj=self.metadata_list, ensure_ascii=False, indent=2).encode("utf-8")
        open(file_path, "wb").write(json_str)
