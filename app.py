#!/usr/bin/env python3

from aws_cdk import core

from batch_stack.batch_stack_stack import BatchStackStack


app = core.App()
BatchStackStack(app, "batch-stack")

app.synth()
