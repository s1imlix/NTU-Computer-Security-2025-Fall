<?php

use DI\Container;
use Slim\Factory\AppFactory;
use Doctrine\ODM\MongoDB\Configuration;
use Doctrine\ODM\MongoDB\Mapping\Driver\AttributeDriver; 
use Doctrine\ODM\MongoDB\DocumentManager;
use MongoDB\Client;

require_once __DIR__ . '/../vendor/autoload.php';

$container = new Container();
$container->set('documentManager', function() {
    $config = new Configuration();
    $cacheDir = __DIR__ . '/../cache';
    $config->setProxyDir($cacheDir . '/proxies');
    $config->setProxyNamespace('Proxies');
    $config->setHydratorDir($cacheDir . '/hydrators');
    $config->setHydratorNamespace('Hydrators');
    $config->setMetadataDriverImpl(AttributeDriver::create([__DIR__ . '/../src/Documents']));
    $config->setDefaultDB('doctrine_odm');
    $client = new Client('mongodb://mongo:27017');
    $dm = DocumentManager::create($client, $config);
    return $dm;
});
$container->set('memcached', function() {
    $memcached = new Memcached();
    $memcached->addServer('memcached', 11211);
    return $memcached;
});

AppFactory::setContainer($container);

$app = AppFactory::create();
$app->addBodyParsingMiddleware();
$app->addRoutingMiddleware();
$app->addErrorMiddleware(false, true, true);

return $app;
