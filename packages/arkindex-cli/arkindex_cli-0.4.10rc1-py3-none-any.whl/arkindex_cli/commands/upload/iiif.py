import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote_plus, urlparse
from uuid import UUID

from arkindex.exceptions import ErrorResponse
from rich import print
from rich.progress import Progress

from arkindex_cli.auth import Profiles

SIMPLE_URL_REGEX = re.compile("^http(s)?://")


def add_iiif_parser(subcommands):
    iiif_parser = subcommands.add_parser(
        "iiif-images",
        description="Create elements on a corpus grouped by prefix from a list of IIIF paths.",
        help="Create elements on a corpus grouped by prefix from a list of IIIF paths.",
    )
    iiif_parser.add_argument(
        "input_file",
        help="Path to a local file containing IIIF images complete URIs, one by line.",
    )
    iiif_parser.add_argument(
        "--import-folder-name",
        help="Name of the main folder created to contain imported elements.",
        default="IIIF import",
    )
    iiif_parser.add_argument(
        "--import-folder-type",
        help="Type of the main folder created to contain imported elements.",
        default="folder",
    )
    iiif_parser.add_argument(
        "--element-type",
        help="type of elements created from IIIF paths.",
        default="page",
    )
    import_target = iiif_parser.add_mutually_exclusive_group(required=True)
    import_target.add_argument(
        "--corpus-id",
        help="UUID of the corpus to import images to.",
        type=UUID,
    )
    import_target.add_argument(
        "--parent-folder", help="UUID of the folder to import images to.", type=UUID
    )
    iiif_parser.add_argument(
        "--image-name-delimiter",
        help=(
            "Delimit the last part of the image URL path that should be used for the imported element name. "
            "Defaults to '/'."
        ),
        default="/",
    )
    iiif_parser.add_argument(
        "--group-folder-type",
        help=(
            "Type for sub-folders containing grouped IIIF images. "
            "This parameter requires prefix delimiter to be defined or keep-hierachy to be set."
        ),
    )
    group = iiif_parser.add_mutually_exclusive_group()
    group.add_argument(
        "--group-prefix-delimiter",
        help="If defined, create sub-folders containing IIIF images grouped by a similar name prefix. Conflicts with --keep-hierarchy",
    )
    group.add_argument(
        "--keep-hierarchy",
        help=(
            "Recreate an Arkindex folder hierarchy from the files' folders. Conflicts with --group-prefix-delimiter."
        ),
        default=False,
        action="store_true",
    )
    iiif_parser.set_defaults(func=run)


def create_element(client, corpus_id, name, elt_type, **kwargs):
    """
    Perform the creation of an element
    """
    try:
        return client.request(
            "CreateElement",
            body={"corpus": str(corpus_id), "name": name, "type": elt_type, **kwargs},
        )
    except ErrorResponse as e:
        print(
            "[bright_red]"
            f"Failed creating {elt_type} '{name}': {e.status_code} - {e.content}."
        )
        print("Aborting.")
        sys.exit(2)


