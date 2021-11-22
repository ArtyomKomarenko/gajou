<h2>牙城</h2>

<h3>CLI</h3>

* BaseCLI - contains method to send command in terminal with logging. Allure can be passed for adding attaches to
  reports.
* CLIResponse - dataclass for CLI response deserialization.
* ReturnCodes - enum with basic CLI return codes.

<h3>HTTP</h3>

* BaseHTTP - contains all basic HTTP methods with logging. Verifies response status and raises one of errors if status
  is not 2xx. Allure can be passed for adding attaches to reports.
* HTTP errors - set of exceptions for typical HTTP error statuses.

<h3>gRPC</h3>

* BaseInterceptor - adds logging and verifies response status. Allure can be passed for adding attaches to reports.
* BaseStub - simple wrapper which adds BaseInterceptor to channel.
* GRPCError - base gRPC exception.

<h3>DB</h3>

* PostgresHelper - contains all basic commands with logging. Select-command supports simple caching. Can be useful with
  any query language like Pypika.
* DatabaseError - simple DB exception.
* Singleton - simple implementation of singleton used in DB helper to prevent unnecessary propagation of connections. 