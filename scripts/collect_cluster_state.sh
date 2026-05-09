#!/bin/bash

apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: k8s-node-agent
spec:
  selector:
    matchLabels:
      app: node-agent
  template:
    metadata:
      labels:
        app: node-agent
    spec:
      serviceAccountName: k8s-monitor
      containers:
      - name: agent
        image: your-image:latest
        command:["/bin/bash", "/scripts/collect_node_metrics.sh"]
        volumeMounts:
        - name: scripts
          mountPath: /scripts
      volumes:
      - name: scripts
        configMap:
          name: k8s-scripts