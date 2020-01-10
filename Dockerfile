FROM fedora:latest

LABEL maintainer="Ralph Bean" \
      summary="Image used to publish markdown to confluence." \
      distribution-scope="public"

COPY . /usr/local/.

RUN dnf install -y --setopt=tsflags=nodocs \
                pandoc \
                lua \
                python-pypandoc \
                python-requests \
    && dnf clean all