def run(
    input_file: str,
    import_folder_name: str,
    import_folder_type: str,
    element_type: str,
    corpus_id: UUID | None = None,
    parent_folder: UUID | None = None,
    image_name_delimiter: str | None = "/",
    group_prefix_delimiter: str | None = None,
    group_folder_type: str | None = None,
    keep_hierarchy: bool | None = False,
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
) -> int:
    """
    Create elements in a corpus from a list of IIIF paths.
    A single folder will be created at the root of the corpus, with optional name and type.
    Sub-folders are created to group images by prefix if either keep_hierarchy is set or a
    group_prefix_delimiter is defined.
    """

    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        profiles = Profiles(gitlab_secure_file)
        profile = profiles.get_or_exit(profile_slug)
        client = profiles.get_api_client(profile)

    if parent_folder:
        try:
            parent_folder_info = client.request("RetrieveElement", id=parent_folder)
            corpus_id = parent_folder_info["corpus"]["id"]
        except ErrorResponse as e:
            if e.status_code == 404:
                raise Exception(
                    f"Parent folder {parent_folder} does not exist. Check the UUID."
                ) from None
            else:
                raise
        corpus_folders = [
            element_type["slug"]
            for element_type in client.request("RetrieveCorpus", id=corpus_id)["types"]
            if element_type["folder"] is True
        ]
        assert (
            parent_folder_info["type"] in corpus_folders
        ), f"Element {parent_folder} of type {parent_folder_info['type']} is not a folder."
        import_folder = create_element(
            client,
            str(parent_folder_info["corpus"]["id"]),
            import_folder_name,
            import_folder_type,
            parent=str(parent_folder),
        )
        print(
            f"Created import {import_folder_type} '{import_folder_name}' in parent '{parent_folder_info['name']}'"
        )
    else:
        import_folder = create_element(
            client, str(corpus_id), import_folder_name, import_folder_type
        )
        corpus_name = import_folder["corpus"].get("name", "—")
        print(
            f"Created import {import_folder_type} '{import_folder_name}' in corpus '{corpus_name}'"
        )

    group_folders = {}
    path_folders = {}
    for iiif_path in open(input_file).readlines():
        # Import and organize elements for each IIIF image
        iiif_url = iiif_path.strip()
        if not SIMPLE_URL_REGEX.match(iiif_url):
            # URI seems to be invalid
            print(f"[bright_yellow]Invalid IIIF url '{iiif_url}'. Skipping")
            continue

        print(f"Processing {iiif_url}")
        # iiif_url = urllib.parse.quote_plus(iiif_path)
        image = None
        try:
            image = client.request("CreateIIIFURL", body={"url": iiif_url})
            print(f"Created a new image on Arkindex - '{image['id']}'")
        except ErrorResponse as e:
            if e.status_code == 400 and "id" in e.content:
                # In case the image already exists, we retrieve its full information
                image = client.request("RetrieveImage", id=e.content["id"])
                print(f"Retrieved an existing image on Arkindex - '{image['id']}'")
            else:
                print(
                    "[bright_yellow]"
                    f"Failed creating iiif image {iiif_url}: {e.status_code} - {e.content}. Skipping"
                )
                continue
        try:
            client.request(
                "PartialUpdateImage", id=image["id"], body={"status": "checked"}
            )
        except ErrorResponse as e:
            print(
                "[bright_yellow]"
                f"Failed checking image {image['id']}: {e.status_code} - {e.content}. Skipping"
            )
            continue

        path = urlparse(iiif_path).path
        # Unquote to handle a proper image name
        path = unquote_plus(path)
        image_name, _ext = os.path.splitext(path.split(image_name_delimiter)[-1])

        parent = import_folder
        if group_prefix_delimiter:
            # Retrieve or create the group folder for this image
            group_name = image_name.split(group_prefix_delimiter)[0]
            if group_name not in group_folders:
                group_folders[group_name] = create_element(
                    client,
                    corpus_id,
                    group_name,
                    # Use default import folder type if groups type is undefined
                    group_folder_type or import_folder_type,
                    parent=import_folder["id"],
                )
            parent = group_folders[group_name]

        if keep_hierarchy:
            path = unquote_plus(iiif_path)
            path = path[len(image["server"]["url"]) :].replace("\n", "").split("/")
            # remove empty strings and image from path
            path = [f for f in path if f and image_name not in f]
            for folder in path:
                full_folder_name = "/".join(path[0 : path.index(folder) + 1])
                if full_folder_name not in path_folders:
                    path_folders[full_folder_name] = create_element(
                        client,
                        corpus_id,
                        folder,
                        # Use default import folder type if groups type is undefined
                        group_folder_type or import_folder_type,
                        parent=parent["id"],
                    )
                parent = path_folders[full_folder_name]

        # Create the final element for this image
        create_element(
            client,
            corpus_id,
            image_name,
            element_type,
            parent=parent["id"],
            image=image["id"],
        )
        print(f"Successfully created element {image_name} for image {iiif_url}")
