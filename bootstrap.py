import boto3
import os

def handler(event, context):
    autoscaling = boto3.client('autoscaling')
    response = autoscaling.set_desired_capacity(
        AutoScalingGroupName=os.environ['AS_GROUP_NAME'],
        DesiredCapacity=1)
    print(response)
    print('Set desired capacity of prediction cluster to 1')
    
    ecs = boto3.client('ecs')
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
