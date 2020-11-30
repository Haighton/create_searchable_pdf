# Build: 
# docker build -t create_searchable_pdf .
#
# Run example:
# docker run -it \
#   --name create_bkt_pdf \
#   -v '/Volumes/Elements/testset_pdf/MMENK05_000000001_1_01/MMENK05_234392007:/usr/src/object' \
#   -v '/Volumes/Elements/testset_pdf/MMENK05_000000001_v4.xml:/usr/src/dump.xml' \
#   -v '/Users/haighton_macbook/Desktop:/usr/src/output' \
#   --rm create_searchable_pdf
#
# v1 = '/path/to/object_directory:/usr/src/object'
# v2 = '/path/to/Metadatadump.xml:/usr/src/dump.xml'
# v3 = '/path/to/output_folder:/usr/src/output'
#


# Use latest Linux Ubuntu as Base Image.
FROM ubuntu:latest

# Copy src dir to container as /usr/src and make wd.
COPY ./src /usr/src
WORKDIR /usr/src

# Install python3.8 and pip3.
RUN apt-get update && apt-get install -y \
    software-properties-common
RUN apt-get install -y \
    python3.8 \
    python3-pip \
    python2.7 \
    curl
RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
RUN python2.7 get-pip.py

# Install hOCR-tools.
RUN pip2 install hocr-tools

# Install Java.
RUN apt-get install -y openjdk-11-jdk

# Install python3 packages.
RUN pip3 install -r /usr/src/requirements.txt

ENTRYPOINT ["python3.8", "/usr/src/create_searchable_pdf.py"]