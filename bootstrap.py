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
        })
    print(response)
    print('Started ecs prediction task')
