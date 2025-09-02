#!/bin/sh

py -m build
py -m twine upload dist/*