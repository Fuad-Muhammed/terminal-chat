# FIXME - Known Issues

## Client Shutdown Error (Priority: Medium)

**Issue**: Asyncio event loop error when closing the client with Ctrl+C or /quit command

**Error Details**:
```
RuntimeError: Task <Task pending name='Task-39' coro=<ChatClient.shutdown() running at /home/fuad/.asdf/installs/python/3.14.0t/lib/python3.14/site-packages/client/main.py:279>> got Future <Future pending cb=[_chain_future.<locals>._call_check_cancel() at /home/fuad/.asdf/installs/python/3.14.0t/lib/python3.14/asyncio/base_events.py:181]> attached to a different loop
```

**Stack Trace**:
- Originates from `client/main.py:279` in `shutdown()` method
- Related to `connection.disconnect()` call at `client/main.py:288`
- Involves `websocket.close()` operation at `client/connection.py:66`
- Error occurs in asyncio's `send_context()` and event loop handling

**Root Cause**:
The client shutdown process is attempting to run async operations (websocket disconnect) but the event loop context is being torn down, causing futures to be attached to different event loops.

**Location**: `client/main.py:279-288` (shutdown method)

**Reproduction**:
1. Start the client: `python -m client.main`
2. Connect to server
3. Press Ctrl+C or type `/quit`
4. Error appears in traceback after client exits

**Impact**:
- Client does exit successfully despite the error
- Error messages are displayed to user on exit (poor UX)
- No data loss or corruption
- Purely a cleanup/shutdown issue

**Proposed Solutions**:
1. Wrap disconnect operations in proper exception handling
2. Ensure connection cleanup happens before event loop is closed
3. Use `asyncio.shield()` to protect shutdown tasks
4. Add proper task cancellation handling
5. Consider using `asyncio.wait_for()` with timeout for graceful shutdown

**References**:
- Python asyncio documentation on proper shutdown procedures
- Textual app shutdown lifecycle
- WebSocket client cleanup best practices

**Notes**:
- This is a graceful degradation issue - functionality works, just noisy on exit
- May be related to Textual's app shutdown sequence
- Should investigate `client.run()` in `client/main.py:334` and its interaction with `asyncio.run()`
