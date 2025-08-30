# LabCas Workflow

Run workflows for Labcas

Depending on what you do, there are multiple ways of running a labcase workflow:

- **Developers:** for developers: local run, natively running on your OS
- **Integrators:** for AWS Managed Apache Airflow integrators (mwaa), with a local mwaa
- **System Administrators:** for System administors, deployed/configured on AWS
- **End users:** For end users, using the AWS deployment.


## Developers

The tasks of the workflow run independently from Airflow. TODO: integrate to the airflow python API.

### Install

With python 3.11, preferably use a virtual environment


    pip install -e '.[dev]'

### Set AWS connection

    ./aws-login.darwin.amd64
    export AWS_PROFILE=saml-pub

### Run/Test the client

#### Without a dask cluster:

    python src/labcas/workflow/manager/main.py


#### With a local dask cluster

Start the scheduler:

    docker network create dask
    docker run --network dask -p 8787:8787 -p 8786:8786 labcas/workflow scheduler

Start one worker

    docker run  --network dask -p 8786:8786 labcas/workflow worker 


Start the client, same as in previous section but add the `tcp://localhost:8787` argument to the dask client in the `main.py` script 



### Deploy package on pypi

Upgrade the version in file "src/labcas/workflow/VERSION.txt"

Publish the package on pypi:

    pip install build
    pip install twine
    rm dist/*
    python -m build
    twine upload dist/*
   


## Integrators

### Build the Dask worker image

Update the labcas.workflow dependency version as needed in `docker/Dockerfile`, then:

    docker build -f docker/Dockerfile . -t labcas/workflow

### Create a managed AirFlow docker image to be run locally

Use repository https://github.com/aws/aws-mwaa-local-runner, clone it, then:

    ./mwaa-local-env build-image

Then from your local labcas_workflow repository:

    cd mwaa

As needed, update requirements in `requirements` directory and dags in `dags` directory.

### Update the AWS credentials

    aws-login.darwin.amd64
    cp -r ~/.aws .

### Launch the services
 
    docker compose -f docker-compose-local.yml up

Test the server on http://localhost:8080 , login admin/test

### Stop 

    Ctrl^C

### Stop and re-initialize local volumes

    docker compose  -f ./docker-compose-local.yml down -v

    

See the console on http://localhost:8080, admin/test

### Test the requirement.txt files
 
    ./mwaa-local-env test-requirements

### Debug the workflow import

    docker container ls

Pick the container id of image "amazon/mwaa-local:2_10_3", for example '54706271b7fc':

Then open a bash interpreter in the docker container:

    docker exec -it 54706271b7fc bash

And, in the bash prompt:

    cd dags
    python3 -c "import nebraska"


## System administrators

The deployment requires:
- one ECS cluster for the dask cluster.
- Optionally, an EC2 instance client of the Dask cluster
- One managed Airflow

### dask on ECS

Deploy the image created in the previous section on ECR

Have a s3 bucket `labcas-infra` for the terraform state.

Other pre-requisites are:
 - a VPC
 - subnets
 - a security group allowing incoming request whre the client runs, at JPL, on EC2 or Airflow, to port 8786 and port 8787
 - a task role allowing to write on CloudWatch
 - a task execution role which pull image from ECR and standard ECS task Excecution role policy "AmazonECSTaskExecutionRolePolicy"
 

Deploy the ECS cluster with the following terraform command:

    cd terraform
    terraform init
    terraform apply \
        -var consortium="edrn" \
        -var venue="dev" \
        -var aws_fg_image=<uri of the docker image deployed on ECR>
        -var aws_fg_subnets=<private subnets of the AWS account> \
        -var aws_fg_vpc=<vpc of the AWS account> \
        -var aws_fg_security_groups  <security group> \
        -var ecs_task_role <arn of a task role>
        -var ecs_task_execution_role <arn of task execution role>

### Test the dask cluster

#### Connect to an EC2 instance, client of the Dask cluster


    ssh {ip of the EC2 instance}
    aws-login
    export AWS_PROFILE=saml-pub
    git clone {this repository}
    cd workflows
    source venv/bin/activate
    python src/labcas/workflow/manager/main.py


To See Dask Dashboard, open SSH tunnels:

    ssh -L 8787:{dask scheduler ip on ECS}:8787 {username}@{ec2 instance ip}
    ssh -L 8787:{dask scheduler ip on ECS}:8787 {username}@{ec2 instance ip}

in browser: http://localhost:8787


### Apache Airflow

An AWS managed Airflow is deployed in version 2.10.3.

The managed Airflow is authorized to read and write in the data bucket.

The managed Airflow is authorized to access the ECS security group.

It uses s3 bucket {labcas_airflow}.

Upload to S3 the `./mwaa/requirements/requirements.txt` file to the bucket in: `s3:/{labas_airflow}/requirements/`

Upload to S3 the `./mwaa/dags/nebraska.py` file to the bucket in: `s3:/{labas_airflow}/dags/`

Update the version of the `requirements.txt` file in the Airflow configuration console.

Test, go the the Airflow web console, and trigger the nebraska dag.













