import numpy as np
from xml.etree import ElementTree


def infer_header_size(file_path: str):
    "Find the size of the header of a rec file"
    with open(file_path, "rb") as file:
        # Find the header size by searching for the '</Configuration>' marker
        marker = b"</Configuration>"
        marker_size = len(marker)
        header_size = file.read().find(marker) + marker_size

    return header_size


def get_header(file_path):
    "Get header of a rec file"
    header_size = infer_header_size(file_path)
    with open(file_path, mode="rb") as f:
        header_txt = f.read(header_size).decode("utf8")
    return header_txt


def xml_string_to_dict(xml_string):
    "Parse XML to python dictionary"
    root = ElementTree.fromstring(xml_string)

    # Recursive function to convert an XML element to a dictionary
    def element_to_dict(element):
        result = {}
        if element.attrib:
            result.update(element.attrib)
        for child in element:
            child_dict = element_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict
        # if element.text:
        #     result[element.tag] = element.text
        if (
            element.text and element.text.strip()
        ):  # Check if text content exists and is not just whitespace
            result[element.tag] = element.text.strip()
        return result

    return element_to_dict(root)


def read_one_packet(file_path, start_packet_location, packet_size):
    with open(file_path, "rb") as file:
        # Set the file position to the location of the first packet
        file.seek(start_packet_location)
        packet = file.read(packet_size)
        return packet


def bytes_to_integer(data, signed=False):
    return int.from_bytes(data, byteorder="little", signed=False)


# # Example
# header_packet_size = infer_header_size('20230411_174940.rec')
# header = get_header('20230411_174940.rec')
# header_dict = xml_string_to_dict(header)
# # sum over all the devices to get packet header size
# packet_header_size = np.sum([int(header_dict['HardwareConfiguration']['Device'][i]['numBytes']) for i in range(len(header_dict['HardwareConfiguration']['Device']))])
# # must add another 4 bytes for the trodes timestamp (sample count)
# packet_header_size = packet_header_size + 4
# packet_ephys_size = int(header_dict['HardwareConfiguration']['numChannels'])*2
# packet = read_one_packet('20230411_174940.rec', header_packet_size+1, packet_header_size+packet_ephys_size)
# bytes_to_integer(packet[50:54])
