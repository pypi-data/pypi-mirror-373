import os
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def generate_sitemap(root_path, base_url, output_file="sitemap.xml", excluded_paths=None, show_progress=False):
    """
    Generates a sitemap XML file by crawling a directory structure.

    Parameters:
        root_path: The root directory of your website.
        base_url: The base URL of your website (e.g., "https://example.com").
        output_file: The name of the output XML file (default: "sitemap.xml").
        excluded_paths: A list of file paths or directories to exclude from the sitemap.
    """
    if excluded_paths is None:
        excluded_paths = []

    urlset = Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    urlset.set("xsi:schemaLocation", "http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd")

    for root, dirs, files in os.walk(root_path):
        # Add directories to the sitemap
        for dir_name in dirs:
            full_dir_path = os.path.join(root, dir_name)
            if any(excluded in full_dir_path for excluded in excluded_paths):
                continue
            if show_progress:
                print(f"Mapping directory: {full_dir_path}")
            relative_dir_path = os.path.relpath(full_dir_path, root_path)
            url = os.path.join(base_url, relative_dir_path).replace("\\", "/") + "/"
            lastmod = datetime.datetime.fromtimestamp(os.path.getmtime(full_dir_path)).isoformat()
            lastmod = lastmod[:lastmod.find(".")+4] + "+00:00"

            url_entry = SubElement(urlset, "url")
            SubElement(url_entry, "loc").text = url
            SubElement(url_entry, "lastmod").text = lastmod
            SubElement(url_entry, "priority").text = "0.80"

        for file in files:
            if file.endswith((".html", ".htm")):
                full_path = os.path.join(root, file)

                if show_progress:
                    print(f"Found file: {full_path}")

                relative_path = os.path.relpath(full_path, root_path)

                # Check if the file should be excluded
                if any(excluded in full_path for excluded in excluded_paths):
                    continue

                url = os.path.join(base_url, relative_path).replace("\\", "/")
                lastmod = datetime.datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat()
                lastmod = lastmod[:lastmod.find(".")+4] + "+00:00"

                url_entry = SubElement(urlset, "url")
                SubElement(url_entry, "loc").text = url
                SubElement(url_entry, "lastmod").text = lastmod
                SubElement(url_entry, "priority").text = "0.80"

    # Add homepage to the sitemap
    url_entry = SubElement(urlset, "url")
    SubElement(url_entry, "loc").text = base_url
    lastmod = datetime.datetime.fromtimestamp(os.path.getmtime(root_path)).isoformat()
    lastmod = lastmod[:lastmod.find(".")+4] + "+00:00"
    SubElement(url_entry, "lastmod").text = lastmod
    SubElement(url_entry, "priority").text = "1.00"

    # Write the XML to a file
    xml_string = tostring(urlset, "utf-8")
    reparsed = minidom.parseString(xml_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    if show_progress:
        print(f"Total pages mapped: {len(urlset)}")
        print(f"Saving sitemap to {output_file}...")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)