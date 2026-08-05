#!/bin/bash

python build_wallpapers.py

hugo

git add .

git commit -m "update blog"

git push