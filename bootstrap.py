import boto3
import os

def handler(event, context):
    client = boto3.client('ecs')
    response = client.run_task(cluster=os.environ['ECS_CLUSTER'], taskDefinition=os.environ['ECS_TASK'])
    print(response)
