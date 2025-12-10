echo "STARTING PRODUCTION BUILD..."

cd broken-app 

npx tsc --noEmit 2>&1 | tee ../build.log

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -ne 0 ]; then
    echo "X BUILD FAILED! Sentinel has been notified via logs."
    exit 1
else
    echo "✓ SYSTEM IS STABLE"
    exit 0
fi