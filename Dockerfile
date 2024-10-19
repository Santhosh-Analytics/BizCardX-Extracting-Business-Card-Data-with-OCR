# Use Miniconda as the base image
FROM continuumio/miniconda3

# Install Mamba for faster package management
RUN conda install -n base -c conda-forge mamba

# Set the working directory inside the Docker container
WORKDIR /app

# Copy the environment.yml file to the working directory
COPY environment.yaml .

# Create the Conda environment using Mamba
RUN mamba env create -f environment.yaml

# Activate the Conda environment and ensure it remains active for subsequent commands
# Add the Conda environment to PATH for easier access to the environment's Python packages
ENV PATH /opt/conda/envs/BC/bin:$PATH

# Set the default shell to use the conda environment for all following commands
SHELL ["conda", "run", "-n", "BC", "/bin/bash", "-c"]

# Copy the requirements.txt file if it exists (handle the case where both Conda and pip are needed)
# COPY requirements.txt .

# Install additional pip dependencies if the requirements.txt file is present
# RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Check if Streamlit is installed in the activated environment
RUN streamlit --version

# Copy the rest of your app files into the working directory
COPY . .

# Expose the port that Streamlit uses
EXPOSE 8501

# Set the entry point to run your Streamlit app
CMD ["streamlit", "run", "BizCard_main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
