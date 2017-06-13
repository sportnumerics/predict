import boto3
import os
import decimal

dynamodb = boto3.resource('dynamodb')
teams_table = dynamodb.Table(os.environ['TEAMS_TABLE_NAME'])

def round_float_to_decimal(float_value):
    """
    Convert a floating point value to a decimal that DynamoDB can store,
    and allow rounding.
    """

    # Perform the conversion using a copy of the decimal context that boto3
    # uses. Doing so causes this routine to preserve as much precision as
    # boto3 will allow.
    with decimal.localcontext(boto3.dynamodb.types.DYNAMODB_CONTEXT) as \
         decimalcontext:

        # Allow rounding.
        decimalcontext.traps[decimal.Inexact] = 0
        decimalcontext.traps[decimal.Rounded] = 0
        decimal_value = decimalcontext.create_decimal_from_float(float_value)

        return decimal_value

def serialize_rating(rating):
    return {
        'offense': round_float_to_decimal(rating['offense']),
        'defense': round_float_to_decimal(rating['defense']),
        'overall': round_float_to_decimal(rating['overall']),
    }

def persist(year, division, ratings):
    for team_id, rating in ratings.iteritems():
        teams_table.update_item(
            Key={'id': team_id, 'season': year},
            UpdateExpression='SET rating = :rating',
            ExpressionAttributeValues={
                ':rating': serialize_rating(rating)
            }
        )
