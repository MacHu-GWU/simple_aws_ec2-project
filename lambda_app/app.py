# -*- coding: utf-8 -*-

from chalice import Chalice
from simple_aws_ec2.lbd import hello

app = Chalice(app_name="simple_aws_ec2")


@app.lambda_function(name="hello")
def handler_hello(event, context):
    return hello.high_level_api(event, context)
