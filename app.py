#!/usr/bin/env python3

from aws_cdk import core

from batch_stack.fetch_and_run import FetchAndRunStack

app = core.App()
FetchAndRunStack(app, "fetch-and-run-stack")

app.synth()
