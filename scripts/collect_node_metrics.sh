while true; do
  echo "=== NODE METRICS ==="
  date

  echo "--- CPU / MEMORY ---"
  kubectl top nodes

  echo "--- KUBELET PODS ---"
  kubectl get pods -A -o wide

  sleep 30
done