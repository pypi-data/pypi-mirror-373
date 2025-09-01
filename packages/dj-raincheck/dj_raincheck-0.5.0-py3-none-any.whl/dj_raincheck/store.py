from collections import deque

# Global queue that stores functions to be executed after the HTTP response is sent.
function_queue: deque = deque()
