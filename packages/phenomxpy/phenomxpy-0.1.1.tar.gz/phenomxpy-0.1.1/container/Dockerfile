FROM containers.ligo.org/docker/base:conda
LABEL name="phenomxpy CI testing" \
maintainer="Cecilio García Quirós"

COPY env-template.yml env.yml
ENV conda_env python310

RUN mamba env create -f env.yml -n ${conda_env} && mamba clean -afy
RUN echo "source activate ${conda_env}" > ~/.bashrc
ENV PATH /opt/conda/envs/${conda_env}/bin:$PATH
RUN /bin/bash -c "source activate ${conda_env}"
RUN mamba info
RUN python --version
