import boto3
import os


def handler(event, context):
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
        },
        count=1,
        platformVersion='LATEST',
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    'subnet-53f5bb0a',
                    'subnet-24bfda41'
                ],
                'assignPublicIp': 'ENABLED'
            }
        })
    print(response)
    print('Started ecs prediction task')
