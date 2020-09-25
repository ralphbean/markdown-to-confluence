FROM fedora:latest

LABEL maintainer="Ralph Bean" \
      summary="Image used to publish markdown to confluence." \
      distribution-scope="public"

RUN dnf install -y --setopt=tsflags=nodocs \
                pandoc \
                lua \
    && dnf clean all

RUN pip3 install -r requirements.txt

COPY . /usr/local/.
