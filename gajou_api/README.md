<h2>牙城</h2>

<h3>HTTP</h3>

* BaseHTTP - contains all basic HTTP methods with logging. Verifies response status and raises one of errors if status
  is not 2xx. Allure can be passed for adding attaches to reports.
* RetrySession - simple implementation of retrying requests for flaky cases.
* HTTP errors - set of exceptions for typical HTTP error statuses.

<h3>gRPC</h3>

* BaseInterceptor - adds logging and verifies response status. Allure can be passed for adding attaches to reports.
* BaseStub - simple wrapper which adds BaseInterceptor to channel.
* GRPCError - base gRPC exception.
