import boto3
import os
import time

def wait_for_cluster_spin_up(ecs_client, cluster):
    while True:
        print('Polling registered container count...')
        response = ecs_client.describe_clusters(cluster)
        count = response['clusters'][0]['registeredContainerInstancesCount']
        if count > 0:
            print('Container count is positive, continuing.')
            break
        time.sleep(10)

def handler(event, context):
    autoscaling = boto3.client('autoscaling')
    response = autoscaling.set_desired_capacity(
        AutoScalingGroupName=os.environ['AS_GROUP_NAME'],
        DesiredCapacity=1)
    print(response)
    print('Set desired capacity of prediction cluster to 1')

    ecs = boto3.client('ecs')
    wait_for_cluster_spin_up(
        ecs_client=ecs,
        cluster=os.environ['ECS_CLUSTER'])

    response = ecs.run_task(
        cluster=os.environ['ECS_CLUSTER'],
        taskDefinition=os.environ['ECS_TASK'],
        overrides={
            'containerOverrides': [
                {
                    'name': 'predict',
                    'environment': [
                        {
                            'name': 'PREDICTION_YEAR',
                            'value': event['year']
                        }
                    ]
                }
            ]
        })
    print(response)
    print('Started ecs prediction task')
