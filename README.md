This script automates the process of creating a searchable PDF file that
conforms to de BKT2/BKT3 specifications for digitized historical material of the National Library of the
Netherlands | KB. This can be used when a delivered PDF for a digitized object is
corrupt or missing.

The script is based around [hocr-pdf](https://github.com/ocropus/hocr-tools#hocr-pdf) from [hocr-tools](https://github.com/ocropus/hocr-tools), which can create a searchable PDF from a directory of JPEG and hOCR files.

To be able to use hocr-pdf the ALTO-XML files have to be converted into hOCR files. This is done by an XSL transformation using [alto2hocr.xsl](https://github.com/kba/hOCR-to-ALTO) in [Saxon-HE 9.7.0.21J](https://www.saxonica.com/documentation9.7/documentation.xml). The JP2 scans, which is the format the KB uses for digitized historical material, have to be converted to JPEG. It also needs a Metadatadump XML file which contains information about the object which have to be put in the Document Information of the final PDF.