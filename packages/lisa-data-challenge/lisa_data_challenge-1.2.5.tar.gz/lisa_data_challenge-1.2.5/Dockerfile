FROM gitlab-registry.in2p3.fr/lisa/lisa-cde:0.4.0
USER root
RUN apt-get -y update \
    && apt-get -y --no-install-recommends install \
        wget \
        liblapacke-dev \
        nano \
        python3-venv

RUN pip3 install \
    --no-cache-dir \
    mistune==0.8.4 \
    sphinx==6.2.1 \
    sphinx_rtd_theme \
    mkdocs-material \
    m2r2 \
    tqdm \
    pytest \
    lisagwresponse

#RUN pip3 install setuptools --upgrade

RUN mkdir /codes
COPY FastEMRIWaveforms /codes/FastEMRIWaveforms
RUN rm -r /codes/FastEMRIWaveforms/docs

RUN mkdir /codes/LDC
COPY .git /codes/LDC/.git
COPY ldc /codes/LDC/ldc
COPY test /codes/LDC/test
COPY doc /codes/LDC/doc
COPY data_generation /codes/LDC/data_generation
COPY README.md setup.py pyproject.toml requirements.txt requirements.jupyter.txt /codes/LDC/
WORKDIR /codes/LDC
RUN pip3 install -r requirements.txt
RUN pip3 install .
#RUN python3 setup.py install
#RUN python3 setup.py clean --all
#WORKDIR /codes/LDC/ldc/lisa/orbits/lib
#RUN make

WORKDIR /codes/FastEMRIWaveforms
RUN sed -i 's/"hdf5_hl"/"hdf5_hl", "lapacke"/' setup.py
RUN LDSHARED='h5c++ -shlib -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions  -Wl,-z,relro -g -fwrapv -O2    ' CC='h5c++ -shlib' CXX='h5c++ -shlib' python3 setup.py install clean --all
WORKDIR /codes/LDC/test
RUN python3 install_emri_files.py

# this does not work on the current image as lisagwresponse requires python 3.10+
# for the types annotations
# RUN pytest test_tdi_sbbh.py
RUN python3 -c "import fastGB;print('ok')"
RUN python3 -c "import fastAK;print('ok')"
RUN python3 -c "import pyimrphenomD;print('ok')"

USER lisauser
