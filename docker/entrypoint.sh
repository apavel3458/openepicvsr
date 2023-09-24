#!/bin/bash
# nohup bash -c "jupyter notebook --no-browser --allow-root --ip=0.0.0.0 --port=8070 &" && sleep 4
jupyter notebook --no-browser --allow-root --ip=0.0.0.0 --port=8070
# tail nohup.out