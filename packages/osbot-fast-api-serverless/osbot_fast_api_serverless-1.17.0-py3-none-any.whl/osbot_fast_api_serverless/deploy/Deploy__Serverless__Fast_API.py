from osbot_utils.utils.Http                                                    import GET_json
from osbot_utils.utils.Objects                                                 import obj
from osbot_aws.aws.lambda_.Lambda                                              import DEFAULT__LAMBDA__EPHEMERAL_STORAGE, DEFAULT__LAMBDA__MEMORY_SIZE
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency                     import Lambda__Dependency
from osbot_utils.type_safe.primitives.safe_str.identifiers.Random_Guid         import Random_Guid
from osbot_utils.utils.Env                                                     import get_env
from osbot_fast_api.api.Fast_API                                               import ENV_VAR__FAST_API__AUTH__API_KEY__NAME, ENV_VAR__FAST_API__AUTH__API_KEY__VALUE
from osbot_aws.AWS_Config                                                      import AWS_Config
from osbot_aws.deploy.Deploy_Lambda                                            import Deploy_Lambda
from osbot_utils.decorators.methods.cache_on_self                              import cache_on_self
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                                               import Safe_Id
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from osbot_fast_api_serverless.deploy.Schema__AWS_Setup__Serverless__Fast_API  import Schema__AWS_Setup__Serverless__Fast_API

BASE__LAMBDA_NAME__FAST_API__SERVERLESS  = 'fast-api__serverless'        # make this a Safe_Str__Lambda_Name
DEFAULT__ERROR_MESSAGE__WHEN_FAST_API_IS_OK = ('The adapter was unable to infer a handler to use for the '
                                                'event. This is likely related to how the Lambda function was '
                                                'invoked. (Are you testing locally? Make sure the request '
                                                'payload is valid for a supported handler.)')

class Deploy__Serverless__Fast_API(Type_Safe):
    aws_config       : AWS_Config
    stage            : Safe_Id = Safe_Id('dev')
    ephemeral_storage: int = DEFAULT__LAMBDA__EPHEMERAL_STORAGE
    memory_size      : int = DEFAULT__LAMBDA__MEMORY_SIZE

    @cache_on_self
    def api_key__name(self):
        return get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME, "api_key__name")

    @cache_on_self
    def api_key__value (self):
        return get_env(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, Random_Guid())

    @cache_on_self
    def s3(self):
        return self.lambda_function().s3()

    @cache_on_self
    def deploy_lambda(self):
        kwargs = dict(lambda_name       = self.lambda_name()    ,
                      stage             = self.stage            ,
                      ephemeral_storage = self.ephemeral_storage,
                      memory_size       = self.memory_size      )
        with Deploy_Lambda(self.handler(), **kwargs) as _:
            _.add_file__boto3__lambda()                     # this file allows the dynamically load of dependencies
            _.set_env_variable(ENV_VAR__FAST_API__AUTH__API_KEY__NAME , self.api_key__name ())
            _.set_env_variable(ENV_VAR__FAST_API__AUTH__API_KEY__VALUE, self.api_key__value())
            return _

    def delete(self):
        return self.lambda_function().delete()

    def create(self):
        if self.create_or_update__lambda_function():
            self.create__lambda_function__url()
            return True
        return False

    def create_or_update__lambda_function(self):
        with self.deploy_lambda() as _:
            result = _.update()
            if result == "Successful":
                return True
            if result == 'Pending':
                result = self.lambda_function().wait_for_function_update_to_complete(wait_time=0.5)                # todo: see if there a is a better to proactively handle the first install (I think the delay that happens on first install is caused by the download of the docker image for running the lambda inside localstack)
                if result == "Successful":
                    return True
            raise Exception(f"Lambda update failed: {result}")

    def create__lambda_function__url(self):
        with self.lambda_function() as _:
            if _.function_url_exists():
                function_url = _.function_url()
            else:
                result = _.function_url_create_with_public_access()
                function_url = result.get('function_url_create').get('FunctionUrl')
            return function_url

    def invoke(self, payload=None):
        return self.lambda_function().invoke(payload)

    def invoke__function_url(self, path=''):
        with self.lambda_function() as _:
            url     = _.function_url() +  path
            headers = { self.api_key__name(): self.api_key__value()}
            return GET_json(url, headers=headers)

    def handler(self):                                                          # override to control target
        from osbot_fast_api_serverless.fast_api.lambda_handler import run
        return run

    def lambda_configuration(self):
        return obj(self.lambda_function().info().get('Configuration'))

    def lambda_dependencies(self):                                              # override to control lambdas dependencies to install, upload and use
        from osbot_fast_api_serverless.fast_api.lambda_handler import LAMBDA_DEPENDENCIES
        return LAMBDA_DEPENDENCIES

    def lambda_name(self):
        return BASE__LAMBDA_NAME__FAST_API__SERVERLESS

    def lambda_function(self):
        return self.deploy_lambda().lambda_function()

    def lambda_files_bucket_name(self):
        return self.lambda_function().s3_bucket

    def setup_aws_environment(self):

        kwargs = dict(bucket__osbot_lambdas__exists = self.s3().bucket_exists(self.lambda_files_bucket_name()),
                      bucket__osbot_lambdas__name   = self.lambda_files_bucket_name(),
                      current_aws_region            = self.aws_config.region_name())

        aws_setup = Schema__AWS_Setup__Serverless__Fast_API(**kwargs)
        with aws_setup as _:
            if _.bucket__osbot_lambdas__exists is False:
                result = self.s3().bucket_create(_.bucket__osbot_lambdas__name, _.current_aws_region)
                if result.get('status') == 'ok':
                    _.bucket__osbot_lambdas__exists = True
                else:
                    raise Exception(result)
        return aws_setup


    def upload_lambda_dependencies_to_s3(self):
        upload_results = {}
        for package_name in self.lambda_dependencies():
            with Lambda__Dependency(package_name=package_name) as _:
                upload_results[package_name] = _.install_and_upload()
        return upload_results

        # with Lambda__Upload_Package() as _:
        #     return _.upload_lambda_dependencies(LAMBDA_DEPENDENCIES)
        #     status__packages = {}
            # for package in LAMBDA_DEPENDENCIES:
            #     if
            #     with capture_duration()  as duration__install_locally:
            #         result__install_locally = lambda_upload_package.install_locally(package)
            #     with capture_duration() as duration__upload_to_s3:
            #         result__upload_to_s3    = lambda_upload_package.upload_to_s3(package)
            #
            #     status__package = dict(duration__install_locally = duration__install_locally.seconds,
            #                            duration__upload_to_s3    = duration__upload_to_s3   .seconds,
            #                            result__install_locally   = result__install_locally  ,
            #                            result__upload_to_s3      = result__upload_to_s3     )
            #     status__packages[package] = status__package
            # return status__packages


