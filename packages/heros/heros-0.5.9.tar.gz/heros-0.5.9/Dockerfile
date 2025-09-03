# #########################################################################################
# Build image with everything required to run local and remote HEROS
# #########################################################################################

FROM python:3-slim

# Copy the contents of the repository into the image
WORKDIR /git
COPY . heros

# Install HEROS in editable mode
RUN pip install --break-system-packages -e heros/
