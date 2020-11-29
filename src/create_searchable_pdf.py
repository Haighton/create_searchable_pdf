#!/usr/bin/env python3
"""Create a searchable PDF from ALTO-XML files and JP2 image files.

# Create Searchable PDF from ALTO and scans

## Description

This script automates the process of creating a searchable PDF file that
conforms to de BKT2/BKT3 specifications of the National Library of the
Netherlands. This can be used when a delivered PDF for a digitized object is
corrupt or missing.

## Dependencies

### Stylesheet alto2hocr.xsl, which depends on codes_lookup.xml
[kba github](https://github.com/kba/hOCR-to-ALTO)
[direct link xsl](https://raw.githubusercontent.com/kba/hOCR-to-ALTO/master/alto2hocr.xsl)
[direct link xml](https://raw.githubusercontent.com/kba/hOCR-to-ALTO/master/codes_lookup.xml)

### Saxon-HE 9.7.0.21J
This version supports XSLT 2.0, also needs Java to be installed on the computer.
[download](https://sourceforge.net/projects/saxon/files/Saxon-HE/9.7/)
[documentation](https://www.saxonica.com/documentation9.7/documentation.xml)

### hocr-tools
This software can be installed with `python2 -m pip hocr-tools`
https://github.com/ocropus/hocr-tools

## Usage 
An object contains ALTO-XML files and JP2 image files.
`python3 create_searchable_pdf.py "/PATH/TO/OBJECT" "/PATH/TO/METADATADUMP"`


## To do
- Add Creator to PDF Document Info. 
specs: "de naam van de software die de oorspronkelijke scan heeft gecreëerd."
Moet uit de METS waarschijnlijk.
- Check vPDF version in specifications. PyPDF only makes version 1.3 (should
be 1.5?).
- Check JPG compression.
- Validate PDF.
- Dockerize.

testset:
/Users/haighton_macbook/Documents/KB/Data/testsets/MMECAL02_000000003_1_01/MMECAL02_179966004

/Users/haighton_macbook/Documents/KB/Data/testsets/templates/mets-templates/MMTUK04_000000002_v1/MMTUK04_000000002_v1.xml
"""

import sys
import os
import subprocess
from datetime import datetime

from PIL import Image
from lxml import etree
from PyPDF2 import PdfFileMerger
from tqdm import tqdm


TEMP_DIR = r'../output/tmp'
XSL_FILE = r'alto2hocr.xsl'
SAXON_JAR = r'SaxonHE9-7-0-21J/saxon9he.jar'


def alto_paths(path_object):
    """Gets paths of all alto.xml and access.jp2 files"""
    alto_files = []
    scans = []
    for dir_path, dirnames, filenames in os.walk(path_object):
        for filename in filenames:
            if filename.endswith('_alto.xml'):
                alto_files.append(os.path.join(dir_path, filename))
            elif filename.endswith('_access.jp2'):
                scans.append(os.path.join(dir_path, filename))
    if len(alto_files) != len(scans):
        print('Unequal number of ALTO and scans. Stopping!')
        sys.exit()
    else:
        return(alto_files, scans)


def alto2hocr(alto_files):
    """Converts ALTO XML to hOCR XML."""
    temp_hocr = []
    for alto_file in alto_files:
        filename = os.path.basename(alto_file)
        filename = filename.replace('_alto.xml', '')
        hocr_path = os.path.join(TEMP_DIR, filename + ".hocr")
        temp_hocr.append(hocr_path)

        # Call Saxon for XSL transformation.
        subprocess.call(['java', '-cp', SAXON_JAR,
                         'net.sf.saxon.Transform', '-t',
                         f'-s:{alto_file}',
                         f'-xsl:{XSL_FILE}',
                         f'-o:{hocr_path}'])
    return(temp_hocr)


def convert2jpg(scans):
    """Converts jp2 scans to jpg."""
    temp_images = []
    for scan in tqdm(scans):
        filename = os.path.basename(scan)
        filename = filename.replace('_access.jp2', '')
        im = Image.open(scan)
        out_path = os.path.join(TEMP_DIR, filename + '.jpg')
        temp_images.append(out_path)
        im.save(out_path)
    return(temp_images)


