<?php

use App\Documents\Page;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

require_once __DIR__ . '/../vendor/autoload.php';

error_reporting(0);
ini_set('display_errors', 0);
session_cache_limiter(false);
session_start();

$app = require_once __DIR__ . '/../config/bootstrap.php';

$app->get('/', function (Request $request, Response $response, $args) {
    $code = highlight_string(file_get_contents(__FILE__), true);
    $response->getBody()->write($code);
    return $response;
});

$app->post('/pages', function (Request $request, Response $response, $args) {
    $dm = $this->get('documentManager');
    $data = $request->getParsedBody();
    $url = $data['url'] ?? '';
    $sessionId = session_id();
    if (!$sessionId) {
        $response->getBody()->write("Invalid session.");
        return $response->withStatus(400);
    }
    if (
        gettype($url) === 'string' &&
        strlen($url) < 1024 &&
        filter_var($url, FILTER_VALIDATE_URL)
    ) {
        // Do not fetch the same URL if cache hits
        $memcached = $this->get('memcached');
        $cacheKey = hash('sha256', $url . '|' . $sessionId);
        $id = $memcached->get($cacheKey);
        if ($id) {
            return $response->withHeader('Location', value: '/pages/' . $id)->withStatus(302);
        }

        // Fetch the page content
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        $result = curl_exec(handle: $ch);
        curl_close($ch);

        // Validate fetched content
        if (!$result || strlen($result) > 2048) {
            $response->getBody()->write("Content too large or empty.");
            return $response->withStatus(400);
        }

        // Save the fetched content to the database
        $page = new Page($url, $sessionId, $result);
        $dm->persist($page);
        $dm->flush();

        // Cache the page ID for 1 minutes
        $memcached->set($cacheKey, $page->getId(), 60);
        return $response->withHeader('Location', '/pages/' . $page->getId())->withStatus(302);
    } else {
        $response->getBody()->write("Invalid URL provided.");
        return $response->withStatus(400);
    }
});

$app->get('/pages/{id}', function (Request $request, Response $response, $args) {
    if (!preg_match('/^[a-f0-9]{24}$/', $args['id'])) {
        $response->getBody()->write("Invalid page ID.");
        return $response->withStatus(400);
    }

    $dm = $this->get('documentManager');
    $page = $dm->getRepository(Page::class)->find($args['id']);
    if ($page && $page->getSessionId() === session_id()) {
        $response->getBody()->write($page->getContent());
        return $response->withHeader('Content-Security-Policy', "default-src 'none'; sandbox")->withStatus(200);
    } else {
        $response->getBody()->write("Page not found.");
        return $response->withStatus(404);
    }
});

$app->run();
