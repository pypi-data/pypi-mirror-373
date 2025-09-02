from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id        import Safe_Id
from osbot_utils.type_safe.Type_Safe    import Type_Safe

class Schema__AWS_Setup__Serverless__Fast_API(Type_Safe):
    bucket__osbot_lambdas__exists : bool
    bucket__osbot_lambdas__name   : Safe_Id
    current_aws_region            : Safe_Id
