# syntax=docker/dockerfile:1
FROM node:20-bullseye


# Install Chromium and wkhtmltopdf + Python
RUN apt-get update && apt-get install -y \
chromium \
wkhtmltopdf \
python3 python3-pip \
&& rm -rf /var/lib/apt/lists/*


WORKDIR /tool
COPY openapi_to_pdf.py /tool/openapi_to_pdf.py


# Run commands via bash so npx can fetch redoc-cli on demand
ENTRYPOINT ["bash", "-lc"]