import boto3
import time


class AmplifyProject:
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.amplify_client = boto3.client("amplify")
        self.lambda_client = boto3.client("lambda")
        self.sqs_client = boto3.client("sqs")
        self.sqs_resource = boto3.resource("sqs")

        # Verify app exists
        try:
            response = self.amplify_client.get_app(appId=self.app_id)
            self.app_name = response["app"]["name"]
        except self.amplify_client.exceptions.NotFoundException:
            raise ValueError(f"Amplify app with ID '{self.app_id}' does not exist.")

    def get_app_name(self):
        return self.app_name

    def get_region(self):
        return self.amplify_client.meta.region_name

    def get_account_id(self):
        sts_client = boto3.client("sts")
        return sts_client.get_caller_identity()["Account"]

    def list_backend_branches(self):
        branches = []
        paginator = self.amplify_client.get_paginator("list_branches")
        for page in paginator.paginate(appId=self.app_id):
            for branch in page.get("branches", []):
                branches.append(branch["branchName"])
        return branches

    def filtered_env_vars(self, raw_env_vars):
        return {k: v for k, v in raw_env_vars.items() if not k.startswith("_")}

    def get_merged_env_vars(self, branch):
        all_vars = {}

        # Global env vars
        app_response = self.amplify_client.get_app(appId=self.app_id)
        global_vars = self.filtered_env_vars(
            app_response["app"].get("environmentVariables", {})
        )
        # print("📦 Global env vars (All branches):")
        # for k, v in global_vars.items():
        #     print(f"  {k}: {v}")
        all_vars.update(global_vars)

        # Branch-specific vars
        try:
            branch_response = self.amplify_client.get_branch(
                appId=self.app_id, branchName=branch
            )
            branch_vars = self.filtered_env_vars(
                branch_response["branch"].get("environmentVariables", {})
            )
            # print(f"🌿 Branch-specific env vars for '{branch}':")
            # for k, v in branch_vars.items():
            #     print(f"  {k}: {v}")
            all_vars.update(branch_vars)
        except self.amplify_client.exceptions.BadRequestException:
            print(f"⚠️ Branch '{branch}' not found. Skipping branch-level overrides.")

        return all_vars

    def list_lambda_functions_filtered(self, env_name):
        paginator = self.lambda_client.get_paginator("list_functions")
        for page in paginator.paginate():
            for fn in page["Functions"]:
                name = fn["FunctionName"]
                if self.app_name in name and env_name in name:
                    yield fn

    def update_lambda_function(
        self,
        function_name,
        replace_env_vars=None,
        merge_env_vars=None,
        replace_vpc_config=None,
        merge_vpc_config=None,
        subnet_ids=None,
        security_group_ids=None,
        description=None,
        role=None,
        handler=None,
        runtime=None,
        timeout=None,
        memory_size=None,
        dead_letter_config=None,
        kms_key_arn=None,
        tracing_config=None,
        revision_id=None,
        layers=None,
        file_system_configs=None,
        image_config=None,
        ephemeral_storage=None,
        environment_secrets=None,
    ):
        # Fetch existing configuration
        config = self.lambda_client.get_function_configuration(
            FunctionName=function_name
        )

        update_params = {"FunctionName": function_name}

        # Environment variables: replace OR merge
        if replace_env_vars is not None and merge_env_vars is not None:
            raise ValueError(
                "Cannot specify both replace_env_vars and merge_env_vars at the same time."
            )

        if replace_env_vars is not None:
            update_params["Environment"] = {"Variables": replace_env_vars}
        elif merge_env_vars is not None:
            existing_env = config.get("Environment", {}).get("Variables", {})
            merged_env = {**existing_env, **merge_env_vars}
            update_params["Environment"] = {"Variables": merged_env}

        # Environment secrets (always merge style)
        if environment_secrets is not None:
            existing_secrets = config.get("Environment", {}).get("Secrets", {})
            merged_secrets = {**existing_secrets, **environment_secrets}
            if "Environment" not in update_params:
                update_params["Environment"] = {}
            update_params["Environment"]["Secrets"] = merged_secrets

        # VPC config: replace OR merge
        if replace_vpc_config is not None and merge_vpc_config is not None:
            raise ValueError(
                "Cannot specify both replace_vpc_config and merge_vpc_config at the same time."
            )

        vpc_config_to_apply = None

        if replace_vpc_config is not None:
            vpc_config_to_apply = replace_vpc_config
        else:
            # Start with existing or empty
            existing_vpc = config.get("VpcConfig", {})
            # print(f"Existing VPC config for {function_name}: {existing_vpc}")
            if "VpcId" in existing_vpc:
                del existing_vpc["VpcId"]  # Remove VpcId if present
            vpc_config_to_apply = dict(existing_vpc)

            if merge_vpc_config is not None:
                vpc_config_to_apply.update(merge_vpc_config)

            if subnet_ids is not None:
                vpc_config_to_apply["SubnetIds"] = subnet_ids

            if security_group_ids is not None:
                vpc_config_to_apply["SecurityGroupIds"] = security_group_ids

        # If vpc_config_to_apply has any keys, add to update_params
        if vpc_config_to_apply and any(vpc_config_to_apply.values()):
            update_params["VpcConfig"] = vpc_config_to_apply

        # Other parameters
        if description is not None:
            update_params["Description"] = description

        if role is not None:
            update_params["Role"] = role

        if handler is not None:
            update_params["Handler"] = handler

        if runtime is not None:
            update_params["Runtime"] = runtime

        if timeout is not None:
            update_params["Timeout"] = timeout

        if memory_size is not None:
            update_params["MemorySize"] = memory_size

        if dead_letter_config is not None:
            update_params["DeadLetterConfig"] = dead_letter_config

        if kms_key_arn is not None:
            update_params["KMSKeyArn"] = kms_key_arn

        if tracing_config is not None:
            update_params["TracingConfig"] = tracing_config

        if revision_id is not None:
            update_params["RevisionId"] = revision_id

        if layers is not None:
            update_params["Layers"] = layers

        if file_system_configs is not None:
            update_params["FileSystemConfigs"] = file_system_configs

        if image_config is not None:
            update_params["ImageConfig"] = image_config

        if ephemeral_storage is not None:
            update_params["EphemeralStorage"] = ephemeral_storage

        # Call update if needed
        if len(update_params) > 1:  # FunctionName is always present
            self.lambda_client.update_function_configuration(**update_params)
        else:
            print(f"No updates provided for Lambda function '{function_name}'.")

    def set_environment_variable(self, key: str, value: str, branch: str = None):
        if branch:
            response = self.amplify_client.get_branch(
                appId=self.app_id, branchName=branch
            )
            env_vars = response["branch"].get("environmentVariables", {})
            env_vars[key] = value
            self.amplify_client.update_branch(
                appId=self.app_id, branchName=branch, environmentVariables=env_vars
            )
        else:
            response = self.amplify_client.get_app(appId=self.app_id)
            env_vars = response["app"].get("environmentVariables", {})
            env_vars[key] = value
            self.amplify_client.update_app(
                appId=self.app_id, environmentVariables=env_vars
            )

    def update_custom_redirect_rules(self):
        srv_list = [
            "css",
            "gif",
            "ico",
            "jpg",
            "js",
            "json",
            "map",
            "otf",
            "png",
            "svg",
            "ttf",
            "txt",
            "webp",
            "woff",
            "xml",
            "pdf",
        ]
        self.amplify_client.update_app(
            appId=self.app_id,
            customRules=[
                {"source": "/<*>", "target": "/index.html", "status": "404-200"},
                {
                    "source": f'</^[^.]+$|\\.(?!({"|".join(srv_list)})$)([^.]+$)/>',
                    "target": "/",
                    "status": "200",
                },
            ],
        )

    def get_sqs_policy_template(
        self,
        queue_name: str,
        queue_producers: str,
        queue_handler: str,
    ) -> str:
        account_id = self.get_account_id()
        region = self.get_region()
        roles = [qp["Role"] for qp in queue_producers]
        return f"""
{{
  "Version": "2008-10-17",
  "Id": "__default_policy_ID",
  "Statement": [
    {{
      "Sid": "__owner_statement",
      "Effect": "Allow",
      "Principal": {{
        "AWS": "arn:aws:iam::{account_id}:root"
      }},
      "Action": "SQS:*",
      "Resource": "arn:aws:sqs:{region}:{account_id}:{queue_name}"
    }},
    {{
      "Sid": "__sender_statement",
      "Effect": "Allow",
      "Principal": {{
        "AWS": {repr(roles).replace("'", '"')}
      }},
      "Action": [
        "SQS:GetQueueAttributes",
        "SQS:SendMessage"
      ],
      "Resource": "arn:aws:sqs:{region}:{account_id}:{queue_name}"
    }},
    {{
      "Sid": "__receiver_statement",
      "Effect": "Allow",
      "Principal": {{
        "AWS": "{queue_handler["Role"]}"
      }},
      "Action": [
        "SQS:GetQueueAttributes",
        "SQS:ChangeMessageVisibility",
        "SQS:DeleteMessage",
        "SQS:ReceiveMessage"
      ],
      "Resource": "arn:aws:sqs:{region}:{account_id}:{queue_name}"
    }}
  ]
}}"""

    def get_lambda_vpc_policy_template(
        self,
    ) -> str:
        return """
 {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Resource": "*",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:CreateNetworkInterface",
                "ec2:AttachNetworkInterface",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeSecurityGroups",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupEgress",
                "cognito-idp:*"
            ],
        }
    ],
}"""

    def setup_sqs_queue_and_permissions(
        self,
        branch: str,
        queue_name: str,
        queue_producers: list,
        queue_handler: object,
        use_reserved_concurrency: bool = True,
    ):
        account_id = self.get_account_id()
        region = self.get_region()

        policy_json = self.get_sqs_policy_template(
            queue_name,
            queue_producers,
            queue_handler,
        )
        # print(f"Setting up SQS queue '{queue_name}' with policy:\n{policy_json}")
        try:
            queue = self.sqs_resource.get_queue_by_name(QueueName=queue_name)
            self.sqs_client.set_queue_attributes(
                QueueUrl=queue.url,
                Attributes={"Policy": policy_json, "VisibilityTimeout": "900"},
            )
        except self.sqs_client.exceptions.QueueDoesNotExist:
            queue = self.sqs_resource.create_queue(
                QueueName=queue_name,
                Attributes={"Policy": policy_json, "VisibilityTimeout": "900"},
            )

        try:
            self.lambda_client.create_event_source_mapping(
                EventSourceArn=f"arn:aws:sqs:{region}:{account_id}:{queue_name}",
                FunctionName=queue_handler["FunctionName"],
                Enabled=True,
                BatchSize=1,
            )
        except self.lambda_client.exceptions.ResourceConflictException:
            pass

        if use_reserved_concurrency:
            reserved = 10 if branch == "production" else 3
            try:
                self.lambda_client.put_function_concurrency(
                    FunctionName=queue_handler["FunctionName"],
                    ReservedConcurrentExecutions=reserved,
                )
            except Exception:
                self.lambda_client.delete_function_concurrency(
                    FunctionName=queue_handler["FunctionName"]
                )
        else:
            try:
                self.lambda_client.delete_function_concurrency(
                    FunctionName=queue_handler["FunctionName"]
                )
            except Exception:
                pass

    def check_policies(self, function):
        # Attach a role policy
        iam_client = boto3.client("iam")
        response = iam_client.list_attached_role_policies(
            RoleName=function["Role"].split("/")[1]
        )
        has_policy_attached = False
        for policy in response["AttachedPolicies"]:
            if policy["PolicyName"] == "lambda-vpc-execution":
                has_policy_attached = True
        if not has_policy_attached:
            account_id = self.get_account_id()
            iam_client.attach_role_policy(
                PolicyArn=f"arn:aws:iam::{account_id}:policy/lambda-vpc-execution",
                RoleName=function["Role"].split("/")[1],
            )
            time.sleep(15)
        has_policy_attached = False
        for policy in response["AttachedPolicies"]:
            if policy["PolicyName"] == "AmazonSQSFullAccess":
                has_policy_attached = True
        if not has_policy_attached:
            iam_client.attach_role_policy(
                PolicyArn="arn:aws:iam::aws:policy/AmazonSQSFullAccess",
                RoleName=function["Role"].split("/")[1],
            )

    def sync(self, branch):
        print(
            f"\n🚀 Syncing environment variables for app '{self.app_id}' and environment '{branch}'..."
        )
        env_vars = self.get_merged_env_vars(branch)

        print(f"\n🔧 Applying {len(env_vars)} environment variables...")
        for function_name in self.list_lambda_functions_filtered(branch):
            print(f"➡️ Updating Lambda function: {function_name}")
            self.update_lambda_function(function_name, env_vars)

        print(
            "✅ Environment variables successfully applied to matching Lambda functions.\n"
        )


def main():
    app_id = "d3c209q3ri53mk"
    app = AmplifyProject(app_id)
    print(app.list_backend_branches())


if __name__ == "__main__":
    main()
