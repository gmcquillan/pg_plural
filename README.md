# pg_plural

PLProxy-based Sharding for high throughput OLAP systems.

![Shard Elephant](media/shard_elephant.png)

## Slides


```bash

npm install grunt
cd slides/reveal.js && grunt serve
```

## Ansible Automation

```bash
#Instal vagrant/virtualbox somehow
cd ansible
vagrant up
ssh-add ~/.vagrant.d/insecure_private_key
cd pg_plural
ansible-playbook site.yml
```
