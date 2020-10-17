# syntax=docker/dockerfile:experimental
FROM continuumio/miniconda3:latest

# Set current workdir, we assume code is already in there
WORKDIR /immoproject

# Install git and SSH
RUN apt-get update && apt-get install wget git ssh -y

# Get the conda environment definition 
COPY environment.yml /immoproject/environment.yml

# Setup SSH connection (for other git repos), 
# and create the environment
# Remove the SSH key after use
ARG SSH_KEY
# SSH Key is first taken as a secret, then as env var
RUN --mount=type=secret,id=ssh_key mkdir /root/.ssh/ && \
    file="/run/secrets/ssh_key" && \
    if [ -f "$file" ] ; then cp $file /root/.ssh/id_rsa ; else echo "SSH Secret not found"; fi && \
    if [ ! -z "${SSH_KEY}" ]; then echo "$SSH_KEY" > /root/.ssh/id_rsa; fi && \
    chmod 600 /root/.ssh/id_rsa && \
    touch /root/.ssh/known_hosts && \
    ssh-keyscan github.gamma.bcg.com >> /root/.ssh/known_hosts && \
    conda env create -f /immoproject/environment.yml && \
    rm -rf /root/.ssh/id_rsa

# GUROBI licence setup
RUN --mount=type=secret,id=gur_key file="/run/secrets/gur_key" && \
    if [ -f "$file" ] ; then cp $file /root/gurobi.lic ; else echo "Gurobi Secret not found"; fi && \
    chmod 600 /root/gurobi.lic
ENV GRB_LICENSE_FILE=/root/gurobi.lic


# Activate the environment
RUN echo "source activate immoproject" > ~/.bashrc
ENV PATH /opt/conda/envs/immoproject/bin/:$PATH

#CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''","--NotebookApp.password=''"]
ENTRYPOINT ["tail", "-f", "/dev/null"]