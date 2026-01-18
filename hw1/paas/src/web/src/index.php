<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Ping</title>
    <link href="/styles.css" rel="stylesheet">
  </head>
  <body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="bg-white shadow-lg rounded-2xl p-8 w-full max-w-lg">
      <h1 class="text-2xl font-bold text-gray-800 mb-6 text-center">
        Ping a Host
      </h1>

      <form method="POST" action="" class="flex space-x-2 mb-6">
        <input
          type="text"
          name="host"
          placeholder="Enter hostname or IP address"
          required
          class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          class="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
        >
          Ping
        </button>
      </form>

      <pre
        class="bg-gray-900 text-green-400 p-4 rounded-lg text-sm overflow-x-auto"
      ><?php if (
          $_SERVER["REQUEST_METHOD"] === "POST" &&
          isset($_POST["host"])
      ) {
          $host = $_POST["host"];
          $result = shell_exec("ping -c 4 $host");
          if ($result === null || $result === false) {
              echo "Network error or host unreachable";
          } else {
              // truncate output to 1024 characters
              if (strlen($result) > 1024) {
                  $result = substr($result, 0, 1024) . "...[truncated]";
              }
              echo htmlspecialchars($result);
          }
      } ?></pre>
    </div>
  </body>
</html>
