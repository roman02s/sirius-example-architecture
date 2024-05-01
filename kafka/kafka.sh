#!/bin/bash
kafka-topics --create --topic user-inputs --bootstrap-server localhost:29092
kafka-topics --create --topic assistant-responses --bootstrap-server localhost:29092
