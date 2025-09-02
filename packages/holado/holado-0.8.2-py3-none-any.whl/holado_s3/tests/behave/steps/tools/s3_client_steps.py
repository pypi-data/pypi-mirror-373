# -*- coding: utf-8 -*-

#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################


from holado_test.scenario.step_tools import StepTools
from holado.common.context.session_context import SessionContext
from holado_test.behave.behave import *  # @UnusedWildImport
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_scripting.common.tools.variable_manager import VariableManager
from holado_test.common.context.scenario_context import ScenarioContext
from holado_s3.tools.s3.boto3_s3_client import Boto3S3Client
from holado_s3.tools.s3.minio_client import MinioS3Client
import logging
from holado_core.common.exceptions.verify_exception import VerifyException
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from holado_test.behave.scenario.behave_step_tools import BehaveStepTools
from holado_scripting.text.verifier.text_verifier import TextVerifier
from holado_python.standard_library.typing import Typing

logger = logging.getLogger(__name__)


def __get_session_context() -> SessionContext:
    return SessionContext.instance()

def __get_scenario_context() -> ScenarioContext:
    return __get_session_context().get_scenario_context()

def __get_text_verifier() -> TextVerifier:
    return __get_scenario_context().get_text_verifier()

def __get_variable_manager() -> VariableManager:
    return __get_scenario_context().get_variable_manager()

def __get_path_manager():
    return SessionContext.instance().path_manager


################################################"
# Define steps specific to Minio S3 client
################################################"

