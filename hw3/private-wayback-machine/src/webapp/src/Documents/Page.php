<?php

namespace App\Documents;

use Doctrine\ODM\MongoDB\Mapping\Annotations\Document;
use Doctrine\ODM\MongoDB\Mapping\Annotations\Id;
use Doctrine\ODM\MongoDB\Mapping\Annotations\Field;

#[Document(collection: "pages")]
class Page
{
    #[Id]
    private $id;

    #[Field(type: "string")]
    private $url;

    #[Field(type: "string")]
    private $sessionId;
    
    #[Field(type: "string")]
    private $content;

    public function __construct($url, $sessionId, $content)
    {
        $this->url = $url;
        $this->sessionId = $sessionId;
        $this->content = $content;
    }

    public function getId()
    {
        return $this->id;
    }

    public function getSessionId()
    {
        return $this->sessionId;
    }

    public function getUrl()
    {
        return $this->url;
    }

    public function getContent()
    {
        return $this->content;
    }
}