def create_pdf(TEMP_DIR, path_object):
    """Combines hOCR and JPG into a searchable PDF."""
    fname = os.path.basename(path_object) + '_pdf.pdf'
    path_pdf = os.path.join(TEMP_DIR, fname)
    subprocess.call(f'hocr-pdf {TEMP_DIR} > {path_pdf}',
                    shell=True)
    return(path_pdf)


def add_pdf_did(path_batch, path_mddump, path_pdf):
    with open(path_mddump, 'rb') as mddump_xml:
        dump = etree.parse(mddump_xml)
        # barcode = os.path.basename(path_batch)
        object_id = 'MMTUK04210988001'
        material = dump.xpath('/shipment/@material')[0]
        # print(material)

        try:
            if material == 'tijdschriften' or material == 'kranten':
                referredRecordID = dump.xpath(f'//issue[@ID="{object_id}"]\
                                              /@referredRecordID')[0]
                sourceProvider = dump.xpath(f'//issue[@ID="{object_id}"]\
                                            /parent::entity/@sourceProvider')[0]
                shelfmark = dump.xpath(f'//issue[@ID="{object_id}"]\
                                       /parent::entity/@shelfmark')[0]
                title = dump.xpath(f'//record[@ID="{referredRecordID}"]\
                                   /@title')[0]
                # issue_nr = dump.xpath(f'//issue[@ID="{object_id}"]/@issueNo')[0]
                volumeNo = dump.xpath(f'//issue[@ID="{object_id}"]\
                                      /@volumeNo')[0]

            if material == 'tijdschriften':
                sequenceNo = dump.xpath(f'//issue[@ID="{object_id}"]\
                                        /@sequenceNo')[0]
                volumeYear = dump.xpath(f'//issue[@ID="{object_id}"]\
                                        /@volumeYear')[0]

                if dump.xpath(f'//issue[@ID="{object_id}"]/@part'):
                    part = dump.xpath(f'//issue[@ID="{object_id}"]/@part')
                else:
                    part = ''
                publicationYear = dump.xpath(f'//issue[@ID="{object_id}"]\
                                             /@publicationYear')[0]

                if dump.xpath(f'//issue[@ID="{object_id}"]/@publicationMonth'):
                    publicationMonth = dump.xpath(f'//issue[@ID="{object_id}"]\
                                                  /@publicationMonth')[0]
                else:
                    publicationMonth = ''
                if dump.xpath(f'//issue[@ID="{object_id}"]/@publicationDay'):
                    publicationDay = dump.xpath(f'//issue[@ID="{object_id}"]\
                                                /@publicationDay')[0]
                else:
                    publicationDay = ''
                publicationType = dump.xpath(f'//issue[@ID="{object_id}"]\
                                             /@publicationType')[0]

            if material == 'kranten':
                publicationDate = dump.xpath(f'//issue[@ID="{object_id}"]\
                                             /@publicationDate')[0]
                edition = dump.xpath(f'//issue[@ID="{object_id}"]/@edition')[0]
                issue_nr = dump.xpath(f'//issue[@ID="{object_id}"]\
                                      /@issueNo')[0]

            if material == 'boeken':
                referredRecordID = dump.xpath(f'//entity[@ID="{object_id}"]\
                                              /@referredRecordID')[0]
                sourceProvider = dump.xpath(f'//entity[@ID="{object_id}"]\
                                            /@sourceProvider')[0]
                shelfmark = dump.xpath(f'//entity[@ID="{object_id}"]\
                                       /@shelfmark')[0]
                title = dump.xpath(f'//record[@ID="{referredRecordID}"]\
                                   /@title')[0]
                author = dump.xpath(f'//record[@ID="{referredRecordID}"]\
                                    /@author')[0]
                issued = dump.xpath(f'//record[@ID="{referredRecordID}"]\
                                    /@issued')[0]
                sequenceNo = dump.xpath(f'//entity[@ID="{object_id}"]\
                                        /@sequenceNo')[0]
                if dump.xpath(f'//entity[@ID="{object_id}]"/@part'):
                    part = dump.xpath(f'//entity[@ID="{object_id}]"/@part')[0]
                else:
                    part = ''
        except IndexError as e:
            print(e)

    # Material specific metadata.
    if material == 'tijdschriften':
        pdf_title = f'{title}, jrg. {volumeNo}, {volumeYear}, {part}, {publicationDay}, {publicationMonth}, {publicationYear}, [{publicationType}, volgnr. {sequenceNo}], {sourceProvider}, {shelfmark}'
        keywords = 'Gedigitaliseerd door de Koninklijke Bibliotheek; Nederlandse geschiedenis; tijdschriften, historische tijdschriften, oude tijdschriften, archief tijdschriften, tijdschrift online, cultuur, letterkunde, religie, wetenschap, politiek, sport, economie'
    elif material == 'kranten':
        pdf_title = f'{title}, jrg. {volumeNo}, {issueNo}, {publicationDate}, editie {edition}, {sourceProvider}, {shelfmark}'
        keywords = 'Gedigitaliseerd door de Koninklijke Bibliotheek; Nederlandse geschiedenis; kranten, historische kranten, oude kranten, archief kranten, krantenarchieven, krant online, familieberichten, stamboom familie, dagblad, overlijdensberichten, nieuwsberichten, Nederlandstalige kranten, namen familie, familie Nederland, oorlogskranten, kranten van toen, Surinaamse kranten, Indische kranten, Antilliaanse kranten, databank kranten'
    elif material == 'boeken':
        pdf_title = f'{title}, {part}, {sequenceNo}, {author}, {issued}, {sourceProvider}, {shelfmark}'
        keywords = 'Gedigitaliseerd door de Koninklijke Bibliotheek; Nederlandse geschiedenis; boeken, oude drukken, Nederlands taalgebied, geschiedenis, politiek, theologie, letterkundige werken, naamlijsten, boeken online, historische teksten, oude boeken, bijzondere collecties, cultuur'


    # Add metadata as Document Information to PDF.
    now = datetime.now()
    pdf_datestamp = now.strftime("D:%Y%m%d%H%M%S+01'00'")

    merger = PdfFileMerger()
    merger.append(path_pdf)

    merger.addMetadata({
        '/Title': pdf_title,
        '/Keywords': keywords,
        '/CreationDate': pdf_datestamp,
        '/ModDate': pdf_datestamp,
        '/Copyright-information': 'Gedigitaliseerd door de Koninklijke Bibliotheek, de Nationale Bibliotheek van Nederland  / Digitised by  the Koninklijke Bibliotheek, the National Library of the Netherlands'
    })
    if material == 'boeken':
        merger.addNetadata({
            '/Author': author
        })
    # Save final PDF in output folder.
    merger.write(f'../output/{os.path.basename(path_pdf)}')
    merger.close()


if __name__ == '__main__':
    # Create output and tmp folders.
    if not os.path.exists('../output'):
        try:
            os.mkdir('../output')
            os.mkdir('../output/tmp')
        except OSError:
            print('Creation of output directory failed!')

    if not os.path.exists('../output/tmp'):
        try:
            os.mkdir('../output/tmp')
        except OSError:
            print("can't make ../output/tmp directory!")


    print('\nLooking for files.')
    alto_files, scans = alto_paths(sys.argv[1])

    print('\nTransforming ALTO-XML into hOCR.')
    temp_hocr = alto2hocr(alto_files)

    print('\nConverting JP2 files into JPG.')
    temp_images = convert2jpg(scans)

    print('\nCreating searchable PDF file.')
    path_pdf = create_pdf(TEMP_DIR, sys.argv[1])
    add_pdf_did(sys.argv[1], sys.argv[2], path_pdf)

    # Remove tmp files and folder.
    temp_files = temp_hocr + temp_images + [path_pdf]
    for temp_file in temp_files:
        os.remove(temp_file)
    os.rmdir('../output/tmp')

    print(f'\nCreated searchable PDF in {os.getcwd()}/output/{os.path.basename(path_pdf)}')
    print('\nDONE!')
