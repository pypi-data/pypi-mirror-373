
#  Copyright (C) 2025 Y Hsu <yh202109@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public license as published by
#  the Free software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details
#
#  You should have received a copy of the GNU General Public license
#  along with this program. If not, see <https://www.gnu.org/license/>


import os
import json
import pandas as pd
import time
import numpy as np
import re
import xml.etree.ElementTree as ET

def find_domain_files(folder, domain="", extensions=None):
    if not os.path.exists(folder):
        return {}
    if extensions is None:
        extensions = ['.xpt', '.sas7bdat', '.csv']

    domain_files = {}
    for fname in os.listdir(folder):
        if extensions is None:
            if domain:
                if fname.lower().startswith(domain.lower()):
                    domain_files.setdefault(domain, []).append(os.path.join(folder, fname))
            else:
                # If domain is empty, include all files
                domain_files.setdefault('', []).append(os.path.join(folder, fname))
            continue
        # If extensions is a string, convert to list
        if isinstance(extensions, str):
            extensions = [extensions]
        # Only include files with allowed extensions
        if any(fname.lower().endswith(ext.lower()) for ext in extensions):
            if domain:
                if fname.lower().startswith(domain.lower()):
                    domain_files.setdefault(domain, []).append(os.path.join(folder, fname))
            else:
                domain_files.setdefault('', []).append(os.path.join(folder, fname))
    return domain_files

def _file_to_df(filepath, extension=None):
    if extension is None:
        _, extension = os.path.splitext(filepath)
        extension = extension.lower()
    elif isinstance(extension, str):
        if not filepath.lower().endswith(extension.lower()):
            print(f"File extension mismatch: {filepath} does not end with {extension}")
            return pd.DataFrame()
        extension = extension.lower()

    # Only allow .xpt, .sas7bdat, .csv
    allowed_exts = ['.xpt', '.sas7bdat', '.csv']
    if extension not in allowed_exts:
        print(f"Unsupported file type: {filepath}")
        return pd.DataFrame()
    
    try:
        if not os.path.isfile(filepath):
            print(f"File not found: {filepath}")
            return pd.DataFrame()
        if extension == '.xpt':
            return pd.read_sas(filepath, format='xport')
        elif extension == '.sas7bdat':
            return pd.read_sas(filepath, format='sas7bdat')
        elif extension == '.csv':
            return pd.read_csv(filepath)
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return pd.DataFrame()

