import time

def retry(max_tries:int=3, expnential_backoff_c=1):
  """
  A decorator that provides a mechanism for retrying a function in case of exceptions.

  Args:
    max_tries (int): Maximum number of times the decorated function is allowed to be retried.
      Default value is 3.
    expnential_backoff_c (int/float): The factor by which the delay between retries is increased on each
      subsequent retry attempt. Default value is 1, meaning there will be no exponential backoff.

  Returns:
    A decorator that wraps the passed-in function, providing a mechanism for retrying it in case of exceptions.

  Example usage:
    @retry(max_tries=5, expnential_backoff_c=2)
    def foo():
      # function implementation
  """
  def decorator(func):
    def wrapper(*args, **kwargs):
      delay = 1
      for _ in range(max_tries):
        try:
          return func(*args, **kwargs)
        except Exception as e:
          print(f"Exception caught: {e}")
          time.sleep(delay)
          delay *= expnential_backoff_c
      raise Exception("Failed after multiple retries.")
    return wrapper
  return decorator