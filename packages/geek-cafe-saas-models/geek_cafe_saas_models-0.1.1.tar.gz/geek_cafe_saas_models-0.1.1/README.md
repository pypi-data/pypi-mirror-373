# Geek Cafe SaaS Models

**NOTE: These models are in beta and are subject to change.**

## Overview
These are dynamodb and transport layer modules.  This heavily uses the `boto3-assist` library for dynamodb.  Feel free to checkout that project as well.

The models are free and open source.  We'll be using these models in our backend systems for production loads as well as for educational purposes.

My goal is to define an open architecture for SaaS Models which are used as transport (in flight api's) and storage models (database NoSQL or SQL models).  For DynamoDB, we use the `boto3-assist` library to interact with it, and we heavily use a single-table design pattern, with generic pk and sk attributes.  Your not force to use this pattern but it's built into the models.



## Developer Setup
Getting started is easy with our `./setup.sh` which will install the required dependencies and set up your environment.  The `./setup.sh` script is a wrapper around the `py-setup-tool` which is a tool for setting up Python projects.  I hope to turn the py-setup-tool into a proper module at some point, but for now the scripts should work.


## Final Notices

**Feel free to use these models "as-is" or fork it for your changes.**

Until a version 1.0.0 is released, these models are subject to change.  However since we're using these in our current production loads, we'll try to maintain backward compatibility as much as possible.