if MinioS3Client.is_available():

    @Given(r"(?P<var_name>{Variable}) = new Minio S3 client")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)
        
        try:
            client = MinioS3Client(**kwargs)
        except Exception as exc:
            raise FunctionalException(str(exc)) from exc

        __get_variable_manager().register_variable(var_name, client)
        
    @Step(r"execute \[(?P<command>{Any})\] \(Minio S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, command, var_client):
        """
        Execute any method in class Minio (cf https://min.io/docs/minio/linux/developers/python/API.html).
        An exception is raised if the method returns a result.
        """
        # command = StepTools.evaluate_scenario_parameter(command)
        command = StepTools.evaluate_string_parameter(command)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable
        
        result = eval("client.internal_client." + command)
        if result:
            raise TechnicalException(f"Unexpected result to command [{command}]: {result}")
        
    @Step(r"(?P<var_name>{Variable}) = result of \[(?P<command>{Any})\] \(Minio S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, command, var_client):
        """
        Execute any method in class Minio (cf https://docs.min.io/docs/python-client-api-reference).
        The result is stored in given variable.
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        # command = StepTools.evaluate_scenario_parameter(command)
        command = StepTools.evaluate_string_parameter(command)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable
        
        result = eval("client.internal_client." + command)
        
        __get_variable_manager().register_variable(var_name, result)
        


################################################"
# Define steps specific to Boto3 S3 client
################################################"

if Boto3S3Client.is_available():

    @Given(r"(?P<var_name>{Variable}) = new Boto3 S3 client")
    def step_impl(context, var_name):
        var_name = StepTools.evaluate_variable_name(var_name)
        table = BehaveStepTools.convert_step_table_2_value_table_with_header(context.table)
        kwargs = ValueTableConverter.convert_name_value_table_2_dict(table)

        try:
            client = Boto3S3Client(**kwargs)
        except Exception as exc:
            raise FunctionalException(str(exc)) from exc

        __get_variable_manager().register_variable(var_name, client)

    @Step(r"execute \[(?P<command>{Any})\] \(Boto3 S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, command, var_client):
        """
        Execute any method in class S3.Client (cf https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html).
        An exception is raised if the method returns a result.
        """
        # command = StepTools.evaluate_scenario_parameter(command)
        command = StepTools.evaluate_string_parameter(command)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable

        result = eval("client.internal_client." + command)
        if result:
            raise TechnicalException(f"Unexpected result to command [{command}]: {result}")

    @Step(r"(?P<var_name>{Variable}) = result of \[(?P<command>{Any})\] \(Boto3 S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, command, var_client):
        """
        Execute any method in class S3.Client (cf https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html).
        The result is stored in given variable.
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        # command = StepTools.evaluate_scenario_parameter(command)
        command = StepTools.evaluate_string_parameter(command)
        client = StepTools.evaluate_variable_value(var_client)  # @UnusedVariable

        result = eval("client.internal_client." + command)

        __get_variable_manager().register_variable(var_name, result)
        


################################################"
# Define steps generic for any S3 client
################################################"

if MinioS3Client.is_available() or Boto3S3Client.is_available():
    
    @Step(r"(?P<var_name>{Variable}) = list of buckets \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            execute_steps(u"""
                {keyword} __RESULT_LIST_BUCKETS__@ = result of [list_buckets()] (Minio S3 client: {var_client})
                """.format(keyword=context.step.keyword, var_client=var_client) )
            result = __get_variable_manager().get_variable_value("__RESULT_LIST_BUCKETS__@")
            res = [bucket.name for bucket in result]
            __get_variable_manager().register_variable(var_name, res)
        elif isinstance(client, Boto3S3Client):
            execute_steps(u"""
                {keyword} __RESULT_LIST_BUCKETS__@ = result of [list_buckets()] (Boto3 S3 client: {var_client})
                """.format(keyword=context.step.keyword, var_client=var_client) )
            result = __get_variable_manager().get_variable_value("__RESULT_LIST_BUCKETS__@")
            res = [rb['Name'] for rb in result['Buckets']]
            __get_variable_manager().register_variable(var_name, res)
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        
    @Step(r"create bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, bucket, var_client):
        bucket = StepTools.evaluate_scenario_parameter(bucket)
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            execute_steps(u"""
                {keyword} execute [make_bucket('{bucket}')] (Minio S3 client: {var_client})
                """.format(keyword=context.step.keyword, bucket=bucket, var_client=var_client) )
        elif isinstance(client, Boto3S3Client):
            execute_steps(u"""
                {keyword} __RESULT__@ = result of [create_bucket(Bucket='{bucket}')] (Boto3 S3 client: {var_client})
                Then __RESULT__@['ResponseMetadata']['HTTPStatusCode'] == 200
                """.format(keyword=context.step.keyword, bucket=bucket, var_client=var_client) )
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        
    @Step(r"(?P<var_name>{Variable}) = list of objects in bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, bucket, var_client):
        """Get list of objects from a bucket.
        An optional table can be added to filter objects (cf S3 client documentation for a list of possible filters).
        Example: filter on 'Prefix'
        """
        var_name = StepTools.evaluate_variable_name(var_name)
        bucket = StepTools.evaluate_scenario_parameter(bucket)
        client = StepTools.evaluate_variable_value(var_client)
        table = BehaveStepTools.get_step_table(context)
        
        # Build command parameters
        if table:
            params = ValueTableConverter.convert_table_with_header_to_dict(table)
        else:
            params = {}
        if isinstance(client, MinioS3Client):
            if 'Prefix' in params:
                params['prefix'] = params.pop('Prefix')
            if 'recursive' not in params:
                params['recursive'] = True
        elif isinstance(client, Boto3S3Client):
            if 'MaxKeys' not in params:
                params['MaxKeys'] = client.MAX_KEYS
            if 'Delimiter' not in params:
                params['Delimiter'] = client.FAKE_DELIMITER
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        
        # Call command
        if params:
            params_str = ", " + ", ".join([f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in params.items()])
        else:
            params_str = ""
        if isinstance(client, MinioS3Client):
            execute_steps(u"""
                {keyword} __RESPONSE_LIST_OBJECTS__@ = result of [list_objects('{bucket}'{params})] (Minio S3 client: {var_client})
                {keyword} {var_name} = convert object value __RESPONSE_LIST_OBJECTS__@ to list
                """.format(keyword=context.step.keyword, var_name=var_name, bucket=bucket, params=params_str, var_client=var_client) )
        elif isinstance(client, Boto3S3Client):
            execute_steps(u"""
                {keyword} __RESPONSE_LIST_OBJECTS__@ = result of [list_objects_v2(Bucket='{bucket}'{params})] (Boto3 S3 client: {var_client})
                Then __RESPONSE_LIST_OBJECTS__@['ResponseMetadata']['HTTPStatusCode'] == 200
                Then __RESPONSE_LIST_OBJECTS__@['IsTruncated'] == False
                """.format(keyword=context.step.keyword, bucket=bucket, params=params_str, var_client=var_client) )
            result = __get_variable_manager().get_variable_value("__RESPONSE_LIST_OBJECTS__@")
            if 'Contents' in result:
                res = result['Contents']
            else:
                res = []
            __get_variable_manager().register_variable(var_name, res)
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        
    @Step(r"(?P<var_name>{Variable}) = list of object names in bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, bucket, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        
        execute_steps(format_step_with_context(context, 
                           u"__LIST_OBJECTS__@ = list of objects in bucket {bucket} (S3 client: {var_client})"
                           .format(bucket=bucket, var_client=var_client) ) )
        list_obj = __get_variable_manager().get_variable_value("__LIST_OBJECTS__@")
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            res = [obj.object_name for obj in list_obj]
        elif isinstance(client, Boto3S3Client):
            res = [obj['Key'] for obj in list_obj]
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        __get_variable_manager().register_variable(var_name, res)
        
    @Step(r"(?P<var_name>{Variable}) = data of object (?P<obj_name>{Str}) in bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, var_name, obj_name, bucket, var_client):
        var_name = StepTools.evaluate_variable_name(var_name)
        obj_name = StepTools.evaluate_scenario_parameter(obj_name)
        bucket = StepTools.evaluate_scenario_parameter(bucket)
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            execute_steps(u"""
                {keyword} __RESPONSE_GET__@ = result of [get_object('{bucket}', '{obj_name}')] (Minio S3 client: {var_client})
                {keyword} {var_name} = __RESPONSE_GET__@.data
                {keyword} __TMP__@ = __RESPONSE_GET__@.close()
                {keyword} __TMP__@ = __RESPONSE_GET__@.release_conn()
                """.format(keyword=context.step.keyword, var_name=var_name, obj_name=obj_name, bucket=bucket, var_client=var_client) )
        elif isinstance(client, Boto3S3Client):
            execute_steps(u"""
                {keyword} __RESPONSE_GET__@ = result of [get_object(Bucket='{bucket}', Key='{obj_name}')] (Boto3 S3 client: {var_client})
                {keyword} {var_name} = __RESPONSE_GET__@['Body'].read()
                """.format(keyword=context.step.keyword, var_name=var_name, obj_name=obj_name, bucket=bucket, var_client=var_client) )
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        
    @Step(r"put data (?P<data>{Str}) in object (?P<obj_name>{Str}) in bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, data, obj_name, bucket, var_client):
        data = StepTools.evaluate_scenario_parameter(data)
        obj_name = StepTools.evaluate_scenario_parameter(obj_name)
        bucket = StepTools.evaluate_scenario_parameter(bucket)
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            raise TechnicalException(fr"This sentence is not possible with Minio S3 client ; use instead \"{context.step.keyword} put file {{file_path}} in object {{obj_name}} in bucket {{bucket}} \(S3 client: {{var_client}}\)\"")
        elif isinstance(client, Boto3S3Client):
            if not isinstance(data, bytes):
                raise FunctionalException(f"Unmanaged data type '{Typing.get_object_class_fullname(data)}' (possible type: bytes)")
            result = client.internal_client.put_object(Bucket=bucket, Key=obj_name, Body=data)
            if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                raise TechnicalException(f"Failed to put data in object '{obj_name}' in bucket '{bucket}': {result['ResponseMetadata']}")
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        
    @Step(r"get file (?P<file_path>{Str}) from object (?P<obj_name>{Str}) in bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, file_path, obj_name, bucket, var_client):
        file_path = StepTools.evaluate_scenario_parameter(file_path)
        obj_name = StepTools.evaluate_scenario_parameter(obj_name)
        bucket = StepTools.evaluate_scenario_parameter(bucket)
        
        __get_path_manager().makedirs(file_path)
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            execute_steps(u"""
                {keyword} __STAT__@ = result of [fget_object('{bucket}', '{obj_name}', '{file_path}')] (Minio S3 client: {var_client})
                """.format(keyword=context.step.keyword, file_path=file_path, obj_name=obj_name, bucket=bucket, var_client=var_client) )
        elif isinstance(client, Boto3S3Client):
            execute_steps(u"""
                {keyword} execute [download_file(Bucket='{bucket}', Key='{obj_name}', Filename='{file_path}')] (Boto3 S3 client: {var_client})
                """.format(keyword=context.step.keyword, file_path=file_path, obj_name=obj_name, bucket=bucket, var_client=var_client) )
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        
    @Step(r"put file (?P<file_path>{Str}) in object (?P<obj_name>{Str}) in bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, file_path, obj_name, bucket, var_client):
        file_path = StepTools.evaluate_scenario_parameter(file_path)
        obj_name = StepTools.evaluate_scenario_parameter(obj_name)
        bucket = StepTools.evaluate_scenario_parameter(bucket)
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            execute_steps(u"""
                {keyword} __WRITE_RESULT__@ = result of [fput_object('{bucket}', '{obj_name}', '{file_path}')] (Minio S3 client: {var_client})
                """.format(keyword=context.step.keyword, file_path=file_path, obj_name=obj_name, bucket=bucket, var_client=var_client) )
        elif isinstance(client, Boto3S3Client):
            with open(file_path, 'rb') as fin:
                file_content = fin.read()
            __get_variable_manager().register_variable("__BYTES__@", file_content)
            execute_steps(u"""
                {keyword} put data __BYTES__@ in object '{obj_name}' in bucket '{bucket}' (S3 client: {var_client})
                """.format(keyword=context.step.keyword, obj_name=obj_name, bucket=bucket, var_client=var_client) )
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
    
    @Then(r"object named (?P<obj_name>{Str}) exists in bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, obj_name, bucket, var_client):
        obj_name = StepTools.evaluate_scenario_parameter(obj_name)
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            execute_steps(u"""
                Given __LIST_RESULT__@ = list of object names in bucket {bucket} (S3 client: {var_client})
                    | prefix     |
                    | '{prefix}' |
                """.format(bucket=bucket, var_client=var_client, prefix=obj_name) )
        elif isinstance(client, Boto3S3Client):
            execute_steps(u"""
                Given __LIST_RESULT__@ = list of object names in bucket {bucket} (S3 client: {var_client})
                    | Prefix     |
                    | '{prefix}' |
                """.format(bucket=bucket, var_client=var_client, prefix=obj_name) )
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        list_result = __get_variable_manager().get_variable_value("__LIST_RESULT__@")
        
        found = False
        for list_obj in list_result:
            found = __get_text_verifier().verify(list_obj, obj_name, raise_exception=False)
            if found:
                break
            
        if not found:
            raise VerifyException(f"Object '{obj_name}' doesn't exist in bucket '{StepTools.evaluate_scenario_parameter(bucket, log_level=logging.NOTSET)}' (existing {len(list_result)} objects: {list_result})")
    
    @Then(r"object named with prefix (?P<obj_name_prefix>{Str}) exists in bucket (?P<bucket>{Str}) \(S3 client: (?P<var_client>{Variable})\)")
    def step_impl(context, obj_name_prefix, bucket, var_client):
        obj_name_prefix = StepTools.evaluate_scenario_parameter(obj_name_prefix)
        
        client = StepTools.evaluate_variable_value(var_client)
        if isinstance(client, MinioS3Client):
            execute_steps(u"""
                Given __LIST_RESULT__@ = list of object names in bucket {bucket} (S3 client: {var_client})
                    | prefix     |
                    | '{prefix}' |
                """.format(bucket=bucket, var_client=var_client, prefix=obj_name_prefix) )
        elif isinstance(client, Boto3S3Client):
            execute_steps(u"""
                Given __LIST_RESULT__@ = list of object names in bucket {bucket} (S3 client: {var_client})
                    | Prefix     |
                    | '{prefix}' |
                """.format(bucket=bucket, var_client=var_client, prefix=obj_name_prefix) )
        else:
            raise TechnicalException(f"Unmanaged S3 client type {Typing.get_object_class_fullname(client)}")
        list_result = __get_variable_manager().get_variable_value("__LIST_RESULT__@")
        
        found = len(list_result) > 0
        if not found:
            raise VerifyException(f"Object with prefix '{obj_name_prefix}' doesn't exist in bucket '{StepTools.evaluate_scenario_parameter(bucket, log_level=logging.NOTSET)}' (existing {len(list_result)} objects: {list_result})")
  
