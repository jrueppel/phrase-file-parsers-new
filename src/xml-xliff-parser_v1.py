import xml.etree.ElementTree as ET
import os
from xml.dom import minidom

def create_xliff(english_file, french_file, output_xliff):
    
    # Parse English strings
    en_tree = ET.parse(english_file)
    en_root = en_tree.getroot()
    en_strings = {elem.attrib['name']: elem.text or '' for elem in en_root.findall('string')}

    # Parse French strings
    fr_tree = ET.parse(french_file)
    fr_root = fr_tree.getroot()
    fr_strings = {elem.attrib['name']: elem.text or '' for elem in fr_root.findall('string')}

    # Create XLIFF structure
    xliff = ET.Element('xliff', {
        'version': '1.2',
        'xmlns': 'urn:oasis:names:tc:xliff:document:1.2'
    })
    file_elem = ET.SubElement(xliff, 'file', {
        'source-language': 'en',
        'target-language': 'fr',
        'datatype': 'plaintext',
        'original': 'strings'
    })
    body = ET.SubElement(file_elem, 'body')

    for key in en_strings:
        trans_unit = ET.SubElement(body, 'trans-unit', {'id': key})
        source = ET.SubElement(trans_unit, 'source')
        source.text = en_strings[key]

        target = ET.SubElement(trans_unit, 'target')
        target.text = fr_strings.get(key, '')

    # Write to XLIFF file (pretty printed)
    tree = ET.ElementTree(xliff)
    ET.indent(tree, space="  ", level=0)  # Python 3.9+ only
    tree.write(output_xliff, encoding='utf-8', xml_declaration=True)

def align_translations(english_file, french_file, output_file):
    # Parse English XML to get the correct order
    english_tree = ET.parse(english_file)
    english_root = english_tree.getroot()
    english_order = [elem.attrib['name'] for elem in english_root.findall('string')]
    
    # Parse French XML and create a map of name -> text
    french_tree = ET.parse(french_file)
    french_root = french_tree.getroot()
    french_map = {elem.attrib['name']: elem.text for elem in french_root.findall('string')}
    
    # Create a new root for the aligned French file
    new_root = ET.Element('resources')

    for name in english_order:
        text = french_map.get(name, '')
        new_elem = ET.Element('string', name=name)
        new_elem.text = text
        new_root.append(new_elem)
        
    # Convert ElementTree to a string
    rough_string = ET.tostring(new_root, encoding='utf-8')
    
    #use minidom to pretty-print with indentation and hard returns
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ") # 4 spaces for indentation

    # Write the new aligned French XML
    with open(output_file, 'w', encoding="utf-8") as f:
              f.write('<?xml version="1.0" encoding="utf-8"?>\n')
              lines=pretty_xml.splitlines()[1:]  
              f.write('\n'.join(lines))              
    
   
    #Let's create an xliff file for from those aligned xml files
    strings_en_fr_xliff = os.path.join(parent_dir, 'test', 'strings_en_fr_.xliff')
    create_xliff(english_file, output_file, strings_en_fr_xliff)

#The Business 

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
    
#Quick and Dirty - hard-coded file paths, modify as needed, to get to test directories & files    
xml_path_en = os.path.join(parent_dir, 'test', 'xml_strings_en.xml')
xml_path_fr_random = os.path.join(parent_dir, 'test', 'xml_strings_fr_misAligned.xml')
xml_path_fr_aligned = os.path.join(parent_dir, 'test', 'xml_strings_fr_aligned.xml')

#testing output paths if off by one
#print(xml_path_en)
#print(xml_path_fr_random)
#print(xml_path_fr_aligned)    

#Align 2 xml files that contain the same strings in a different order (let's assume these were built at different times)
#Generates target language file (FR) aligned to order of source language file (EN)
#Now - Also calls to embeddeed create_xliff() to generate clean xliff for translation for aligned files. 
align_translations(xml_path_en,xml_path_fr_random,xml_path_fr_aligned)