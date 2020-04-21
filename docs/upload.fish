#!/usr/bin/env fish

rm -rf _build

make html

cd _build/html

AWS_PROFILE=sugarush aws s3 cp --recursive . s3://sugar-api-docs-sugarush-io/
