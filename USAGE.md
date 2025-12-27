# Usage Guide: HPC Assistant Server

This guide explains how to launch the HPC Assistant Server on a Slurm-managed HPC cluster and how to access it from your local machine.

## 1. Prerequisites

Before you begin, ensure you have the following:

*   Access to an HPC cluster with Slurm and GPUs.
*   [Poetry](https://python-poetry.org/docs/#installation) installed on your local machine and on the cluster.
*   The project code checked out on the cluster's filesystem.

## 2. Installation

First, install the required Python dependencies using Poetry.

```bash
cd /path/to/your/hpc-assistant
poetry install
```

This command will create a virtual environment and install all necessary packages.

## 3. Launching the Server

The server is designed to run as a job on a single compute node.

### 3.1. Create a Job Script

Create a file named `run_server.sbatch` with the following content. This script requests the necessary resources and starts the FastAPI server.

```bash
#!/bin/bash

# Slurm job configuration
#SBATCH --job-name=hpc-assistant
#SBATCH --output=hpc-assistant-%j.out
#SBATCH --error=hpc-assistant-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=60G
#SBATCH --time=1-00:00:00 # Request 1 day of runtime

# Activate the poetry environment
# Make sure your shell is configured to use poetry
# (e.g., by adding it to your .bashrc)
source $HOME/.poetry/env

# Navigate to the project directory
cd /path/to/your/hpc-assistant

# Launch the server on a specific port
# We choose port 8888, but you can change it.
poetry run uvicorn src.hpc_assistant.main:app --host 0.0.0.0 --port 8888
```

**Important:**
*   Replace `/path/to/your/hpc-assistant` with the actual path to the project directory.
*   Adjust the Slurm parameters (`--gres`, `--mem`, etc.) to match the resources specified in `spec.md` and your cluster's configuration.

### 3.2. Submit the Job

Submit the job to Slurm using `sbatch`:

```bash
sbatch run_server.sbatch
```

This will queue your job. Once it starts running, the server will be active on a compute node.

## 4. Accessing the Server from Off-Cluster

To use the API from your local machine, you need to forward a local port to the server running on the compute node.

### 4.1. Find Your Job\'s Node

First, find out which node your job is running on. Use `squeue` with your username:

```bash
squeue --me
```

Look for your `hpc-assistant` job in the output. The `NODELIST(REASON)` column will show the hostname of the compute node (e.g., `compute-node-123`).

### 4.2. Set Up an SSH Tunnel

Once you have the node name, open a **new terminal on your local machine** and run the following command to create an SSH tunnel:

```bash
ssh -L 8000:COMPUTE_NODE_HOSTNAME:8888 YOUR_USERNAME@CLUSTER_HOSTNAME
```

**Explanation:**
*   `-L 8000:COMPUTE_NODE_HOSTNAME:8888`: This forwards your local port `8000` to port `8888` on `COMPUTE_NODE_HOSTNAME`.
*   Replace `8000` with any available port on your local machine.
*   Replace `COMPUTE_NODE_HOSTNAME` with the node name you found in the previous step.
*   Replace `YOUR_USERNAME@CLUSTER_HOSTNAME` with your SSH login for the cluster\'s head node.

Keep this SSH session running. As long as it\'s active, the tunnel will be open.

## 5. Using the API

With the tunnel active, you can now interact with the server as if it were running on `localhost:8000`.

Here is an example of submitting a task using `curl`:

```bash
curl -X POST "http://localhost:8000/submit" \
     -H "Content-Type: application/json" \
     -d '{
           "workflow": "report_suggest_execute",
           "params": {
             "query": "benefits of using reinforcement learning for robotics"
           }
         }'
```

This will return a `job_id`. You can then use other endpoints to check the status or get the results:

```bash
# Check job status
curl http://localhost:8000/status/YOUR_JOB_ID

# Get job results
curl http://localhost:8000/results/YOUR_JOB_ID
```
