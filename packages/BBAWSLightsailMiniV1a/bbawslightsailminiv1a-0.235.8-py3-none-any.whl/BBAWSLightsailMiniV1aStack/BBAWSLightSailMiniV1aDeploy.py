import boto3
import subprocess
import json
import os
import time



class BBAWSLightsailMiniV1aDeploy:
    def __init__(self, product, app,  tier, organization, region="ca-central-1", docker_file="Dockerfile",
                 debug=True, version=1):
        self.organization = organization
        self.product = product
        self.app = app
        self.tier = tier
        self.region = region
        self.docker_file = docker_file
        self.debug = str(debug)
        self.version = str(version)
        self.allowed_hosts_csv = ""
        self.server_url_csv = "" 

        self.verbose = os.environ.get("VERBOSE", False)
        self.lightsail_service_name = f"{product}-{app}-{tier}".lower()
        self.container_name = self.lightsail_service_name
        self.secret_name = self.get_secret_name().lower()
        self.secret_path = self.get_secret_path()
        self.secrets_dict = {}

    def get_secret_path(self):
        secret_path = f"{self.organization}/{self.tier}/{self.product}-{self.app}-{self.tier}"
        print (f"Secret Path: {secret_path}")
        return secret_path

    def get_secret_name(self):
        return self.get_secret_path()

    def output(self, message, data=None):
        if self.verbose:
            print(message)
            if data:
                print(data)
        else:
            print(f">>> {message}")

    def run_cmd(self, cmd, capture_output=True):
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        if result.returncode != 0:
            print(f"Command failed: {cmd}")
            print(result.stderr)
            raise Exception(result.stderr)
        return result.stdout.strip()

    def get_docker_cache_images(self):
        self.output("Listing Docker Cache Images...")
        output = self.run_cmd("docker images")
        for line in output.splitlines():
            if self.lightsail_service_name in line:
                self.docker_cache_image = line
                return line
        return None

    def get_container_fqdn(self):
        self.output("Getting FQDN from AWS LightSail Directly...")
        result = self.run_cmd(f"aws lightsail get-container-services --region {self.region} --output json")
        services = json.loads(result).get("containerServices", [])
        service = next((s for s in services if s["containerServiceName"] == self.container_name), None)
        if not service:
            raise Exception(f"No service found with name: {self.container_name}")

        public_domains = service.get("publicDomainNames", {})
        service_url = service.get("url", "")
        domains = list(public_domains.keys()) + [service_url.replace("https://", "").replace("http://", "")]
        domains = list(set(filter(None, domains)))

        for domain in domains:
            if domain not in self.allowed_hosts_csv:
                self.allowed_hosts_csv += f",{domain}"

        self.allowed_hosts_csv = self.allowed_hosts_csv.strip(",/")
        self.output("Allowed Hosts CSV:", self.allowed_hosts_csv)
        return self.allowed_hosts_csv

    def authenticate_aws(self):
        self.output("Authenticating AWS...")
        self.run_cmd("aws sts get-caller-identity")

    def list_hosted_zones(self):
        self.output("Listing Hosted Zones...")
        self.run_cmd("aws route53 list-hosted-zones")

    def list_lightsail_images(self):
        self.output("Listing LightSail Container Images...")
        result = self.run_cmd(
            f"aws lightsail get-container-images --service-name {self.lightsail_service_name} --region {self.region}")
        return json.loads(result)

    def build_docker_image(self):
        if self.get_docker_cache_images():
            self.output(f"Using Docker Cached Image: {self.docker_cache_image}. Skipping Build.")
            return
        self.output("Building Docker image...")
        self.run_cmd(f"docker build -t {self.lightsail_service_name} .")

    def tag_docker_image(self):
        tag = str(int(time.time()))
        self.tag = f"{self.lightsail_service_name}:{tag}"
        self.run_cmd(f"docker tag {self.lightsail_service_name} {self.tag}")
        self.output("Tagged Docker Image:", self.tag)
        return tag

    def push_docker_image(self):
        self.output("Pushing Docker image to Lightsail...")
        cmd = (
            f"aws lightsail push-container-image "
            f"--region {self.region} "
            f"--service-name {self.lightsail_service_name} "
            f"--label {self.container_name} "
            f"--image {self.tag}"
        )
        result = self.run_cmd(cmd)
        image_ref = result.split('"')[-2]
        self.image_reference = f":{image_ref}"
        self.output("Captured image reference:", self.image_reference)
        return self.image_reference

    def get_all_secrets(self):
        client = boto3.client("secretsmanager", region_name=self.region)
        paginator = client.get_paginator("list_secrets")
        secrets = []

        for page in paginator.paginate():
            secrets.extend([s for s in page["SecretList"] if s["Name"].startswith(self.secret_path)])

        for secret in secrets:
            name = secret["Name"]
            response = client.get_secret_value(SecretId=name)
            self.secrets_dict[name.split("/")[-1]] = response["SecretString"]

        self.output("Loaded Secrets:", self.secrets_dict)

    def aws_get_secret(self):
        self.output("Getting secret string...")
        client = boto3.client("secretsmanager", region_name=self.region)


        print(f"Secret Name: {self.secret_name}")

        response = client.get_secret_value(SecretId=self.secret_name, VersionStage="AWSCURRENT")
        self.secret = response["SecretString"]
        return self.secret

    def deploy_docker_image(self):
        container_config = {
            self.container_name: {
                "image": self.image_reference,
                "environment": {
                    "VERSION": self.version,
                    "SERVER_URL_CSV": self.server_url_csv,
                    "DEBUG": self.debug,
                    "ALLOWED_HOSTS_CSV": self.allowed_hosts_csv,
                    "AWS_REGION": self.region,
                    "SECRET_STRING": self.secret,
                },
                "ports": {"80": "HTTP"},
            }
        }

        public_endpoint = {
            "containerName": self.container_name,
            "containerPort": 80,
            "healthCheck": {
                "path": "/",
                "intervalSeconds": 120,
                "timeoutSeconds": 60,
                "healthyThreshold": 5,
                "unhealthyThreshold": 5,
            }
        }

        cmd = (
            f"aws lightsail create-container-service-deployment "
            f"--region {self.region} "
            f"--service-name {self.lightsail_service_name} "
            f"--containers '{json.dumps(container_config)}' "
            f"--public-endpoint '{json.dumps(public_endpoint)}'"
        )
        self.run_cmd(cmd)
        self.output("Deployment Complete")

    def app_deploy(self):
        try:
            self.output("🐎 Starting app deployment pipeline 🐎")
            self.authenticate_aws()
            self.list_hosted_zones()
            self.aws_get_secret()
            self.get_container_fqdn()
            self.list_lightsail_images()
            self.build_docker_image()
            self.tag_docker_image()
            self.push_docker_image()
            self.deploy_docker_image()
            self.output("✅ App Deployment Completed Successfully!")
        except Exception as e:
            print("❌ ERROR DURING DEPLOYMENT:", e)
