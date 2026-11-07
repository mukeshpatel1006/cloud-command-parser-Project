# source me: starts a port-forward to SeaweedFS and exports S3 env vars. Call `s3_stop` when done.
kubectl -n data port-forward svc/seaweedfs 8333:8333 >/dev/null 2>&1 &
S3_PF=$!
s3_stop() { kill $S3_PF 2>/dev/null || true; }
trap s3_stop EXIT
export S3_ENDPOINT=http://localhost:8333
export AWS_ACCESS_KEY_ID=$(kubectl -n data get secret s3-credentials -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d)
export AWS_SECRET_ACCESS_KEY=$(kubectl -n data get secret s3-credentials -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 -d)
for i in $(seq 1 30); do (echo > /dev/tcp/localhost/8333) 2>/dev/null && break; sleep 1; done
