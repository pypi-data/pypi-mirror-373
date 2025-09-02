from mcp.server import FastMCP
import boto3
import json
import os
from botocore.exceptions import ClientError


aws_profile = os.getenv("AWS_PROFILE")
app = FastMCP("eks-infra-server")

@app.tool(description="""
    Get all the EKS clusters in the account.

    Use this tool:
        - when user asks for generating either audit summary or report of the EKS cluster and you dont have any cluster information or names.
        - when user says to tell all the EKS clusters

    This tools gets the list of all the EKS cluster.

    Example response:  List of EKS cluster in json string.

    Args:
        None

    Returns:
        List of EKS cluster in json string based on which AGENT can initiated next process
""")
def getListOfCluster() -> str:
    try:
        # Use AWS profile for boto3 session
        session = boto3.Session(profile_name=aws_profile)
        eks_client = session.client("eks")

        clusters = eks_client.list_clusters()["clusters"]

        return json.dumps(clusters, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})        


@app.tool(description="""
    Fetchs EKS cluster infra details such as:
        - EKS API endpoint
        - Logging Enabled
        - EKS Version
        - Encryption Configs
        - Node Groups: AMI Type, Instances Type, SSH Enabled or not, Subnets, Scaling Config
    
    Use this tool:
        - when user asks for generating either audit summary or report of the EKS cluster and you need information of the cluster and have cluster-name with you.
        - when user says to tell about the EKS cluster infra details

    Example response:  Structured Json string with all the information.

    Notes:
        - if you dont have cluster name kindly ask the user to provide the cluster name after you provide the list of cluster by calling tool 'getListOfCluster'

    Args:
        cluster_name: Type is string 

    Returns:
        Structured Json string with all the information.
""")
def getEksInfra(cluster_name: str) -> str:
    try:
        # Use AWS profile for boto3 session
        session = boto3.Session(profile_name=aws_profile)
        eks_client = session.client("eks")
        asg_client = session.client("autoscaling")

        # 1. Get EKS cluster details
        cluster_info = eks_client.describe_cluster(name=cluster_name)["cluster"]

        node_groups_details = {}
        # 2. Get all the nodegroup and their types
        node_groups = eks_client.list_nodegroups(clusterName = cluster_name)
        for node_group in node_groups["nodegroups"]:
            ng_info = eks_client.describe_nodegroup(
                clusterName=cluster_name,
                nodegroupName=node_group
            )

            ng=ng_info['nodegroup']
            node_groups_details[node_group] = {
                "version" : ng.get('version',''),
                'status':ng.get('status',''),
                'capacityType':ng.get('capacityType',''),
                'scalingConfig':ng.get('scalingConfig',''),
                'instanceTypes':ng.get('instanceTypes',''),
                'subnets':ng.get('subnets',''),
                'remoteAccess':ng.get('remoteAccess'),
                'amiType':ng.get('amiType')
            }
        # 3. Get add-on details
        addons = eks_client.list_addons(clusterName=cluster_name)["addons"]

        addon_details = {}
        for addon in addons:
            addon_info = eks_client.describe_addon(clusterName=cluster_name, addonName=addon)["addon"]
            addon_details[addon] = {"version": addon_info['addonVersion']}

        eks_details = {
            "cluster_name": cluster_info["name"],
            "status": cluster_info["status"],
            "version": cluster_info["version"],
            "endpoint": cluster_info["endpoint"],
            "roleArn": cluster_info.get("roleArn"),
            "vpc_config": cluster_info.get("resourcesVpcConfig", {}),
            "logging":cluster_info.get("logging"),
            "encryptionConfig":cluster_info.get("encryptionConfig"),
            "addons": addon_details,
            "node_groups" : node_groups_details
        }

        result = eks_details

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})

def main():
    app.run()

if __name__ == "__main__":
    main()
