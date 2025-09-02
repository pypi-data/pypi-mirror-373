from osbot_aws.aws.lambda_.boto3__lambda import load_dependencies       # using the lightweight file (which only has the boto3 calls required to load_dependencies)

LAMBDA_DEPENDENCIES =  ['osbot-fast-api==v0.14.0', 'mangum']

load_dependencies(LAMBDA_DEPENDENCIES)

from osbot_fast_api_serverless.fast_api.Serverless__Fast_API import Serverless__Fast_API

with Serverless__Fast_API() as _:
    _.setup()
    handler = _.handler()
    app     = _.app()

def run(event, context=None):
    return handler(event, context)