#!/bin/bash
cd initdb
python3 init_db.py
cd ..
pytest --tb=long -vv tests
