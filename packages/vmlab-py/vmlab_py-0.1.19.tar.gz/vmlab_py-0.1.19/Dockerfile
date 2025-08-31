# FROM arm64v8/python:3.12.0
FROM quay.io/pypa/manylinux_2_28_aarch64


RUN yum install -y python3.11 python3.11-pip python3.11-devel gcc gcc-c++ make

RUN ln -sf /usr/bin/python3.11 /usr/bin/python

# Install Rust using rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Rust to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /project

COPY . .

# password as a build argument
ARG PASS

RUN pip3 install maturin

RUN maturin build --release --compatibility 'manylinux_2_28'

RUN maturin upload target/wheels/vmlab_py*linux*.whl --username __token__ --password $PASS