class DefineXML:
    def __init__(self):
        self.meta = []
        self.ig_desc = []
        self.ig_structure = []
        self.ig_it_desc = []
    
    def read(self, filepath):
        if isinstance(filepath, str) and filepath and os.path.isfile(filepath) and filepath.lower().endswith('.xml'):
            self.filepath = filepath
        else:
            print(f"Invalid Define-XML file path: {filepath}")
            self.meta.append({"key": "error", "value": "define.xml not found (case-insensitive)", "ns": ""})
            return None

        try:
            with open(self.filepath, "rb") as fxml:
                first_line = fxml.readline()
                if first_line.startswith(b'<?xml') or first_line.startswith('<?xml'):
                    try:
                        first_line_str = first_line.decode("utf-8")
                        match1 = re.search(r'version="([^"]+)"', first_line_str)
                        match2 = re.search(r'encoding="([^"]+)"', first_line_str)
                    except Exception:
                        first_line_str = first_line.decode("latin1")
                if match1:
                    self.meta.append({"key": "xml_version", "value": match1.group(1), "ns": ""})
                if match2:
                    self.meta.append({"key": "xml_encoding", "value": match2.group(1), "ns": ""})
        except:
            self.meta.append({"key": "error", "value": "XML version not found in define.xml", "ns": ""})
        

        try:
            tree = ET.parse(self.filepath)
            node0 = tree.getroot()

            ns0_matched = re.match(r"^\{(.+)\}", node0.tag)
            ns0 = ns0_matched.group(1) if ns0_matched else None
            tag0 = re.sub(r'^\{.*\}', '', node0.tag)
            self.meta.append({"key": "root_tag", "value": tag0, "ns": ns0})

            for key, value in node0.attrib.items():
                if any(substring in key for substring in ["Version", "Date", "OID", "Source"]):
                    self.meta.append({"key": "root_"+key, "value": value, "ns": ""})

            for node1_idx, node1 in enumerate(node0):
                ns1_matched = re.match(r"\{(.+)\}Study", node1.tag)
                if ns1_matched:
                    ns1 = ns1_matched.group(1)
                    self.meta.append({"key": f"study{node1_idx}_OID", "value": node1.attrib.get('OID', ''), "ns": ns1})

                global_vars = node1.find(f"{{{ns1}}}GlobalVariables")
                if global_vars is not None:
                    for node3_idx, node3 in enumerate(global_vars):
                        if "}" in node3.tag:
                            ns3_matched = re.match(r"^\{(.+)\}", node3.tag)
                            ns3 = ns3_matched.group(1) if ns3_matched else ""
                            node3_tag_clean = re.sub(r'^\{.*\}', '', node3.tag)
                        else:
                            ns3 = ""
                            node3_tag_clean = node3.tag
                        self.meta.append({
                            "key": f"study{node1_idx}_gv{node3_idx}_{node3_tag_clean}",
                            "value": node3.text if node3.text is not None else '',
                            "ns": ns3
                        })

                mdv = node1.find(f"{{{ns1}}}MetaDataVersion")
                if mdv is not None:
                    ig_list = [c for c in mdv if re.sub(r'^\{.*\}', '', c.tag) == "ItemGroupDef"]
                    for ig_idx, ig in enumerate(ig_list):
                        ns4_matched = re.match(r"^\{(.+)\}", ig.tag)
                        ns4 = ns4_matched.group(1) if ns4_matched else ""

                        ig_attr_oid = ig.attrib.get("OID", "")
                        if ig_attr_oid.startswith("IG."):
                            ig_attr_oid = ig_attr_oid[3:]
                        self.ig_structure.append(ig_attr_oid)
                        self.ig_structure.append(ig_attr_oid+".Attr")

                        desc = ig.find(f"{{{ns4}}}Description")
                        if desc is not None:
                            translate_text = desc.find(f"{{{ns4}}}TranslatedText")

                        self.ig_desc.append({
                            "key": f"study{node1_idx}_mdv_Ig{ig_idx}_OID",
                            "value": ig_attr_oid,
                            "description": translate_text.text
                        })

                        for attr_key, attr_value in ig.attrib.items():
                            if attr_key.lower() == "oid":
                                continue
                            if attr_key.startswith("{"):
                                attr_key_clean = re.sub(r'^\{.*\}', '', attr_key)
                                attr_key_clean = attr_key_clean.replace('.', '__')
                            else:
                                attr_key_clean = attr_key.replace('.', '__')
                            attr_value_clean = attr_value.replace('.', '__')
                            self.ig_structure.append(ig_attr_oid + ".Attr." + attr_key_clean + ':' + attr_value_clean)


                        self.ig_structure.append(ig_attr_oid+".IT")
                        itemref_list = [itemref for itemref in ig if re.sub(r'^\{.*\}', '', itemref.tag) == "ItemRef"]
                        # Get last section of ig_attr_oid separated by "."
                        for itemref in itemref_list:
                            item_oid = itemref.attrib.get("ItemOID", "")
                            mandatory = itemref.attrib.get("Mandatory", "")
                            item_oid = re.sub(r'^\{.*\}', '', item_oid)
                            item_oid = item_oid.replace(f"IT.{ig_attr_oid}.", "IT.")
                            if item_oid:
                                if mandatory == "Yes":
                                    self.ig_structure.append(f"{ig_attr_oid}.{item_oid} (Mandatory)")
                                else:
                                    self.ig_structure.append(f"{ig_attr_oid}.{item_oid}")

                    itemdef_list = [c for c in mdv if re.sub(r'^\{.*\}', '', c.tag) == "ItemDef"]
                    for item_idx, itemdef in enumerate(itemdef_list):
                        item_flag=False
                        item_aval=False
                        item_oid = itemdef.attrib.get("OID", "")
                        item_domain = ""
                        item_col = ""
                        parts = item_oid.split(".")
                        if len(parts) >= 3:
                            if parts[0] == "IT":
                                item_domain = parts[1]
                                item_col = ".".join(parts[2:])
                            else:
                                item_domain = parts[0]
                                item_col = ".".join(parts[1:])
                        elif len(parts) == 2:
                            item_domain = parts[0]
                            item_col = parts[1]
                        else: 
                            item_col = item_oid

                        if item_oid.startswith("IT."):
                            item_oid = item_oid[3:]
                        if item_oid.endswith("FL"):
                            item_flag = True
                        if re.search(r".AVAL.", item_oid):
                            item_aval = True
                        desc = itemdef.find(f"{{{ns1}}}Description")
                        data_type = itemdef.attrib.get("DataType", "")
                        code_list_ref = itemdef.find(f"{{{ns1}}}CodeListRef")
                        code_list_oid = code_list_ref.attrib.get("CodeListOID", "") if code_list_ref is not None else ""
                        length = itemdef.attrib.get("Length", "")
                        if desc is not None:
                            translate_text = desc.find(f"{{{ns1}}}TranslatedText")
                            description = translate_text.text if translate_text is not None else ""
                        else:
                            description = ""
                        if item_oid:
                            self.ig_it_desc.append([item_idx, item_domain, item_col, data_type, length, description, code_list_oid, item_flag, item_aval])

        except Exception as e:
            self.meta.append({"key": "error", "value": f"XML parse error: {e}", "ns": ""})

        return {
            "meta": self.meta,
            "ig_desc": self.ig_desc,
            "ig_structure": self.ig_structure,
            "ig_it_desc": self.ig_it_desc
        }

if __name__ == "__main__":
    pass


