import os
import requests

from velocity.aws.amplify import AmplifyProject

DEBUG = (os.environ.get("ENV") != "production") or (os.environ.get("DEBUG") == "Y")


# This is helpful for running HTTPS clients on lambda.
if os.path.exists("/opt/python/ca-certificates.crt"):
    os.environ["REQUESTS_CA_BUNDLE"] = "/opt/python/ca-certificates.crt"


class AWS(object):
    # Get AWS EC2 Instance ID. Must run this from the EC2 instance itself to get the ID
    @staticmethod
    def instance_id(cls):
        response = requests.get("http://169.254.169.254/latest/meta-data/instance-id")
        instance_id = response.text
        return instance_id


__all__ = ["AmplifyProject", "AWS"]
